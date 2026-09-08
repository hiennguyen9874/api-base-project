import { env } from '@/lib/env'

export class ApiError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(status: number, body: unknown) {
    super(`API request failed with status ${status}`)
    this.status = status
    this.body = body
  }
}

/** The request never reached the API (offline, DNS failure, CORS rejection). */
export class NetworkError extends Error {
  constructor(message = 'Không thể kết nối tới CashLens', options?: ErrorOptions) {
    super(message, options)
  }
}

/** The CashLens session is gone: refresh failed, so private state must be dropped. */
export class SessionExpiredError extends Error {
  constructor(message = 'Phiên đăng nhập đã hết hạn', options?: ErrorOptions) {
    super(message, options)
  }
}

export interface TransportConfig {
  /** Rotates the HttpOnly session cookies; rejects when the session is dead. */
  refresh: () => Promise<void>
  /** Invoked once when the session is definitively lost. */
  onSessionLost: () => void
}

interface RecoveredResponse {
  data: unknown
  status: number
  headers: Headers
}

// Endpoints that must never trigger cookie recovery: login cannot fix a 401,
// refresh must not recurse into itself, and logout revokes the refresh token
// that recovery would use.
const NON_RECOVERABLE_PATHS = [
  '/api/v0/authen/login',
  '/api/v0/authen/refresh',
  '/api/v0/authen/logout',
]

let transportConfig: TransportConfig | null = null
let refreshPromise: Promise<void> | null = null
let refreshGeneration = 0
let sessionLost = false

/**
 * Wire session recovery to the app's refresh endpoint and private-state cleanup.
 * Called once during bootstrap to avoid a static cycle between this module and
 * the generated authentication client.
 */
export function configureTransport(config: TransportConfig): void {
  transportConfig = config
}

/** Re-arm recovery after a successful login establishes a fresh session. */
export function resetTransportSession(): void {
  refreshPromise = null
  refreshGeneration += 1
  sessionLost = false
}

function isRecoverable(url: string): boolean {
  if (transportConfig === null) {
    return false
  }
  return !NON_RECOVERABLE_PATHS.some(path => url.startsWith(path))
}

function expireSession(cause?: unknown): SessionExpiredError {
  if (!sessionLost) {
    sessionLost = true
    transportConfig?.onSessionLost()
  }
  return new SessionExpiredError('Phiên đăng nhập đã hết hạn', { cause })
}

async function ensureRefreshed(): Promise<void> {
  if (sessionLost) {
    throw new SessionExpiredError()
  }
  const config = transportConfig
  if (config === null) {
    throw new SessionExpiredError()
  }
  // Every concurrent expired request awaits the same single refresh attempt.
  refreshPromise ??= config
    .refresh()
    .then(() => {
      refreshGeneration += 1
      refreshPromise = null
    })
    .catch((cause: unknown) => {
      refreshPromise = null
      throw expireSession(cause)
    })
  return refreshPromise
}

async function sendRequest(url: string, options: RequestInit): Promise<Response> {
  try {
    return await fetch(`${env.apiBaseUrl}${url}`, {
      ...options,
      credentials: 'include',
      headers: {
        Accept: 'application/json',
        ...options.headers,
      },
    })
  } catch (cause) {
    throw new NetworkError('Không thể kết nối tới CashLens', { cause })
  }
}

async function finalizeResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new ApiError(response.status, await readBody(response))
  }
  if (response.status === 204) {
    return { data: undefined, status: response.status, headers: response.headers } as T
  }
  const recovered: RecoveredResponse = {
    data: await readBody(response),
    status: response.status,
    headers: response.headers,
  }
  return recovered as T
}

/**
 * Shared transport for the generated client. Sends credentialed requests,
 * retries an ordinary request exactly once after a shared cookie refresh, and
 * never refreshes on behalf of the authentication endpoints themselves.
 */
export async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
  const requestGeneration = refreshGeneration
  const response = await sendRequest(url, options)

  if (response.status === 401 && isRecoverable(url)) {
    // Once the session is known to be dead, fail fast instead of refreshing again.
    if (sessionLost) {
      throw new SessionExpiredError()
    }
    // Another concurrent request may already have refreshed while this request
    // was in flight. In that case, retry with the new cookies without rotating
    // the single-use refresh token a second time.
    if (requestGeneration === refreshGeneration) {
      await ensureRefreshed()
    }
    const retried = await sendRequest(url, options)
    if (retried.status === 401) {
      const cause = new ApiError(retried.status, await readBody(retried))
      throw expireSession(cause)
    }
    return finalizeResponse<T>(retried)
  }

  return finalizeResponse<T>(response)
}

async function readBody(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return undefined
  }
}
