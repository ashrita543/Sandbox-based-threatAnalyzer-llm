import React, { useState } from 'react'
import FileUpload from './FileUpload'

function InfoTooltip({ isDark }) {
  return (
    <span className="relative group inline-flex">
      <span className={`inline-flex h-4 w-4 items-center justify-center rounded-full text-[10px] font-semibold ${isDark ? 'bg-slate-700 text-slate-200' : 'bg-slate-200 text-slate-700'}`}>
        i
      </span>
      <span
        className={`pointer-events-none absolute left-1/2 top-[120%] z-20 hidden w-64 -translate-x-1/2 rounded-md p-2 text-xs shadow-lg group-hover:block ${isDark ? 'bg-slate-800 text-slate-100 border border-slate-700' : 'bg-white text-slate-700 border border-slate-200'}`}
      >
        Simple is faster. Detailed includes MITRE ATT&CK mapping and full attack chain.
      </span>
    </span>
  )
}

export default function LeftPanel({
  mode,
  file,
  setFile,
  uploadError,
  setUploadError,
  reportMode,
  setReportMode,
  options,
  setOptions,
  runningStage,
  onRun,
  isDark,
}) {
  const [advancedOpen, setAdvancedOpen] = useState(false)
  const running = Boolean(runningStage)

  if (mode === 'crash') {
    return (
      <div className="h-full flex flex-col justify-center text-center px-4">
        <h2 className="text-lg font-semibold mb-2">Crash Log Analyzer</h2>
        <p className={isDark ? 'text-slate-300' : 'text-slate-600'}>
          Mode switch is active. Connect this panel to your crash-log parser backend in the same pattern as Script Analyzer.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4 h-full">
      <div className="h-[32%] min-h-[220px]">
        <FileUpload file={file} setFile={setFile} uploadError={uploadError} setUploadError={setUploadError} isDark={isDark} />
      </div>

      <div>
        <div className="flex items-center gap-2">
          <div className="font-semibold">Report mode</div>
          <InfoTooltip isDark={isDark} />
        </div>
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => setReportMode('simple')}
            className={`px-3 py-1.5 rounded-full text-sm transition ${
              reportMode === 'simple'
                ? 'bg-cyan-500 text-white'
                : isDark
                  ? 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            Simple
          </button>
          <button
            onClick={() => setReportMode('detailed')}
            className={`px-3 py-1.5 rounded-full text-sm transition ${
              reportMode === 'detailed'
                ? 'bg-cyan-500 text-white'
                : isDark
                  ? 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            Detailed
          </button>
        </div>
      </div>

      <div>
        <button
          className={`text-sm ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-cyan-700 hover:text-cyan-800'}`}
          onClick={() => setAdvancedOpen(!advancedOpen)}
        >
          Advanced options {advancedOpen ? '▴' : '▾'}
        </button>
        {advancedOpen && (
          <div className={`mt-2 space-y-3 rounded-lg border p-3 ${isDark ? 'border-slate-700 bg-slate-800/40' : 'border-slate-200 bg-slate-100/60'}`}>
            <div>
              <div className="flex justify-between text-sm">
                <div>Sandbox timeout</div>
                <div>{options.timeout}s</div>
              </div>
              <input
                type="range"
                min="10"
                max="60"
                value={options.timeout}
                onChange={(e) => setOptions({ ...options, timeout: Number(e.target.value) })}
                className="w-full accent-cyan-500"
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={options.includeRaw}
                onChange={(e) => setOptions({ ...options, includeRaw: e.target.checked })}
                className="accent-cyan-500"
              />
              Include raw behavioral log in output
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={options.flagLow}
                onChange={(e) => setOptions({ ...options, flagLow: e.target.checked })}
                className="accent-cyan-500"
              />
              Flag low-severity findings
            </label>
          </div>
        )}
      </div>

      <div className="mt-auto">
        <button
          disabled={!file || running}
          onClick={onRun}
          className={`w-full py-3 rounded-lg text-white font-medium transition flex items-center justify-center gap-2 ${
            !file || running ? 'bg-slate-400 cursor-not-allowed' : 'bg-rose-500 hover:bg-rose-600'
          }`}
        >
          {running ? (
            <>
              <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Running sandbox...
            </>
          ) : (
            'Analyze Script'
          )}
        </button>
      </div>
    </div>
  )
}
