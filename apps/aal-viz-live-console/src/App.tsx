import { useEffect, useReducer } from 'react';
import { liveConsoleReducer } from './state/liveConsoleReducer';
import type { LiveConsoleState } from './state/liveConsoleReducer';
import { sampleProjectionBundle } from './data/sampleProjectionBundle';
import { loadProjectionBundle } from './data/loadProjectionBundle';
import {
  resolveProjectionFeedConfig,
  startProjectionFeed,
} from './data/liveProjectionFeed';
import { loadOperatorActionPackets } from './data/loadOperatorActionPackets';
import { Layout } from './components/Layout';
import './styles.css';

const initialState: LiveConsoleState = {
  bundle: sampleProjectionBundle,
  selectedSystemId: null,
  source_mode: 'SAMPLE_FALLBACK',
  fail_closed_reason: null,
  packets: null,
  connection_status: 'SAMPLE_FALLBACK',
  connection_last_updated: null,
  connection_reconnect_attempts: 0,
  connection_retry_delay_ms: null,
  connection_transport_mode: 'SAMPLE',
  connection_last_error_reason: null,
  connection_fallback_reason: null,
};

export default function App(): JSX.Element {
  const [state, dispatch] = useReducer(liveConsoleReducer, initialState);

  useEffect(() => {
    let stopFeed: (() => void) | null = null;
    let cancelled = false;
    void loadProjectionBundle()
      .then((result) => {
        if (cancelled) return;
        dispatch({
          type: 'SET_BUNDLE',
          payload: {
            bundle: result.bundle,
            source_mode: result.source_mode,
            fail_closed_reason: result.fail_closed_reason,
          },
        });
        const config = resolveProjectionFeedConfig();
        const WebSocketCtor = typeof window !== 'undefined' && 'WebSocket' in window ? WebSocket : undefined;
        stopFeed = startProjectionFeed(
          (event) => {
            dispatch({
              type: 'SET_CONNECTION_STATUS',
              payload: {
                connection_status: event.connection_status,
                connection_last_updated: event.last_updated,
                connection_reconnect_attempts: event.reconnect_attempts,
                connection_retry_delay_ms: event.retry_delay_ms,
                connection_transport_mode: event.transport_mode,
                connection_last_error_reason: event.last_error_reason,
                connection_fallback_reason: event.fallback_reason,
              },
            });
            if (event.connection_status !== 'CONNECTING') {
              dispatch({
                type: 'SET_BUNDLE',
                payload: {
                  bundle: event.result.bundle,
                  source_mode: event.result.source_mode,
                  fail_closed_reason: event.result.fail_closed_reason,
                  preserve_selection: true,
                },
              });
            }
          },
          { ...config, WebSocketCtor, initialResult: result },
        );
      })
      .catch(() => {
        if (!cancelled) {
          dispatch({
            type: 'SET_BUNDLE',
            payload: {
              bundle: sampleProjectionBundle,
              source_mode: 'SAMPLE_FALLBACK',
              fail_closed_reason: null,
            },
          });
        }
      });
    return () => {
      cancelled = true;
      stopFeed?.();
    };
  }, []);

  useEffect(() => {
    loadOperatorActionPackets()
      .then((pkts) => {
        dispatch({ type: 'SET_PACKETS', payload: pkts });
      })
      .catch(() => {
        dispatch({ type: 'SET_PACKETS', payload: null });
      });
  }, []);

  return <Layout state={state} dispatch={dispatch} />;
}
