import type { SubnetSignal } from '../types';
import { signalBadgeClass, formatPercent, formatTimestamp } from '../lib/format';

export function SignalHistory({ data }: { data: SubnetSignal[] | undefined }) {
  if (!data || data.length === 0) {
    return (
      <div className="card-terminal p-4">
        <div className="text-[11px] text-text-muted tracking-wide-label mb-3">
          <span className="text-accent">$</span> cat signal_history.log
        </div>
        <div className="text-text-muted text-[11px] py-8 text-center tracking-terminal">
          No signals recorded
        </div>
      </div>
    );
  }

  return (
    <div className="card-terminal p-4">
      <div className="text-[11px] text-text-muted tracking-wide-label mb-3">
        <span className="text-accent">$</span> cat signal_history.log
      </div>
      <div className="space-y-0">
        {data.map((sig) => (
          <div
            key={`sig-${sig.created_at}-${sig.signal_type}`}
            className="flex items-center gap-2.5 py-2 border-b border-border/40 last:border-0"
          >
            <span
              className={`text-[10px] font-semibold tracking-terminal px-1.5 py-0.5 border flex-shrink-0 ${signalBadgeClass(sig.signal_type)}`}
            >
              {sig.signal_type}
            </span>
            <div className="flex-1 flex items-center gap-3 text-[11px]">
              <span className="text-text-dim tabular-nums">
                conf {formatPercent(sig.confidence)}
              </span>
              <span className="text-text-dim">
                flow {typeof sig.flow_signal === 'number' ? sig.flow_signal.toFixed(4) : String(sig.flow_signal)}
              </span>
              <span className="text-text-muted tabular-nums">
                score {sig.composite_score.toFixed(2)}
              </span>
            </div>
            <span className="text-text-muted text-[10px] flex-shrink-0 tabular-nums">
              {formatTimestamp(sig.created_at)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
