import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import type { User } from '@/api/generated/models'
import { ApiError, NetworkError } from '@/api/client'

import { LoginForm } from '@/features/auth/login-form'
import { login } from '@/features/auth/session'

vi.mock('@/features/auth/session', async importOriginal => {
  const actual = await importOriginal<typeof import('@/features/auth/session')>()
  return { ...actual, login: vi.fn() }
})

const loginSpy = vi.mocked(login)

const owner: User = { id: 1, email: 'owner@example.com', full_name: 'Session Owner' }

beforeEach(() => {
  vi.clearAllMocks()
})

function renderForm(onSuccess = vi.fn()) {
  const queryClient = new QueryClient()
  render(
    <QueryClientProvider client={queryClient}>
      <LoginForm onSuccess={onSuccess} />
    </QueryClientProvider>
  )
  return { onSuccess, queryClient }
}

async function submitCredentials(email: string, password: string) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('Email'), email)
  await user.type(screen.getByLabelText(/^Mật khẩu$/), password)
  await user.click(screen.getByRole('button', { name: 'Đăng nhập' }))
}

describe('LoginForm', () => {
  test('renders an accessible Vietnamese login form', () => {
    renderForm()

    expect(screen.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
    const email = screen.getByLabelText('Email')
    expect(email).toHaveAccessibleDescription('Địa chỉ email dùng để đăng nhập.')
    expect(email).toHaveAttribute('autocomplete', 'email')
    expect(email).toHaveAttribute('type', 'email')
    const password = screen.getByLabelText('Mật khẩu')
    expect(password).toHaveAttribute('autocomplete', 'current-password')
    expect(password).toHaveAttribute('type', 'password')
    expect(screen.getByRole('button', { name: 'Đăng nhập' })).toBeEnabled()
  })

  test('submits valid credentials and reports the signed-in user', async () => {
    loginSpy.mockResolvedValueOnce(owner)
    const { onSuccess } = renderForm()

    await submitCredentials('owner@example.com', 'correct-password')

    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(owner))
    expect(loginSpy).toHaveBeenCalledWith(expect.anything(), {
      email: 'owner@example.com',
      password: 'correct-password',
    })
    expect(screen.getByLabelText(/^Mật khẩu$/)).toHaveValue('')
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  test('shows the invalid-credentials message and clears the password', async () => {
    loginSpy.mockRejectedValueOnce(new ApiError(401, { error: { code: 'unauthorized' } }))
    const { onSuccess } = renderForm()

    await submitCredentials('owner@example.com', 'wrong-password')

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('Email hoặc mật khẩu không đúng.')
    expect(onSuccess).not.toHaveBeenCalled()
    expect(screen.getByLabelText(/^Mật khẩu$/)).toHaveValue('')
    expect(screen.getByLabelText('Email')).toHaveValue('owner@example.com')
  })

  test.each([
    {
      name: 'inactive account',
      error: new ApiError(403, { error: { code: 'not_enough_privileges' } }),
      message: 'Tài khoản đã bị vô hiệu hóa.',
    },
    {
      name: 'rate limit',
      error: new ApiError(429, { error: { code: 'rate_limited' } }),
      message: 'Bạn đã thử đăng nhập quá nhiều lần.',
    },
    {
      name: 'network failure',
      error: new NetworkError(),
      message: 'Không thể kết nối tới CashLens.',
    },
  ])('shows the $name message and keeps the form retryable', async ({ error, message }) => {
    loginSpy.mockRejectedValueOnce(error)
    renderForm()

    await submitCredentials('owner@example.com', 'secret-password')

    expect(await screen.findByRole('alert')).toHaveTextContent(message)
    expect(screen.getByLabelText(/^Mật khẩu$/)).toHaveValue('')
    expect(screen.getByRole('button', { name: 'Đăng nhập' })).toBeEnabled()
  })

  test('rejects an empty or malformed submission without calling the API', async () => {
    const { onSuccess } = renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByRole('button', { name: 'Đăng nhập' }))

    expect(await screen.findByText('Vui lòng nhập email.')).toBeVisible()
    expect(await screen.findByText('Vui lòng nhập mật khẩu.')).toBeVisible()
    await user.type(screen.getByLabelText('Email'), 'not-an-email')
    await user.click(screen.getByRole('button', { name: 'Đăng nhập' }))
    expect(await screen.findByText('Email không hợp lệ.')).toBeVisible()
    expect(onSuccess).not.toHaveBeenCalled()
    expect(loginSpy).not.toHaveBeenCalled()
  })

  test('disables submission while the request is pending', async () => {
    let resolveLogin: (user: User) => void = () => undefined
    loginSpy.mockReturnValueOnce(
      new Promise(resolve => {
        resolveLogin = resolve
      })
    )
    renderForm()
    const user = userEvent.setup()

    await submitCredentials('owner@example.com', 'correct-password')

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveTextContent('Đang đăng nhập…')
    await user.click(button).catch(() => undefined)
    expect(loginSpy).toHaveBeenCalledTimes(1)

    resolveLogin(owner)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Đăng nhập' })).toBeEnabled())
  })
})
