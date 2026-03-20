import { useState, useEffect, type ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { getHealth } from '../api/client'
import type { HealthStatus } from '../types'

export function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [healthLoading, setHealthLoading] = useState(true)

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const h = await getHealth();
        if (!cancelled) setHealth(h);
      } catch {
        if (!cancelled) setHealth(null);
      } finally {
        if (!cancelled) setHealthLoading(false);
      }
    };
    check();
    const id = setInterval(check, 15000);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  const isRoot = location.pathname === '/'

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-md">
        <div className="max-w-[1600px] mx-auto px-4 h-12 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {!isRoot && (
              <Link
                to="/"
                className="text-text-dim hover:text-accent transition-colors text-[11px] tracking-terminal"
              >
                &larr; BACK
              </Link>
            )}
            <Link to="/" className="flex items-center gap-2 no-underline">
              <span className="text-[13px] font-bold tracking-heading text-text uppercase">
                Bittorrent Intel
              </span>
            </Link>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-text-dim tracking-terminal uppercase">
            <span className="flex items-center gap-1.5">
              <span
                className={`inline-block w-[6px] h-[6px] rounded-full ${
                  healthLoading
                    ? 'bg-text-muted animate-pulse'
                    : health?.status === 'ok'
                    ? 'bg-accent animate-pulse-live'
                    : 'bg-avoid'
                }`}
              />
              {healthLoading ? '...' : health?.status === 'ok' ? 'online' : 'offline'}
            </span>
            {health?.version && (
              <span className="text-text-muted">v{health.version}</span>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 py-4">
        {children}
      </main>
    </div>
  )
}
