import type { TopSignal } from '../types';
import { signalBadgeClass, formatPercent } from '../lib/format';

export function TopOpportunities({ data }: { data: TopSignal[] | undefined }) {
  if (!data || data.length === 0) return <OpportunitiesSkeleton />;

  return (
    <div className="space-y-2">
      <div className="text-[11px] text-text-muted tracking-wide-label mb-2">
        <span className="text-accent">$</span> cat SIGNALS.md
      </div>
      <div className="space-y-1.5">
        {data.map((sig) => (
          <div
            key={`${sig.netuid}-${sig.signal_type}-${sig.confidence}`}
            className="card-terminal p-2.5 flex items-start gap-2.5"
          >
            <div className="flex-shrink-0 flex flex-col items-center gap-0.5">
              <span
                className={`text-[10px] font-semibold tracking-terminal px-1.5 py-0.5 border ${signalBadgeClass(sig.signal_type)}`}
              >
                {sig.signal_type}
              </span>
              <span className="text-[10px] text-text-muted tabular-nums">
                SN{sig.netuid}
              </span>
            </div>

            <div className="flex-1 min-w-0">
              <div className="text-[12px] font-medium text-text truncate tracking-terminal">
                {sig.subnet_name ?? `Subnet ${sig.netuid}`}
              </div>
              {sig.reasoning && (
                <p className="text-[11px] text-text-dim mt-0.5 line-clamp-2 leading-relaxed">
                  {sig.reasoning}
                </p>
              )}
            </div>

            <div className="flex-shrink-0 w-24 flex flex-col items-end gap-1">
              <span className="text-[11px] text-text-dim tabular-nums tracking-terminal">
                {formatPercent(sig.confidence)}
              </span>
              <div className="w-full h-[5px] bg-border rounded-[3px] overflow-hidden">
                <div
                  className="h-full rounded-[3px] transition-all duration-500"
                  style={{
                    width: `${Math.min(sig.confidence * 100, 100)}%`,
                    backgroundColor: 'var(--color-accent)',
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OpportunitiesSkeleton() {
  return (
    <div className="space-y-2">
      <div className="text-[11px] text-text-muted tracking-wide-label mb-2">
        <span className="text-accent">$</span> cat SIGNALS.md
      </div>
      {(['a', 'b', 'c'] as const).map((id) => (
        <div
          key={`skel-${id}`}
          className="card-terminal p-2.5 animate-pulse flex items-start gap-2.5"
        >
          <div className="w-14 h-4 bg-border rounded-[3px]" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3.5 w-40 bg-border rounded-[3px]" />
            <div className="h-3 w-56 bg-border rounded-[3px]" />
          </div>
        </div>
      ))}
    </div>
  );
}
