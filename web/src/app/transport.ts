import { configureTransport } from '@/api/client'
import { refreshTokenApiV0AuthenRefreshPost } from '@/api/generated/authentication/authentication'

import { queryClient } from '@/app/query-client'
import { clearPrivateData, notifySessionLost } from '@/features/auth/session'

/**
 * Bind the shared transport to the CashLens session: cookie refresh goes through
 * the generated client (whose own 401 never recurses), and a lost session drops
 * every private query before the UI is redirected. Called once during bootstrap
 * so `@/api/client` stays free of generated imports and static cycles.
 */
export function initializeTransport(): void {
  configureTransport({
    refresh: async () => {
      // A 200 here means the server rotated the HttpOnly cookies; the token
      // body is deliberately discarded.
      await refreshTokenApiV0AuthenRefreshPost()
    },
    onSessionLost: () => {
      clearPrivateData(queryClient)
      notifySessionLost()
    },
  })
}
