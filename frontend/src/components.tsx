import type { ReactNode } from 'react'
import { Check, Circle, ShieldCheck } from 'lucide-react'
import { dateLabel, statuses } from './api'
import type { PublicReport } from './api'

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) { return <section className={`card ${className}`}>{children}</section> }
export function Notice({ children }: { children: ReactNode }) { return <div className="notice"><ShieldCheck size={20} aria-hidden="true"/><span>{children}</span></div> }
export function ErrorMessage({ message }: { message: string }) { return message ? <p role="alert" className="error">{message}</p> : null }
export function Loading() { return <p role="status" className="loading">Carregando…</p> }
export function Timeline({ report, privateNotes = false }: { report: PublicReport; privateNotes?: boolean }) {
  return <ol className="timeline">{report.events.map((event, index) => <li key={`${event.created_at}-${index}`}><span className="timeline-dot"><Check size={15} aria-hidden="true"/></span><div><strong>{statuses[event.status]}</strong><p className="muted">{dateLabel(event.created_at)}</p>{privateNotes && event.note_private_optional && <p className="private-note">Nota interna: {event.note_private_optional}</p>}</div></li>)}{report.status !== 'atendimento_realizado' && <li className="future"><span className="timeline-dot"><Circle size={14}/></span><div><strong>Próximas etapas</strong><p className="muted">As atualizações aparecerão aqui após a consulta.</p></div></li>}</ol>
}
