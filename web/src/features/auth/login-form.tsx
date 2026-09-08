import { useEffect, useRef, useState } from 'react'

import { Button } from '@/components/ui/button'
import { useQueryClient } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { classifyLoginError } from '@/features/auth/login-errors'
import { login } from '@/features/auth/session'
import type { User } from '@/api/generated/models'

const loginSchema = z.object({
  email: z
    .string()
    .min(1, { error: 'Vui lòng nhập email.' })
    .pipe(z.email({ error: 'Email không hợp lệ.' })),
  password: z.string().min(1, { error: 'Vui lòng nhập mật khẩu.' }),
})

type LoginValues = z.infer<typeof loginSchema>

interface LoginFormProps {
  onSuccess?: (user: User) => void
}

const inputClassName =
  'h-9 w-full rounded-lg border border-input bg-background px-3 text-sm text-foreground shadow-xs transition-colors outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20'

export function LoginForm({ onSuccess }: LoginFormProps) {
  const queryClient = useQueryClient()
  const [serverError, setServerError] = useState<string | null>(null)
  const alertRef = useRef<HTMLParagraphElement>(null)
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  useEffect(() => {
    if (serverError) {
      alertRef.current?.focus()
    }
  }, [serverError])

  const onSubmit = handleSubmit(async values => {
    setServerError(null)
    try {
      const user = await login(queryClient, values)
      setValue('password', '')
      onSuccess?.(user)
    } catch (error) {
      setServerError(classifyLoginError(error).message)
      // The password never survives a failed attempt.
      setValue('password', '')
    }
  })

  return (
    <main className="grid min-h-screen place-items-center bg-background p-6">
      <section className="w-full max-w-sm space-y-6" aria-labelledby="login-heading">
        <div className="space-y-1.5 text-center">
          <p className="text-sm font-medium text-muted-foreground">Quản lý tài chính riêng tư</p>
          <h1 id="login-heading" className="text-2xl font-semibold tracking-tight">
            Đăng nhập CashLens
          </h1>
        </div>

        <form className="space-y-4" noValidate onSubmit={event => void onSubmit(event)}>
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none" htmlFor="login-email">
              Email
            </label>
            <input
              {...register('email')}
              aria-describedby={errors.email ? 'login-email-error' : 'login-email-hint'}
              aria-invalid={errors.email ? true : undefined}
              autoComplete="email"
              className={inputClassName}
              id="login-email"
              name="email"
              placeholder="ban@vd.com"
              type="email"
            />
            {errors.email ? (
              <p className="text-sm text-destructive" id="login-email-error">
                {errors.email.message}
              </p>
            ) : (
              <p className="text-sm text-muted-foreground" id="login-email-hint">
                Địa chỉ email dùng để đăng nhập.
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium leading-none" htmlFor="login-password">
              Mật khẩu
            </label>
            <input
              {...register('password')}
              aria-describedby={errors.password ? 'login-password-error' : undefined}
              aria-invalid={errors.password ? true : undefined}
              autoComplete="current-password"
              className={inputClassName}
              id="login-password"
              name="password"
              type="password"
            />
            {errors.password ? (
              <p className="text-sm text-destructive" id="login-password-error">
                {errors.password.message}
              </p>
            ) : null}
          </div>

          {serverError ? (
            <p
              aria-live="assertive"
              className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
              ref={alertRef}
              role="alert"
              tabIndex={-1}
            >
              {serverError}
            </p>
          ) : null}

          <Button className="w-full" disabled={isSubmitting} size="lg" type="submit">
            {isSubmitting ? 'Đang đăng nhập…' : 'Đăng nhập'}
          </Button>
        </form>

        <p className="text-center text-xs text-muted-foreground">
          Đăng nhập CashLens riêng cho việc xem dữ liệu; kết nối Money Lover được cấu hình sau khi
          đăng nhập.
        </p>
      </section>
    </main>
  )
}
