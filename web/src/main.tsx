import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { RouterProvider } from '@tanstack/react-router'

import { AppProviders } from '@/app/providers'
import { router } from '@/app/router'
import { enableMocking } from '@/mocks/enable'

import './index.css'

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Root element not found')
}

const root = createRoot(rootElement)

async function bootstrap() {
  await enableMocking()

  root.render(
    <StrictMode>
      <AppProviders>
        <RouterProvider router={router} />
      </AppProviders>
    </StrictMode>
  )
}

void bootstrap()
