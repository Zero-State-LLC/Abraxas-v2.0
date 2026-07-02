import type { ConnectionStatus, LiveConsoleProjectionBundle } from '../types';
import {
  failClosed,
  loadProjectionBundle,
  type LoadResult,
  validateProjectionBundle,
} from './loadProjectionBundle';

export interface ProjectionFeedConfig {
  wsUrl: string | null;
  pollMs: number;
}

export interface ProjectionFeedEvent {
  result: LoadResult;
  connection_status: ConnectionStatus;
  reconnect_attempts: number;
  last_updated: string | null;
}

interface StartProjectionFeedOptions extends ProjectionFeedConfig {
  WebSocketCtor?: typeof WebSocket;
  now?: () => string;
  setIntervalFn?: typeof window.setInterval;
  clearIntervalFn?: typeof window.clearInterval;
}

export type StopProjectionFeed = () => void;

const DEFAULT_POLL_MS = 5000;
const MIN_POLL_MS = 1000;

function getDefaultEnv(): Record<string, unknown> {
  const meta = import.meta as ImportMeta & {
    readonly env?: Record<string, unknown>;
  };
  return meta.env ?? {};
}

export function normalizePollMs(value: unknown): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < MIN_POLL_MS) {
    return DEFAULT_POLL_MS;
  }
  return Math.round(parsed);
}

export function resolveProjectionFeedConfig(
  env: Record<string, unknown> = getDefaultEnv(),
): ProjectionFeedConfig {
  const rawWsUrl = env.VITE_AAL_VIZ_WS_URL;
  return {
    wsUrl: typeof rawWsUrl === 'string' && rawWsUrl.trim() !== '' ? rawWsUrl : null,
    pollMs: normalizePollMs(env.VITE_AAL_VIZ_POLL_MS),
  };
}

export function parseProjectionStreamMessage(data: unknown): LoadResult {
  if (typeof data !== 'string') {
    return failClosed('projection stream message is not text JSON');
  }
  try {
    return validateProjectionBundle(JSON.parse(data) as LiveConsoleProjectionBundle);
  } catch {
    return failClosed('projection stream message is not valid JSON');
  }
}

export function startProjectionFeed(
  onEvent: (event: ProjectionFeedEvent) => void,
  options: StartProjectionFeedOptions,
): StopProjectionFeed {
  let stopped = false;
  let reconnectAttempts = 0;
  let pollTimer: number | null = null;
  const now = options.now ?? (() => new Date().toISOString());
  const setIntervalFn = options.setIntervalFn ?? window.setInterval.bind(window);
  const clearIntervalFn = options.clearIntervalFn ?? window.clearInterval.bind(window);

  const emit = (result: LoadResult, status: ConnectionStatus): void => {
    onEvent({
      result,
      connection_status: status,
      reconnect_attempts: reconnectAttempts,
      last_updated: status === 'CONNECTING' ? null : now(),
    });
  };

  const pollOnce = async (): Promise<void> => {
    const result = await loadProjectionBundle('LIVE_ARTIFACT_BUNDLE');
    const status: ConnectionStatus =
      result.source_mode === 'FAIL_CLOSED' ? 'FAIL_CLOSED' : 'POLLING_FALLBACK';
    emit(result, status);
  };

  const startPolling = (): void => {
    void pollOnce();
    pollTimer = setIntervalFn(() => {
      void pollOnce();
    }, options.pollMs);
  };

  emit(
    {
      bundle: failClosed('projection feed connecting').bundle,
      source_mode: 'FAIL_CLOSED',
      fail_closed_reason: null,
    },
    'CONNECTING',
  );

  if (options.wsUrl === null || options.WebSocketCtor === undefined) {
    startPolling();
    return () => {
      stopped = true;
      if (pollTimer !== null) {
        clearIntervalFn(pollTimer);
      }
    };
  }

  const socket = new options.WebSocketCtor(options.wsUrl);

  socket.onopen = (): void => {
    emit(
      {
        bundle: failClosed('projection stream opened').bundle,
        source_mode: 'LIVE_ARTIFACT_BUNDLE',
        fail_closed_reason: null,
      },
      'LIVE_STREAM',
    );
  };

  socket.onmessage = (event: MessageEvent): void => {
    const result = parseProjectionStreamMessage(event.data);
    emit(result, result.source_mode === 'FAIL_CLOSED' ? 'FAIL_CLOSED' : 'LIVE_STREAM');
  };

  socket.onerror = (): void => {
    reconnectAttempts += 1;
  };

  socket.onclose = (): void => {
    if (!stopped) {
      reconnectAttempts += 1;
      startPolling();
    }
  };

  return () => {
    stopped = true;
    if (pollTimer !== null) {
      clearIntervalFn(pollTimer);
    }
    socket.close();
  };
}
