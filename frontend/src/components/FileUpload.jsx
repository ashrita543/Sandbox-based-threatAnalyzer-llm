import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

const ACCEPT = {
  'text/x-python': ['.py'],
  'application/x-sh': ['.sh'],
  'text/javascript': ['.js'],
  'application/octet-stream': ['.exe'],
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function getTypeIcon(filename) {
  const ext = filename.split('.').pop()?.toLowerCase()
  if (ext === 'py') return '🐍'
  if (ext === 'sh') return '⌘'
  if (ext === 'js') return 'JS'
  if (ext === 'exe') return '⚙️'
  return '📄'
}

export default function FileUpload({ file, setFile, uploadError, setUploadError, isDark }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    setUploadError('')
    setFile(acceptedFiles[0])
  }, [setFile, setUploadError])

  const onDropRejected = useCallback(() => {
    setFile(null)
    setUploadError('Unsupported file type. Please upload .py, .sh, .js, or .exe')
  }, [setFile, setUploadError])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    accept: ACCEPT,
    maxFiles: 1,
    multiple: false,
  })

  const baseBorder = file ? 'border-solid' : isDragActive ? 'border-cyan-500 border-solid' : 'border-dashed'
  const palette = isDark ? 'bg-slate-900/60 border-slate-700 text-slate-100' : 'bg-slate-50 border-slate-300 text-slate-900'

  return (
    <div>
      <div
        {...getRootProps()}
        className={`${baseBorder} ${palette} relative h-full min-h-[220px] border-2 rounded-xl p-6 text-center cursor-pointer flex items-center justify-center`}
      >
      <input {...getInputProps()} />
      {!file ? (
        <div>
          <div className="text-4xl mb-2">☁️⬆️</div>
          <div className="font-semibold text-base">Drop your script here</div>
          <div className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>or click to browse</div>
          <div className={`mt-3 text-xs inline-block px-2.5 py-1 rounded-full ${isDark ? 'text-slate-300 bg-slate-800' : 'text-slate-500 bg-slate-200'}`}>
            .py &nbsp; .sh &nbsp; .js &nbsp; .exe
          </div>
        </div>
      ) : (
        <div className="w-full text-left">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setFile(null)
              setUploadError('')
            }}
            className={`absolute right-3 top-3 h-7 w-7 rounded-full ${isDark ? 'hover:bg-slate-700 text-slate-300' : 'hover:bg-slate-200 text-slate-500'}`}
            aria-label="Remove uploaded file"
          >
            ✕
          </button>

          <div className="flex items-center gap-3">
            <span className={`inline-flex h-10 w-10 items-center justify-center rounded-lg text-sm font-semibold ${isDark ? 'bg-slate-800 text-slate-100' : 'bg-slate-200 text-slate-700'}`}>
              {getTypeIcon(file.name)}
            </span>
          </div>

          <div>
            <div className="font-bold mt-3 break-all">{file.name}</div>
            <div className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{formatFileSize(file.size)}</div>
          </div>
        </div>
      )}
      </div>
      {uploadError && <p className="mt-2 text-sm text-rose-500">{uploadError}</p>}
    </div>
  )
}
