import { useState, useRef } from 'react'
import { apiFetch } from '../lib/api'

export default function DocumentUpload({ documents, onDocumentsChange }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  async function handleFileChange(e) {
    const file = e.target.files?.[0]
    if (!file) return

    setError('')
    setUploading(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      await apiFetch('/documents/upload', {
        method: 'POST',
        body: formData,
      })
      // Refresh the document list
      const { documents: fresh } = await apiFetch('/documents/list')
      onDocumentsChange(fresh)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleDelete(docId) {
    try {
      await apiFetch(`/documents/${docId}`, { method: 'DELETE' })
      onDocumentsChange(documents.filter((d) => d.id !== docId))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-2">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        disabled={uploading}
        className="hidden"
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="w-full text-xs bg-bg border border-border hover:border-border-strong
                   text-fg-muted hover:text-fg rounded-md py-2 px-3 transition-colors
                   disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : '+ Upload PDF'}
      </button>

      {error && (
        <div className="text-xs text-error bg-error/10 border border-error/20 rounded-md px-2 py-1.5">
          {error}
        </div>
      )}

      {documents.length > 0 && (
        <div className="space-y-1 pt-1">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="group flex items-center justify-between gap-2 text-xs
                         bg-bg border border-border rounded-md px-2 py-1.5"
            >
              <span className="text-fg-muted truncate flex-1" title={doc.filename}>
                {doc.filename}
              </span>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-fg-dim hover:text-error transition-colors opacity-0
                           group-hover:opacity-100"
                title="Delete document"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}