import { createServer } from 'node:http'

/**
 * Contract-backed mock of the CashLens authentication API for browser e2e
 * tests (and local development). It implements the same cookie lifecycle as
 * the real backend — HttpOnly cookies, single-use refresh rotation, logout
 * revocation — because service-worker-based mocking (MSW) cannot store
 * `Set-Cookie` responses in the browser's cookie jar.
 *
 * Sanitized fixtures only: no real accounts, tokens, or provider data.
 */

const PORT = Number(process.env.MOCK_API_PORT ?? 11199)

const CORS_ALLOWED_ORIGINS = new Set(['http://localhost:4173', 'http://localhost:5173'])

const fixtureAccounts = [
  {
    id: 101,
    email: 'owner@cashlens.dev',
    password: 'owner-fixture-password',
    full_name: 'Chủ sở hữu CashLens',
    is_active: true,
  },
  {
    id: 102,
    email: 'colleague@cashlens.dev',
    password: 'colleague-fixture-password',
    full_name: 'Đồng nghiệp CashLens',
    is_active: true,
  },
  {
    id: 103,
    email: 'inactive@cashlens.dev',
    password: 'inactive-fixture-password',
    full_name: 'Tài khoản vô hiệu hóa',
    is_active: false,
  },
  {
    id: 104,
    email: 'rate-limited@cashlens.dev',
    password: 'rate-limited-fixture-password',
    full_name: 'Tài khoản bị giới hạn',
    is_active: true,
    login_status: 429,
  },
  {
    id: 105,
    email: 'logout-fails@cashlens.dev',
    password: 'logout-fails-fixture-password',
    full_name: 'Tài khoản kiểm thử đăng xuất',
    is_active: true,
    logout_fails: true,
  },
]

// Live mock sessions. Access tokens stay valid until superseded (like
// stateless JWTs); refresh tokens are single-use and revoked on logout.
const accessTokens = new Map()
const refreshTokens = new Map()
let rotationCounter = 0

function accountByEmail(email) {
  return fixtureAccounts.find(account => account.email === email)
}

function accountForToken(map, token) {
  return token ? map.get(token) : undefined
}

function publicUser(account) {
  return {
    id: account.id,
    email: account.email,
    full_name: account.full_name,
    is_active: account.is_active,
    default_currency: 'VND',
    language_preference: 'vi-VN',
    account_status: 'ACTIVE',
  }
}

function sessionCookies(access, refresh) {
  return [
    `access_token=${access}; Path=/; HttpOnly; SameSite=None; Secure`,
    `refresh_token=${refresh}; Path=/; HttpOnly; SameSite=None; Secure`,
  ]
}

function clearedCookies() {
  return ['access_token=; Path=/; Max-Age=0', 'refresh_token=; Path=/; Max-Age=0']
}

function readCookie(request, name) {
  const header = request.headers.cookie
  if (!header) return undefined
  for (const part of header.split(';')) {
    const [key, ...rest] = part.trim().split('=')
    if (key === name) return rest.join('=')
  }
  return undefined
}

function sendJson(response, status, body, extraHeaders = []) {
  response.writeHead(status, {
    'Content-Type': 'application/json',
    ...(extraHeaders.length > 0 ? { 'Set-Cookie': extraHeaders } : {}),
  })
  response.end(JSON.stringify(body))
}

function sendError(response, status, code, message) {
  sendJson(response, status, { status: 'error', error: { code, message }, data: null })
}

function corsHeaders(request) {
  const origin = request.headers.origin
  if (!origin || !CORS_ALLOWED_ORIGINS.has(origin)) {
    return {}
  }
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    Vary: 'Origin',
  }
}

async function readBody(request) {
  const chunks = []
  for await (const chunk of request) {
    chunks.push(chunk)
  }
  return Buffer.concat(chunks).toString('utf8')
}

