import { useState } from 'react'

import { useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute, useNavigate } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'
import { currentUserQueryOptions, logout } from '@/features/auth/session'

export const Route = createFileRoute('/_authenticated/')({
  component: HomePage,
})

function HomePage() {
  const { data: user } = useQuery(currentUserQueryOptions)
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [logoutFailed, setLogoutFailed] = useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    setLogoutFailed(false)
    try {
      await logout(queryClient)
      await navigate({ to: '/login', replace: true })
    } catch {
      // The server session may still be alive: stay authenticated and let the
      // owner retry rather than pretending the logout succeeded.
      setLogoutFailed(true)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <main className="grid min-h-screen place-items-center p-6">
      <section className="max-w-lg space-y-4 text-center">
        <p className="text-sm font-medium text-muted-foreground">
          Bảng điều khiển tài chính riêng tư
        </p>
        <h1 className="text-4xl font-semibold tracking-tight">CashLens</h1>
        <p className="text-muted-foreground">
          {user?.email ? `Đang đăng nhập với tư cách ${user.email}.` : 'Đang tải phiên đăng nhập…'}
        </p>
        {logoutFailed ? (
          <p className="text-sm text-destructive" role="alert">
            Đăng xuất không thành công. Phiên đăng nhập vẫn còn trên máy chủ — vui lòng thử lại.
          </p>
        ) : null}
        <div className="flex justify-center gap-2">
          <Button
            disabled={isLoggingOut}
            onClick={() => void handleLogout()}
            type="button"
            variant="outline"
          >
            {isLoggingOut ? 'Đang đăng xuất…' : 'Đăng xuất'}
          </Button>
        </div>
      </section>
    </main>
  )
}
