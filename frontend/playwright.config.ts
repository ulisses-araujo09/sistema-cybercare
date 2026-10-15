import { defineConfig, devices } from '@playwright/test'
export default defineConfig({
  testDir: './tests', fullyParallel: false, workers: 1, retries: 0, timeout: 45000,
  reporter: [['list'], ['json', { outputFile: 'test-results/resultados.json' }]],
  use: { baseURL: 'http://127.0.0.1:5173', trace: 'off', screenshot: 'only-on-failure' },
  projects: [
    { name: 'computador', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1000 } } },
    { name: 'celular', use: { ...devices['iPhone SE'], defaultBrowserType: 'chromium', viewport: { width: 375, height: 812 } } }
  ]
})
