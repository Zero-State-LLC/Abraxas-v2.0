import { useReducer } from 'react';
import { liveConsoleReducer } from './state/liveConsoleReducer';
import type { LiveConsoleState } from './state/liveConsoleReducer';
import { sampleProjectionBundle } from './data/sampleProjectionBundle';
import { Layout } from './components/Layout';
import './styles.css';

const initialState: LiveConsoleState = {
  bundle: sampleProjectionBundle,
  selectedSystemId: null,
};

export default function App(): JSX.Element {
  const [state, dispatch] = useReducer(liveConsoleReducer, initialState);
  return <Layout state={state} dispatch={dispatch} />;
}
