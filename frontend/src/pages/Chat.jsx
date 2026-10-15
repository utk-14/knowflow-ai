import { useEffect, useState, useCallback } from 'react'
import { apiFetch } from '../lib/api'
import Sidebar from '../components/Sidebar'
import MessageList from '../components/MessageList'
import MessageInput from '../components/MessageInput'

export default function Chat() {
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [messages, setMessages] = useState([])
  const [documents, setDocuments] = useState([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    (async () => {
      try {
        const [{ chats }, { documents }] = await Promise.all([
          apiFetch('/chats'),
          apiFetch('/documents/list'),
        ])
        setChats(chats)
        setDocuments(documents)
      } catch (err) {
        setError(err.message)
      }
    })()
  }, [])

  useEffect(() => {
    if (!activeChatId) {
      setMessages([])
      return
    }
    (async () => {
      try {
        const { messages } = await apiFetch(`/chats/${activeChatId}/messages`)
        setMessages(messages)
      } catch (err) {
        setError(err.message)
      }
    })()
  }, [activeChatId])

  const handleNewChat = useCallback(async () => {
    try {
      const { chat } = await apiFetch('/chats', {
        method: 'POST',
        body: JSON.stringify({}),
      })
      setChats((prev) => [chat, ...prev])
      setActiveChatId(chat.id)
      setMessages([])
      setSidebarOpen(false)   // close drawer on mobile
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const handleSelectChat = useCallback((id) => {
    setActiveChatId(id)
    setSidebarOpen(false)     // close drawer on mobile
  }, [])

  const handleSend = useCallback(async (text) => {
    if (!activeChatId || sending) return
    setError('')
    setSending(true)

    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
    }
    setMessages((prev) => [...prev, tempUserMsg])

    try {
      const res = await apiFetch(`/chats/${activeChatId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ message: text }),
      })

      const assistantMsg = {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: res.reply,
        route: res.route,
        sources: res.sources,
      }
      setMessages((prev) => [...prev, assistantMsg])

      const { chats: freshChats } = await apiFetch('/chats')
      setChats(freshChats)
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }, [activeChatId, sending])

  return (
    <div className="h-screen bg-bg flex overflow-hidden">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        documents={documents}
        onDocumentsChange={setDocuments}
      />

      <main className="flex-1 flex flex-col min-w-0">
        {/* Mobile header with menu toggle */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-border bg-surface">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-fg-muted hover:text-fg transition-colors"
            aria-label="Open menu"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M3 6h18M3 12h18M3 18h18" />
            </svg>
          </button>
          <span className="text-sm font-medium text-fg">KnowFlow AI</span>
        </div>

        {error && (
          <div className="bg-error/10 border-b border-error/20 px-4 md:px-6 py-2
                          text-xs text-error">
            {error}
          </div>
        )}

        {!activeChatId ? (
          <div className="flex-1 flex items-center justify-center px-4">
            <div className="text-center">
              <h2 className="text-lg font-medium text-fg mb-2">
                Welcome to KnowFlow AI
              </h2>
              <p className="text-sm text-fg-muted mb-6">
                Start a new chat or pick a conversation from the sidebar.
              </p>
              <button
                onClick={handleNewChat}
                className="bg-accent hover:bg-accent-hover text-bg
                           text-sm font-medium rounded-md px-4 py-2 transition-colors"
              >
                Start a new chat
              </button>
            </div>
          </div>
        ) : (
          <>
            <MessageList messages={messages} loading={sending} />
            <MessageInput onSend={handleSend} disabled={sending} />
          </>
        )}
      </main>
    </div>
  )
}