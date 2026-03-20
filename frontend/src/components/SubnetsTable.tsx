import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Subnet, SortConfig, SortField } from '../types';
import { formatNumber, formatPercent, formatPrice } from '../lib/format';

const SORT_FIELDS: { key: SortField; label: string }[] = [
  { key: 'name', label: 'Subnet' },
  { key: 'price', label: 'Price' },
  { key: 'emission_share', label: 'Emission' },
  { key: 'active_miners', label: 'Miners' },
  { key: 'fundamental_score', label: 'Fund.' },
  { key: 'risk_score', label: 'Risk' },
];

export function SubnetsTable({ data }: { data: Subnet[] | undefined }) {
  const [sort, setSort] = useState<SortConfig>({ field: 'emission_share', dir: 'desc' });
  const navigate = useNavigate();

  const sorted = useMemo(() => {
    if (!data) return [];
    const arr = [...data];
    arr.sort((a, b) => {
      const av = a[sort.field];
      const bv = b[sort.field];
      const cmp = typeof av === 'string' ? av.localeCompare(bv as string) : (av as number) - (bv as number);
      return sort.dir === 'asc' ? cmp : -cmp;
    });
    return arr;
  }, [data, sort]);

  const toggleSort = (field: SortField) => {
    setSort((prev) => ({
      field,
      dir: prev.field === field && prev.dir === 'desc' ? 'asc' : 'desc',
    }));
  };

  if (!data || data.length === 0) return <TableSkeleton />;

  return (
    <div className="card-terminal overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-[12px]">
          <thead>
            <tr className="border-b border-border text-text-muted">
              {SORT_FIELDS.map(({ key, label }) => (
                <th
                  key={key}
                  className="text-left px-3 py-2 font-semibold tracking-terminal uppercase cursor-pointer hover:text-text transition-colors select-none whitespace-nowrap text-[11px]"
                  onClick={() => toggleSort(key)}
                >
                  {label}
                  {sort.field === key && (
                    <span className="ml-1 text-accent">{sort.dir === 'desc' ? '\u25BC' : '\u25B2'}</span>
                  )}
                </th>
              ))}
              <th className="text-right px-3 py-2 font-semibold tracking-terminal uppercase text-text-muted text-[11px]">
                Validators
              </th>
              <th className="text-right px-3 py-2 font-semibold tracking-terminal uppercase text-text-muted text-[11px]">
                SSI
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((s) => (
                <tr
                  key={s.netuid}
                  className="border-b border-border/40 hover:border-border transition-colors cursor-pointer"
                  onClick={() => navigate(`/subnet/${s.netuid}`)}
                >
                  <td className="px-3 py-2 font-medium text-text whitespace-nowrap tracking-terminal">
                    <span className="text-text-muted mr-1.5">#{s.netuid}</span>
                    {s.name}
                  </td>
                  <td className="px-3 py-2 tabular-nums text-text-dim">{formatPrice(s.price)}</td>
                  <td className="px-3 py-2 tabular-nums text-text-dim">{formatPercent(s.emission_share)}</td>
                  <td className="px-3 py-2 tabular-nums">{formatNumber(s.active_miners)}</td>
                  <td className="px-3 py-2 tabular-nums">
                    <ScoreCell value={s.fundamental_score} />
                  </td>
                  <td className="px-3 py-2 tabular-nums">
                    <ScoreCell value={s.risk_score} invert />
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums text-text-dim">{formatNumber(s.active_validators)}</td>
                  <td className="px-3 py-2 text-right tabular-nums text-text-dim">{s.ssi_score != null ? s.ssi_score.toFixed(1) : '-'}</td>
                </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ScoreCell({ value, invert = false }: { value: number | null; invert?: boolean }) {
  if (value == null) return <span className="text-text-muted">-</span>;
  const color =
    value >= 0.7 ? (invert ? 'text-avoid' : 'text-buy') :
    value >= 0.4 ? 'text-accumulate' :
    invert ? 'text-buy' : 'text-avoid';
  return <span className={color}>{value.toFixed(2)}</span>;
}

function TableSkeleton() {
  return (
    <div className="card-terminal overflow-hidden p-4 space-y-2.5 animate-pulse">
      {['s1','s2','s3','s4','s5','s6','s7','s8'].map((id) => (
        <div key={`skel-${id}`} className="h-5 bg-border rounded-[3px]" style={{ width: `${70 + Math.random() * 30}%` }} />
      ))}
    </div>
  );
}
