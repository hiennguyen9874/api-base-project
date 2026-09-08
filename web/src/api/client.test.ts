import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'

type ClientModule = typeof import('@/api/client')

const API_BASE = 'http://localhost:11112'

let fetchMock: ReturnType<typeof vi.fn>

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  })
}

function noContentResponse(): Response {
  return new Response(null, { status: 204 })
}

async function importFreshClient(): Promise<ClientModule> {
  vi.resetModules()
  return await import('@/api/client')
}

async function importConfiguredClient(
  refresh: () => Promise<void>,
  onSessionLost: () => void = vi.fn()
): Promise<ClientModule> {
  const client = await importFreshClient()
  client.configureTransport({ refresh, onSessionLost })
  return client
}

beforeEach(() => {
  fetchMock = vi.fn()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.clearAllMocks()
})

describe('apiFetch request shape', () => {
  test('sends a credentialed request and wraps the JSON response', async () => {
    const envelope = { status: 'success', data: { email: 'owner@example.com' }, error: null }
    fetchMock.mockResolvedValueOnce(jsonResponse(envelope))
    const { apiFetch } = await importFreshClient()

    const result = await apiFetch<{ data: unknown; status: number; headers: Headers }>(
      '/api/v0/users/me'
    )

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toBe(`${API_BASE}/api/v0/users/me`)
    expect(init.credentials).toBe('include')
    const headers = new Headers(init.headers)
    expect(headers.get('accept')).toBe('application/json')
    expect(result.status).toBe(200)
    expect(result.data).toEqual(envelope)
    expect(result.headers).toBeInstanceOf(Headers)
  })

  test('maps 204 responses to undefined data', async () => {
    fetchMock.mockResolvedValueOnce(noContentResponse())
    const { apiFetch } = await importFreshClient()

    const result = await apiFetch<{ data: unknown; status: number; headers: Headers }>(
      '/api/v0/authen/logout',
      { method: 'POST' }
    )

    expect(result.status).toBe(204)
    expect(result.data).toBeUndefined()
  })

  test('throws ApiError with the status and parsed body on failure', async () => {
    const body = { status: 'error', error: { code: 'unauthorized', message: 'nope' }, data: null }
    fetchMock.mockResolvedValueOnce(jsonResponse(body, 401))
    const { apiFetch, ApiError } = await importFreshClient()

    const error = await apiFetch('/api/v0/users/me').catch((thrown: unknown) => thrown)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as InstanceType<typeof ApiError>).status).toBe(401)
    expect((error as InstanceType<typeof ApiError>).body).toEqual(body)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  test('wraps fetch failures in NetworkError', async () => {
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'))
    const { apiFetch, NetworkError } = await importFreshClient()

    const error = await apiFetch('/api/v0/users/me').catch((thrown: unknown) => thrown)

    expect(error).toBeInstanceOf(NetworkError)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})

describe('apiFetch session recovery', () => {
  test('refreshes once and retries the failed request', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ status: 'error' }, 401))
      .mockResolvedValueOnce(jsonResponse({ status: 'success', data: { email: 'owner' } }))
    const refresh = vi.fn().mockResolvedValue(undefined)
    const { apiFetch } = await importConfiguredClient(refresh)

    const result = await apiFetch<{ data: unknown; status: number; headers: Headers }>(
      '/api/v0/users/me'
    )

    expect(result.status).toBe(200)
    expect(refresh).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(fetchMock.mock.calls[1]).toEqual(fetchMock.mock.calls[0])
  })

  test('concurrent expired requests share a single refresh', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ status: 'error' }, 401))
      .mockResolvedValueOnce(jsonResponse({ status: 'error' }, 401))
      .mockResolvedValueOnce(jsonResponse({ status: 'success' }))
      .mockResolvedValueOnce(jsonResponse({ status: 'success' }))
    const refresh = vi.fn().mockResolvedValue(undefined)
    const { apiFetch } = await importConfiguredClient(refresh)

    await Promise.all([apiFetch('/api/v0/finance/wallets'), apiFetch('/api/v0/finance/categories')])

    expect(refresh).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenCalledTimes(4)
  })

  test('a still-unauthorized retry expires the session without a second refresh', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ status: 'error' }, 401))
      .mockResolvedValueOnce(jsonResponse({ status: 'error' }, 401))
    const refresh = vi.fn().mockResolvedValue(undefined)
    const onSessionLost = vi.fn()
    const { apiFetch, SessionExpiredError } = await importConfiguredClient(refresh, onSessionLost)

    const error = await apiFetch('/api/v0/finance/wallets').catch((thrown: unknown) => thrown)

    expect(error).toBeInstanceOf(SessionExpiredError)
    expect((error as InstanceType<typeof SessionExpiredError>).cause).toMatchObject({ status: 401 })
    expect(refresh).toHaveBeenCalledTimes(1)
    expect(onSessionLost).toHaveBeenCalledTimes(1)
  })

  test('a late concurrent 401 retries against refreshed cookies without rotating twice', async () => {
    let releaseSecondResponse: () => void = () => undefined
    const secondResponse = new Promise<Response>(resolve => {
      releaseSecondResponse = () => resolve(jsonResponse({ status: 'error' }, 401))
    })
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ status: 'error' }, 401))
      .mockReturnValueOnce(secondResponse)
      .mockResolvedValue(jsonResponse({ status: 'success' }))
    const refresh = vi.fn().mockImplementation(async () => {
      releaseSecondResponse()
    })
    const { apiFetch } = await importConfiguredClient(refresh)

    await Promise.all([apiFetch('/api/v0/finance/wallets'), apiFetch('/api/v0/finance/categories')])

    expect(refresh).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenCalledTimes(4)
  })

  test('a failed refresh fails every waiting request and reports session loss once', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ status: 'error' }, 401))
    const refresh = vi.fn().mockRejectedValue(new Error('refresh rejected'))
    const onSessionLost = vi.fn()
    const { apiFetch, SessionExpiredError } = await importConfiguredClient(refresh, onSessionLost)

    const [first, second] = await Promise.allSettled([
      apiFetch('/api/v0/finance/wallets'),
      apiFetch('/api/v0/finance/categories'),
    ])

    expect(first.status).toBe('rejected')
    expect(second.status).toBe('rejected')
    expect((first as PromiseRejectedResult).reason).toBeInstanceOf(SessionExpiredError)
    expect(refresh).toHaveBeenCalledTimes(1)
    expect(onSessionLost).toHaveBeenCalledTimes(1)
  })

  test('after a session loss, later 401 responses fail fast without another refresh', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ status: 'error' }, 401))
    const refresh = vi.fn().mockRejectedValue(new Error('refresh rejected'))
    const onSessionLost = vi.fn()
    const { apiFetch, SessionExpiredError } = await importConfiguredClient(refresh, onSessionLost)

    await apiFetch('/api/v0/finance/wallets').catch(() => undefined)
    const callsAfterFirstLoss = fetchMock.mock.calls.length
    const refreshesAfterFirstLoss = refresh.mock.calls.length

    const error = await apiFetch('/api/v0/finance/wallets').catch((thrown: unknown) => thrown)

    expect(error).toBeInstanceOf(SessionExpiredError)
    expect(fetchMock.mock.calls.length).toBe(callsAfterFirstLoss + 1)
    expect(refresh.mock.calls.length).toBe(refreshesAfterFirstLoss)
    expect(onSessionLost).toHaveBeenCalledTimes(1)
  })

  test('resetTransportSession re-arms recovery after a fresh login', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ status: 'error' }, 401))
    const refresh = vi.fn().mockRejectedValue(new Error('refresh rejected'))
    const { apiFetch, resetTransportSession, SessionExpiredError } =
      await importConfiguredClient(refresh)

    await apiFetch('/api/v0/finance/wallets').catch((thrown: unknown) => thrown as void)
    resetTransportSession()

    const error = await apiFetch('/api/v0/finance/wallets').catch((thrown: unknown) => thrown)

    expect(error).toBeInstanceOf(SessionExpiredError)
    expect(refresh).toHaveBeenCalledTimes(2)
  })

  test('does not refresh for the authentication endpoints themselves', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ status: 'error' }, 401))
    const refresh = vi.fn().mockResolvedValue(undefined)
    const { apiFetch, ApiError } = await importConfiguredClient(refresh)

    for (const url of [
      '/api/v0/authen/login',
      '/api/v0/authen/refresh',
      '/api/v0/authen/logout',
      '/api/v0/authen/logout-all',
    ]) {
      const error = await apiFetch(url).catch((thrown: unknown) => thrown)
      expect(error).toBeInstanceOf(ApiError)
    }

    expect(refresh).not.toHaveBeenCalled()
    expect(fetchMock).toHaveBeenCalledTimes(4)
  })

  test('leaves 401 responses untouched when no transport is configured', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ status: 'error' }, 401))
    const { apiFetch, ApiError } = await importFreshClient()

    const error = await apiFetch('/api/v0/users/me').catch((thrown: unknown) => thrown)

    expect(error).toBeInstanceOf(ApiError)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
