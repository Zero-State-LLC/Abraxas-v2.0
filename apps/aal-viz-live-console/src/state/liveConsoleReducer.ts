import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle, SourceMode } from '../types';

export interface LiveConsoleState {
  bundle: LiveConsoleProjectionBundle;
  selectedSystemId: string | null;
  source_mode: SourceMode;
  fail_closed_reason: string | null;
  packets: OperatorActionPacketsBundle | null;
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
      };
    }
  | { type: 'SET_PACKETS'; payload: OperatorActionPacketsBundle | null };

export function liveConsoleReducer(
  state: LiveConsoleState,
  action: LiveConsoleAction,
): LiveConsoleState {
  switch (action.type) {
    case 'SELECT_SYSTEM':
      return { ...state, selectedSystemId: action.payload };
    case 'DESELECT_SYSTEM':
      return { ...state, selectedSystemId: null };
    case 'SET_BUNDLE':
      return {
        ...state,
        bundle: action.payload.bundle,
        source_mode: action.payload.source_mode,
        fail_closed_reason: action.payload.fail_closed_reason,
        selectedSystemId: null,
      };
    case 'SET_PACKETS':
      return { ...state, packets: action.payload };
    default:
      return state;
  }
}
