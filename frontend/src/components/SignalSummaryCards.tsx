import type { SignalType, SignalSummary } from '../types';
import { signalColor } from '../lib/format';

const SIGNALS: SignalType[] = ['BUY', 'ACCUMULATE', 'HOLD', 'REDUCE', 'AVOID'];

export function SignalSummaryCards({ data }: { data: SignalSummary | undefined }) {
  if (!data) return <CardsSkeleton />;

  return (
    <div className="grid grid-cols-5 gap-3">
      {SIGNALS.map((type) => {
        const isHighlighted = type === 'BUY' || type === 'AVOID';
        return (
          <div
            key={type}
            className={`card-terminal p-3 flex flex-col gap-1.5 ${isHighlighted ? 'glow-accent' : ''}`}
            style={isHighlighted ? { borderColor: `${signalColor(type)}22` } : undefined}
          >
            <span
              className="text-[11px] font-semibold tracking-terminal uppercase"
              style={{ color: signalColor(type) }}
            >
              {type}
            </span>
            <span className="text-xl font-bold tabular-nums tracking-terminal">
              {data[type] ?? 0}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function CardsSkeleton() {
  return (
    <div className="grid grid-cols-5 gap-3">
      {SIGNALS.map((type) => (
        <div
          key={`skel-${type}`}
          className="card-terminal p-3 flex flex-col gap-1.5 animate-pulse"
        >
          <div className="h-3 w-12 bg-border rounded-[3px]" />
          <div className="h-6 w-8 bg-border rounded-[3px]" />
        </div>
      ))}
    </div>
  );
}
