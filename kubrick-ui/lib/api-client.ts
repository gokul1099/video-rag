
import Cookies from "js-cookie"

const DEFAULT_API_URL = "http://localhost:8080"

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

export async function apiRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
  const response = await fetch(buildApiUrl(endpoint), {
    ...options,
    headers: buildHeaders(options.headers, options.body),
  })

  if (response.status === 401) {
    Cookies.remove("authToken")
    globalThis.location.href = "/login"
    throw new Error("Unauthorized - redirecting to login")
  }

  if (!response.ok) {
    const errorJson = (await response.json().catch(() => null)) as { message?: string } | null
    throw new Error(errorJson?.message || `API Error: ${response.status}`)
  }

  return response
}

export async function apiFetch<T = unknown>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await apiRequest(endpoint, options)
  return response.json() as Promise<T>
}
