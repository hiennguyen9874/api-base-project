import { ApiError, NetworkError } from '@/api/client'

export type LoginErrorKind =
  'invalid-credentials' | 'inactive-account' | 'rate-limited' | 'network' | 'unexpected'

export interface ClassifiedLoginError {
  kind: LoginErrorKind
  message: string
}

/**
 * Map a failed login attempt to an accessible Vietnamese message. Unknown email
 * (404) and wrong password (401) are deliberately indistinguishable so the form
 * never reveals which part of the credentials was wrong.
 */
export function classifyLoginError(error: unknown): ClassifiedLoginError {
  if (error instanceof NetworkError) {
    return {
      kind: 'network',
      message: 'Không thể kết nối tới CashLens. Vui lòng kiểm tra kết nối và thử lại.',
    }
  }
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
      case 404:
        return { kind: 'invalid-credentials', message: 'Email hoặc mật khẩu không đúng.' }
      case 403:
        return {
          kind: 'inactive-account',
          message: 'Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ chủ sở hữu CashLens.',
        }
      case 429:
        return {
          kind: 'rate-limited',
          message: 'Bạn đã thử đăng nhập quá nhiều lần. Vui lòng thử lại sau ít phút.',
        }
      default:
        break
    }
  }
  return {
    kind: 'unexpected',
    message: 'Đăng nhập không thành công. Vui lòng thử lại.',
  }
}
