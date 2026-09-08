import { QueryClient } from '@tanstack/react-query'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { ApiError } from '@/api/client'
import type { User } from '@/api/generated/models'
import { logoutApiV0AuthenLogoutPost } from '@/api/generated/authentication/authentication'
import { readUserMeApiV0UsersMeGet } from '@/api/generated/users/users'
import { resetTransportSession } from '@/api/client'

import {
  clearPrivateData,
  currentUserQueryOptions,
  fetchCurrentUser,
  login,
  logout,
  notifySessionLost,
  subscribeSessionLost,
} from '@/features/auth/session'

vi.mock('@/api/client', async importOriginal => {
  const actual = await importOriginal<typeof import('@/api/client')>()
  return { ...actual, resetTransportSession: vi.fn() }
})

vi.mock('@/api/generated/authentication/authentication', () => ({
  loginAccessTokenApiV0AuthenLoginPost: vi.fn(),
  logoutApiV0AuthenLogoutPost: vi.fn(),
  refreshTokenApiV0AuthenRefreshPost: vi.fn(),
  logoutAllApiV0AuthenLogoutAllPost: vi.fn(),
}))

vi.mock('@/api/generated/users/users', () => ({
  readUserMeApiV0UsersMeGet: vi.fn(),
}))

const loginEndpoint = vi.mocked(
  await import('@/api/generated/authentication/authentication')
).loginAccessTokenApiV0AuthenLoginPost
const logoutEndpoint = vi.mocked(logoutApiV0AuthenLogoutPost)
const meEndpoint = vi.mocked(readUserMeApiV0UsersMeGet)

const owner: User = { id: 1, email: 'owner@example.com', full_name: 'Session Owner' }

function meResponse(user: User) {
  return {
    data: { status: 'success' as const, data: user, error: null },
    status: 200 as const,
    headers: new Headers(),
  }
}

let queryClient: QueryClient

beforeEach(() => {
  vi.clearAllMocks()
  queryClient = new QueryClient()
})

describe('login', () => {
  test('logs in, discards the token body, and verifies the session server-side', async () => {
    loginEndpoint.mockResolvedValue({
      data: { access_token: 'a-token', refresh_token: 'r-token', token_type: 'bearer' },
      status: 200 as const,
      headers: new Headers(),
    })
    meEndpoint.mockResolvedValue(meResponse(owner))

    const user = await login(queryClient, {
      email: 'owner@example.com',
      password: 'correct-password',
    })

    expect(loginEndpoint).toHaveBeenCalledWith({
      username: 'owner@example.com',
      password: 'correct-password',
    })
    expect(meEndpoint).toHaveBeenCalledTimes(1)
    expect(user).toEqual(owner)
    // Tokens are never cached: only the verified user lands in the query cache.
    expect(queryClient.getQueryData(currentUserQueryOptions.queryKey)).toEqual(owner)
    expect(JSON.stringify(queryClient.getQueryCache())).not.toContain('a-token')
    expect(JSON.stringify(queryClient.getQueryCache())).not.toContain('r-token')
    expect(resetTransportSession).toHaveBeenCalledTimes(1)
  })

  test('rejects without seeding state when the credentials are wrong', async () => {
    loginEndpoint.mockRejectedValue(new ApiError(401, { error: { code: 'unauthorized' } }))

    await expect(
      login(queryClient, { email: 'owner@example.com', password: 'wrong' })
    ).rejects.toBeInstanceOf(ApiError)

    expect(meEndpoint).not.toHaveBeenCalled()
    expect(queryClient.getQueryData(currentUserQueryOptions.queryKey)).toBeUndefined()
    expect(resetTransportSession).not.toHaveBeenCalled()
  })

  test('rejects when the server cannot verify the fresh session', async () => {
    loginEndpoint.mockResolvedValue({
      data: { access_token: 'a-token', refresh_token: 'r-token', token_type: 'bearer' },
      status: 200 as const,
      headers: new Headers(),
    })
    meEndpoint.mockRejectedValue(new ApiError(401, { error: { code: 'unauthorized' } }))

    await expect(
      login(queryClient, { email: 'owner@example.com', password: 'correct-password' })
    ).rejects.toBeInstanceOf(ApiError)

    expect(queryClient.getQueryData(currentUserQueryOptions.queryKey)).toBeUndefined()
  })
})

