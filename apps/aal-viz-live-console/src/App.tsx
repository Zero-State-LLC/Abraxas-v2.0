import { useEffect, useReducer } from 'react';
import { liveConsoleReducer } from './state/liveConsoleReducer';
import type { LiveConsoleState } from './state/liveConsoleReducer';
import { sampleProjectionBundle } from './data/sampleProjectionBundle';
import { loadProjectionBundle } from './data/loadProjectionBundle';
import { Layout } from './components/Layout';
import './styles.css';

const initialState: LiveConsoleState = {
  bundle: sampleProjectionBundle,
  selectedSystemId: null,
  source_mode: 'SAMPLE_FALLBACK',
  fail_closed_reason: null,
};

export default function App(): JSX.Element {
  const [state, dispatch] = useReducer(liveConsoleReducer, initialState);

  useEffect(() => {
    loadProjectionBundle()
      .then((result) => {
        dispatch({
          type: 'SET_BUNDLE',
          payload: {
            bundle: result.bundle,
            source_mode: result.source_mode,
            fail_closed_reason: result.fail_closed_reason,
          },
        });
      })
      .catch(() => {
        dispatch({
          type: 'SET_BUNDLE',
          payload: {
            bundle: sampleProjectionBundle,
            source_mode: 'SAMPLE_FALLBACK',
            fail_closed_reason: null,
          },
        });
      });
  }, []);

  return <Layout state={state} dispatch={dispatch} />;
}
