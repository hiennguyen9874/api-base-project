import { useEffect } from 'react'

import {
  createFileRoute,
  Outlet,
  redirect,
  useNavigate,
  useRouterState,
} from '@tanstack/react-router'

import { currentUserQueryOptions, subscribeSessionLost } from '@/features/auth/session'

/**
 * Pathless layout guarding every private screen. Session verification happens
 * server-side: `ensureQueryData` performs the `/users/me` request (refreshing
 * cookies once if the access token expired), and any failure routes to login
 * with a safe return target.
 */
export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ context, location }) => {
    try {
      await context.queryClient.ensureQueryData(currentUserQueryOptions)
    } catch {
      throw redirect({
        to: '/login',
        search: { returnTo: location.href },
        replace: true,
      })
    }
  },
  component: AuthenticatedLayout,
})

function AuthenticatedLayout() {
  const navigate = useNavigate()
  const location = useRouterState({ select: state => state.location })

  // A session that dies mid-use must leave private screens immediately.
  useEffect(
    () =>
      subscribeSessionLost(() => {
        void navigate({
          to: '/login',
          search: { returnTo: location.href },
          replace: true,
        })
      }),
    [navigate, location.href]
  )

  return <Outlet />
}
