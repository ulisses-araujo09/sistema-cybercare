import { useEffect, useRef, useState } from 'react'
import { Accessibility, MessageCircle, X } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { educationalReply, educationalTopics, helpChannels } from './educational'
import './assistive.css'

const storageKey = 'cybercare.acessibilidade.v1'
const defaults = { dark: false, contrast: false, size: 100, underline: false, spacing: false, motion: false, readable: false }
type Preferences = typeof defaults
function readPreferences(): Preferences {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{}')
    const result = { ...defaults }
    for (const key of ['dark', 'contrast', 'underline', 'spacing', 'motion', 'readable'] as const) result[key] = saved?.[key] === true
    result.size = [100, 125, 150, 175, 200].includes(saved?.size) ? saved.size : 100
    return result
  } catch { return { ...defaults } }
}
type Exchange = { question: string; reply: ReturnType<typeof educationalReply> }
export default function AssistiveTools() {
  const [preferences, setPreferences] = useState(readPreferences)
  const [panel, setPanel] = useState<'accessibility' | 'chat' | null>(null)
  const [question, setQuestion] = useState(''), [exchanges, setExchanges] = useState<Exchange[]>([])
  const [busy, setBusy] = useState(false)
  const pending = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const [storageError, setStorageError] = useState(false)
  const dialog = useRef<HTMLDialogElement>(null), chatEnd = useRef<HTMLDivElement>(null)
  const location = useLocation()
  const publicPage = ['/', '/denunciar', '/acompanhar', '/apoio', '/quiz', '/sobre'].includes(location.pathname)
  useEffect(() => {
    const root = document.documentElement
    root.dataset.careTheme = preferences.contrast ? 'contrast' : preferences.dark ? 'dark' : 'light'
    root.dataset.careUnderline = String(preferences.underline)
    root.dataset.careSpacing = String(preferences.spacing)
    root.dataset.careMotion = String(preferences.motion)
    root.dataset.careReadable = String(preferences.readable)
    root.style.setProperty('--care-font-scale', `${preferences.size}%`)
    try {
      if (JSON.stringify(preferences) === JSON.stringify(defaults)) localStorage.removeItem(storageKey)
      else localStorage.setItem(storageKey, JSON.stringify(preferences))
      setStorageError(false)
    } catch { setStorageError(true) }
  }, [preferences])
  useEffect(() => { close(); return () => clearTimeout(pending.current) }, [location.pathname])
  useEffect(() => {
    if (panel && !dialog.current?.open) dialog.current?.showModal()
    else if (!panel && dialog.current?.open) dialog.current?.close()
  }, [panel])
  useEffect(() => { chatEnd.current?.scrollIntoView({ block: 'nearest' }) }, [exchanges])
  function close() { clearTimeout(pending.current); setBusy(false); setPanel(null); setQuestion(''); setExchanges([]) }
  function ask(value: string) {
    const clean = value.trim().slice(0, 300)
    if (!clean || busy) return
    setBusy(true); setQuestion('')
    pending.current = setTimeout(() => {
      setExchanges(previous => [...previous.slice(-9), { question: clean, reply: educationalReply(clean) }]); setBusy(false)
    }, 0)
  }
  const toggle = (key: Exclude<keyof Preferences, 'size'>, label: string) => <label className="care-toggle"><span>{label}</span><input type="checkbox" checked={preferences[key]} onChange={e => setPreferences(p => ({ ...p, [key]: e.target.checked }))}/></label>
  return <><div className="care-launchers" aria-label="Ferramentas de apoio"><button className="care-launcher" onClick={() => setPanel('accessibility')} aria-haspopup="dialog" aria-expanded={panel === 'accessibility'}><Accessibility aria-hidden="true" size={24}/><span>Acessibilidade</span></button>{publicPage && <button className="care-launcher care-chat-launcher" onClick={() => setPanel('chat')} aria-haspopup="dialog" aria-expanded={panel === 'chat'}><MessageCircle aria-hidden="true" size={24}/><span>Ajuda educativa</span></button>}</div>
    <dialog ref={dialog} className="care-dialog" aria-labelledby="care-panel-title" onCancel={close} onClose={close}>
      <div className="care-panel-heading"><h2 id="care-panel-title">{panel === 'chat' ? 'Assistente CyberCare' : 'Acessibilidade'}</h2><button className="care-close" autoFocus aria-label="Fechar painel" onClick={close}><X aria-hidden="true"/></button></div>
      {panel === 'accessibility' && <div className="care-panel-body"><p>Personalize sua leitura. Feche com Escape ou no botão acima.</p>{toggle('dark', 'Modo escuro')}{toggle('contrast', 'Alto contraste')}<fieldset className="care-font"><legend>Tamanho do texto</legend><div><button aria-label="Diminuir fonte" disabled={preferences.size === 100} onClick={() => setPreferences(p => ({ ...p, size: p.size - 25 }))}>A−</button><output aria-live="polite">{preferences.size}%</output><button aria-label="Aumentar fonte" disabled={preferences.size === 200} onClick={() => setPreferences(p => ({ ...p, size: p.size + 25 }))}>A+</button></div></fieldset>{toggle('underline', 'Sublinhar links')}{toggle('spacing', 'Maior espaçamento de texto')}{toggle('motion', 'Reduzir animações')}{toggle('readable', 'Fonte de leitura facilitada')}<p className="care-caption">A preferência do dispositivo por movimento reduzido também é respeitada. O alto contraste tem prioridade sobre o modo escuro.</p><button className="btn dark" onClick={() => setPreferences({ ...defaults })}>Restaurar configurações</button>{storageError && <p role="status">Seu navegador não permite salvar preferências. Elas continuam ativas nesta sessão.</p>}</div>}
      {panel === 'chat' && <div className="care-panel-body"><p><strong>Olá! Sou o assistente educativo do CyberCare.</strong> Como posso ajudar você a aprender e buscar orientação?</p><p className="care-chat-notice">Respostas educativas de uma base revisada, sem IA generativa. Não envie nomes, relatos, protocolos ou chaves. Não há atendimento em tempo real. A conversa é apagada ao fechar ou mudar de página.</p><div className="care-suggestions" aria-label="Perguntas sugeridas">{educationalTopics.map(topic => <button key={topic.title} disabled={busy} onClick={() => ask(topic.title)}>{topic.title}</button>)}</div><div className="care-conversation" role="log" aria-live="polite" aria-relevant="additions" aria-label="Conversa educativa">{exchanges.map((exchange, index) => <div key={index} className="care-exchange"><p><strong>Você:</strong> {exchange.question}</p><div className="care-answer"><p><strong>CyberCare:</strong> {exchange.reply.answer}</p><Link to={exchange.reply.to}>{exchange.reply.link}</Link>{exchange.reply.source && <p><a href="https://www.unicef.org/brazil/cyberbullying-o-que-eh-e-como-para-lo" target="_blank" rel="noopener noreferrer">Fonte educativa: UNICEF (nova aba)</a></p>}{exchange.reply.help && <><ul className="care-channels">{helpChannels.map(channel => <li key={channel.number}><a href={channel.href}>{channel.number}</a> — <strong>{channel.label}</strong>: {channel.purpose} <a href={channel.source} target="_blank" rel="noopener noreferrer">Fonte (nova aba)</a></li>)}</ul><p>Esses serviços não substituem o acompanhamento escolar ou profissional. Contate os serviços diretamente; o chat não aciona equipes.</p></>}</div></div>)}</div>{busy && <p role="status">Preparando resposta educativa…</p>}<div ref={chatEnd}/><form onSubmit={event => { event.preventDefault(); ask(question) }}><label htmlFor="care-question">Sua dúvida educativa (até 300 caracteres)</label><input id="care-question" value={question} maxLength={300} autoComplete="off" onChange={event => setQuestion(event.target.value)}/><div className="actions"><button className="btn dark" disabled={busy || !question.trim()}>Enviar pergunta</button><button type="button" className="btn light" onClick={() => { clearTimeout(pending.current); setBusy(false); setExchanges([]); setQuestion('') }}>Limpar conversa</button></div></form></div>}
    </dialog></>
}
