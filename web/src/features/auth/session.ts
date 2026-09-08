import type { QueryClient } from '@tanstack/react-query'
import { queryOptions } from '@tanstack/react-query'

import { ApiError, resetTransportSession } from '@/api/client'
import type { SuccessfulResponseUser, User } from '@/api/generated/models'
import {
  loginAccessTokenApiV0AuthenLoginPost,
  logoutApiV0AuthenLogoutPost,
} from '@/api/generated/authentication/authentication'
import { readUserMeApiV0UsersMeGet } from '@/api/generated/users/users'

export interface LoginCredentials {
  email: string
  password: string
}

export const currentUserKey = ['session', 'current-user'] as const

/** Server-side session verification: the only source of "who is signed in". */
export async function fetchCurrentUser(): Promise<User> {
  const response = await readUserMeApiV0UsersMeGet()
  // The transport throws on non-2xx, so only the success envelope reaches here.
  const user = (response.data as SuccessfulResponseUser).data
  if (!user?.email) {
    throw new ApiError(response.status, response.data)
  }
  return user
}

export const currentUserQueryOptions = queryOptions({
  queryKey: currentUserKey,
  queryFn: fetchCurrentUser,
  // The transport already handles expired-access recovery; blind retries would
  // only multiply failed refreshes.
  retry: false,
})

/**
 * Establish a CashLens session. The login response tokens are discarded: the
 * browser only ever holds them as HttpOnly cookies, and a successful login is
 * defined by the server accepting the new session on `/users/me`.
 */
export async function login(
  queryClient: QueryClient,
  credentials: LoginCredentials
): Promise<User> {
  await loginAccessTokenApiV0AuthenLoginPost({
    username: credentials.email,
    password: credentials.password,
  })
  resetTransportSession()
  const user = await fetchCurrentUser()
  queryClient.setQueryData(currentUserKey, user)
  return user
}

/**
 * Revoke the session server-side, then drop every private query. A 401 means
 * the server-side session is already gone (nothing left to revoke), so the
 * client signs out locally; any other failure keeps the authenticated state
 * and surfaces the error so the owner can retry.
 */
export async function logout(queryClient: QueryClient): Promise<void> {
  try {
    await logoutApiV0AuthenLogoutPost()
  } catch (error) {
    if (!(error instanceof ApiError && error.status === 401)) {
      throw error
    }
  }
  clearPrivateData(queryClient)
}

/** Drop all cached private data so nothing survives into another session. */
export function clearPrivateData(queryClient: QueryClient): void {
  queryClient.clear()
}

type SessionLostListener = () => void

const sessionLostListeners = new Set<SessionLostListener>()

export function subscribeSessionLost(listener: SessionLostListener): () => void {
  sessionLostListeners.add(listener)
  return () => sessionLostListeners.delete(listener)
}

/** Announce that the CashLens session died mid-use; the UI must leave private screens. */
export function notifySessionLost(): void {
  for (const listener of [...sessionLostListeners]) {
    listener()
  }
}
