import React, { useMemo, useState } from 'react'
import Navbar from './components/Navbar'
import LeftPanel from './components/LeftPanel'
import RightPanel from './components/RightPanel'

const MOCK_SIMPLE_REPORT = {
  threat_name: 'Reverse Shell with Credential Harvesting',
  severity: 'CRITICAL',
  summary:
    'The script attempted sensitive file access, initiated external network communication, and spawned command execution patterns consistent with an interactive reverse shell. This behavior strongly indicates active post-exploitation activity and credential collection attempts.',
  malware_category: ['Backdoor', 'Infostealer'],
  indicators_of_compromise: {
    files: [
      { value: '/etc/passwd', suspicion: 'high' },
      { value: '/tmp/.cache/cred_dump.txt', suspicion: 'high' },
      { value: '/var/tmp/.hidden.sock', suspicion: 'medium' },
    ],
    processes: [
      { value: 'python3 -c socket connection loop', suspicion: 'high' },
      { value: '/bin/sh -i', suspicion: 'high' },
      { value: 'curl -fsSL remote payload', suspicion: 'medium' },
    ],
    network: [
      { value: '185.199.110.153:4444', suspicion: 'high' },
      { value: 'dns query: api.drop-file.net', suspicion: 'medium' },
    ],
  },
  likely_intent: 'Reconnaissance or intelligence gathering',
  recommended_action: 'Monitor system for further malicious activity, but no immediate action required.',
}

const MOCK_DETAILED_FIELDS = {
  severity_justification:
    'The script accessed a sensitive file, /etc/passwd, which contains system user information, and spawned an unusual process, suggesting malicious intent.',
  likely_intent:
    'The attacker\'s likely intent is to steal or exfiltrate sensitive user information, potentially for unauthorized access or malicious activities.',
  false_positive_assessment:
    'Low confidence. This script\'s behavior is unusual and suggests malicious intent. While Python can be used for legitimate purposes, the specific file accesses and process spawned are indicative of an attacker\'s actions.',
  attack_chain: [
    'Step 1: Enumerated local system artifacts and touched sensitive account files.',
    'Step 2: Spawned shell and helper processes to prepare command execution.',
    'Step 3: Attempted outbound callback over a suspicious high-risk port.',
  ],
  mitre_attack_techniques: [
    { id: 'T1059', description: 'Command and Scripting Interpreter' },
    { id: 'T1071', description: 'Application Layer Protocol' },
    { id: 'T1005', description: 'Data from Local System' },
  ],
  recommended_action: {
    immediate: 'Immediately isolate the system to prevent further data extraction or manipulation.',
    short_term: 'Review system logs and network activity to identify potential entry points and implement additional security measures.',
    long_term: 'Implement secure password storage, restrict access to sensitive files, and consider using a security information and event management (SIEM) system to monitor for similar attacks.',
  },
}

const STAGE = {
  SANDBOX: 'sandbox',
  EXECUTE: 'execute',
  REPORT: 'report',
}

function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

export default function App() {
  const [mode, setMode] = useState('script')
  const [theme, setTheme] = useState('light')
  const [file, setFile] = useState(null)
  const [uploadError, setUploadError] = useState('')
  const [reportMode, setReportMode] = useState('simple')
  const [options, setOptions] = useState({ timeout: 30, includeRaw: false, flagLow: true })
  const [runningStage, setRunningStage] = useState(null)
  const [executeProgress, setExecuteProgress] = useState(0)
  const [timedOut, setTimedOut] = useState(false)
  const [error, setError] = useState('')
  const [report, setReport] = useState(null)

  const isDark = theme === 'dark'

  const shellClass = useMemo(
    () =>
      isDark
        ? 'min-h-screen bg-slate-950 text-slate-100 transition-colors duration-300'
        : 'min-h-screen bg-slate-100 text-slate-900 transition-colors duration-300',
    [isDark],
  )

  async function runAnalysis() {
    if (!file) return

    setError('')
    setReport(null)
    setTimedOut(false)
    setRunningStage(STAGE.SANDBOX)

    try {
      await wait(800)

      setRunningStage(STAGE.EXECUTE)
      setExecuteProgress(0)

      // Prepare form data with file and options
      const formData = new FormData()
      formData.append('file', file)
      formData.append('mode', reportMode)
      formData.append('timeout', options.timeout.toString())

      // Start the upload and analysis
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Analysis failed: ${response.statusText}`)
      }

      // Simulate execution progress while waiting for response
      const timeoutMs = options.timeout * 1000
      const tickMs = 100
      const steps = Math.max(1, Math.floor(timeoutMs / tickMs))

      for (let step = 1; step <= steps; step += 1) {
        if (step % 10 === 0) {
          setExecuteProgress(Math.round((step / steps) * 100))
        }
        await wait(tickMs)
      }

      const data = await response.json()

      setRunningStage(STAGE.REPORT)
      await wait(600)

      // Merge the threat report with metadata
      const enrichedReport = {
        ...data.threat_report,
        filename: file.name,
        mode: reportMode,
      }

      setReport(enrichedReport)
      setRunningStage(null)
      setExecuteProgress(0)
    } catch (err) {
      setRunningStage(null)
      setError(err.message || 'Analysis failed. Make sure the backend server is running on localhost:5000')
      console.error('Analysis error:', err)
    }
  }

  return (
    <div className={`${shellClass} ${isDark ? 'dark' : ''}`}>
      <div className="app-atmosphere" aria-hidden="true" />
      <Navbar mode={mode} setMode={setMode} theme={theme} setTheme={setTheme} />
      <main className="p-3 sm:p-4 lg:p-6 h-[calc(100vh-60px)]">
        <section className="workspace-grid h-full gap-4 lg:gap-6">
          <div className={`rounded-2xl border p-4 lg:p-5 flex flex-col shadow-sm ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}`}>
            <LeftPanel
              mode={mode}
              file={file}
              setFile={setFile}
              uploadError={uploadError}
              setUploadError={setUploadError}
              reportMode={reportMode}
              setReportMode={setReportMode}
              options={options}
              setOptions={setOptions}
              runningStage={runningStage}
              onRun={runAnalysis}
              isDark={isDark}
            />
          </div>
          <div className={`rounded-2xl border p-4 lg:p-5 overflow-auto shadow-sm ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}`}>
            <RightPanel
              mode={mode}
              file={file}
              report={report}
              error={error}
              runningStage={runningStage}
              executeProgress={executeProgress}
              timedOut={timedOut}
              includeRaw={options.includeRaw}
              isDark={isDark}
            />
          </div>
        </section>
      </main>
    </div>
  )
}
