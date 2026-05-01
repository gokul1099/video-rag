import Cookies from "js-cookie"

const DEFAULT_API_URL = "http://localhost:8080"

// ========== Race Condition Handling ==========
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach(cb => cb(newToken))
  refreshSubscribers = []
}
// =============================================

export function buildApiUrl(endpoint: string) {
  const base = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL
  return `${base}${endpoint}`
}

function buildHeaders(options?: RequestInit["headers"], body?: BodyInit | null) {
  const headers = new Headers(options)

  const token = Cookies.get("authToken")
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  if (body instanceof FormData) {
    return headers
  }

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }

  return headers
}

async function refreshToken(): Promise<string | null> {
  const refreshTokenValue = Cookies.get("refreshToken")
  if (!refreshTokenValue) {
    return null
  }

  try {
    const response = await fetch(buildApiUrl("/auth/refresh"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshTokenValue }),
    })

    if (!response.ok) {
      return null
    }

    const data = await response.json()
    const expiresInDays = data.expires_in ? data.expires_in / 86400 : 7
    Cookies.set("authToken", data.access_token, { expires: expiresInDays, sameSite: "lax" })
    Cookies.set("refreshToken", data.refresh_token, { expires: 30, sameSite: "lax" })

    return data.access_token
  } catch {
    return null
  }
}

function clearTokensAndRedirect() {
  Cookies.remove("authToken")
  Cookies.remove("refreshToken")
  globalThis.location.href = "/login"
}

export async function apiRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const response = await fetch(buildApiUrl(endpoint), {
    ...options,
    headers: buildHeaders(options.headers, options.body),
  })

  if (response.status === 401) {
    const refreshTokenValue = Cookies.get("refreshToken")

    if (!refreshTokenValue) {
      clearTokensAndRedirect()
      throw new Error("Unauthorized - redirecting to login")
    }

    // ========== Race Condition Logic ==========
    if (!isRefreshing) {
      isRefreshing = true

      const newToken = await refreshToken()

      if (newToken) {
        onTokenRefreshed(newToken)
        isRefreshing = false

        // Retry with new token
        return fetch(buildApiUrl(endpoint), {
          ...options,
          headers: buildHeaders(options.headers, options.body),
        })
      } else {
        isRefreshing = false
        clearTokensAndRedirect()
        throw new Error("Token refresh failed - redirecting to login")
      }
    } else {
      // Another refresh is in progress - queue this request
      return new Promise((resolve) => {
        subscribeTokenRefresh(() => {
          resolve(apiRequest(endpoint, options))
        })
      })
    }
    // ==========================================
  }

  if (!response.ok) {
    const errorJson = (await response.json().catch(() => null)) as { message?: string, detail?: string | any } | null
    let errorMsg = errorJson?.message
    if (!errorMsg && errorJson?.detail) {
      errorMsg = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail)
    }
    throw new Error(errorMsg || `API Error: ${response.status}`)
  }

  return response
}

export async function apiFetch<T = unknown>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await apiRequest(endpoint, options)
  return response.json() as Promise<T>
}