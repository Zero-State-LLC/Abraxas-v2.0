import { useMemo } from 'react';
import { buildOperatorNarrativeReportFrame } from '../data/buildOperatorNarrativeReportFrame';
import type { LiveConsoleProjectionBundle } from '../types';

interface OperatorNarrativeReportPanelProps {
  bundle: LiveConsoleProjectionBundle;
}

function formatSourceMode(sourceMode: string): string {
  return sourceMode.toLowerCase().replace(/_/g, ' ');
}

function formatObservedFields(fields: Record<string, unknown> | undefined): string {
  if (fields === undefined || Object.keys(fields).length === 0) {
    return 'No observed fields';
  }
  return Object.entries(fields)
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
    .join(' · ');
}

export function OperatorNarrativeReportPanel({
  bundle,
}: OperatorNarrativeReportPanelProps): JSX.Element {
  const frame = useMemo(() => buildOperatorNarrativeReportFrame(bundle), [bundle]);

  const captionParts = [
    `P42/P44 projection-only operator narrative (${formatSourceMode(frame.source_mode)})`,
  ];
  if (frame.source_mode === 'P44_ARTIFACT') {
    captionParts.push(
      `${frame.final_status} · ${frame.overlay_posture}`,
      `${frame.section_count} sections · ${frame.blocker_total} blockers`,
    );
  }

  return (
    <section className="panel-section" data-testid="operator-narrative-report-panel">
      <h3 className="panel-heading">Operator Narrative Report</h3>
      <p className="panel-caption">{captionParts.join(' · ')}</p>
      <p className="panel-caption" data-testid="operator-narrative-advisory-notice">
        Advisory-only deterministic report overlay; no execution authority or command routing.
      </p>

      {frame.sections.length > 0 ? (
        <div className="narrative-summary-grid" data-testid="operator-narrative-sections">
          {frame.sections.map((section) => (
            <div className="narrative-summary-section" key={section.section_id}>
              <div className="narrative-summary-section__label">{section.title}</div>
              <span>{section.status}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="narrative-empty" data-testid="operator-narrative-empty">
          Operator narrative overlay not present in projection bundle.
        </div>
      )}

      {frame.cards.length > 0 ? (
        <div className="narrative-summary-grid" data-testid="operator-narrative-cards">
          {frame.cards.map((card) => (
            <div className="narrative-summary-section" key={card.card_id}>
              <div className="narrative-summary-section__label">{card.title}</div>
              {card.status !== undefined ? <span>{card.status}</span> : null}
              <span>{formatObservedFields(card.observed_fields)}</span>
            </div>
          ))}
        </div>
      ) : null}

      {frame.blocker_total > 0 ? (
        <div className="narrative-summary-section" data-testid="operator-narrative-blockers">
          <div className="narrative-summary-section__label">
            Blocker preview ({frame.blocker_preview.length}/{frame.blocker_total})
          </div>
          <ul className="narrative-list">
            {frame.blocker_preview.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
