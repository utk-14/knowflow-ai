import { useState } from 'react'
import { supabase } from '../lib/supabase'

export default function Login() {
  const [mode, setMode] = useState('login') // 'login' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (mode === 'signup') {
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) throw error
        setError('Check your email to confirm your account.')
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        // App.jsx will detect the session change and redirect
      }
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Logo / title */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-fg tracking-tight">
            KnowFlow AI
          </h1>
          <p className="text-fg-muted text-sm mt-1">
            {mode === 'login' ? 'Sign in to your workspace' : 'Create your account'}
          </p>
        </div>

        {/* Form card */}
        <form
          onSubmit={handleSubmit}
          className="bg-surface border border-border rounded-lg p-6 space-y-4"
        >
          <div>
            <label className="block text-xs font-medium text-fg-muted mb-2 uppercase tracking-wide">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-bg border border-border rounded-md px-3 py-2 text-fg text-sm
                         placeholder-fg-dim
                         focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent
                         transition-colors"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-fg-muted mb-2 uppercase tracking-wide">
              Password
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-bg border border-border rounded-md px-3 py-2 text-fg text-sm
                         placeholder-fg-dim
                         focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent
                         transition-colors"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="text-sm text-error bg-error/10 border border-error/20 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent hover:bg-accent-hover text-bg font-medium text-sm
                       rounded-md py-2 transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        {/* Mode toggle */}
        <p className="text-center text-sm text-fg-muted mt-6">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError('') }}
            className="text-accent hover:text-accent-hover transition-colors"
          >
            {mode === 'login' ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  )
}