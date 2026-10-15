import { supabase } from './supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function apiFetch(path, options = {}) {
  // Get the current session — Supabase auto-refreshes tokens for us
  const { data: { session } } = await supabase.auth.getSession()

  const headers = {
    ...options.headers,
  }

  // Attach JWT if we have a session
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`
  }

  // Only set JSON content-type if body isn't FormData
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}