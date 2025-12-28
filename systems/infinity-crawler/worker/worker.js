import { chromium } from 'playwright';

const ORCHESTRATOR_URL =
  process.env.ORCHESTRATOR_URL || 'http://localhost:8000';

async function processJob(job) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(job.url, { waitUntil: 'networkidle' });
  const html = await page.content();
  await browser.close();

  const result = {
    url: job.url,
    bytes: html.length,
    status: 'success',
    html: html,
  };

  // Post result to orchestrator
  try {
    await fetch(`${ORCHESTRATOR_URL}/results`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result),
    });
  } catch (error) {
    console.error('Failed to post result:', error.message);
  }

  console.log(JSON.stringify(result));
}

async function run() {
  console.log('Crawler worker started, polling for jobs...');
  while (true) {
    try {
      const response = await fetch(`${ORCHESTRATOR_URL}/jobs`);
      const data = await response.json();
      const jobs = data.jobs || [];
      if (jobs.length > 0) {
        await processJob(jobs[0]); // Process one job
      }
    } catch (error) {
      console.error('Error polling jobs:', error.message);
    }
    await new Promise((resolve) => setTimeout(resolve, 1000)); // Poll every second
  }
}

run().catch(console.error);
