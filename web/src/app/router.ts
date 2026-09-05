import type { QueryClient } from '@tanstack/react-query'
import { createRouter } from '@tanstack/react-router'

import { queryClient } from '@/app/query-client'
import { routeTree } from '@/routeTree.gen'

export interface RouterContext {
  queryClient: QueryClient
}

export const router = createRouter({
  routeTree,
  context: {
    queryClient,
  },
  defaultPreload: 'intent',
  defaultPreloadStaleTime: 0,
  scrollRestoration: true,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
