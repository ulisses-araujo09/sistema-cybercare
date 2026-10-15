export type Role = 'socioemocional' | 'gestao'
export type Status = 'recebida' | 'em_analise' | 'encaminhada' | 'atendimento_realizado'
export type Category = 'bullying' | 'cyberbullying' | 'racismo' | 'ameaca' | 'outros'
export const statuses: Record<Status, string> = { recebida: 'Denúncia recebida', em_analise: 'Em análise', encaminhada: 'Encaminhada', atendimento_realizado: 'Atendimento realizado' }
export const categories: Record<Category, string> = { bullying: 'Bullying', cyberbullying: 'Cyberbullying', racismo: 'Racismo', ameaca: 'Ameaça', outros: 'Outra situação' }
export type ReportEvent = { status: Status; created_at: string; note_private_optional?: string | null }
export type PublicReport = { protocol: string; status: Status; created_at: string; updated_at: string; events: ReportEvent[] }
export type PrivateReport = PublicReport & { id: string; category: Category; reporter_type: string; description: string; location_optional?: string; identification_optional?: string }
export type ReportItem = Pick<PrivateReport, 'id' | 'protocol' | 'status' | 'category' | 'created_at'>
export type Question = { id: string; question: string; options: string[] }
export type Band = { range: string; lower: number | null; suppressed: boolean }
export type Metrics = { total: Band; threshold: number; categories: (Band & { label: Category })[]; statuses: (Band & { label: Status })[]; privacy_note: string }
export type Config = { demo: boolean; support_name: string; support_contact: string; retention_days: number }
let token: string | null = null
export function setToken(value: string | null) { token = value }
export class ApiError extends Error { constructor(message: string, public status: number) { super(message) } }
export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 15000)
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL || ''}/api${path}`, { ...options, signal: controller.signal, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } })
    const data = await response.json()
    if (!response.ok) {
      if (response.status === 401 && token) window.dispatchEvent(new Event('session-expired'))
      throw new ApiError(typeof data.detail === 'string' ? data.detail : 'Não foi possível concluir. Confira os campos.', response.status)
    }
    return data as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new Error('Não foi possível conectar ao CyberCare. Verifique sua conexão e tente novamente.')
  } finally { clearTimeout(timer) }
}
export const post = <T>(path: string, body: unknown) => api<T>(path, { method: 'POST', body: JSON.stringify(body) })
export const dateLabel = (date: string) => new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(date.endsWith('Z') || /[+-]\d\d:\d\d$/.test(date) ? date : `${date}Z`))
