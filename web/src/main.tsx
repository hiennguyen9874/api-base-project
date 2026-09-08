import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { RouterProvider } from '@tanstack/react-router'

import { installE2eBridge } from '@/app/e2e-bridge'
import { AppProviders } from '@/app/providers'
import { router } from '@/app/router'
import { initializeTransport } from '@/app/transport'
import { enableMocking } from '@/mocks/enable'

import './index.css'

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Root element not found')
}

const root = createRoot(rootElement)

async function bootstrap() {
  await enableMocking()
  initializeTransport()
  installE2eBridge()

  root.render(
    <StrictMode>
      <AppProviders>
        <RouterProvider router={router} />
      </AppProviders>
    </StrictMode>
  )
}

void bootstrap()
