export type OperatorPlatformView =
  | 'status'
  | 'yggdrasil'
  | 'production'
  | 'contracts'
  | 'evidence'
  | 'changes'
  | 'alerts';

export const OPERATOR_PLATFORM_VIEWS: Array<{
  id: OperatorPlatformView;
  label: string;
}> = [
  { id: 'status', label: 'Status' },
  { id: 'yggdrasil', label: 'YGGDRASIL' },
  { id: 'production', label: 'Production' },
  { id: 'contracts', label: 'Contracts' },
  { id: 'evidence', label: 'Evidence' },
  { id: 'changes', label: 'Changes' },
  { id: 'alerts', label: 'Alerts' },
];
