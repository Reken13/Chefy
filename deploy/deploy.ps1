<#
  Sube la carpeta projeto/ al servidor de la UA (carpeta de red) con robocopy.
  Se ejecuta en WINDOWS, desde la raiz del repositorio.

    .\deploy\deploy.ps1             # SIMULACRO: lista lo que copiaria, no toca nada
    .\deploy\deploy.ps1 -Executar   # copia de verdad

  Requisitos: tener acceso a la carpeta de red (VPN de la UA si estas fuera del campus
  y sesion iniciada en \\arca.ua.pt). El script NO guarda ni pide contrasenas.

  Seguridad del despliegue:
   - NO usa /MIR: nunca borra nada en el servidor (ni config.php ni ficheiros subidos).
   - NO copia config\config.php (tiene las credenciales de tu PC) ni .git.
   - NO copia docs, sql, tests ni uploads (la BD se importa a mano con phpMyAdmin).
#>
param([switch]$Executar)

$ErrorActionPreference = 'Stop'

$Origem  = (Resolve-Path (Join-Path $PSScriptRoot '..\projeto')).Path
$Destino = '\\arca.ua.pt\Hosting\esan-tesp-ds-paw.web.ua.pt\tesp-ds-g16\projeto'

if (-not (Test-Path $Destino)) {
    throw "No se puede acceder a $Destino . Comprueba la VPN de la UA y que has iniciado sesion en la carpeta de red."
}

$excluirFicheiros = @('config.php', '.gitignore', 'README.md')
$excluirPastas    = @('docs', 'sql', 'tests', 'uploads', '.git')

$opcoes = @($Origem, $Destino, '/E', '/R:2', '/W:2', '/NP', '/XF') + $excluirFicheiros + @('/XD') + $excluirPastas
if (-not $Executar) {
    $opcoes += '/L'    # /L = solo listar
    Write-Host '>>> SIMULACRO (no se copia nada). Usa -Executar para subir de verdad.' -ForegroundColor Yellow
}

robocopy @opcoes
$codigo = $LASTEXITCODE
# robocopy: 0-7 = correcto (con o sin ficheiros copiados); 8 o mas = error.
if ($codigo -ge 8) {
    throw "robocopy fallo con el codigo $codigo"
}

if ($Executar) {
    Write-Host 'Subida terminada.' -ForegroundColor Green
    if (-not (Test-Path (Join-Path $Destino 'config\config.php'))) {
        Write-Host 'AVISO: en el servidor falta config\config.php. Crealo a partir de config.example.php con los datos de la BD de la UA.' -ForegroundColor Yellow
    }
}
