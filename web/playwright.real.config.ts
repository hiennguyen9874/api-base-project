import { defineConfig, devices } from '@playwright/test'

const apiOrigin = process.env.CASHLENS_E2E_API_ORIGIN ?? 'http://localhost:11112'
const frontendOrigin = process.env.CASHLENS_E2E_FRONTEND_ORIGIN ?? 'http://localhost:5173'
const frontendUrl = new URL(frontendOrigin)

function shellQuote(value: string): string {
  return `'${value.replaceAll("'", "'\\''")}'`
}

/**
 * Real-backend cookie acceptance suite.
 *
 * The API must already be running from the supported Compose stack (`make up`),
 * and credentials must be supplied outside the repository:
 *
 *   CASHLENS_E2E_EMAIL=... CASHLENS_E2E_PASSWORD=... pnpm test:e2e:real
 */
export default defineConfig({
  testDir: './e2e',
  testMatch: '**/real-auth.spec.ts',
  fullyParallel: false,
  forbidOnly: true,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: frontendOrigin,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
  ],
  webServer: {
    command: `VITE_API_BASE_URL=${shellQuote(apiOrigin)} VITE_ENABLE_MSW=false pnpm build && pnpm preview --host ${shellQuote(frontendUrl.hostname)} --port ${shellQuote(frontendUrl.port || '80')} --strictPort`,
    url: frontendOrigin,
    reuseExistingServer: false,
    timeout: 180_000,
  },
})
