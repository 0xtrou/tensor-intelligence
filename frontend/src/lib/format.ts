const SIGNAL_COLORS: Record<string, string> = {
  BUY: 'var(--color-buy)',
  ACCUMULATE: 'var(--color-accumulate)',
  HOLD: 'var(--color-hold)',
  REDUCE: 'var(--color-reduce)',
  AVOID: 'var(--color-avoid)',
};

const SIGNAL_BG: Record<string, string> = {
  BUY: 'bg-buy/15 text-buy border-buy/30',
  ACCUMULATE: 'bg-accumulate/15 text-accumulate border-accumulate/30',
  HOLD: 'bg-hold/15 text-hold border-hold/30',
  REDUCE: 'bg-reduce/15 text-reduce border-reduce/30',
  AVOID: 'bg-avoid/15 text-avoid border-avoid/30',
};

export function signalColor(type: string): string {
  return SIGNAL_COLORS[type] ?? 'var(--color-text-dim)';
}

export function signalBadgeClass(type: string): string {
  return SIGNAL_BG[type] ?? 'bg-text-muted/15 text-text-dim border-border';
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000_000) return (n / 1_000_000_000).toFixed(1) + 'B';
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
  return n.toFixed(2);
}

export function formatPercent(n: number): string {
  return n.toFixed(2) + '%';
}

export function formatPrice(n: number): string {
  if (n >= 1) return '$' + n.toFixed(2);
  if (n >= 0.001) return '$' + n.toFixed(4);
  return '$' + n.toFixed(8);
}

export function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
