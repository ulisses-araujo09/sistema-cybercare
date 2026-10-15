$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $branchCyberCare = git branch --show-current
    if ($LASTEXITCODE -ne 0 -or $branchCyberCare -ne 'main') { throw 'Publique a partir da branch main.' }
    git diff --quiet
    if ($LASTEXITCODE -ne 0) { throw 'Há alterações não commitadas. Revise e crie o commit antes da publicação.' }
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) { throw 'Há alterações preparadas ainda sem commit.' }
    $destinosCyberCare = @{
        origin = 'https://github.com/ulisses-araujo09/sistema-cybercare.git'
        backup = 'https://github.com/ulissesoliveiraa/CYBERCARE.git'
    }
    foreach ($nomeCyberCare in @('origin', 'backup')) {
        $urlCyberCare = git remote get-url --push $nomeCyberCare
        if ($LASTEXITCODE -ne 0 -or $urlCyberCare -ne $destinosCyberCare[$nomeCyberCare]) {
            throw "O remote $nomeCyberCare não corresponde ao destino autorizado. Confira a configuração."
        }
    }
    $hashCyberCare = git rev-parse HEAD
    $falhasCyberCare = @()
    foreach ($nomeCyberCare in @('origin', 'backup')) {
        git push $nomeCyberCare HEAD:refs/heads/main
        if ($LASTEXITCODE -ne 0) { $falhasCyberCare += $nomeCyberCare; continue }
        $referenciaCyberCare = git ls-remote $nomeCyberCare refs/heads/main
        if ($LASTEXITCODE -ne 0 -or -not $referenciaCyberCare.StartsWith($hashCyberCare)) {
            $falhasCyberCare += $nomeCyberCare
        } else { Write-Host "$nomeCyberCare confirmado no commit $hashCyberCare" }
    }
    if ($falhasCyberCare.Count -gt 0) { throw "Publicação pendente em: $($falhasCyberCare -join ', '). Não houve force push." }
    Write-Host 'Repositório oficial e cópia sincronizados.'
} finally { Pop-Location }
