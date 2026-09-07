import { defineConfig } from 'orval'

const openApiTarget = process.env.CASHLENS_OPENAPI_URL ?? 'http://localhost:8000/openapi.json'

export default defineConfig({
  cashlens: {
    input: {
      target: openApiTarget,
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
