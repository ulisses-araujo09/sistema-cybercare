"""Manutenção periódica sem armazenar conteúdo em logs ou criar serviço adicional."""
import asyncio
import logging
from .retention import purge

log = logging.getLogger('cybercare.manutencao')


async def run_retention_loop():
    while True:
        try:
            await asyncio.to_thread(purge)
        except Exception:
            # Não incluir consulta, parâmetros, URL do banco ou conteúdo na mensagem.
            log.warning('Rotina de retenção temporariamente indisponível; será tentada novamente.')
        await asyncio.sleep(3600)
