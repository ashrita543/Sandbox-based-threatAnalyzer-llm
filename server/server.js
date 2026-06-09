const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Setup file upload directory
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const timestamp = Date.now();
    const cleanName = file.originalname.replace(/[^a-zA-Z0-9.-]/g, '_');
    cb(null, `${timestamp}_${cleanName}`);
  },
});

const fileFilter = (req, file, cb) => {
  const allowedMimes = [
    'text/x-python',
    'text/plain',
    'text/x-shellscript',
    'application/x-sh',
    'text/javascript',
    'application/x-msdownload',
    'application/octet-stream',
  ];

  const allowedExtensions = ['.py', '.sh', '.js', '.exe'];
  const fileExt = path.extname(file.originalname).toLowerCase();

  if (allowedExtensions.includes(fileExt)) {
    cb(null, true);
  } else {
    cb(new Error(`Invalid file type. Allowed: ${allowedExtensions.join(', ')}`), false);
  }
};

const upload = multer({ storage, fileFilter });

/**
 * POST /api/analyze
 * Accepts a file upload and runs it through the Python sandbox analyzer
 */
app.post('/api/analyze', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file provided' });
    }

    const filePath = req.file.path;
    const filename = req.file.originalname;
    const mode = req.body.mode || 'simple';
    const timeout = parseInt(req.body.timeout) || 30;

    console.log(`Analyzing file: ${filename} (mode: ${mode})`);

    // Call Python main.py with the uploaded file
    const mainPyPath = path.resolve(__dirname, '..', 'main.py');
    console.log(`Calling: python3 ${mainPyPath} ${filePath} --mode ${mode}`);

    const pythonProcess = spawn('python3', [
      mainPyPath,
      filePath,
      '--mode',
      mode,
      '--timeout',
      timeout.toString(),
    ], {
      cwd: path.resolve(__dirname, '..'),
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      const chunk = data.toString();
      stderr += chunk;
      process.stderr.write(chunk);
    });

    pythonProcess.on('close', (code) => {
      // Clean up uploaded file
      fs.unlink(filePath, (err) => {
        if (err) console.error('Failed to delete uploaded file:', err);
      });

      console.log(`Python process exited with code ${code}`);
      console.log(`STDOUT length: ${stdout.length} chars`);
      console.log(`STDERR length: ${stderr.length} chars`);

      if (code !== 0) {
        console.error('Python process failed with code:', code);
        console.error('STDERR:', stderr);
        return res.status(500).json({
          error: 'Analysis failed',
          details: stderr || `Process exited with code ${code}`,
        });
      }

      try {
        // Extract JSON from stdout
        const jsonMatch = stdout.match(/\{[\s\S]*\}/);
        if (!jsonMatch) {
          console.error('Could not find JSON in stdout');
          console.error('Full stdout length:', stdout.length);
          console.error('Full stdout preview:', stdout.substring(0, 500));
          throw new Error('No JSON response from analyzer');
        }

        let jsonStr = jsonMatch[0];
        console.log(`Found JSON candidate (${jsonStr.length} chars)`);
        
        let threatReport;
        try {
          threatReport = JSON.parse(jsonStr);
        } catch (parseError) {
          console.warn('Initial JSON parse failed, attempting recovery...');
          // Try to find valid JSON by trimming from the end
          let parsed = false;
          for (let i = jsonStr.length - 1; i > jsonStr.length - 500 && i > 0; i--) {
            if (jsonStr[i] === '}') {
              const trimmed = jsonStr.substring(0, i + 1);
              try {
                threatReport = JSON.parse(trimmed);
                console.log(`Successfully parsed JSON (trimmed to ${trimmed.length} chars)`);
                parsed = true;
                break;
              } catch (e) {
                // Continue trying
              }
            }
          }
          
          if (!parsed) {
            throw parseError;
          }
        }

        const terminalSummary = threatReport.executive_summary || threatReport.summary;
        if (terminalSummary) {
          console.log('LLM summary:', terminalSummary);
        }

        return res.json({
          success: true,
          filename,
          mode,
          threat_report: threatReport,
        });
      } catch (parseError) {
        console.error('Failed to parse threat report:', parseError.message);
        console.error('JSON preview:', stdout.substring(0, 500));
        return res.status(500).json({
          error: 'Failed to parse threat report',
          details: parseError.message,
        });
      }
    });

    // Handle process errors
    pythonProcess.on('error', (err) => {
      fs.unlink(filePath, (unlinkErr) => {
        if (unlinkErr) console.error('Failed to delete uploaded file:', unlinkErr);
      });
      console.error('Process error:', err);
      res.status(500).json({
        error: 'Process error',
        details: err.message,
      });
    });
  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({
      error: 'Server error',
      details: error.message,
    });
  }
});

/**
 * GET /api/health
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handling middleware
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    return res.status(400).json({
      error: 'File upload error',
      details: err.message,
    });
  } else if (err) {
    return res.status(400).json({
      error: err.message || 'Unknown error',
    });
  }
  next();
});

const server = app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
  console.log(`Upload endpoint: POST http://localhost:${PORT}/api/analyze`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Stop the existing server or start this one with a different PORT.`);
    process.exit(1);
  }

  console.error('Server failed to start:', err);
  process.exit(1);
});
