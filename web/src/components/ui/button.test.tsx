import { describe, expect, it } from 'vitest'

import { screen } from '@testing-library/react'

import { Button } from '@/components/ui/button'
import { renderWithProviders } from '@/test/render'

describe('Button', () => {
  it('renders its label', () => {
    renderWithProviders(<Button>Continue</Button>)

    expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument()
  })
})
