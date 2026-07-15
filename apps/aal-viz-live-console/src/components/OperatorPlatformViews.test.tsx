import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { sampleProjectionBundle } from '../data/sampleProjectionBundle';
import { OperatorPlatformGraphViewPanel, type OperatorPlatformGraphState } from './OperatorPlatformViews';
import { OperatorPlatformSimpleViewPanel } from './OperatorPlatformSimpleViews';
import OperatorPlatformChangesView from './OperatorPlatformChangesView';

const graphState: OperatorPlatformGraphState = {
  yggQuery: '',
  yggSelectedTypes: ['CONTRACT', 'PACKET', 'RECEIPT', 'ROUTE', 'RUNE', 'SYSTEM'],
  yggSelectedId: null,
  contractQuery: '',
  contractSelectedId: null,
};

function TestGraph({ view }: { view: 'yggdrasil' | 'contracts' }): JSX.Element {
  const [state, setState] = useState(graphState);
  return <OperatorPlatformGraphViewPanel view={view} platform={sampleProjectionBundle.operator_platform} graphState={state} onGraphStateChange={setState} />;
}

describe('OperatorPlatformViewPanel', () => {
  it('filters topology entity types into an explicit empty state', async () => {
    const user = userEvent.setup();
    render(
      <TestGraph view="yggdrasil" />,
    );
    expect(screen.getByTestId('topology-canvas')).toBeInTheDocument();
    for (const checkbox of screen.getAllByRole('checkbox')) await user.click(checkbox);
    expect(screen.getByText('No matching topology')).toBeInTheDocument();
  });

  it('renders the production flow in deterministic stage order', () => {
    render(
      <OperatorPlatformSimpleViewPanel
        view="production"
        platform={sampleProjectionBundle.operator_platform}
      />,
    );
    expect(screen.getByRole('heading', { name: 'Entry' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Receipts' })).toBeInTheDocument();
  });

  it('renders contract missing-evidence state', () => {
    render(
      <TestGraph view="contracts" />,
    );
    expect(screen.getByText('No contracts')).toBeInTheDocument();
  });

  it('searches evidence records', async () => {
    const user = userEvent.setup();
    render(
      <OperatorPlatformSimpleViewPanel
        view="evidence"
        platform={sampleProjectionBundle.operator_platform}
      />,
    );
    await user.type(screen.getByLabelText('Search evidence'), 'not-present');
    expect(screen.getByText('No matching evidence')).toBeInTheDocument();
  });

  it('renders a stable zero-change generation', () => {
    render(
      <OperatorPlatformChangesView platform={sampleProjectionBundle.operator_platform} />,
    );
    expect(screen.getByText('No changes observed')).toBeInTheDocument();
  });

  it('groups typed changes and renders generation labels', () => {
    const bundle = structuredClone(sampleProjectionBundle);
    const diff = bundle.operator_platform.temporal_diff.payload;
    if (diff == null) throw new Error('sample temporal payload is required');
    diff.prior_generation_id = 'a'.repeat(64);
    diff.current_generation_id = 'b'.repeat(64);
    diff.total_change_count = 1;
    diff.category_counts.OWNERSHIP = 1;
    diff.entries = [{
      id: 'c'.repeat(64),
      operation: 'CHANGED',
      category: 'OWNERSHIP',
      impact: 'STRENGTHENED',
      surface: 'contract_graph',
      entity_id: 'contract:1',
      summary: 'Ownership evidence resolved.',
      severity: 'INFO',
      field_path: '/contract_graph/payload/contracts/contract:1/owner',
      prior_value: 'UNRESOLVED',
      current_value: 'core.owner',
      provenance: 'OBSERVED',
      prior_generation_id: 'a'.repeat(64),
      current_generation_id: 'b'.repeat(64),
      prior_evidence_status: 'AVAILABLE',
      current_evidence_status: 'AVAILABLE',
      reason_code: null,
      source_keys: ['contract_inventory'],
    }];
    render(<OperatorPlatformChangesView platform={bundle.operator_platform} />);
    expect(screen.getByRole('heading', { name: 'OWNERSHIP' })).toBeInTheDocument();
    expect(screen.getByText('STRENGTHENED')).toBeInTheDocument();
    expect(screen.getByText('aaaaaaaaaaaa')).toBeInTheDocument();
    expect(screen.getByText('bbbbbbbbbbbb')).toBeInTheDocument();
  });
});
import { useState } from 'react';
