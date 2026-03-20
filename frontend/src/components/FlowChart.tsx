import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { FlowDataPoint } from '../types';
import { formatTimestamp } from '../lib/format';

interface ChartTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; name: string }>;
  label?: string;
}

function ChartTooltip({ active, payload, label }: ChartTooltipProps) {
  if (!active || !payload?.length || !label) return null;
  return (
    <div className="card-terminal px-3 py-2 text-[11px]">
      <div className="text-text-muted mb-1 tracking-terminal">{label}</div>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-[6px] h-[6px] rounded-full bg-accent" />
          <span className="text-text-dim">{p.name}:</span>
          <span className="text-text font-medium tabular-nums">{p.value.toFixed(4)}</span>
        </div>
      ))}
    </div>
  );
}

export function FlowChart({ data }: { data: FlowDataPoint[] | undefined }) {
  if (!data || data.length === 0) {
    return (
      <div className="card-terminal p-4">
        <div className="text-[11px] text-text-muted tracking-wide-label mb-3">
          <span className="text-accent">$</span> cat flow_ema.log
        </div>
        <div className="h-52 flex items-center justify-center text-text-muted text-[11px] tracking-terminal">
          No flow data available
        </div>
      </div>
    );
  }

  const chartData = data.map((d) => ({
    ...d,
    time: formatTimestamp(d.timestamp),
  }));

  return (
    <div className="card-terminal p-4">
      <div className="text-[11px] text-text-muted tracking-wide-label mb-3">
        <span className="text-accent">$</span> cat flow_ema.log
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }}
            interval="preserveStartEnd"
            tickFormatter={(v: string) => {
              const parts = v.split(', ');
              return parts.length > 1 ? parts[0] : v;
            }}
            axisLine={{ stroke: 'var(--color-border)' }}
          />
          <YAxis
            tick={{ fontSize: 10, fill: 'var(--color-text-muted)' }}
            tickFormatter={(v: number) => v.toFixed(2)}
            width={60}
            axisLine={{ stroke: 'var(--color-border)' }}
          />
          <Tooltip content={<ChartTooltip />} />
          <Line
            type="monotone"
            dataKey="flow_ema"
            name="Flow EMA"
            stroke="var(--color-accent)"
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, stroke: 'var(--color-accent)', strokeWidth: 2, fill: 'var(--color-bg)' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
