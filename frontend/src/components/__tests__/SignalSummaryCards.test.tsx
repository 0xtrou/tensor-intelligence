import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SignalSummaryCards } from '../SignalSummaryCards'

describe('SignalSummaryCards', () => {
  it('renders all 5 signal types', () => {
    const data = { BUY: 2, ACCUMULATE: 1, HOLD: 0, REDUCE: 0, AVOID: 0 }
    render(<SignalSummaryCards data={data} />)
    expect(screen.getByText('BUY')).toBeDefined()
    expect(screen.getByText('ACCUMULATE')).toBeDefined()
    expect(screen.getByText('HOLD')).toBeDefined()
    expect(screen.getByText('REDUCE')).toBeDefined()
    expect(screen.getByText('AVOID')).toBeDefined()
  })

  it('displays counts', () => {
    const data = { BUY: 3, ACCUMULATE: 1, HOLD: 5, REDUCE: 2, AVOID: 0 }
    render(<SignalSummaryCards data={data} />)
    expect(screen.getByText('3')).toBeDefined()
    expect(screen.getByText('1')).toBeDefined()
    expect(screen.getByText('5')).toBeDefined()
  })

  it('renders skeleton when data is null', () => {
    const { container } = render(<SignalSummaryCards data={undefined} />)
    const skeletons = container.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })
})
