/**
 * Reduce an untrusted `returnTo` search value to a local application path.
 *
 * Only same-origin application paths survive: one leading slash, no
 * protocol-relative or backslash tricks, no control characters, and never the
 * login route itself. Anything else falls back to the app root so a login can
 * never be turned into an open redirect.
 */
export function sanitizeReturnTo(raw: string | undefined): string {
  if (!raw) {
    return '/'
  }
  const startsLikeLocalPath = /^\/(?!\/)/.test(raw) && !raw.startsWith('/\\')
  if (!startsLikeLocalPath) {
    return '/'
  }
  // eslint-disable-next-line no-control-regex
  if (/[\u0000-\u001f\u007f]/.test(raw)) {
    return '/'
  }
  if (raw === '/login' || raw.startsWith('/login?') || raw.startsWith('/login/')) {
    return '/'
  }
  return raw
}
