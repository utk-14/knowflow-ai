import { useEffect, useRef } from 'react'
import SourceBadge from './SourceBadge'

export default function MessageList({ messages, loading }) {
  const bottomRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  if (messages.length === 0 && !loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-lg font-medium text-fg mb-2">
            Ask anything
          </h2>
          <p className="text-sm text-fg-muted">
            Upload a PDF to get answers from your documents, or ask general questions
            and KnowFlow will search the web.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 md:px-6 py-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-2">
            {msg.role === 'user' ? (
              <div className="flex justify-end">
                <div className="max-w-[80%] bg-accent/15 border border-accent/25
                                rounded-lg px-4 py-2.5 text-sm text-fg whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            ) : (
              <div className="space-y-1.5">
                <div className="text-xs text-fg-dim uppercase tracking-wider">
                  KnowFlow AI
                </div>
                <div className="text-sm text-fg whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>
                {msg.route && <SourceBadge route={msg.route} />}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="space-y-1.5">
            <div className="text-xs text-fg-dim uppercase tracking-wider">
              KnowFlow AI
            </div>
            <div className="flex items-center gap-2 text-sm text-fg-muted">
              <span className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-fg-dim rounded-full animate-pulse" />
                <span className="w-1.5 h-1.5 bg-fg-dim rounded-full animate-pulse"
                      style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-fg-dim rounded-full animate-pulse"
                      style={{ animationDelay: '300ms' }} />
              </span>
              Thinking...
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}