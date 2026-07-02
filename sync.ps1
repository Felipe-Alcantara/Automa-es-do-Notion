# Sincroniza os módulos do ecossistema e verifica o workspace.
# Uso: .\sync.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Sincronizando modulos..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python bootstrap.py
$bootstrap_exit = $LASTEXITCODE

if ($bootstrap_exit -ne 0) {
    Write-Host ""
    Write-Host "Erro no bootstrap. Abortando." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Verificando workspace..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python check-dev.py
$check_exit = $LASTEXITCODE

if ($check_exit -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "Tudo sincronizado e pronto!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    exit 0
} else {
    exit $check_exit
}
