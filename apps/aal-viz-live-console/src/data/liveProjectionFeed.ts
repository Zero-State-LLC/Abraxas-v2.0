import type {
  ConnectionStatus,
  FallbackReason,
  LiveConsoleProjectionBundle,
  TransportMode,
} from '../types';
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
  retry_delay_ms: number | null;
  transport_mode: TransportMode;
  last_error_reason: string | null;
  fallback_reason: FallbackReason;
}

interface StartProjectionFeedOptions extends ProjectionFeedConfig {
  initialResult?: LoadResult;
  WebSocketCtor?: typeof WebSocket;
  now?: () => string;
  setIntervalFn?: typeof window.setInterval;
  clearIntervalFn?: typeof window.clearInterval;
  setTimeoutFn?: typeof window.setTimeout;
  clearTimeoutFn?: typeof window.clearTimeout;
}

export type StopProjectionFeed = () => void;

const DEFAULT_POLL_MS = 5000;
const MIN_POLL_MS = 1000;
const DEFAULT_RECONNECT_BASE_MS = 1000;
const MAX_RECONNECT_DELAY_MS = 8000;

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
  let reconnectTimer: number | null = null;
  let currentSocket: WebSocket | null = null;
  let lastResult: LoadResult = options.initialResult ?? {
    bundle: failClosed('projection feed connecting').bundle,
    source_mode: 'FAIL_CLOSED',
    fail_closed_reason: null,
  };
  let hasValidResult = lastResult.source_mode !== 'FAIL_CLOSED';
  let lastErrorReason: string | null = null;
  let fallbackReason: FallbackReason = null;
  let transportMode: TransportMode = 'SAMPLE';
  let retryDelayMs: number | null = null;
  const now = options.now ?? (() => new Date().toISOString());
  const setIntervalFn = options.setIntervalFn ?? window.setInterval.bind(window);
  const clearIntervalFn = options.clearIntervalFn ?? window.clearInterval.bind(window);
  const setTimeoutFn = options.setTimeoutFn ?? window.setTimeout.bind(window);
  const clearTimeoutFn = options.clearTimeoutFn ?? window.clearTimeout.bind(window);

  const clearPolling = (): void => {
    if (pollTimer !== null) {
      clearIntervalFn(pollTimer);
      pollTimer = null;
    }
  };

  const clearReconnect = (): void => {
    if (reconnectTimer !== null) {
      clearTimeoutFn(reconnectTimer);
      reconnectTimer = null;
    }
    retryDelayMs = null;
  };

  const closeSocket = (): void => {
    if (currentSocket !== null) {
      currentSocket.onopen = null;
      currentSocket.onmessage = null;
      currentSocket.onerror = null;
      currentSocket.onclose = null;
      currentSocket.close();
      currentSocket = null;
    }
  };

  const emit = (result: LoadResult, status: ConnectionStatus): void => {
    lastResult = result;
    hasValidResult = result.source_mode !== 'FAIL_CLOSED';
    onEvent({
      result,
      connection_status: status,
      reconnect_attempts: reconnectAttempts,
      last_updated: status === 'CONNECTING' ? null : now(),
      retry_delay_ms: retryDelayMs,
      transport_mode: transportMode,
      last_error_reason: lastErrorReason,
      fallback_reason: fallbackReason,
    });
  };

  const pollOnce = async (): Promise<void> => {
    const result = await loadProjectionBundle('LIVE_ARTIFACT_BUNDLE');
    transportMode = 'POLLING';
    fallbackReason =
      result.source_mode === 'FAIL_CLOSED'
        ? 'POLLING_BUNDLE_FAIL_CLOSED'
        : fallbackReason === 'WS_URL_UNSET' || fallbackReason === 'WEBSOCKET_UNAVAILABLE'
          ? fallbackReason
          : 'POLLING_FETCH_FALLBACK';
    if (result.source_mode === 'FAIL_CLOSED' && hasValidResult) {
      lastErrorReason = result.fail_closed_reason ?? 'POLLING_BUNDLE_FAIL_CLOSED';
      onEvent({
        result: lastResult,
        connection_status: 'POLLING_FALLBACK',
        reconnect_attempts: reconnectAttempts,
        last_updated: now(),
        retry_delay_ms: retryDelayMs,
        transport_mode: transportMode,
        last_error_reason: lastErrorReason,
        fallback_reason: fallbackReason,
      });
      return;
    }
    const status: ConnectionStatus = result.source_mode === 'FAIL_CLOSED' ? 'FAIL_CLOSED' : 'POLLING_FALLBACK';
    emit(result, status);
  };

  const startPolling = (): void => {
    clearPolling();
    void pollOnce();
    pollTimer = setIntervalFn(() => {
      void pollOnce();
    }, options.pollMs);
  };

  const reconnectDelay = (attempt: number): number =>
    Math.min(
      DEFAULT_RECONNECT_BASE_MS * 2 ** Math.max(attempt - 1, 0),
      MAX_RECONNECT_DELAY_MS,
    );

  const scheduleReconnect = (reason: Exclude<FallbackReason, null>): void => {
    if (stopped || options.wsUrl === null || options.WebSocketCtor === undefined) {
      return;
    }
    reconnectAttempts += 1;
    lastErrorReason = reason;
    fallbackReason = reason;
    const delayMs = reconnectDelay(reconnectAttempts);
    retryDelayMs = delayMs;
    emit(lastResult, 'POLLING_FALLBACK');
    if (reconnectTimer !== null) {
      clearTimeoutFn(reconnectTimer);
    }
    reconnectTimer = setTimeoutFn(() => {
      reconnectTimer = null;
      retryDelayMs = null;
      openSocket();
    }, delayMs);
  };

  const handleMalformedStreamMessage = (result: LoadResult): void => {
    lastErrorReason = result.fail_closed_reason ?? 'projection stream message is invalid';
    fallbackReason = 'STREAM_MESSAGE_INVALID';
    transportMode = 'POLLING';
    if (hasValidResult) {
      onEvent({
        result: lastResult,
        connection_status: 'POLLING_FALLBACK',
        reconnect_attempts: reconnectAttempts,
        last_updated: now(),
        retry_delay_ms: retryDelayMs,
        transport_mode: transportMode,
        last_error_reason: lastErrorReason,
        fallback_reason: fallbackReason,
      });
    } else {
      emit(result, 'FAIL_CLOSED');
    }
    closeSocket();
    startPolling();
    scheduleReconnect('STREAM_MESSAGE_INVALID');
  };

  const openSocket = (): void => {
    if (stopped || options.wsUrl === null || options.WebSocketCtor === undefined) {
      return;
    }
    clearReconnect();
    closeSocket();
    transportMode = 'WEBSOCKET';
    emit(lastResult, 'CONNECTING');
    currentSocket = new options.WebSocketCtor(options.wsUrl);

    currentSocket.onopen = (): void => {
      clearPolling();
      lastErrorReason = null;
      fallbackReason = null;
      transportMode = 'WEBSOCKET';
      emit(lastResult, 'LIVE_STREAM');
    };

    currentSocket.onmessage = (event: MessageEvent): void => {
      const result = parseProjectionStreamMessage(event.data);
      if (result.source_mode === 'FAIL_CLOSED') {
        handleMalformedStreamMessage(result);
        return;
      }
      const incomingTime = Date.parse(result.bundle.generated_at);
      const acceptedTime = Date.parse(lastResult.bundle.generated_at);
      if (Number.isFinite(incomingTime) && Number.isFinite(acceptedTime) && incomingTime < acceptedTime) {
        lastErrorReason = 'STREAM_MESSAGE_STALE';
        fallbackReason = 'STREAM_MESSAGE_STALE';
        onEvent({
          result: lastResult,
          connection_status: 'POLLING_FALLBACK',
          reconnect_attempts: reconnectAttempts,
          last_updated: now(),
          retry_delay_ms: retryDelayMs,
          transport_mode: 'POLLING',
          last_error_reason: lastErrorReason,
          fallback_reason: fallbackReason,
        });
        closeSocket();
        startPolling();
        scheduleReconnect('STREAM_MESSAGE_STALE');
        return;
      }
      lastErrorReason = null;
      fallbackReason = null;
      transportMode = 'WEBSOCKET';
      emit(result, 'LIVE_STREAM');
    };

    currentSocket.onerror = (): void => {
      lastErrorReason = 'SOCKET_ERROR';
      fallbackReason = 'SOCKET_ERROR';
      transportMode = 'WEBSOCKET';
      emit(lastResult, 'CONNECTING');
    };

    currentSocket.onclose = (): void => {
      currentSocket = null;
      if (stopped) {
        return;
      }
      transportMode = 'POLLING';
      fallbackReason = fallbackReason ?? 'SOCKET_CLOSED';
      lastErrorReason = lastErrorReason ?? 'SOCKET_CLOSED';
      startPolling();
      scheduleReconnect(fallbackReason);
    };
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
    transportMode = 'POLLING';
    fallbackReason = options.wsUrl === null ? 'WS_URL_UNSET' : 'WEBSOCKET_UNAVAILABLE';
    lastErrorReason = fallbackReason;
    startPolling();
    return () => {
      stopped = true;
      clearPolling();
      clearReconnect();
    };
  }

  openSocket();

  return () => {
    stopped = true;
    clearPolling();
    clearReconnect();
    closeSocket();
  };
}
