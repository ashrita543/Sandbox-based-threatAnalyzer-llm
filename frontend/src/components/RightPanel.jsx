import React, { useMemo, useState } from 'react'

const STAGE_MESSAGES = {
  sandbox: 'Spinning up sandbox...',
  execute: 'Executing script...',
  report: 'Generating report...',
}

const SEVERITY_STYLES = {
  LOW: 'bg-emerald-100 text-emerald-800',
  MEDIUM: 'bg-amber-100 text-amber-800',
  HIGH: 'bg-orange-100 text-orange-800',
  CRITICAL: 'bg-rose-100 text-rose-800 animate-pulse',
}

function ContainerIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden="true">
      <rect x="4" y="6" width="16" height="12" rx="2" className="stroke-cyan-500" strokeWidth="1.4" />
      <path d="M8 10h8M8 14h8" className="stroke-cyan-500" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  )
}

function SparkIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden="true">
      <path d="m12 3 1.7 4.2L18 9l-4.3 1.7L12 15l-1.7-4.3L6 9l4.3-1.8L12 3Z" className="fill-amber-400/25 stroke-amber-500" strokeWidth="1.2" />
      <circle cx="18.5" cy="4.5" r="1" className="fill-amber-400" />
      <circle cx="5" cy="18" r="1.3" className="fill-cyan-400" />
    </svg>
  )
}

function ShieldPlaceholder({ isDark }) {
  return (
    <div className="h-full flex items-center justify-center text-center px-4">
      <div>
        <div className={`mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-full ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`}>
          <svg viewBox="0 0 24 24" className="h-12 w-12" fill="none" aria-hidden="true">
            <path
              d="M12 2.5 4.5 5.2v6.7c0 4.8 3.1 8.8 7.5 9.9 4.4-1.1 7.5-5.1 7.5-9.9V5.2L12 2.5Z"
              className={isDark ? 'stroke-slate-500 fill-slate-700/30' : 'stroke-slate-400 fill-slate-300/40'}
              strokeWidth="1.3"
            />
          </svg>
        </div>
        <p className={isDark ? 'text-slate-300' : 'text-slate-500'}>Upload a script to see the threat report.</p>
      </div>
    </div>
  )
}

function LoadingState({ runningStage, executeProgress, timedOut, isDark }) {
  const stageText = STAGE_MESSAGES[runningStage] || 'Preparing analysis...'

  return (
    <div className="h-full flex items-center justify-center">
      <div className="w-full max-w-xl">
        <div className="mb-3 flex items-center gap-3 text-lg font-semibold">
          {runningStage === 'sandbox' && (
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500/15 animate-pulse">
              <ContainerIcon />
            </span>
          )}
          {runningStage === 'execute' && (
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500/15">
              <ContainerIcon />
            </span>
          )}
          {runningStage === 'report' && (
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/15">
              <SparkIcon />
            </span>
          )}
          <span>{stageText}</span>
        </div>

        <div className={`rounded-full h-3 overflow-hidden ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`}>
          <div
            className={`h-full transition-all duration-200 ${timedOut ? 'bg-rose-500' : 'bg-cyan-500'}`}
            style={{
              width:
                runningStage === 'sandbox'
                  ? '20%'
                  : runningStage === 'execute'
                    ? `${Math.max(5, executeProgress)}%`
                    : '100%',
            }}
          />
        </div>

        {timedOut && (
          <p className="mt-2 text-sm text-rose-500">Sandbox timeout - partial results below.</p>
        )}
      </div>
    </div>
  )
}

function ErrorState({ error, isDark }) {
  return (
    <div className="h-full flex items-center justify-center px-2">
      <div className={`w-full max-w-2xl rounded-xl border p-4 ${isDark ? 'border-rose-700 bg-rose-950/30' : 'border-rose-300 bg-rose-50'}`}>
        <p className="text-rose-500 font-semibold">Analysis failed. The sandbox encountered an error.</p>
        <details className="mt-3">
          <summary className={isDark ? 'text-slate-200 cursor-pointer' : 'text-slate-700 cursor-pointer'}>Raw error</summary>
          <pre className={`mt-2 rounded-lg p-3 text-xs overflow-x-auto ${isDark ? 'bg-slate-900 text-slate-200' : 'bg-white text-slate-700'}`}>{error}</pre>
        </details>
      </div>
    </div>
  )
}

