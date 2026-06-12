import { useMemo } from 'react';
import { buildCinematicBriefingFrame } from '../data/buildCinematicBriefingFrame';
import type { LiveConsoleProjectionBundle, OperatorActionPacketsBundle } from '../types';

interface CinematicBriefingPanelProps {
  bundle: LiveConsoleProjectionBundle;
  packetsBundle: OperatorActionPacketsBundle | null;
}

export function CinematicBriefingPanel({ bundle, packetsBundle }: CinematicBriefingPanelProps): JSX.Element {
  const frame = useMemo(() => buildCinematicBriefingFrame(bundle, packetsBundle), [bundle, packetsBundle]);

  return (
    <section
      className="cinematic-briefing-panel"
      data-testid="cinematic-briefing-panel"
      aria-label="AAL-Viz Cinematic Briefing"
    >
      <div className="cinematic-briefing-panel__header">
        <span className="cinematic-briefing-panel__title">CINEMATIC BRIEFING GENERATOR</span>
        <span className="cinematic-briefing-panel__notice">
          {frame.authority} · {frame.mutation_policy}
        </span>
      </div>

      <div className="cinematic-briefing-grid">
        <div className="cinematic-briefing-section cinematic-briefing-section--wide" data-testid="briefing-story-blocks">
          <div className="cinematic-briefing-section__label">ANALYTICS STORY BLOCKS</div>
          <div className="cinematic-story-strip">
            {frame.story_blocks.map((block) => (
              <article className={`cinematic-story-card cinematic-story-card--${block.provenance}`} key={block.block_id}>
                <strong>{block.title}</strong>
                <span>{block.narration}</span>
                <span>{block.provenance} · confidence {block.confidence.toFixed(2)}</span>
              </article>
            ))}
          </div>
          <div className="cinematic-briefing-section__meta">SOURCE NARRATIVE {frame.source_narrative_id}</div>
        </div>

        <div className="cinematic-briefing-section" data-testid="briefing-camera-path">
          <div className="cinematic-briefing-section__label">NARRATIVE CAMERA PATH</div>
          <div className="cinematic-camera-path">
            {frame.camera_path.map((segment) => (
              <div className="cinematic-camera-segment" key={segment.segment_id}>
                <span>{segment.segment_id}</span>
                <strong>{segment.camera_mode}</strong>
                <span>{segment.focus_label} · {segment.duration_ms}ms · {segment.authority}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="cinematic-briefing-section" data-testid="briefing-coaching-suggestions">
          <div className="cinematic-briefing-section__label">OPERATOR COACHING SUGGESTIONS</div>
          {frame.operator_coaching_suggestions.length === 0 ? (
            <div className="cinematic-empty">NO REVIEW-ONLY COACHING PROMPTS</div>
          ) : (
            <ul className="cinematic-list">
              {frame.operator_coaching_suggestions.map((suggestion) => (
                <li key={suggestion.suggestion_id}>
                  <strong>{suggestion.prompt}</strong>
                  <span>{suggestion.provenance} · review only</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="cinematic-briefing-section" data-testid="briefing-export-snapshots">
          <div className="cinematic-briefing-section__label">BRIEFING EXPORT SNAPSHOTS</div>
          {frame.export_snapshots.map((snapshot) => (
            <div className="cinematic-snapshot" key={snapshot.snapshot_id}>
              <strong>{snapshot.label}</strong>
              <span>{snapshot.format} · {snapshot.export_authority}</span>
              <span>file write {String(snapshot.file_write_allowed).toUpperCase()}</span>
            </div>
          ))}
        </div>

        <div className="cinematic-briefing-section" data-testid="briefing-voiceover-script">
          <div className="cinematic-briefing-section__label">VOICEOVER SCRIPT PREVIEW</div>
          <ol className="cinematic-list cinematic-list--ordered">
            {frame.voiceover_script_lines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ol>
        </div>

        <div className="cinematic-briefing-section cinematic-briefing-section--wide" data-testid="briefing-locks">
          <div className="cinematic-briefing-section__label">CINEMATIC BRIEFING LOCKS</div>
          <div className="cinematic-lock-grid">
            <span>STORY FACTS</span><strong>{String(frame.briefing_locks.story_blocks_create_new_facts).toUpperCase()}</strong>
            <span>CAMERA MUTATION</span>
            <strong>{String(!frame.briefing_locks.camera_paths_visual_projection_only).toUpperCase()}</strong>
            <span>SNAPSHOT WRITE</span><strong>{String(frame.briefing_locks.snapshot_export_writes_files).toUpperCase()}</strong>
            <span>VOICEOVER WRITE</span><strong>{String(frame.briefing_locks.voiceover_export_writes_files).toUpperCase()}</strong>
            <span>NOTION WRITE</span><strong>{String(frame.briefing_locks.notion_write_adapter_enabled).toUpperCase()}</strong>
            <span>WEBSOCKET</span><strong>{String(frame.briefing_locks.websocket_broadcast_enabled).toUpperCase()}</strong>
            <span>AUTO EXECUTION</span><strong>{String(frame.briefing_locks.autonomous_execution_allowed).toUpperCase()}</strong>
            <span>TRUTH AUTHORITY</span><strong>{String(frame.briefing_locks.truth_authority).toUpperCase()}</strong>
          </div>
          <div className="cinematic-briefing-section__meta">FRAME HASH {frame.provenance_hash}</div>
        </div>
      </div>
    </section>
  );
}
