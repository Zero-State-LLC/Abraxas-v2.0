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
  static instance: FakeWebSocket | null = null;

  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onopen: (() => void) | null = null;
  readonly url: string;

  constructor(url: string) {
    this.url = url;
    FakeWebSocket.instance = this;
  }

  close = vi.fn();
}

describe('liveProjectionFeed', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    FakeWebSocket.instance = null;
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

    FakeWebSocket.instance?.onopen?.();
    FakeWebSocket.instance?.onmessage?.({
      data: JSON.stringify(sampleProjectionBundle),
    } as MessageEvent);

    expect(events.map((event) => event.connection_status)).toContain('LIVE_STREAM');
    expect(events[events.length - 1]?.result.bundle.systems[0]?.system_id).toBe(
      sampleProjectionBundle.systems[0]?.system_id,
    );
    stop();
    expect(FakeWebSocket.instance?.close).toHaveBeenCalled();
  });

  it('falls back to polling when no websocket URL is configured', async () => {
    const events: ProjectionFeedEvent[] = [];
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
      clearIntervalFn: vi.fn() as unknown as typeof window.clearInterval,
    });

    await Promise.resolve();
    await Promise.resolve();

    expect(events[events.length - 1]?.connection_status).toBe('POLLING_FALLBACK');
    expect(events[events.length - 1]?.last_updated).toBe('viz01-poll-ts');
    stop();
  });
});
