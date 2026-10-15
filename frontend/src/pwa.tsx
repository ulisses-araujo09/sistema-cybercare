import { useEffect, useState } from 'react'
import { Download, RefreshCw, WifiOff, X } from 'lucide-react'
import { registerSW } from 'virtual:pwa-register'

type InstallPrompt = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}
let updateApp: ((reloadPage?: boolean) => Promise<void>) | undefined
let updateReady = false
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  updateApp = registerSW({
    onNeedRefresh() { updateReady = true; window.dispatchEvent(new Event('pwa-update-ready')) },
    onRegisterError() { window.dispatchEvent(new Event('pwa-registration-error')) }
  })
}

export function InstallButton() {
  const [prompt, setPrompt] = useState<InstallPrompt | null>(null)
  const [guide, setGuide] = useState(false)
  const [installed, setInstalled] = useState(() => window.matchMedia('(display-mode: standalone)').matches || !!(navigator as Navigator & { standalone?: boolean }).standalone)
  useEffect(() => {
    const before = (event: Event) => { event.preventDefault(); setPrompt(event as InstallPrompt) }
    const done = () => { setInstalled(true); setPrompt(null); setGuide(false) }
    window.addEventListener('beforeinstallprompt', before)
    window.addEventListener('appinstalled', done)
    return () => { window.removeEventListener('beforeinstallprompt', before); window.removeEventListener('appinstalled', done) }
  }, [])
  async function install() {
    if (!prompt) { setGuide(value => !value); return }
    try { await prompt.prompt(); await prompt.userChoice } finally { setPrompt(null) }
  }
  if (installed) return null
  return <div className="install-control"><button type="button" className="install-button" onClick={() => { install().catch(() => setGuide(true)) }} aria-expanded={guide} aria-controls="install-guide"><Download size={16}/> Instalar app</button>{guide && <div id="install-guide" className="install-guide" role="region" aria-label="Como instalar o CyberCare"><div><strong>CyberCare no seu dispositivo</strong><button onClick={() => setGuide(false)} aria-label="Fechar instruções de instalação"><X size={18}/></button></div><p><strong>Android ou computador:</strong> abra o menu do Chrome ou Edge e escolha “Instalar CyberCare” ou “Adicionar à tela inicial”, quando disponível.</p><p><strong>iPhone ou iPad:</strong> abra no Safari, toque em Compartilhar e em “Adicionar à Tela de Início”.</p><p>O aplicativo precisa de internet para registrar e acompanhar denúncias. A instalação depende do suporte do navegador.</p></div>}</div>
}

export function PwaStatus() {
  const [online, setOnline] = useState(navigator.onLine)
  const [update, setUpdate] = useState(updateReady)
  useEffect(() => {
    const status = () => setOnline(navigator.onLine)
    const ready = () => setUpdate(true)
    window.addEventListener('online', status); window.addEventListener('offline', status); window.addEventListener('pwa-update-ready', ready)
    return () => { window.removeEventListener('online', status); window.removeEventListener('offline', status); window.removeEventListener('pwa-update-ready', ready) }
  }, [])
  return <>{!online && <div className="connection-notice" role="status"><WifiOff size={20}/><p><strong>Você está sem conexão.</strong> Conecte-se à internet para enviar, consultar ou gerenciar registros. Nenhum envio será guardado para depois.</p></div>}{update && <div className="connection-notice" role="status"><RefreshCw size={20}/><p>Uma nova versão do CyberCare está disponível. Guarde sua chave e conclua qualquer formulário antes de atualizar.</p><button className="btn dark" onClick={() => { updateApp?.(true).catch(() => {}) }}>Atualizar aplicativo</button></div>}</>
}