function SeverityBadge({ severity }) {
  const text = (severity || 'LOW').toUpperCase()
  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${SEVERITY_STYLES[text] || SEVERITY_STYLES.LOW}`}>{text}</span>
}

function asArray(value) {
  if (!value) return []
  return Array.isArray(value) ? value : [value]
}

function IocTabs({ iocs, isDark }) {
  const [activeTab, setActiveTab] = useState('files')
  const tabs = ['files', 'processes', 'network']
  const activeList = asArray(iocs?.[activeTab])

  return (
    <div className={`rounded-xl border overflow-hidden ${isDark ? 'border-slate-700' : 'border-slate-200'}`}>
      <div className={`px-4 py-2 text-sm font-semibold ${isDark ? 'bg-slate-800 text-slate-100' : 'bg-slate-900 text-white'}`}>
        Indicators of Compromise
      </div>
      <div className="px-4 pt-3">
        <div className="flex gap-3 text-sm">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`capitalize pb-1 border-b-2 ${activeTab === tab ? 'border-cyan-500 text-cyan-500' : isDark ? 'border-transparent text-slate-300' : 'border-transparent text-slate-600'}`}
            >
              {tab}
            </button>
          ))}
        </div>
        <ul className="py-3 space-y-2">
          {activeList.length === 0 && (
            <li className={isDark ? 'text-slate-400 text-sm' : 'text-slate-500 text-sm'}>No indicators detected.</li>
          )}
          {activeList.map((item, index) => {
            const value = typeof item === 'string' ? item : item?.value || item?.name || JSON.stringify(item)
            const suspicion = typeof item === 'object' && item ? item.suspicion : null

            return (
              <li key={`${activeTab}-${value}-${index}`} className="flex items-start gap-2 text-sm">
                <span className={`mt-1 h-2.5 w-2.5 rounded-full ${suspicion === 'high' ? 'bg-rose-500' : suspicion === 'medium' ? 'bg-amber-500' : 'bg-slate-400'}`} />
                <span className="font-mono break-all">{value}</span>
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}

function AttackChain({ steps, isDark }) {
  if (!steps?.length) return null

  return (
    <div className={`rounded-xl border p-4 ${isDark ? 'border-slate-700' : 'border-slate-200'}`}>
      <h3 className="font-semibold mb-3">Attack chain</h3>
      <ol className="space-y-3">
        {steps.map((step, idx) => (
          <li key={step} className="flex gap-3">
            <div className="flex flex-col items-center">
              <span className="h-7 w-7 rounded-full bg-cyan-500 text-white text-xs font-semibold inline-flex items-center justify-center">
                {idx + 1}
              </span>
              {idx !== steps.length - 1 && <span className={`mt-1 w-[1px] flex-1 ${isDark ? 'bg-slate-600' : 'bg-slate-300'}`} />}
            </div>
            <p className={`pt-1 text-sm ${isDark ? 'text-slate-200' : 'text-slate-700'}`}>{step}</p>
          </li>
        ))}
      </ol>
    </div>
  )
}

function MitreTable({ techniques, isDark }) {
  const rows = asArray(techniques)
  if (!rows.length) return null

  return (
    <div className={`rounded-xl border overflow-hidden ${isDark ? 'border-slate-700' : 'border-slate-200'}`}>
      <h3 className={`px-4 py-3 font-semibold ${isDark ? 'bg-slate-800' : 'bg-slate-100'}`}>MITRE ATT&CK techniques</h3>
      <table className="w-full text-sm">
        <thead className={isDark ? 'bg-slate-900 text-slate-300' : 'bg-slate-50 text-slate-600'}>
          <tr>
            <th className="text-left px-4 py-2">Technique ID</th>
            <th className="text-left px-4 py-2">Description</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((tech, index) => {
            if (typeof tech === 'string') {
              return (
                <tr key={`${tech}-${index}`} className={isDark ? 'border-t border-slate-800' : 'border-t border-slate-200'}>
                  <td className="px-4 py-2" colSpan={2}>
                    {tech}
                  </td>
                </tr>
              )
            }

            return (
              <tr key={tech.id || index} className={isDark ? 'border-t border-slate-800' : 'border-t border-slate-200'}>
                <td className="px-4 py-2">
                  {tech.id ? (
                    <a
                      className="text-cyan-500 hover:text-cyan-400"
                      href={`https://attack.mitre.org/techniques/${tech.id}/`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {tech.id}
                    </a>
                  ) : (
                    'Unknown'
                  )}
                </td>
                <td className="px-4 py-2">{tech.description || tech.value || ''}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function TechnicalAnalysis({ analysis, isDark }) {
  if (!analysis) return null

  const sections = [
    ['Filesystem behavior', analysis.filesystem_behavior],
    ['Process behavior', analysis.process_behavior],
    ['Network behavior', analysis.network_behavior],
    ['Syscall patterns', analysis.syscall_patterns],
  ].filter(([, body]) => Boolean(body))

  if (sections.length === 0) return null

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {sections.map(([title, body]) => (
        <section key={title} className={`rounded-xl border p-4 ${isDark ? 'border-slate-700 bg-slate-800/30' : 'border-slate-200 bg-slate-50'}`}>
          <h3 className="mb-2 font-semibold text-sm">{title}</h3>
          <p className={`text-sm leading-6 ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{body}</p>
        </section>
      ))}
    </div>
  )
}

function RecommendedActions({ actions, isDark, severity }) {
  if (!actions) return null

  const isString = typeof actions === 'string'

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text)
    } catch (e) {
      // ignore
    }
  }

  // Simple mode: single string
  if (isString) {
    return (
      <div className={`rounded-xl p-4 ${isDark ? 'bg-slate-900/40' : 'bg-slate-50'} border-l-4 border-cyan-500/50`}>
        <h3 className={`font-semibold mb-2 ${isDark ? 'text-slate-100' : 'text-slate-700'}`}>Recommended action</h3>
        <p className={`text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{actions}</p>
      </div>
    )
  }

  // Detailed mode: object with immediate/short_term/long_term
  const items = [
    { key: 'immediate', label: 'Immediate', icon: '⚡', body: actions.immediate },
    { key: 'short_term', label: 'Next 48 hours', icon: '⏰', body: actions.short_term },
    { key: 'long_term', label: 'Long term', icon: '🛡️', body: actions.long_term },
  ]

  const accent = severity === 'CRITICAL' ? 'ring-rose-400/30' : severity === 'HIGH' ? 'ring-orange-400/25' : 'ring-cyan-400/18'

  return (
    <div className={`rounded-xl p-0 ${isDark ? 'bg-slate-900/40' : 'bg-white'} ${accent}`}>
      <h3 className={`px-4 py-3 font-semibold ${isDark ? 'text-slate-100' : 'text-slate-700'}`}>Recommended action</h3>
      <ol className="divide-y" role="list">
        {items.map((it) => (
          <li key={it.key} className={`flex items-start gap-3 px-4 py-3 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
            <div className="flex-shrink-0">
              <div className={`h-9 w-9 flex items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 text-sm font-semibold ${isDark ? 'text-slate-100' : 'text-cyan-700'}`}>
                {it.icon}
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-semibold">{it.label}</div>
                <div className="text-xs text-slate-400">{it.key === 'immediate' ? 'Priority: High' : it.key === 'short_term' ? 'Priority: Medium' : 'Priority: Low'}</div>
              </div>
              <p className={`mt-1 text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{it.body}</p>
            </div>
            <div className="flex items-start">
              <button onClick={() => copyText(it.body)} className={`ml-2 h-8 w-8 rounded-md text-sm ${isDark ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`} aria-label={`Copy ${it.label}`}>
                ⧉
              </button>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}

export default function RightPanel({ mode, file, report, error, runningStage, executeProgress, timedOut, includeRaw, isDark }) {
  const severityBorder = useMemo(() => {
    const s = report?.severity?.toUpperCase()
    if (s === 'LOW') return 'border-emerald-500'
    if (s === 'MEDIUM') return 'border-amber-500'
    if (s === 'HIGH') return 'border-orange-500'
    return 'border-rose-500'
  }, [report])

  function copyReport() {
    if (!report) return
    navigator.clipboard.writeText(JSON.stringify(report, null, 2))
  }

  function downloadReport() {
    if (!report) return
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${report.filename || 'report'}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (mode === 'crash') {
    return (
      <div className="h-full flex items-center justify-center text-center">
        <div>
          <p className="text-xl font-semibold mb-2">Crash Log Analyzer</p>
          <p className={isDark ? 'text-slate-300' : 'text-slate-600'}>Switch is wired. You can render the crash-analysis output panel here.</p>
        </div>
      </div>
    )
  }

  if (error) {
    return <ErrorState error={error} isDark={isDark} />
  }

  if (!file && !report) {
    return <ShieldPlaceholder isDark={isDark} />
  }

  if (runningStage) {
    return <LoadingState runningStage={runningStage} executeProgress={executeProgress} timedOut={timedOut} isDark={isDark} />
  }

  if (!report) return null

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div className="font-mono text-sm break-all">{report.filename}</div>
        <div className="flex items-center gap-2">
          <SeverityBadge severity={report.severity} />
          <button
            onClick={copyReport}
            className={`h-8 px-2 rounded-md text-sm ${isDark ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'}`}
            aria-label="Copy report"
          >
            ⧉
          </button>
          <button
            onClick={downloadReport}
            className={`h-8 px-2 rounded-md text-sm ${isDark ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'}`}
            aria-label="Download report JSON"
          >
            ⇩
          </button>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-semibold">{report.threat_name}</h2>
        <div className="mt-2 flex flex-wrap gap-2">
          {asArray(report.malware_category).map((tag, index) => (
            <span key={`${tag}-${index}`} className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-slate-800 text-slate-300' : 'bg-slate-200 text-slate-700'}`}>
              {tag}
            </span>
          ))}
        </div>
      </div>

      <article className={`rounded-xl border-l-4 p-4 ${severityBorder} ${isDark ? 'bg-slate-800/40' : 'bg-slate-50'}`}>
        <p className={isDark ? 'text-slate-200' : 'text-slate-700'}>{report.summary || report.executive_summary}</p>
      </article>

      {report.mode === 'detailed' && report.executive_summary && (
        <div className={`rounded-xl border-l-4 border-cyan-500/50 p-4 ${isDark ? 'bg-slate-800/30' : 'bg-cyan-50'}`}>
          <h3 className={`font-semibold text-sm mb-2 ${isDark ? 'text-slate-100' : 'text-slate-700'}`}>Executive summary</h3>
          <p className={`text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{report.executive_summary}</p>
        </div>
      )}

      {report.mode === 'detailed' && report.technical_analysis && (
        <TechnicalAnalysis analysis={report.technical_analysis} isDark={isDark} />
      )}

      <IocTabs iocs={report.indicators_of_compromise} isDark={isDark} />

      {report.severity_justification && (
        <div className={`rounded-xl border-l-4 border-orange-500/50 p-4 ${isDark ? 'bg-slate-800/30' : 'bg-orange-50'}`}>
          <h3 className={`font-semibold text-sm mb-2 ${isDark ? 'text-slate-100' : 'text-slate-700'}`}>Severity justification</h3>
          <p className={`text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{report.severity_justification}</p>
        </div>
      )}

      {report.mode === 'detailed' && (
        <>
          <AttackChain steps={report.attack_chain} isDark={isDark} />
          <MitreTable techniques={report.mitre_attack_techniques} isDark={isDark} />
        </>
      )}

      {report.likely_intent && (
        <div className={`rounded-xl border-l-4 border-cyan-500/50 p-4 ${isDark ? 'bg-slate-800/30' : 'bg-cyan-50'}`}>
          <h3 className={`font-semibold text-sm mb-2 ${isDark ? 'text-slate-100' : 'text-slate-700'}`}>Likely intent</h3>
          <p className={`text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{report.likely_intent}</p>
        </div>
      )}

      {report.false_positive_assessment && (
        <div className={`rounded-xl border-l-4 border-amber-500/50 p-4 ${isDark ? 'bg-slate-800/30' : 'bg-amber-50'}`}>
          <h3 className={`font-semibold text-sm mb-2 ${isDark ? 'text-slate-100' : 'text-slate-700'}`}>False positive assessment</h3>
          <p className={`text-sm ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{report.false_positive_assessment}</p>
        </div>
      )}

      <RecommendedActions actions={report.recommended_action} isDark={isDark} severity={report.severity} />

      {includeRaw && (
        <details className={`rounded-xl border ${isDark ? 'border-slate-700' : 'border-slate-200'}`}>
          <summary className={`cursor-pointer px-4 py-2 text-sm font-semibold ${isDark ? 'bg-slate-800 text-slate-100' : 'bg-slate-100 text-slate-700'}`}>
            Raw sandbox output
          </summary>
          <pre className={`p-4 text-xs overflow-auto max-h-72 font-mono ${isDark ? 'bg-slate-950 text-slate-200' : 'bg-slate-900 text-slate-100'}`}>
            {report.raw_log}
          </pre>
        </details>
      )}
    </div>
  )
}
