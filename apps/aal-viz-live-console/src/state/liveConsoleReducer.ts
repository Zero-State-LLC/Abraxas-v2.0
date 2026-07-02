import type {
  ConnectionStatus,
  LiveConsoleProjectionBundle,
  OperatorActionPacketsBundle,
  SourceMode,
} from '../types';

export interface LiveConsoleState {
  bundle: LiveConsoleProjectionBundle;
  selectedSystemId: string | null;
  source_mode: SourceMode;
  fail_closed_reason: string | null;
  packets: OperatorActionPacketsBundle | null;
  connection_status: ConnectionStatus;
  connection_last_updated: string | null;
  connection_reconnect_attempts: number;
}

export type LiveConsoleAction =
  | { type: 'SELECT_SYSTEM'; payload: string }
  | { type: 'DESELECT_SYSTEM' }
  | {
      type: 'SET_BUNDLE';
      payload: {
        bundle: LiveConsoleProjectionBundle;
        source_mode: SourceMode;
        fail_closed_reason: string | null;
        preserve_selection?: boolean;
      };
    }
  | { type: 'SET_PACKETS'; payload: OperatorActionPacketsBundle | null }
  | {
      type: 'SET_CONNECTION_STATUS';
      payload: {
        connection_status: ConnectionStatus;
        connection_last_updated: string | null;
        connection_reconnect_attempts: number;
      };
    };

export function liveConsoleReducer(
  state: LiveConsoleState,
  action: LiveConsoleAction,
): LiveConsoleState {
  switch (action.type) {
    case 'SELECT_SYSTEM':
      return { ...state, selectedSystemId: action.payload };
    case 'DESELECT_SYSTEM':
      return { ...state, selectedSystemId: null };
    case 'SET_BUNDLE': {
      const selectedSystemId =
        action.payload.preserve_selection === true &&
        state.selectedSystemId != null &&
        action.payload.bundle.systems.some(
          (s) => s.system_id === state.selectedSystemId,
        )
          ? state.selectedSystemId
          : null;
      return {
        ...state,
        bundle: action.payload.bundle,
        source_mode: action.payload.source_mode,
        fail_closed_reason: action.payload.fail_closed_reason,
        selectedSystemId,
      };
    }
    case 'SET_PACKETS':
      return { ...state, packets: action.payload };
    case 'SET_CONNECTION_STATUS':
      return {
        ...state,
        connection_status: action.payload.connection_status,
        connection_last_updated: action.payload.connection_last_updated,
        connection_reconnect_attempts: action.payload.connection_reconnect_attempts,
      };
    default:
      return state;
  }
}
