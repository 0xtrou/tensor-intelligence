export interface Subnet {
  netuid: number;
  name: string;
  price: number;
  market_cap: number;
  emission: number;
  emission_share: number;
  active_miners: number;
  active_validators: number;
  fundamental_score: number | null;
  risk_score: number | null;
  ssi_score: number | null;
  updated_at: string;
}

export interface FlowDataPoint {
  timestamp: string;
  flow_ema: number;
  emission_share: number;
  miners_count: number;
  validators_count: number;
  price: number;
}

export interface SubnetSignal {
  signal_type: SignalType;
  flow_signal: number;
  confidence: number;
  composite_score: number;
  created_at: string;
}

export type SignalType = 'BUY' | 'ACCUMULATE' | 'HOLD' | 'REDUCE' | 'AVOID';

export interface SubnetDetail {
  subnet: Subnet;
  recent_flow: FlowDataPoint[];
  recent_signals: SubnetSignal[];
}

export interface SignalSummary {
  BUY: number;
  ACCUMULATE: number;
  HOLD: number;
  REDUCE: number;
  AVOID: number;
}

export interface TopSignal {
  netuid: number;
  signal_type: SignalType;
  confidence: number;
  composite_score: number;
  reasoning: string;
  subnet_name: string;
}

export interface LatestSignal {
  signal_type: SignalType;
  flow_signal: number;
  confidence: number;
  composite_score: number;
  subnet_name: string;
  netuid: number;
  created_at: string;
}

export interface LatestReport {
  report_type: string;
  title: string;
  content: string;
  metadata_: string;
  created_at: string;
}

export interface HealthStatus {
  status: string;
  version: string;
}

export type SortField = 'name' | 'price' | 'emission_share' | 'active_miners' | 'fundamental_score' | 'risk_score';
export type SortDir = 'asc' | 'desc';

export interface SortConfig {
  field: SortField;
  dir: SortDir;
}

export interface SignalFlowResponse {
  subnet: {
    netuid: number;
    name: string;
    price: number;
    emission_share: number;
    active_miners: number;
    active_validators: number;
  };
  pipeline: FlowStage[];
  composite: FlowComposite;
  signal: FlowSignal;
  evidence: Record<string, unknown>;
  formula: string;
  snapshots_analyzed: number;
  data_timespan_days: number;
}

export interface FlowStage {
  name: string;
  score: number;
  output: Record<string, unknown>;
  description: string;
}

export interface FlowComposite {
  score: number;
  formula: string;
  weights: Record<string, number>;
  inputs: Record<string, number>;
  thresholds: Record<string, string>;
}

export interface FlowSignal {
  type: SignalType;
  confidence: number;
  reasoning: string;
}
