import { useState, useRef, useEffect } from 'react'

export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  // Auto-resize textarea up to a max height
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }, [value])

  function handleKeyDown(e) {
    // Enter sends, Shift+Enter adds newline
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <div className="border-t border-border bg-bg">
      <div className="max-w-3xl mx-auto px-4 md:px-6 py-4">
        <div className="relative bg-surface border border-border rounded-lg
                        focus-within:border-border-strong transition-colors">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
            placeholder="Ask anything..."
            className="w-full bg-transparent text-sm text-fg placeholder-fg-dim
                       px-4 py-3 pr-12 resize-none focus:outline-none
                       disabled:opacity-50"
          />
          <button
            onClick={submit}
            disabled={disabled || !value.trim()}
            className="absolute right-2 bottom-2 bg-accent hover:bg-accent-hover
                       text-bg rounded-md px-3 py-1.5 text-xs font-medium
                       transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
        <p className="text-[10px] text-fg-dim mt-2 text-center">
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}