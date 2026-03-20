import { useState, useEffect } from 'react';
import { fetchSignalFlow } from '../api/client';
import { signalBadgeClass } from '../lib/format';
import type { SignalFlowResponse, FlowStage } from '../types';

/* ── Constants ── */

const WEIGHT_COLORS: Record<string, string> = {
  flow: '#4488ff',
  fundamentals: '#aa66ff',
  trend_alignment: '#ffaa00',
  risk: '#ff8844',
};

const WEIGHT_LABELS: Record<string, string> = {
  flow: 'Flow',
  fundamentals: 'Fund',
  trend: 'Trend',
  risk: 'Risk',
};

const BREAKDOWN_LABELS: Record<string, string> = {
  team_quality: 'Team',
  use_case_clarity: 'Use Case',
  technical_execution: 'Exec',
  network_effects: 'Network',
  community_sentiment: 'Comm',
  tokenomics_health: 'Token',
  competitive_moat: 'Moat',
  flow_volatility: 'Volatility',
  liquidity: 'Liquidity',
  emission_sustainability: 'Emission',
  concentration: 'Concentr.',
  crash_risk: 'Crash',
};

const THRESHOLD_SEGMENTS = [
  { min: 70, max: 100, label: 'BUY', color: '#00ff88' },
  { min: 50, max: 70, label: 'ACCUM', color: '#ffaa00' },
  { min: 30, max: 50, label: 'HOLD', color: '#888888' },
  { min: 15, max: 30, label: 'REDUCE', color: '#ff8844' },
  { min: 0, max: 15, label: 'AVOID', color: '#ff4455' },
];

function scoreColor(score: number): string {
  if (score >= 70) return '#00ff88';
  if (score >= 50) return '#ffaa00';
  if (score >= 30) return '#ff8844';
  return '#ff4455';
}

function barBg(): string {
  return '#111111';
}

/* ── Resonance ── */

interface ResonanceInfo {
  type: 'aligned' | 'bearish' | 'conflicting';
  dotColor: string;
  label: string;
  delta: number;
  prevScore: number;
  nextScore: number;
}

function computeResonance(prev: number, next: number, _stageName: string): ResonanceInfo {
  const delta = next - prev;
  const bothUp = prev >= 50 && next >= 50;
  const bothDown = prev < 50 && next < 50;

  if (bothUp) {
    return {
      type: 'aligned',
      dotColor: '#00ff88',
      label: 'aligned',
      delta,
      prevScore: prev,
      nextScore: next,
    };
  }
  if (bothDown) {
    return {
      type: 'bearish',
      dotColor: '#ff4455',
      label: 'bearish consensus',
      delta,
      prevScore: prev,
      nextScore: next,
    };
  }
  return {
    type: 'conflicting',
    dotColor: '#ffaa00',
    label: 'conflicting',
    delta,
    prevScore: prev,
    nextScore: next,
  };
}

function resonanceDescription(r: ResonanceInfo, nextStageName: string): string {
  const name = nextStageName.replace(/^\d+\.\s*/, '').toUpperCase();
  if (r.type === 'aligned') {
    return `${name} confirms bullish outlook. +${r.delta.toFixed(1)} pts`;
  }
  if (r.type === 'bearish') {
    return `${name} confirms bearish outlook. ${r.delta.toFixed(1)} pts`;
  }
  if (r.nextScore > r.prevScore) {
    return `${name} pushes bullish despite prior weakness. +${r.delta.toFixed(1)} pts`;
  }
  return `${name} contradicts prior signal. ${r.delta >= 0 ? '+' : ''}${r.delta.toFixed(1)} pts`;
}

/* ── Main Component ── */

