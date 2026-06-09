# SandboxAI Frontend

This is a Vite + React + Tailwind frontend for the SandboxAI project.

Quick start:

```bash
cd frontend
npm install
npm run dev
```

The UI is a two-panel layout with an upload area and a report view. The frontend currently simulates analysis stages for demo purposes; next step is wiring it to your Python backend (e.g. a `/api/analyze` endpoint that accepts `multipart/form-data`).
