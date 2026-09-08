import { defineConfig, devices } from '@playwright/test'

// Mocked-browser suite: the preview build talks to the contract-backed mock
// API server (e2e/mock-api-server.mjs), which reproduces the real cookie
// lifecycle (HttpOnly cookies, single-use refresh rotation, logout
// revocation). Run the real-backend cookie lifecycle suite separately with
// `pnpm test:e2e:real` (requires `make up`).
export default defineConfig({
  testDir: './e2e',
  testMatch: '**/auth.spec.ts',
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'github' : 'html',
  use: {
    baseURL: 'http://localhost:4173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
    {
      name: 'chromium-mobile',
      use: { ...devices['Desktop Chrome'], viewport: { width: 390, height: 844 } },
    },
  ],
  webServer: [
    {
      command: 'node e2e/mock-api-server.mjs',
      url: 'http://localhost:11199/health',
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command:
        'VITE_API_BASE_URL=http://localhost:11199 VITE_ENABLE_MSW=false VITE_E2E=true pnpm build && pnpm preview --host localhost --port 4173 --strictPort',
      url: 'http://localhost:4173',
      reuseExistingServer: false,
      timeout: 180_000,
    },
  ],
})
