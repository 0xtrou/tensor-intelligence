import { describe, it, expect } from 'vitest'
import {
  formatNumber,
  formatPercent,
  formatPrice,
  formatTimestamp,
  signalColor,
  signalBadgeClass,
} from '../format'

describe('formatNumber', () => {
  it('formats billions', () => expect(formatNumber(2_500_000_000)).toBe('2.5B'))
  it('formats millions', () => expect(formatNumber(1_500_000)).toBe('1.5M'))
  it('formats thousands', () => expect(formatNumber(1500)).toBe('1.5K'))
  it('formats small numbers', () => expect(formatNumber(100)).toBe('100.00'))
  it('formats decimals', () => expect(formatNumber(0.05)).toBe('0.05'))
})

describe('formatPercent', () => {
  it('formats percentage', () => expect(formatPercent(0.0819)).toBe('0.08%'))
  it('formats integer percentage', () => expect(formatPercent(100)).toBe('100.00%'))
  it('formats zero', () => expect(formatPercent(0)).toBe('0.00%'))
})

describe('formatPrice', () => {
  it('formats dollars', () => expect(formatPrice(1.5)).toBe('$1.50'))
  it('formats cents', () => expect(formatPrice(0.03)).toBe('$0.0300'))
  it('formats micro prices', () => expect(formatPrice(0.00001)).toBe('$0.00001000'))
})

describe('formatTimestamp', () => {
  it('formats ISO string to readable date', () => {
    const result = formatTimestamp('2026-03-20T10:30:00Z')
    expect(result).toBeTruthy()
    expect(typeof result).toBe('string')
    expect(result.length).toBeGreaterThan(0)
  })
})

describe('signalColor', () => {
  it('returns buy color', () => expect(signalColor('BUY')).toBe('var(--color-buy)'))
  it('returns accumulate color', () => expect(signalColor('ACCUMULATE')).toBe('var(--color-accumulate)'))
  it('returns hold color', () => expect(signalColor('HOLD')).toBe('var(--color-hold)'))
  it('returns reduce color', () => expect(signalColor('REDUCE')).toBe('var(--color-reduce)'))
  it('returns avoid color', () => expect(signalColor('AVOID')).toBe('var(--color-avoid)'))
  it('returns fallback for unknown', () => expect(signalColor('UNKNOWN')).toBe('var(--color-text-dim)'))
})

describe('signalBadgeClass', () => {
  it('returns buy badge classes', () => expect(signalBadgeClass('BUY')).toContain('buy'))
  it('returns fallback for unknown', () => expect(signalBadgeClass('UNKNOWN')).toContain('text-muted'))
})