export function SignalFlowVisualization({ netuid }: { netuid: number }) {
  const [data, setData] = useState<SignalFlowResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchSignalFlow(netuid)
      .then((d) => { if (!cancelled) setData(d); })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load signal flow');
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [netuid]);

  if (loading) return <PipelineSkeleton />;
  if (error) return <PipelineError message={error} />;
  if (!data) return null;

  const resonances: ResonanceInfo[] = [];
  for (let i = 1; i < data.pipeline.length; i++) {
    resonances.push(
      computeResonance(data.pipeline[i - 1].score, data.pipeline[i].score, data.pipeline[i].name)
    );
  }

  return (
    <div className="space-y-0">
      <PipelineHeader data={data} />
      <div className="h-px bg-gradient-to-r from-border to-transparent" />

      <div className="py-2 px-4">
        <div className="text-[11px] text-text-muted tracking-wide-label">
          <span className="text-accent">$</span> cat pipeline.trace
        </div>
      </div>
      <div className="h-px bg-gradient-to-r from-border to-transparent" />

      <DataInputBox snapshots={data.snapshots_analyzed} days={data.data_timespan_days} />
      <FlowConnector />

      {data.pipeline.map((stage, i) => (
        <div key={stage.name}>
          <FlowStageCard stage={stage} />
          {i < resonances.length && (
            <>
              <ResonanceConnector resonance={resonances[i]} nextStageName={data.pipeline[i + 1].name} />
              <FlowConnector />
            </>
          )}
          {i < data.pipeline.length - 1 && i >= resonances.length && <FlowConnector />}
        </div>
      ))}

      <CompositeSection composite={data.composite} />
      <FlowConnector />
      <SignalOutput signal={data.signal} composite={data.composite} />
    </div>
  );
}

/* ── Pipeline Header ── */

function PipelineHeader({ data }: { data: SignalFlowResponse }) {
  const { subnet, signal } = data;
  return (
    <div className="card-terminal p-3 flex items-center justify-between flex-wrap gap-2">
      <div className="flex items-baseline gap-2 flex-wrap">
        <span className="text-[12px] font-bold tracking-heading text-text uppercase">
          Signal Generation Pipeline
        </span>
        <span className="text-[11px] text-text-muted tracking-terminal">
          SN{subnet.netuid} {subnet.name}
        </span>
      </div>
      <span className={`text-[11px] font-bold tracking-terminal px-2 py-0.5 border ${signalBadgeClass(signal.type)}`}>
        {signal.type}
      </span>
    </div>
  );
}

/* ── Data Input ── */

function DataInputBox({ snapshots, days }: { snapshots: number; days: number }) {
  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-bg-section">
      <span className="text-[10px] text-accent tracking-terminal">&#9670;</span>
      <span className="text-[11px] font-semibold tracking-terminal uppercase text-text-muted">
        Data Input
      </span>
      <span className="text-border">|</span>
      <span className="text-[11px] text-text-dim tabular-nums">
        {snapshots.toLocaleString()} snapshots
      </span>
      <span className="text-text-muted">/</span>
      <span className="text-[11px] text-text-dim tabular-nums">
        {days.toFixed(1)} days
      </span>
    </div>
  );
}

/* ── Flow Stage Card ── */

