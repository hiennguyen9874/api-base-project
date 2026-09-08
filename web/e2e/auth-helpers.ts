import { expect, type Page } from '@playwright/test'

export interface TestCredentials {
  email: string
  password: string
}

export async function signIn(page: Page, credentials: TestCredentials): Promise<void> {
  await page.goto('/login')
  await page.getByLabel('Email').fill(credentials.email)
  await page.getByLabel('Mật khẩu').fill(credentials.password)
  await page.getByRole('button', { name: 'Đăng nhập' }).click()
}

export async function expectDashboard(page: Page, email: string): Promise<void> {
  await expect(page.getByRole('heading', { name: 'CashLens' })).toBeVisible()
  await expect(page.getByText(`Đang đăng nhập với tư cách ${email}.`)).toBeVisible()
}
