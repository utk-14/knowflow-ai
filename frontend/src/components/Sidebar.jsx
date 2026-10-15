import { useState } from 'react'
import { supabase } from '../lib/supabase'
import DocumentUpload from './DocumentUpload'

export default function Sidebar({
  isOpen,
  onClose,
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  documents,
  onDocumentsChange,
}) {
  const [showDocs, setShowDocs] = useState(false)

  async function handleLogout() {
    await supabase.auth.signOut()
  }

  return (
    <>
      {/* Mobile overlay — darkens the screen behind the drawer */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 z-40 md:hidden"
        />
      )}

      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          w-[260px] bg-surface border-r border-border flex flex-col h-screen
          transform transition-transform duration-200
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-sm font-semibold text-fg tracking-tight">
              KnowFlow AI
            </h1>
            {/* Close button — only visible on mobile */}
            <button
              onClick={onClose}
              className="md:hidden text-fg-muted hover:text-fg transition-colors text-xl leading-none"
              aria-label="Close menu"
            >
              ×
            </button>
          </div>
          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 bg-accent hover:bg-accent-hover
                       text-bg font-medium text-sm rounded-md py-2 transition-colors"
          >
            <span className="text-base leading-none">+</span>
            New chat
          </button>
        </div>

        {/* Chats list */}
        <div className="flex-1 overflow-y-auto p-2">
          <div className="text-[10px] uppercase tracking-wider text-fg-dim px-2 py-2">
            Conversations
          </div>
          {chats.length === 0 ? (
            <p className="text-xs text-fg-dim px-2 py-3">
              No chats yet. Click "New chat" to start.
            </p>
          ) : (
            <div className="space-y-0.5">
              {chats.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => onSelectChat(chat.id)}
                  className={`w-full text-left text-sm px-2.5 py-2 rounded-md transition-colors truncate
                    ${chat.id === activeChatId
                      ? 'bg-surface-hover text-fg'
                      : 'text-fg-muted hover:bg-surface-hover hover:text-fg'
                    }`}
                >
                  {chat.title || 'Untitled chat'}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Documents section */}
        <div className="border-t border-border">
          <button
            onClick={() => setShowDocs(!showDocs)}
            className="w-full flex items-center justify-between px-4 py-3
                       text-xs uppercase tracking-wider text-fg-muted hover:text-fg transition-colors"
          >
            <span>Documents {documents.length > 0 && `(${documents.length})`}</span>
            <span className={`text-[10px] transition-transform ${showDocs ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
          {showDocs && (
            <div className="px-3 pb-3">
              <DocumentUpload
                documents={documents}
                onDocumentsChange={onDocumentsChange}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-border p-3">
          <button
            onClick={handleLogout}
            className="w-full text-left text-sm text-fg-muted hover:text-fg
                       px-2 py-1.5 rounded-md hover:bg-surface-hover transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>
    </>
  )
}