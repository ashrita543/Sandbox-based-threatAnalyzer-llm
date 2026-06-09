import React from 'react'

function ShieldIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden="true">
      <path
        d="M12 2.5 4.5 5.2v6.7c0 4.8 3.1 8.8 7.5 9.9 4.4-1.1 7.5-5.1 7.5-9.9V5.2L12 2.5Z"
        className="fill-cyan-500/15 stroke-cyan-500"
        strokeWidth="1.4"
      />
      <path d="M12 7.4v9.2" className="stroke-cyan-500" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M8.5 11.3h7" className="stroke-cyan-500" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  )
}

export default function Navbar({ mode, setMode, theme, setTheme }) {
  const isDark = theme === 'dark'

  function navClass(key) {
    const active = mode === key
    return `pb-1 text-sm tracking-wide transition ${active ? 'border-b-2 border-cyan-500 text-cyan-500' : isDark ? 'text-slate-300 hover:text-slate-100 border-b-2 border-transparent' : 'text-slate-600 hover:text-slate-900 border-b-2 border-transparent'}`
  }

  return (
    <header className={`h-[60px] border-b px-4 sm:px-6 flex items-center justify-between ${isDark ? 'bg-slate-950 border-slate-800' : 'bg-white border-slate-200'}`}>
      <div className="flex items-center gap-2.5">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-500/40 bg-cyan-500/10">
          <ShieldIcon />
        </span>
        <div className="font-semibold tracking-wide">SandboxAI</div>
      </div>

      <div className="flex items-center gap-4 sm:gap-6">
        <button
          onClick={() => setMode('script')}
          className={navClass('script')}
        >
          Script Analyzer
        </button>
        {/* <button onClick={() => setMode('crash')} className={navClass('crash')}>
          Crash Log Analyzer
        </button> */}

        <button
          onClick={() => setTheme(isDark ? 'light' : 'dark')}
          className={`ml-1 inline-flex h-8 items-center rounded-full px-3 text-xs font-medium transition ${isDark ? 'bg-slate-800 text-slate-100 hover:bg-slate-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'}`}
          aria-label="Toggle dark and light mode"
        >
          {isDark ? 'Light' : 'Dark'}
        </button>
      </div>
    </header>
  )
}
