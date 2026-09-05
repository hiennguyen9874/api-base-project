import { createFileRoute } from '@tanstack/react-router'

import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  return (
    <main className="grid min-h-screen place-items-center p-6">
      <section className="max-w-lg space-y-4 text-center">
        <p className="text-sm font-medium text-muted-foreground">Private finance dashboard</p>
        <h1 className="text-4xl font-semibold tracking-tight">CashLens</h1>
        <p className="text-muted-foreground">
          The frontend foundation is ready for the authorized CashLens API.
        </p>
        <Button type="button">Get started</Button>
      </section>
    </main>
  )
}
