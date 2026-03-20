import { usePolling } from '../hooks/usePolling';
import { getSubnets, getSignalSummary, getTopSignals } from '../api/client';
import { SignalSummaryCards } from './SignalSummaryCards';
import { TopOpportunities } from './TopOpportunities';
import { SubnetsTable } from './SubnetsTable';

export function Dashboard() {
  const subnets = usePolling({ fetcher: getSubnets, intervalMs: 30_000 });
  const signals = usePolling({ fetcher: getSignalSummary, intervalMs: 30_000 });
  const topSigs = usePolling({ fetcher: () => getTopSignals(10), intervalMs: 30_000 });

  const hasError = subnets.error || signals.error || topSigs.error;
  const isLoading = subnets.loading && signals.loading && topSigs.loading;

  if (hasError && !subnets.data && !signals.data) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="text-avoid text-xs font-semibold tracking-terminal uppercase">Error</div>
        <div className="text-text-dim text-[11px] max-w-md text-center">
          {subnets.error || signals.error || topSigs.error}
        </div>
        <div className="text-text-muted text-[11px] tracking-terminal">
          Ensure backend is running at localhost:8000
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-[11px] text-text-muted tracking-wide-label mb-0.5">
            <span className="text-accent">$</span> cat OVERVIEW.md
          </div>
          <h1 className="text-base font-bold tracking-heading text-text uppercase">
            Subnet Intelligence
          </h1>
        </div>
        {isLoading && (
          <div className="flex items-center gap-2 text-text-muted text-[11px] tracking-terminal uppercase">
            <span className="w-3 h-3 border-2 border-text-muted border-t-transparent rounded-full animate-spin" />
            Loading...
          </div>
        )}
      </div>

      <SignalSummaryCards data={signals.data} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1">
          <TopOpportunities data={topSigs.data} />
        </div>
        <div className="lg:col-span-2">
          <SubnetsTable data={subnets.data} />
        </div>
      </div>
    </div>
  );
}
