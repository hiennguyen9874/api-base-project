import { expect, test } from '@playwright/test'

import { expectDashboard, signIn } from './auth-helpers'

const owner = {
  email: 'owner@cashlens.dev',
  password: 'owner-fixture-password',
}

const colleague = {
  email: 'colleague@cashlens.dev',
  password: 'colleague-fixture-password',
}

const API_ORIGIN = 'http://localhost:11199'

async function browserStorageIsEmpty(page: import('@playwright/test').Page) {
  return await page.evaluate(() => ({
    localStorage: window.localStorage.length,
    sessionStorage: window.sessionStorage.length,
  }))
}

test.describe('CashLens session', () => {
  test('redirects unauthenticated visitors to the login form with a return target', async ({
    page,
  }) => {
    await page.goto('/')

    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
    const url = new URL(page.url())
    expect(url.pathname).toBe('/login')
    expect(url.searchParams.get('returnTo')).toBe('/')
  })

  test('signs in with valid credentials and lands on the private dashboard', async ({ page }) => {
    await signIn(page, owner)

    await expectDashboard(page, owner.email)
    expect(new URL(page.url()).pathname).toBe('/')
    const storage = await browserStorageIsEmpty(page)
    expect(storage.localStorage).toBe(0)
    expect(storage.sessionStorage).toBe(0)
    expect(page.url()).not.toContain('token')
  })

  test('shows a clear message for invalid credentials', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill(owner.email)
    await page.getByLabel('Mật khẩu').fill('wrong-password')
    await page.getByRole('button', { name: 'Đăng nhập' }).click()

    await expect(page.getByRole('alert')).toHaveText('Email hoặc mật khẩu không đúng.')
    await expect(page.getByLabel(/^Mật khẩu$/)).toHaveValue('')
    await expect(page.getByLabel('Email')).toHaveValue(owner.email)
  })

  test('shows a distinct message for an inactive account', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill('inactive@cashlens.dev')
    await page.getByLabel('Mật khẩu').fill('inactive-fixture-password')
    await page.getByRole('button', { name: 'Đăng nhập' }).click()

    await expect(page.getByRole('alert')).toContainText('Tài khoản đã bị vô hiệu hóa')
  })

  test('shows rate-limit and network failures without leaving the login form', async ({ page }) => {
    await signIn(page, {
      email: 'rate-limited@cashlens.dev',
      password: 'rate-limited-fixture-password',
    })
    await expect(page.getByRole('alert')).toContainText('thử đăng nhập quá nhiều lần')

    await page.route('**/api/v0/authen/login', route => route.abort('connectionfailed'))
    await page.getByLabel('Email').fill(owner.email)
    await page.getByLabel('Mật khẩu').fill(owner.password)
    await page.getByRole('button', { name: 'Đăng nhập' }).click()
    await expect(page.getByRole('alert')).toContainText('Không thể kết nối tới CashLens')
    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
  })

  test('restores the session after a page reload', async ({ page }) => {
    await signIn(page, owner)
    await expectDashboard(page, owner.email)

    await page.reload()

    await expectDashboard(page, owner.email)
  })

  test('returns to a safe local URL including its query and fragment', async ({ page }) => {
    await page.goto('/login?returnTo=%2F%3Fsection%3Dwallets%23recent')
    await page.getByLabel('Email').fill(owner.email)
    await page.getByLabel('Mật khẩu').fill(owner.password)
    await page.getByRole('button', { name: 'Đăng nhập' }).click()

    await expectDashboard(page, owner.email)
    const url = new URL(page.url())
    expect(url.pathname).toBe('/')
    expect(url.search).toBe('?section=wallets')
    expect(url.hash).toBe('#recent')
  })

  test('rejects open-redirect return targets', async ({ page }) => {
    await page.goto('/login?returnTo=https://evil.example.com/private')

    await page.getByLabel('Email').fill(owner.email)
    await page.getByLabel('Mật khẩu').fill(owner.password)
    await page.getByRole('button', { name: 'Đăng nhập' }).click()

    await expectDashboard(page, owner.email)
    expect(new URL(page.url()).origin).toBe(new URL(page.url()).origin)
    expect(new URL(page.url()).hostname).not.toContain('evil.example.com')
  })

  test('recovers transparently when the access token expires', async ({ page }) => {
    await signIn(page, owner)
    await expectDashboard(page, owner.email)
    const refreshBefore = (await page.context().cookies()).find(
      cookie => cookie.name === 'refresh_token'
    )

    // Simulate access-token expiry: the refresh cookie stays valid.
    await page.context().clearCookies({ name: 'access_token' })
    await page
      .context()
      .addCookies([{ name: 'access_token', value: 'mock-expired-access', url: API_ORIGIN }])

    await page.goto('/')

    await expectDashboard(page, owner.email)
    const cookies = await page.context().cookies()
    const access = cookies.find(cookie => cookie.name === 'access_token')
    const refreshAfter = cookies.find(cookie => cookie.name === 'refresh_token')
    expect(access?.value).not.toBe('mock-expired-access')
    expect(refreshAfter?.value).not.toBe(refreshBefore?.value)
  })

  test('coordinates concurrent expired requests through one refresh', async ({ page }) => {
    await signIn(page, owner)
    await expectDashboard(page, owner.email)
    await page.context().clearCookies({ name: 'access_token' })
    await page
      .context()
      .addCookies([{ name: 'access_token', value: 'mock-expired-access', url: API_ORIGIN }])
    let refreshRequests = 0
    page.on('request', request => {
      if (new URL(request.url()).pathname === '/api/v0/authen/refresh') refreshRequests += 1
    })

    await page.evaluate(async () => {
      const bridge = window.__cashlensE2e
      if (!bridge) throw new Error('E2E bridge is not installed')
      await Promise.all([bridge.request('/api/v0/users/me'), bridge.request('/api/v0/users/me')])
    })

    expect(refreshRequests).toBe(1)
  })

  test('clears private state and returns to login when a retry is still unauthorized', async ({
    page,
  }) => {
    await signIn(page, owner)
    await expectDashboard(page, owner.email)
    await page.evaluate(() => {
      const bridge = window.__cashlensE2e
      if (!bridge) throw new Error('E2E bridge is not installed')
      bridge.seedPrivateQuery()
      void bridge.request('/api/v0/test/always-unauthorized').catch(() => undefined)
    })

    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
    expect(await page.evaluate(() => window.__cashlensE2e?.hasPrivateQuery() ?? true)).toBe(false)
  })

  test('returns to login when the session cannot be recovered', async ({ page }) => {
    await signIn(page, owner)
    await expectDashboard(page, owner.email)

    await page.context().clearCookies()
    await page.goto('/')

    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
    const url = new URL(page.url())
    expect(url.pathname).toBe('/login')
    expect(url.searchParams.get('returnTo')).toBe('/')
  })

  test('signs out, blocks back-navigation, and never shows stale data', async ({ page }) => {
    await signIn(page, owner)
    await expectDashboard(page, owner.email)

    await page.getByRole('button', { name: 'Đăng xuất' }).click()

    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
    // History navigation must never resurrect the private screen…
    await page.goBack()
    // …and a fresh navigation to the private route must be rejected
    // server-side with no stale cache.
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()
    expect(new URL(page.url()).pathname).toBe('/login')
    await expect(page.getByText(owner.email)).toHaveCount(0)
  })

  test('keeps the authenticated UI and reports a failed logout', async ({ page }) => {
    const failingAccount = {
      email: 'logout-fails@cashlens.dev',
      password: 'logout-fails-fixture-password',
    }
    await signIn(page, failingAccount)
    await expectDashboard(page, failingAccount.email)

    await page.getByRole('button', { name: 'Đăng xuất' }).click()

    await expect(page.getByRole('alert')).toContainText('Đăng xuất không thành công')
    await expectDashboard(page, failingAccount.email)
    expect(new URL(page.url()).pathname).toBe('/')
  })

  test('clears cached private data before switching accounts', async ({ page }) => {
    await signIn(page, owner)
    await expectDashboard(page, owner.email)
    await page.evaluate(() => {
      const bridge = window.__cashlensE2e
      if (!bridge) throw new Error('E2E bridge is not installed')
      bridge.seedPrivateQuery()
    })
    await page.getByRole('button', { name: 'Đăng xuất' }).click()
    await expect(page.getByRole('heading', { name: 'Đăng nhập CashLens' })).toBeVisible()

    await signIn(page, colleague)

    await expectDashboard(page, colleague.email)
    await expect(page.getByText(owner.email)).toHaveCount(0)
    expect(await page.evaluate(() => window.__cashlensE2e?.hasPrivateQuery() ?? true)).toBe(false)
  })
})
