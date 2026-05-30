import type { LiveConsoleProjectionBundle } from '../types';

export interface LiveConsoleState {
  bundle: LiveConsoleProjectionBundle;
  selectedSystemId: string | null;
}

export type LiveConsoleAction =
  | { type: 'SELECT_SYSTEM'; payload: string }
  | { type: 'DESELECT_SYSTEM' };

export function liveConsoleReducer(
  state: LiveConsoleState,
  action: LiveConsoleAction,
): LiveConsoleState {
  switch (action.type) {
    case 'SELECT_SYSTEM':
      return { ...state, selectedSystemId: action.payload };
    case 'DESELECT_SYSTEM':
      return { ...state, selectedSystemId: null };
    default:
      return state;
  }
}
