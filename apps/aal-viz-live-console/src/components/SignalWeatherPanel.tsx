import type { SystemProjection, SignalWeatherMetrics } from '../types';

interface SignalWeatherPanelProps {
  systems: SystemProjection[];
}

function computeMetrics(systems: SystemProjection[]): SignalWeatherMetrics {
  const ready_count = systems.filter((s) => s.status === 'READY').length;
  const partial_count = systems.filter((s) => s.status === 'PARTIAL').length;
  const fail_closed_count = systems.filter((s) => s.status === 'FAIL_CLOSED').length;
  const not_computable_count = systems.filter((s) => s.status === 'NOT_COMPUTABLE').length;
  const average_completion =
    systems.length > 0
      ? Math.round(systems.reduce((acc, s) => acc + s.completion_pct, 0) / systems.length)
      : 0;
  const high_risk_count = systems.filter((s) => s.risk_level === 'HIGH').length;
  return {
    ready_count,
    partial_count,
    fail_closed_count,
    not_computable_count,
    average_completion,
    high_risk_count,
  };
}

export function SignalWeatherPanel({ systems }: SignalWeatherPanelProps): JSX.Element {
  const m = computeMetrics(systems);

  return (
    <div className="panel-block">
      <div className="panel-header">
        <span className="panel-icon">◉</span>
        SIGNAL WEATHER
      </div>
      <div className="panel-body">
        <div className="weather-grid">
          <div className="weather-cell weather-cell--ready">
            <div className="weather-cell__label">READY</div>
            <div className="weather-cell__value">{m.ready_count}</div>
          </div>
          <div className="weather-cell weather-cell--partial">
            <div className="weather-cell__label">PARTIAL</div>
            <div className="weather-cell__value">{m.partial_count}</div>
          </div>
          <div className="weather-cell weather-cell--fail">
            <div className="weather-cell__label">FAIL CLOSED</div>
            <div className="weather-cell__value">{m.fail_closed_count}</div>
          </div>
          <div className="weather-cell weather-cell--nc">
            <div className="weather-cell__label">NOT COMPUTABLE</div>
            <div className="weather-cell__value">{m.not_computable_count}</div>
          </div>
          <div className="weather-cell weather-cell--avg">
            <div className="weather-cell__label">AVG COMPLETION</div>
            <div className="weather-cell__value">{m.average_completion}%</div>
          </div>
          <div className="weather-cell weather-cell--risk">
            <div className="weather-cell__label">HIGH RISK</div>
            <div className="weather-cell__value">{m.high_risk_count}</div>
          </div>
        </div>
        <div className="progress-bar" style={{ marginTop: '8px' }}>
          <div
            className="progress-bar__fill"
            style={{ width: `${m.average_completion}%` }}
          />
        </div>
        <div style={{ fontSize: '9px', color: 'var(--clr-text-muted)', marginTop: '4px', textAlign: 'right' }}>
          {systems.length} systems tracked
        </div>
      </div>
    </div>
  );
}