describe('fetchCurrentUser', () => {
  test('unwraps the shared success envelope', async () => {
    meEndpoint.mockResolvedValue(meResponse(owner))

    await expect(fetchCurrentUser()).resolves.toEqual(owner)
  })
})

describe('logout', () => {
  test('revokes the session and clears all private query state', async () => {
    logoutEndpoint.mockResolvedValue({
      data: undefined,
      status: 204 as const,
      headers: new Headers(),
    })
    queryClient.setQueryData(currentUserQueryOptions.queryKey, owner)
    queryClient.setQueryData(['finance', 'wallets'], [{ id: 1, balance: '1000.00' }])

    await logout(queryClient)

    expect(logoutEndpoint).toHaveBeenCalledTimes(1)
    expect(queryClient.getQueryCache().getAll()).toHaveLength(0)
  })

  test('treats an already-revoked server session as logged out', async () => {
    logoutEndpoint.mockRejectedValue(new ApiError(401, { error: { code: 'unauthorized' } }))
    queryClient.setQueryData(currentUserQueryOptions.queryKey, owner)

    await expect(logout(queryClient)).resolves.toBeUndefined()

    expect(queryClient.getQueryCache().getAll()).toHaveLength(0)
  })

  test('keeps private state and rethrows when revocation fails', async () => {
    logoutEndpoint.mockRejectedValue(new ApiError(500, undefined))
    queryClient.setQueryData(currentUserQueryOptions.queryKey, owner)
    queryClient.setQueryData(['finance', 'wallets'], [{ id: 1, balance: '1000.00' }])

    await expect(logout(queryClient)).rejects.toBeInstanceOf(ApiError)

    expect(queryClient.getQueryData(currentUserQueryOptions.queryKey)).toEqual(owner)
    expect(queryClient.getQueryData(['finance', 'wallets'])).toHaveLength(1)
  })
})

describe('private state and session-loss notification', () => {
  test('clearPrivateData removes every cached query', () => {
    queryClient.setQueryData(currentUserQueryOptions.queryKey, owner)
    queryClient.setQueryData(['finance', 'wallets'], [{ id: 1 }])

    clearPrivateData(queryClient)

    expect(queryClient.getQueryCache().getAll()).toHaveLength(0)
  })

  test('private data from one user cannot survive into the next session', async () => {
    const colleague: User = { id: 2, email: 'colleague@example.com' }
    queryClient.setQueryData(currentUserQueryOptions.queryKey, owner)
    queryClient.setQueryData(['finance', 'wallets'], [{ id: 'owner-wallet' }])
    logoutEndpoint.mockResolvedValue({
      data: undefined,
      status: 204 as const,
      headers: new Headers(),
    })
    loginEndpoint.mockResolvedValue({
      data: { access_token: 'new-access', refresh_token: 'new-refresh', token_type: 'bearer' },
      status: 200 as const,
      headers: new Headers(),
    })
    meEndpoint.mockResolvedValue(meResponse(colleague))

    await logout(queryClient)
    await login(queryClient, { email: colleague.email ?? '', password: 'new-password' })

    expect(queryClient.getQueryData(['finance', 'wallets'])).toBeUndefined()
    expect(queryClient.getQueryData(currentUserQueryOptions.queryKey)).toEqual(colleague)
  })

  test('notifies session-loss subscribers exactly once and supports unsubscribe', () => {
    const first = vi.fn()
    const second = vi.fn()
    const unsubscribeFirst = subscribeSessionLost(first)
    subscribeSessionLost(second)

    notifySessionLost()
    unsubscribeFirst()
    notifySessionLost()

    expect(first).toHaveBeenCalledTimes(1)
    expect(second).toHaveBeenCalledTimes(2)
  })
})
