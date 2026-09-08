import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
import { Toaster } from 'sonner'

import type { RouterContext } from '@/app/router'

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
})

function RootLayout() {
  return (
    <>
      <Outlet />
      <Toaster richColors />
    </>
  )
}
