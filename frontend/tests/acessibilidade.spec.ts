import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
test('acessibilidade automática das telas públicas', async ({ page }) => {
  for (const route of ['/', '/denunciar', '/acompanhar', '/apoio', '/quiz', '/login', '/sobre']) {
    await page.goto(route)
    await expect(page.locator('h1')).toBeVisible()
    const result = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze()
    expect(result.violations.map(v => ({ id: v.id, nodes: v.nodes.map(n => ({ target: n.target, summary: n.failureSummary })) })), route).toEqual([])
  }
})
