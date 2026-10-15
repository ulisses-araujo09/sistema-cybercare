"""Gera arquivo de entrega apenas com fontes e documentação permitidas."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib

root = Path(__file__).resolve().parents[1]
directories = ['backend', 'frontend', 'docs', 'scripts', 'CyberCare_Codex', '.github']
root_files = ['README.md', 'AGENTS.md', '.gitignore', '.gitattributes', 'docker-compose.yml', 'iniciar-demo.ps1']
excluded = {'node_modules', 'dist', '__pycache__', '.pytest_cache', 'test-results', 'playwright-report'}


def allowed(path):
    if excluded.intersection(path.parts):
        return False
    if path.name.startswith('.env') and path.name != '.env.example':
        return False
    return path.suffix not in {'.db', '.pyc', '.tsbuildinfo'} and not path.name.endswith(('.db-wal', '.db-shm'))


files = [root / name for name in root_files]
for directory in directories:
    files.extend(p for p in (root / directory).rglob('*') if p.is_file() and allowed(p.relative_to(root)))
output = root / 'CyberCare_MVP_Entrega.zip'
with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, 'CyberCare_MVP/' + path.relative_to(root).as_posix())
with ZipFile(output) as archive:
    assert all('/.env' not in p or p.endswith('.env.example') for p in archive.namelist())
    assert not any('demo-acessos' in p or 'node_modules' in p for p in archive.namelist())
    assert archive.testzip() is None
print(f'Entrega: {len(files)} arquivos, {output.stat().st_size} bytes')
print('SHA-256:', hashlib.sha256(output.read_bytes()).hexdigest())
