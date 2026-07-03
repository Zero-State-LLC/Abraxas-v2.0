import { afterEach, describe, expect, it, vi } from 'vitest';
import { sampleProjectionBundle } from './sampleProjectionBundle';
import {
  normalizePollMs,
  parseProjectionStreamMessage,
  resolveProjectionFeedConfig,
  startProjectionFeed,
  type ProjectionFeedEvent,
} from './liveProjectionFeed';

class FakeWebSocket {
  static instances: FakeWebSocket[] = [];

  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onopen: (() => void) | null = null;
  readonly url: string;

  constructor(url: string) {
    this.url = url;
    FakeWebSocket.instances.push(this);
  }

  close = vi.fn();
}

describe('liveProjectionFeed', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    FakeWebSocket.instances = [];
  });

  it('accepts valid projection stream messages', () => {
    const result = parseProjectionStreamMessage(JSON.stringify(sampleProjectionBundle));
    expect(result.source_mode).toBe('LIVE_ARTIFACT_BUNDLE');
    expect(result.bundle.systems.length).toBe(sampleProjectionBundle.systems.length);
  });

  it('fails closed on invalid projection stream messages', () => {
    const result = parseProjectionStreamMessage('{not-json');
    expect(result.source_mode).toBe('FAIL_CLOSED');
    expect(result.fail_closed_reason).toMatch(/not valid JSON/i);
  });

  it('normalizes unsafe poll intervals to the deterministic default', () => {
    expect(normalizePollMs('10')).toBe(5000);
    expect(normalizePollMs('2500')).toBe(2500);
    expect(resolveProjectionFeedConfig({}).wsUrl).toBeNull();
  });

  it('emits websocket messages as live stream events', () => {
    const events: ProjectionFeedEvent[] = [];
    const stop = startProjectionFeed((event) => events.push(event), {
      wsUrl: 'ws://localhost/viz',
      pollMs: 5000,
      WebSocketCtor: FakeWebSocket as unknown as typeof WebSocket,
      now: () => 'viz01-ts',
    });

    const socket = FakeWebSocket.instances[0];
    socket?.onopen?.();
    socket?.onmessage?.({
      data: JSON.stringify(sampleProjectionBundle),
    } as MessageEvent);

    expect(events.map((event) => event.connection_status)).toContain('LIVE_STREAM');
    expect(events[events.length - 1]?.transport_mode).toBe('WEBSOCKET');
    expect(events[events.length - 1]?.fallback_reason).toBeNull();
    stop();
    expect(socket?.close).toHaveBeenCalled();
  });

  it('falls back to polling when no websocket URL is configured', async () => {
    const events: ProjectionFeedEvent[] = [];
    const clearIntervalFn = vi.fn();
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => sampleProjectionBundle,
      }),
    );

    const stop = startProjectionFeed((event) => events.push(event), {
      wsUrl: null,
      pollMs: 5000,
      now: () => 'viz01-poll-ts',
      setIntervalFn: (() => 1) as typeof window.setInterval,
      clearIntervalFn: clearIntervalFn as unknown as typeof window.clearInterval,
    });

    await vi.waitFor(() => {
      expect(
        events.some((event) => event.connection_status === 'POLLING_FALLBACK'),
      ).toBe(true);
    });

    const pollEvent = events.find((event) => event.connection_status === 'POLLING_FALLBACK');
    expect(pollEvent?.transport_mode).toBe('POLLING');
    expect(pollEvent?.fallback_reason).toBe('WS_URL_UNSET');
    expect(pollEvent?.last_updated).toBe('viz01-poll-ts');
    stop();
    expect(clearIntervalFn).toHaveBeenCalledWith(1);
  });

  it('schedules deterministic reconnect and polling fallback after socket close', async () => {
    const events: ProjectionFeedEvent[] = [];
    const setIntervalFn = vi.fn(() => 22);
    const clearIntervalFn = vi.fn();
    const setTimeoutFn = vi.fn((handler: TimerHandler) => {
      if (typeof handler === 'function') {
        handler();
      }
      return 11;
    });
    const clearTimeoutFn = vi.fn();

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => sampleProjectionBundle,
      }),
    );

    const stop = startProjectionFeed((event) => events.push(event), {
      wsUrl: 'ws://localhost/viz',
      pollMs: 5000,
      WebSocketCtor: FakeWebSocket as unknown as typeof WebSocket,
      now: () => 'viz01-reconnect-ts',
      setIntervalFn: setIntervalFn as unknown as typeof window.setInterval,
      clearIntervalFn: clearIntervalFn as unknown as typeof window.clearInterval,
      setTimeoutFn: setTimeoutFn as unknown as typeof window.setTimeout,
      clearTimeoutFn: clearTimeoutFn as unknown as typeof window.clearTimeout,
    });

    const firstSocket = FakeWebSocket.instances[0];
    firstSocket?.onopen?.();
    firstSocket?.onclose?.();

    await Promise.resolve();
    await Promise.resolve();

    expect(events.some((event) => event.connection_status === 'POLLING_FALLBACK')).toBe(true);
    expect(events.some((event) => event.retry_delay_ms === 1000)).toBe(true);
    expect(events.some((event) => event.fallback_reason === 'SOCKET_CLOSED')).toBe(true);
    expect(FakeWebSocket.instances).toHaveLength(2);
    expect(setIntervalFn).toHaveBeenCalledTimes(1);
    stop();
  });

  it('fails closed and starts polling when a websocket message is malformed', async () => {
    const events: ProjectionFeedEvent[] = [];
    const setIntervalFn = vi.fn(() => 44);

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => sampleProjectionBundle,
      }),
    );

    const stop = startProjectionFeed((event) => events.push(event), {
      wsUrl: 'ws://localhost/viz',
      pollMs: 5000,
      WebSocketCtor: FakeWebSocket as unknown as typeof WebSocket,
      now: () => 'viz01-invalid-ts',
      setIntervalFn: setIntervalFn as unknown as typeof window.setInterval,
      clearIntervalFn: vi.fn() as unknown as typeof window.clearInterval,
      setTimeoutFn: vi.fn(() => 55) as unknown as typeof window.setTimeout,
      clearTimeoutFn: vi.fn() as unknown as typeof window.clearTimeout,
    });

    const socket = FakeWebSocket.instances[0];
    socket?.onmessage?.({ data: '{invalid' } as MessageEvent);

    await Promise.resolve();
    await Promise.resolve();

    expect(events.some((event) => event.connection_status === 'FAIL_CLOSED')).toBe(true);
    expect(events.some((event) => event.fallback_reason === 'STREAM_MESSAGE_INVALID')).toBe(true);
    expect(setIntervalFn).toHaveBeenCalledTimes(1);
    expect(socket?.close).toHaveBeenCalled();
    stop();
  });
});
