import { test, expect } from '@playwright/test'
import { readFileSync, mkdirSync } from 'node:fs'
import type { Page } from '@playwright/test'
const env = process.env.DEMO_STAFF_PASSWORD && process.env.DEMO_MANAGER_PASSWORD ? '' : readFileSync('../backend/.env', 'utf8')
const screenshots = process.env.CYBERCARE_SCREENSHOT_DIR || '../docs/validacao'
function credential(key: string) { if (process.env[key]) return process.env[key]!; const result = env.match(new RegExp(`^${key}=(.+)$`, 'm')); if (!result) throw new Error(`Configure ${key} no ambiente local.`); return result[1].trim() }
async function login(page: Page, role: 'socioemocional' | 'gestao') {
  await page.getByRole('link', { name: 'Acesso da escola', exact: true }).click()
  await page.getByLabel('E-mail institucional').fill(`${role}@demo.cybercare.local`)
  await page.getByLabel('Senha', { exact: true }).fill(credential(role === 'gestao' ? 'DEMO_MANAGER_PASSWORD' : 'DEMO_STAFF_PASSWORD'))
  await page.getByRole('button', { name: 'Entrar no painel' }).click()
  await expect(page).toHaveURL(new RegExp(`/${role}$`))
}
async function noOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
}

test('denúncia persistida, chave única, consulta, gestão socioemocional e nova consulta', async ({ page }, info) => {
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message))
  await page.goto('/')
  await page.getByRole('link', { name: 'Fazer denúncia', exact: true }).click()
  await page.getByLabel('Tipo de situação').selectOption('cyberbullying')
  const marker = `PERSONAGEM FICTÍCIO ${Date.now()} — colegas inventados compartilham mensagens humilhantes em uma atividade simulada.`
  await page.getByLabel('Descreva a situação fictícia').fill(marker)
  await page.getByLabel('Confirmo que esta denúncia').check()
  await page.getByRole('button', { name: 'Registrar denúncia fictícia' }).click()
  await expect(page.getByText('Sua voz foi acolhida.')).toBeVisible()
  const protocol = await page.locator('.code-box strong').innerText()
  const secret = await page.locator('.code-box code').innerText()
  expect(secret.length).toBeGreaterThan(30)
  await noOverflow(page)
  await page.getByRole('link', { name: 'Acompanhar', exact: true }).last().click()
  await page.getByLabel('Protocolo *', { exact: true }).fill(protocol)
  await page.getByLabel('Chave privada').fill(secret)
  await page.getByRole('button', { name: 'Consultar acompanhamento' }).click()
  await expect(page.locator('.timeline').getByText('Denúncia recebida')).toBeVisible()
  await expect(page.getByText(marker)).toHaveCount(0)
  await login(page, 'socioemocional')
  await page.locator('.case-row').filter({ hasText: protocol }).click()
  await expect(page.getByText(marker, { exact: true })).toBeVisible()
  await noOverflow(page)
  await page.getByLabel('Nota interna').fill('Nota fictícia de acesso restrito.')
  await page.getByRole('button', { name: 'Atualizar etapa' }).click()
  await expect(page.getByText('Etapa atualizada.', { exact: false })).toBeVisible()
  await expect(page.locator('.timeline').getByText('Em análise', { exact: true })).toBeVisible()
  await page.evaluate(() => window.scrollTo(0, 0))
  await page.screenshot({ path: `../docs/validacao/socioemocional-${info.project.name}.png`, fullPage: true })
  await page.getByRole('button', { name: 'Sair', exact: true }).click()
  await expect(page).toHaveURL(/\/login$/)
  await page.getByRole('link', { name: 'Acompanhar', exact: true }).click()
  await page.getByLabel('Protocolo *', { exact: true }).fill(protocol)
  await page.getByLabel('Chave privada').fill(secret)
  await page.getByRole('button', { name: 'Consultar acompanhamento' }).click()
  await expect(page.locator('.timeline').getByText('Em análise', { exact: true })).toBeVisible()
  await expect(page.getByText('Nota fictícia de acesso restrito.')).toHaveCount(0)
  await page.screenshot({ path: `../docs/validacao/acompanhamento-${info.project.name}.png`, fullPage: true })
  await page.goto('/protocolo')
  await expect(page.getByText('Seu acesso é mostrado somente após o envio.')).toBeVisible()
  expect(errors).toEqual([])
})

test('telas públicas responsivas, quiz real e estados de erro', async ({ page }, info) => {
  mkdirSync(screenshots, { recursive: true })
  for (const route of ['/', '/denunciar', '/acompanhar', '/apoio', '/quiz', '/login', '/sobre']) {
    await page.goto(route)
    await expect(page.locator('h1')).toBeVisible()
    await expect(page.locator('.demo-notice')).toBeVisible()
    await noOverflow(page)
    await page.screenshot({ path: `${screenshots}/${route === '/' ? 'inicio' : route.slice(1)}-${info.project.name}.png`, fullPage: true })
  }
  await page.goto('/quiz')
  await expect(page.locator('.quiz-option').first()).toBeVisible()
  for (let i = 0; i < 5; i++) {
    await page.locator('.quiz-option').first().click()
    await expect(page.locator('.feedback')).toBeVisible()
    await page.getByRole('button', { name: i === 4 ? 'Ver resultado' : 'Próxima pergunta' }).click()
  }
  await expect(page.getByText('Você concluiu o Quiz CyberCare!')).toBeVisible()
  await page.goto('/acompanhar')
  await page.getByLabel('Protocolo *', { exact: true }).fill('CYB-INEXISTENTE')
  await page.getByLabel('Chave privada').fill('chave-inexistente-ficticia')
  await page.getByRole('button', { name: 'Consultar acompanhamento' }).click()
  await expect(page.getByRole('alert')).toContainText('Protocolo ou chave inválidos')
})

test('painel gerencial agregado e filtros', async ({ page }, info) => {
  await page.goto('/')
  await login(page, 'gestao')
  await expect(page.getByText('Registros fictícios no período')).toBeVisible()
  await expect(page.locator('.case-row')).toHaveCount(0)
  await noOverflow(page)
  await page.screenshot({ path: `../docs/validacao/gestao-${info.project.name}.png`, fullPage: true })
  await page.getByRole('combobox', { name: 'Categoria', exact: true }).selectOption('ameaca')
  await page.getByRole('button', { name: 'Aplicar filtros' }).click()
  await expect(page.getByText('Registros fictícios no período')).toBeVisible()
  await noOverflow(page)
})
