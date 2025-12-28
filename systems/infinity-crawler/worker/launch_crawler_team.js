import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const NUM_WORKERS = 3; // Number of crawler workers to launch
const workers = [];

console.log(`Launching ${NUM_WORKERS} crawler workers...`);

for (let i = 0; i < NUM_WORKERS; i++) {
  const workerId = `worker-${i + 1}`;
  console.log(`Starting ${workerId}...`);

  const worker = spawn('node', ['worker.js', workerId], {
    cwd: __dirname,
    stdio: 'inherit',
  });

  workers.push(worker);

  worker.on('close', (code) => {
    console.log(`${workerId} exited with code ${code}`);
  });

  worker.on('error', (err) => {
    console.error(`${workerId} error:`, err);
  });
}

console.log('Crawler team launched. Press Ctrl+C to stop all workers.');

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down crawler team...');
  workers.forEach((worker) => {
    worker.kill('SIGINT');
  });
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\nShutting down crawler team...');
  workers.forEach((worker) => {
    worker.kill('SIGTERM');
  });
  process.exit(0);
});
