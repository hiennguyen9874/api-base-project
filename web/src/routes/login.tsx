import { createFileRoute, redirect, useNavigate } from '@tanstack/react-router'
import { z } from 'zod'

import { LoginForm } from '@/features/auth/login-form'
import { sanitizeReturnTo } from '@/features/auth/return-to'
import { currentUserQueryOptions } from '@/features/auth/session'

const loginSearchSchema = z.object({
  returnTo: z.string().optional(),
})

export const Route = createFileRoute('/login')({
  validateSearch: (search: Record<string, unknown>) => loginSearchSchema.parse(search),
  // An already-restored session never needs to see the login form again.
  beforeLoad: ({ context, search }) => {
    const user = context.queryClient.getQueryData(currentUserQueryOptions.queryKey)
    if (user) {
      throw redirect({ to: sanitizeReturnTo(search.returnTo), replace: true })
    }
  },
  component: LoginPage,
})

function LoginPage() {
  const navigate = useNavigate()
  const { returnTo } = Route.useSearch()

  return (
    <LoginForm
      onSuccess={() => {
        void navigate({ to: sanitizeReturnTo(returnTo), replace: true })
      }}
    />
  )
}
