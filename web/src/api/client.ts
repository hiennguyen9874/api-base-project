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

export async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${url}`, {
    ...options,
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    throw new ApiError(response.status, await readBody(response))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

async function readBody(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return undefined
  }
}