function FlowStageCard({ stage }: { stage: FlowStage }) {
  const output = stage.output;
  const breakdown = (output.breakdown ?? null) as Record<string, number> | null;
  const flags = (output.flags ?? null) as string[] | null;
  const notes = (output.notes ?? null) as string[] | null;
  const trend = output.trend as string | undefined;
  const signal = output.signal as string | undefined;
  const momentum = output.momentum as number | undefined;
  const flowDir = output.flow_direction as string | undefined;
  const fundStrength = output.fundamental_strength as string | undefined;
  const riskSafety = output.risk_safety as string | undefined;

  return (
    <div className="card-terminal p-3 space-y-2.5">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-semibold tracking-terminal uppercase text-text">
          {stage.name}
        </span>
        <span className="text-[11px] text-text-dim tabular-nums">
          <span className="font-bold" style={{ color: scoreColor(stage.score) }}>
            {stage.score.toFixed(1)}
          </span>
          <span className="text-text-muted">/100</span>
        </span>
      </div>

      {(trend || signal || momentum != null) && (
        <div className="flex items-center gap-3 flex-wrap text-[11px]">
          {trend && (
            <span>
              <span className="text-text-muted">&#9656; Trend: </span>
              <span className="text-text">{String(trend).toUpperCase()}</span>
            </span>
          )}
          {signal && (
            <span>
              <span className="text-text-muted">&#9656; Signal: </span>
              <span className="text-text tabular-nums">{String(signal).toUpperCase()}</span>
            </span>
          )}
          {momentum != null && (
            <span>
              <span className="text-text-muted">&#9656; Mom: </span>
              <span className="text-text tabular-nums">{momentum.toFixed(1)}</span>
            </span>
          )}
        </div>
      )}

      {flowDir && (
        <div className="flex items-center gap-3 flex-wrap text-[11px]">
          <span>
            <span className="text-text-muted">Flow: </span>
            <span className="text-text">{String(flowDir).toUpperCase()}</span>
          </span>
          {fundStrength && (
            <span>
              <span className="text-text-muted">&#9656; Fund: </span>
              <span className="text-text">{String(fundStrength).toUpperCase()}</span>
            </span>
          )}
          {riskSafety && (
            <span>
              <span className="text-text-muted">&#9656; Risk: </span>
              <span className="text-text">{String(riskSafety).toUpperCase()}</span>
            </span>
          )}
        </div>
      )}

      <ScoreBar score={stage.score} />

      {stage.description && (
        <p className="text-[11px] text-text-muted leading-relaxed">{stage.description}</p>
      )}

      {breakdown && (
        <div className="space-y-1 pt-0.5">
          {Object.entries(breakdown).map(([key, val]) => {
            const label = BREAKDOWN_LABELS[key] ?? key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
            return (
              <div key={key} className="flex items-center gap-2">
                <span className="text-[11px] text-text-dim w-[80px] shrink-0 truncate tracking-terminal">
                  {label}
                </span>
                <div className="flex-1 h-[5px] rounded-[3px] overflow-hidden" style={{ backgroundColor: barBg() }}>
                  <div
                    className="h-full rounded-[3px] transition-all duration-700 ease-out"
                    style={{ width: `${val}%`, backgroundColor: scoreColor(val) }}
                  />
                </div>
                <span
                  className="text-[11px] tabular-nums w-[32px] text-right font-medium"
                  style={{ color: scoreColor(val) }}
                >
                  {typeof val === 'number' ? val.toFixed(0) : val}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {!breakdown && !trend && !flowDir && output && (
        <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 pt-0.5">
          {Object.entries(output).map(([key, val]) => {
            if (key === 'notes' || key === 'breakdown' || key === 'flags') return null;
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
            const display = typeof val === 'number'
              ? (val > 1e9 ? (val / 1e12).toFixed(2) + 'T' : val.toFixed(1))
              : String(val);
            return (
              <div key={key} className="flex items-center justify-between gap-2 text-[11px]">
                <span className="text-text-dim truncate">{label}</span>
                <span className="text-text tabular-nums font-medium">{display}</span>
              </div>
            );
          })}
        </div>
      )}

      {notes && notes.length > 0 && (
        <div className="space-y-0.5 pt-0.5">
          {notes.map((note) => (
            <p key={note} className="text-[10px] text-text-muted leading-relaxed">&#8226; {note}</p>
          ))}
        </div>
      )}

      {flags && flags.length > 0 && (
        <div className="flex flex-wrap gap-1 pt-0.5">
          {flags.map((flag) => (
            <span key={flag} className="text-[10px] px-1.5 py-0.5 bg-avoid/15 text-avoid border border-avoid/30 tracking-terminal">
              {flag}
            </span>
          ))}
        </div>
      )}

      {flags && flags.length === 0 && (
        <p className="text-[11px] text-text-muted tracking-terminal">
          &#9656; No flags raised
        </p>
      )}
    </div>
  );
}

/* ── Resonance Connector ── */

function ResonanceConnector({ resonance, nextStageName }: { resonance: ResonanceInfo; nextStageName: string }) {
  const desc = resonanceDescription(resonance, nextStageName);
  return (
    <div className="flex items-start gap-2 px-4 py-1.5">
      <div className="flex flex-col items-center gap-0.5 shrink-0 pt-0.5">
        <div
          className="w-[8px] h-[8px] rounded-full"
          style={{ backgroundColor: resonance.dotColor }}
        />
        <div className="w-px h-2 bg-border" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold tracking-terminal uppercase" style={{ color: resonance.dotColor }}>
            Resonance
          </span>
          <span className="text-[11px] text-text-muted tracking-terminal">
            {resonance.label}
          </span>
        </div>
        <p className="text-[11px] text-text-dim leading-relaxed">{desc}</p>
      </div>
    </div>
  );
}

/* ── Composite Score Section ── */

function CompositeSection({
  composite,
}: {
  composite: {
    score: number;
    formula: string;
    weights: Record<string, number>;
    inputs: Record<string, number>;
    thresholds: Record<string, string>;
  };
}) {
  const contributions = Object.entries(composite.weights).map(([key, weight]) => ({
    key,
    label: WEIGHT_LABELS[key] ?? key,
    weight,
    input: composite.inputs[key] ?? 0,
    contribution: (composite.inputs[key] ?? 0) * weight,
    color: WEIGHT_COLORS[key] ?? '#555555',
  }));

  const totalWeight = Object.values(composite.weights).reduce((a, b) => a + b, 0);
  const activeSegment = THRESHOLD_SEGMENTS.find(
    (s) => composite.score >= s.min && composite.score < (s.max === 100 ? 101 : s.max)
  );

  return (
    <div className="card-terminal p-4 space-y-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-semibold tracking-terminal uppercase text-text">
          Composite Score
        </span>
        <span className="text-sm font-bold tabular-nums" style={{ color: scoreColor(composite.score) }}>
          {composite.score.toFixed(1)}
          <span className="text-text-muted font-normal text-[11px]">/100</span>
        </span>
      </div>

      <div className="relative">
        <div className="flex h-5 rounded-[3px] overflow-hidden">
          {THRESHOLD_SEGMENTS.map((seg) => {
            const width = (seg.max - seg.min);
            const isActive = activeSegment?.label === seg.label;
            return (
              <div
                key={seg.label}
                className="h-full transition-all duration-500"
                style={{
                  width: `${width}%`,
                  backgroundColor: isActive ? seg.color : `${seg.color}15`,
                  borderRight: '1px solid rgba(255,255,255,0.05)',
                }}
              />
            );
          })}
        </div>

        <div className="flex justify-between mt-1 px-0.5 text-[10px] text-text-muted tabular-nums tracking-terminal">
          <span>AVOID</span>
          <span>REDUCE</span>
          <span>HOLD</span>
          <span>ACCUM</span>
          <span>BUY</span>
        </div>

        <div className="flex justify-between mt-0.5 text-[9px] text-text-muted tabular-nums">
          <span>&lt;15</span>
          <span>&ge;15</span>
          <span>&ge;30</span>
          <span>&ge;50</span>
          <span>&ge;70</span>
        </div>

        <div
          className="absolute top-0 h-full flex flex-col items-center"
          style={{ left: `${composite.score}%`, transform: 'translateX(-50%)' }}
        >
          <div
            className="w-0 h-0"
            style={{
              borderTop: `5px solid ${scoreColor(composite.score)}`,
              borderLeft: '4px solid transparent',
              borderRight: '4px solid transparent',
              marginTop: '-5px',
            }}
          />
          <div
            className="w-[2px] flex-1"
            style={{ backgroundColor: scoreColor(composite.score) }}
          />
        </div>

        <div
          className="absolute top-1 text-[10px] font-bold tabular-nums"
          style={{
            left: `${composite.score}%`,
            transform: `translateX(-50%) translateY(100%)`,
            color: scoreColor(composite.score),
            marginTop: '8px',
          }}
        >
          {composite.score.toFixed(1)}
        </div>
      </div>

      <div className="h-[6px] rounded-[3px] overflow-hidden flex">
        {contributions.map(({ key, contribution, color }) => {
          const pct = totalWeight > 0 ? (contribution / composite.score) * 100 : 0;
          return (
            <div
              key={key}
              className="h-full transition-all duration-700 ease-out"
              style={{
                width: `${pct}%`,
                backgroundColor: color,
                borderRight: '1px solid rgba(10,10,10,0.4)',
              }}
            />
          );
        })}
      </div>

      <div className="space-y-1 pt-1">
        {contributions.map(({ key, label, weight, input, contribution, color }) => (
          <div key={key} className="flex items-center gap-2 text-[11px]">
            <span
              className="w-[6px] h-[6px] rounded-[3px] shrink-0"
              style={{ backgroundColor: color }}
            />
            <span className="text-text-dim w-[60px] shrink-0 tracking-terminal">{label}</span>
            <span className="text-text tabular-nums flex-1">
              {input.toFixed(1)}
              <span className="text-text-muted"> x </span>
              <span className="text-text-muted">{(weight * 100).toFixed(0)}%</span>
              <span className="text-text-muted"> = </span>
              <span className="font-medium" style={{ color }}>{contribution.toFixed(1)}</span>
            </span>
          </div>
        ))}
        <div className="border-t border-border pt-1.5 mt-1 flex items-center justify-between">
          <span className="text-[11px] text-text-muted tracking-terminal">Total</span>
          <span className="text-sm font-bold tabular-nums" style={{ color: scoreColor(composite.score) }}>
            {composite.score.toFixed(1)}
          </span>
        </div>
      </div>
    </div>
  );
}

/* ── Signal Output ── */

function SignalOutput({
  signal,
  composite,
}: {
  signal: { type: string; confidence: number; reasoning: string };
  composite: { score: number };
}) {
  const color = scoreColor(composite.score);

  return (
    <div
      className="card-terminal p-4 space-y-3"
      style={{ borderColor: `${color}33` }}
    >
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <span
            className="px-3 py-1 text-sm font-extrabold tracking-heading border"
            style={{
              borderColor: `${color}55`,
              color,
              backgroundColor: `${color}10`,
            }}
          >
            {signal.type}
          </span>
          <span className="text-[11px] text-text-dim tabular-nums tracking-terminal">
            Score: <span className="text-text font-semibold">{composite.score.toFixed(1)}</span>/100
          </span>
        </div>
        <div className="text-right">
          <span className="text-[10px] font-semibold tracking-terminal uppercase text-text-muted block">
            Confidence
          </span>
          <span className="text-lg font-bold tabular-nums" style={{ color }}>
            {signal.confidence.toFixed(0)}%
          </span>
        </div>
      </div>

      {signal.reasoning && (
        <div className="bg-bg-section border border-border rounded-[6px] p-3 max-h-48 overflow-y-auto">
          <pre className="text-[11px] text-text-dim whitespace-pre-wrap leading-relaxed m-0 font-[var(--font-mono)]">
            {signal.reasoning}
          </pre>
        </div>
      )}
    </div>
  );
}

/* ── Shared Primitives ── */

function ScoreBar({ score }: { score: number }) {
  return (
    <div className="h-[6px] rounded-[3px] overflow-hidden" style={{ backgroundColor: barBg() }}>
      <div
        className="h-full rounded-[3px] transition-all duration-1000 ease-out"
        style={{ width: `${score}%`, backgroundColor: scoreColor(score) }}
      />
    </div>
  );
}

function FlowConnector() {
  return (
    <div className="flex justify-center py-1">
      <div className="w-px h-3 bg-border relative">
        <div
          className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full"
          style={{
            width: 0,
            height: 0,
            borderLeft: '3px solid transparent',
            borderRight: '3px solid transparent',
            borderTop: '3px solid #2a2a2a',
          }}
        />
      </div>
    </div>
  );
}

/* ── Skeletons ── */

function PipelineSkeleton() {
  return (
    <div className="space-y-0">
      <SkeletonBox h={48} />
      <div className="h-px bg-border" />
      <SkeletonBox h={28} />
      <FlowConnector />
      <SkeletonBox h={100} />
      <FlowConnector />
      <SkeletonBox h={160} />
      <FlowConnector />
      <SkeletonBox h={120} />
      <FlowConnector />
      <SkeletonBox h={100} />
      <FlowConnector />
      <SkeletonBox h={200} />
      <FlowConnector />
      <SkeletonBox h={160} />
    </div>
  );
}

function PipelineError({ message }: { message: string }) {
  return (
    <div className="card-terminal p-4 text-center space-y-1.5" style={{ borderColor: 'rgba(255, 68, 85, 0.3)' }}>
      <span className="text-avoid text-xs font-semibold tracking-terminal uppercase block">
        Error
      </span>
      <span className="text-text-dim text-[11px]">{message}</span>
    </div>
  );
}

function SkeletonBox({ h }: { h: number }) {
  return (
    <div
      className="card-terminal animate-pulse"
      style={{ height: h }}
    />
  );
}
