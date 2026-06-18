import type {
  LiveConsoleProjectionBundle,
  OperatorNarrativeOverlayCard,
  OperatorNarrativeReportPacket,
  OperatorNarrativeSectionNav,
} from '../types';

export type OperatorNarrativeSourceMode = 'P44_ARTIFACT' | 'FALLBACK_ABSENT';

export interface OperatorNarrativeReportFrame {
  packet_type: 'AALVizOperatorNarrativeReportFrame.v1';
  authority: 'VISUAL_PROJECTION_ONLY';
  projection_only: true;
  source_mode: OperatorNarrativeSourceMode;
  final_status: string;
  overlay_posture: string;
  section_count: number;
  sections: OperatorNarrativeSectionNav[];
  cards: OperatorNarrativeOverlayCard[];
  blocker_preview: string[];
  blocker_total: number;
}

const BLOCKER_PREVIEW_LIMIT = 5;

function blockerItems(cards: OperatorNarrativeOverlayCard[]): { preview: string[]; total: number } {
  const blockerCard = cards.find((card) => card.card_id === 'card.report_blockers');
  const summary = blockerCard?.blocker_summary ?? [];
  return {
    preview: summary.slice(0, BLOCKER_PREVIEW_LIMIT),
    total: blockerCard?.blocker_count ?? summary.length,
  };
}

function frameFromPacket(packet: OperatorNarrativeReportPacket): OperatorNarrativeReportFrame {
  const blockers = blockerItems(packet.overlay_cards);
  return {
    packet_type: 'AALVizOperatorNarrativeReportFrame.v1',
    authority: 'VISUAL_PROJECTION_ONLY',
    projection_only: true,
    source_mode: 'P44_ARTIFACT',
    final_status: packet.final_status,
    overlay_posture: packet.overlay_posture,
    section_count: packet.section_navigation.length,
    sections: packet.section_navigation,
    cards: packet.overlay_cards.filter((card) => card.card_id.startsWith('card.section.')),
    blocker_preview: blockers.preview,
    blocker_total: blockers.total,
  };
}

function fallbackFrame(): OperatorNarrativeReportFrame {
  return {
    packet_type: 'AALVizOperatorNarrativeReportFrame.v1',
    authority: 'VISUAL_PROJECTION_ONLY',
    projection_only: true,
    source_mode: 'FALLBACK_ABSENT',
    final_status: 'NOT_COMPUTABLE',
    overlay_posture: 'NOT_COMPUTABLE',
    section_count: 0,
    sections: [],
    cards: [],
    blocker_preview: [],
    blocker_total: 0,
  };
}

export function buildOperatorNarrativeReportFrame(
  bundle: LiveConsoleProjectionBundle,
): OperatorNarrativeReportFrame {
  const packet = bundle.operator_narrative_report;
  if (packet === undefined) {
    return fallbackFrame();
  }
  return frameFromPacket(packet);
}
