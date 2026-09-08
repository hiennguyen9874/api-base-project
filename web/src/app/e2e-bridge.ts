import { apiFetch } from '@/api/client'
import { queryClient } from '@/app/query-client'

interface CashLensE2eBridge {
  request: (path: string) => Promise<unknown>
  seedPrivateQuery: () => void
  hasPrivateQuery: () => boolean
}

declare global {
  interface Window {
    __cashlensE2e?: CashLensE2eBridge
  }
}

/** Install a narrow test-only bridge in builds explicitly created for Playwright. */
export function installE2eBridge(): void {
  if (import.meta.env.VITE_E2E !== 'true') {
    return
  }
  window.__cashlensE2e = {
    request: path => apiFetch(path),
    seedPrivateQuery: () => {
      queryClient.setQueryData(['e2e', 'private-finance'], { wallet: 'owner-only' })
    },
    hasPrivateQuery: () => queryClient.getQueryData(['e2e', 'private-finance']) !== undefined,
  }
}
