import { describe, expect, test } from 'vitest'

import { sanitizeReturnTo } from '@/features/auth/return-to'

describe('sanitizeReturnTo', () => {
  test('accepts local application paths with search and hash', () => {
    expect(sanitizeReturnTo('/dashboard?month=2026-09#summary')).toBe(
      '/dashboard?month=2026-09#summary'
    )
    expect(sanitizeReturnTo('/wallets')).toBe('/wallets')
  })

  test('rejects open-redirect targets', () => {
    expect(sanitizeReturnTo('https://evil.example.com')).toBe('/')
    expect(sanitizeReturnTo('//evil.example.com')).toBe('/')
    expect(sanitizeReturnTo('/\\evil.example.com')).toBe('/')
    expect(sanitizeReturnTo('http://localhost:5173/admin')).toBe('/')
    expect(sanitizeReturnTo('mailto:admin@example.com')).toBe('/')
  })

  test('rejects protocol-relative backslash and control-character tricks', () => {
    expect(sanitizeReturnTo('/\tevil')).toBe('/')
    expect(sanitizeReturnTo('/ev\u0000il')).toBe('/')
    expect(sanitizeReturnTo('/ev\ril')).toBe('/')
  })

  test('rejects the login route to avoid a redirect loop', () => {
    expect(sanitizeReturnTo('/login')).toBe('/')
    expect(sanitizeReturnTo('/login?returnTo=%2F')).toBe('/')
  })

  test('falls back to the app root for anything that is not a local path', () => {
    expect(sanitizeReturnTo(undefined)).toBe('/')
    expect(sanitizeReturnTo('')).toBe('/')
    expect(sanitizeReturnTo('dashboard')).toBe('/')
    expect(sanitizeReturnTo('   ')).toBe('/')
    expect(sanitizeReturnTo('/')).toBe('/')
  })
})
