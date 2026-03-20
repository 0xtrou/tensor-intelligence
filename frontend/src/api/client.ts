import type {
  Subnet,
  SubnetDetail,
  SignalSummary,
  TopSignal,
  LatestSignal,
  LatestReport,
  HealthStatus,
  FlowDataPoint,
  SignalFlowResponse,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '');

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText} for ${path}`);
  }
  return res.json() as Promise<T>;
}

export async function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>('/health');
}

export async function getSubnets(): Promise<Subnet[]> {
  return request<Subnet[]>('/subnets/');
}

export async function getSubnetDetail(netuid: number): Promise<SubnetDetail> {
  return request<SubnetDetail>(`/subnets/${netuid}`);
}

export async function getSubnetFlow(netuid: number, hours: number = 168): Promise<FlowDataPoint[]> {
  return request<FlowDataPoint[]>(`/subnets/${netuid}/flow?hours=${hours}`);
}

export async function getSignalSummary(): Promise<SignalSummary> {
  return request<SignalSummary>('/signals/summary');
}

export async function getTopSignals(limit: number = 10): Promise<TopSignal[]> {
  return request<TopSignal[]>(`/signals/top?limit=${limit}`);
}

export async function getLatestSignals(limit: number = 20): Promise<LatestSignal[]> {
  return request<LatestSignal[]>(`/signals/latest?limit=${limit}`);
}

export async function getLatestReport(): Promise<LatestReport> {
  return request<LatestReport>('/reports/latest');
}

export async function fetchSignalFlow(netuid: number): Promise<SignalFlowResponse> {
  return request<SignalFlowResponse>(`/signal-flow/${netuid}`);
}