function issueSession(account) {
  rotationCounter += 1
  const access = `mock-access-${account.email}-${rotationCounter}`
  const refresh = `mock-refresh-${account.email}-${rotationCounter}`
  accessTokens.set(access, account)
  refreshTokens.set(refresh, account)
  return { access, refresh }
}

const server = createServer(async (request, response) => {
  const { method } = request
  const path = (request.url ?? '').split('?')[0]
  const cors = corsHeaders(request)

  // CORS headers must be present on every response, including errors.
  for (const [key, value] of Object.entries(cors)) {
    response.setHeader(key, value)
  }

  if (method === 'OPTIONS') {
    response.writeHead(204)
    response.end()
    return
  }

  try {
    if (method === 'GET' && path === '/health') {
      sendJson(response, 200, { status: 'success', data: null, error: null })
      return
    }

    if (method === 'POST' && path === '/api/v0/authen/login') {
      const form = new URLSearchParams(await readBody(request))
      const account = accountByEmail(form.get('username') ?? '')
      if (!account) {
        sendError(response, 404, 'not_found', 'User not found')
        return
      }
      if (account.password !== (form.get('password') ?? '')) {
        sendError(response, 401, 'unauthorized', 'Incorrect email or password')
        return
      }
      if (account.login_status === 429) {
        sendError(response, 429, 'rate_limited', 'Too Many Requests')
        return
      }
      if (!account.is_active) {
        sendError(response, 403, 'not_enough_privileges', 'inactive user')
        return
      }
      const { access, refresh } = issueSession(account)
      sendJson(
        response,
        200,
        { access_token: access, refresh_token: refresh, token_type: 'bearer' },
        sessionCookies(access, refresh)
      )
      return
    }

    if (method === 'GET' && path === '/api/v0/users/me') {
      const account = accountForToken(accessTokens, readCookie(request, 'access_token'))
      if (!account || !account.is_active) {
        sendError(response, 401, 'unauthorized', 'Not authenticated (oauth2)')
        return
      }
      sendJson(response, 200, { status: 'success', data: publicUser(account), error: null })
      return
    }

    if (method === 'POST' && path === '/api/v0/authen/refresh') {
      const refresh = readCookie(request, 'refresh_token')
      const account = accountForToken(refreshTokens, refresh)
      if (!account || !account.is_active) {
        sendError(response, 401, 'unauthorized', 'not found refresh token in redis')
        return
      }
      refreshTokens.delete(refresh)
      accessTokens.delete(readCookie(request, 'access_token'))
      const { access, refresh: rotatedRefresh } = issueSession(account)
      sendJson(
        response,
        200,
        {
          status: 'success',
          data: { access_token: access, refresh_token: rotatedRefresh, token_type: 'bearer' },
          error: null,
        },
        sessionCookies(access, rotatedRefresh)
      )
      return
    }

    if (method === 'GET' && path === '/api/v0/test/always-unauthorized') {
      sendError(response, 401, 'unauthorized', 'Session rejected after refresh')
      return
    }

    if (method === 'POST' && path === '/api/v0/authen/logout') {
      const refresh = readCookie(request, 'refresh_token')
      const account = accountForToken(refreshTokens, refresh)
      if (!account) {
        sendError(response, 401, 'unauthorized', 'refresh_token not set in cookie or header')
        return
      }
      if (account.logout_fails) {
        sendError(response, 503, 'service_unavailable', 'Logout unavailable')
        return
      }
      refreshTokens.delete(refresh)
      accessTokens.delete(readCookie(request, 'access_token'))
      response.writeHead(204, { 'Set-Cookie': clearedCookies() })
      response.end()
      return
    }

    sendError(response, 404, 'not_found', 'Not Found')
  } catch (error) {
    sendError(response, 500, 'internal_error', String(error))
  }
})

server.listen(PORT, '127.0.0.1', () => {
  console.log(`mock api listening on http://localhost:${PORT}`)
})
