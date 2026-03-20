import { useParams } from 'react-router-dom';
import { usePolling } from '../hooks/usePolling';
import { getSubnetDetail, getSubnetFlow } from '../api/client';
import { FlowChart } from './FlowChart';
import { SignalHistory } from './SignalHistory';
import { SignalFlowVisualization } from './SignalFlowVisualization';
import { formatNumber, formatPercent, formatPrice } from '../lib/format';

export function SubnetDetail() {
  const { netuid } = useParams<{ netuid: string }>();
  const id = Number(netuid);

  const detail = usePolling({
    fetcher: () => getSubnetDetail(id),
    intervalMs: 60_000,
    enabled: !Number.isNaN(id),
  });

  const flow = usePolling({
    fetcher: () => getSubnetFlow(id, 168),
    intervalMs: 60_000,
    enabled: !Number.isNaN(id),
  });

  if (Number.isNaN(id)) {
    return (
      <div className="text-avoid text-xs font-semibold tracking-terminal uppercase py-20 text-center">
        Invalid subnet ID
      </div>
    );
  }

  if (detail.error && !detail.data) {
    return (
      <div className="text-avoid text-xs font-semibold tracking-terminal uppercase py-20 text-center">
        Failed to load subnet #{id}: {detail.error}
      </div>
    );
  }

  const subnet = detail.data?.subnet;
  const recentSignals = detail.data?.recent_signals;

  return (
    <div className="space-y-5">
      {subnet ? (
        <div className="flex items-baseline gap-3 flex-wrap">
          <div>
            <div className="text-[11px] text-text-muted tracking-wide-label mb-0.5">
              <span className="text-accent">$</span> cat subnet/{subnet.netuid}.md
            </div>
            <div className="flex items-baseline gap-3 flex-wrap">
              <h1 className="text-base font-bold tracking-heading text-text uppercase">
                {subnet.name}
              </h1>
              <span className="text-[11px] text-text-muted tracking-terminal">SN{subnet.netuid}</span>
              <span className="text-sm font-semibold text-buy tabular-nums">
                {formatPrice(subnet.price)}
              </span>
              <span className="text-[11px] text-text-dim tabular-nums tracking-terminal">
                {formatPercent(subnet.emission_share)} emission
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="animate-pulse">
          <div className="h-3 w-32 bg-border rounded-[3px] mb-1" />
          <div className="h-6 w-48 bg-border rounded-[3px]" />
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard
          label="Miners"
          value={subnet ? formatNumber(subnet.active_miners) : undefined}
        />
        <MetricCard
          label="Validators"
          value={subnet ? formatNumber(subnet.active_validators) : undefined}
        />
        <MetricCard
          label="Fundamental"
          value={subnet?.fundamental_score != null ? subnet.fundamental_score.toFixed(2) : undefined}
          color={subnet?.fundamental_score != null
            ? (subnet.fundamental_score >= 0.7 ? 'text-buy' : subnet.fundamental_score < 0.4 ? 'text-avoid' : 'text-accumulate')
            : undefined
          }
        />
        <MetricCard
          label="Risk Score"
          value={subnet?.risk_score != null ? subnet.risk_score.toFixed(2) : undefined}
          color={subnet?.risk_score != null
            ? (subnet.risk_score >= 0.7 ? 'text-avoid' : subnet.risk_score < 0.4 ? 'text-buy' : 'text-accumulate')
            : undefined
          }
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <FlowChart data={flow.data} />
        <SignalHistory data={recentSignals} />
      </div>

      <SignalFlowVisualization netuid={id} />
    </div>
  );
}

function MetricCard({
  label,
  value,
  color = 'text-text',
}: {
  label: string;
  value: string | undefined;
  color?: string;
}) {
  return (
    <div className="card-terminal p-3">
      <span className="text-[10px] font-semibold tracking-terminal uppercase text-text-muted block mb-1">
        {label}
      </span>
      {value ? (
        <span className={`text-lg font-bold tabular-nums tracking-terminal ${color}`}>{value}</span>
      ) : (
        <div className="h-6 w-16 bg-border rounded-[3px] animate-pulse" />
      )}
    </div>
  );
}
