import { describe, expect, test } from 'vitest'

import { ApiError, NetworkError } from '@/api/client'
import { classifyLoginError } from '@/features/auth/login-errors'

describe('classifyLoginError', () => {
  test('maps wrong-password (401) and unknown-email (404) to invalid credentials', () => {
    expect(classifyLoginError(new ApiError(401, { error: { code: 'unauthorized' } })).kind).toBe(
      'invalid-credentials'
    )
    expect(classifyLoginError(new ApiError(404, { error: { code: 'not_found' } })).kind).toBe(
      'invalid-credentials'
    )
  })

  test('maps inactive accounts (403) to a disabled-account message', () => {
    const classified = classifyLoginError(
      new ApiError(403, { error: { code: 'not_enough_privileges' } })
    )
    expect(classified.kind).toBe('inactive-account')
    expect(classified.message).toContain('vô hiệu hóa')
  })

  test('maps rate limiting (429) to a retry-later message', () => {
    const classified = classifyLoginError(new ApiError(429, { error: { code: '429' } }))
    expect(classified.kind).toBe('rate-limited')
    expect(classified.message).toContain('thử lại sau')
  })

  test('maps network failures to a connection message', () => {
    const classified = classifyLoginError(new NetworkError())
    expect(classified.kind).toBe('network')
    expect(classified.message).toContain('Không thể kết nối')
  })

  test('maps anything else to a generic retryable failure', () => {
    expect(classifyLoginError(new ApiError(500, undefined)).kind).toBe('unexpected')
    expect(classifyLoginError(new Error('boom')).kind).toBe('unexpected')
    expect(classifyLoginError('not an error').kind).toBe('unexpected')
  })

  test('messages are distinct per kind', () => {
    const kinds = [
      'invalid-credentials',
      'inactive-account',
      'rate-limited',
      'network',
      'unexpected',
    ] as const
    const messages = kinds.map(kind => {
      const error =
        kind === 'network'
          ? new NetworkError()
          : kind === 'unexpected'
            ? new Error('boom')
            : new ApiError(
                kind === 'invalid-credentials' ? 401 : kind === 'inactive-account' ? 403 : 429,
                {}
              )
      return classifyLoginError(error).message
    })
    expect(new Set(messages).size).toBe(kinds.length)
  })
})
