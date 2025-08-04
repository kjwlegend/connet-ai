/**
 * Get URL search parameter value
 */
export function getUrlParam(name: string): string | null {
  if (typeof window === 'undefined') return null
  
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.get(name)
}

/**
 * Get all UTM parameters from URL
 */
export function getUtmParams() {
  if (typeof window === 'undefined') {
    return {
      utm_source: undefined,
      utm_medium: undefined,
      utm_campaign: undefined,
    }
  }
  
  const urlParams = new URLSearchParams(window.location.search)
  
  return {
    utm_source: urlParams.get('utm_source') || undefined,
    utm_medium: urlParams.get('utm_medium') || undefined,
    utm_campaign: urlParams.get('utm_campaign') || undefined,
  }
}

/**
 * Check if user came from an invite link
 */
export function getInviteCode(): string | undefined {
  const inviteParam = getUrlParam('invite')
  return inviteParam || undefined
}

/**
 * Get registration tracking info from URL
 */
export function getRegistrationTracking() {
  const inviteCode = getInviteCode()
  const utmParams = getUtmParams()
  
  return {
    invited_by_code: inviteCode,
    registration_source: 'web' as const,
    registration_channel: inviteCode ? 'invite' as const : 'organic' as const,
    ...utmParams,
  }
}