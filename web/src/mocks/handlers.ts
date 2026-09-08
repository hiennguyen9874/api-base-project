import type { RequestHandler } from 'msw'

/**
 * Browser mock handlers (MSW).
 *
 * Note: the CashLens cookie session cannot be mocked here — Chromium ignores
 * `Set-Cookie` on service-worker-synthesized responses, so login cookies would
 * never reach the browser jar. Use the contract-backed HTTP mock server
 * (`e2e/mock-api-server.mjs`) for session flows instead.
 */
export const handlers: RequestHandler[] = []
