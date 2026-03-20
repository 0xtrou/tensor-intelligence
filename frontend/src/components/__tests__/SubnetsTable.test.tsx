import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SubnetsTable } from '../SubnetsTable'
import type { Subnet } from '../../types'

vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
}))

const mockSubnets: Subnet[] = [
  {
    netuid: 64,
    name: 'Chutes',
    price: 0.03,
    market_cap: 1_500_000_000,
    emission: 100,
    emission_share: 0.0819,
    active_miners: 120,
    active_validators: 40,
    fundamental_score: 0.76,
    risk_score: 0.76,
    ssi_score: null,
    updated_at: '2026-03-20T10:00:00Z',
  },
  {
    netuid: 8,
    name: 'Trading Network',
    price: 0.015,
    market_cap: 500_000_000,
    emission: 50,
    emission_share: 0.11,
    active_miners: 40,
    active_validators: 15,
    fundamental_score: null,
    risk_score: null,
    ssi_score: null,
    updated_at: '2026-03-20T10:00:00Z',
  },
]

describe('SubnetsTable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders subnet data', () => {
    render(<SubnetsTable data={mockSubnets} />)
    expect(screen.getByText('Chutes')).toBeDefined()
    expect(screen.getByText('Trading Network')).toBeDefined()
    expect(screen.getByText('#64')).toBeDefined()
  })

  it('shows dash for null scores', () => {
    render(<SubnetsTable data={mockSubnets} />)
    const cells = screen.getAllByText('-')
    expect(cells.length).toBeGreaterThanOrEqual(3)
  })

  it('renders skeleton when no data', () => {
    const { container } = render(<SubnetsTable data={undefined} />)
    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })
})
