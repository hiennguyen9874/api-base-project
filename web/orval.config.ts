import { defineConfig } from 'orval'

export default defineConfig({
  cashlens: {
    input: {
      target: 'http://localhost:8000/openapi.json',
    },
    output: {
      clean: true,
      client: 'react-query',
      httpClient: 'fetch',
      mode: 'tags-split',
      schemas: './src/api/generated/models',
      target: './src/api/generated/cashlens.ts',
      override: {
        mutator: {
          name: 'apiFetch',
          path: './src/api/client.ts',
        },
      },
    },
  },
})
