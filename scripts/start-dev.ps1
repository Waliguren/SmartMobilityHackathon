param(
    [switch]$UseDockerPostgres,
    [switch]$SkipDependencyInstall
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[smart-mobility] $Message" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-TcpPort {
    param(
        [string]$TargetHost,
        [int]$Port
    )

    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $async = $client.BeginConnect($TargetHost, $Port, $null, $null)
        $connected = $async.AsyncWaitHandle.WaitOne(1500, $false)
        if (-not $connected) {
            $client.Close()
            return $false
        }
        $client.EndConnect($async)
        $client.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Wait-ForPort {
    param(
        [string]$TargetHost,
        [int]$Port,
        [int]$TimeoutSeconds = 40
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-TcpPort -TargetHost $TargetHost -Port $Port) {
            return $true
        }
        Start-Sleep -Seconds 1
    }
    return $false
}

function Get-ShellExecutable {
    if (Test-Command -Name "pwsh") {
        return (Get-Command pwsh).Source
    }
    return (Get-Command powershell).Source
}

function Ensure-EnvFile {
    param(
        [string]$RepoRoot
    )

    $envPath = Join-Path $RepoRoot ".env"
    $templatePath = Join-Path $RepoRoot ".env.example"

    if (-not (Test-Path $envPath)) {
        Copy-Item $templatePath $envPath
        Write-Step "Creado .env a partir de .env.example"
    }
}

function Ensure-BackendEnvironment {
    param(
        [string]$BackendPath,
        [bool]$InstallDependencies
    )

    $venvPath = Join-Path $BackendPath ".venv"
    $activatePath = Join-Path $venvPath "Scripts\Activate.ps1"

    if (-not (Test-Command -Name "python")) {
        throw "No se ha encontrado python en PATH."
    }

    if (-not (Test-Path $venvPath)) {
        Write-Step "Creando entorno virtual del backend"
        & python -m venv $venvPath
    }

    if ($InstallDependencies) {
        Write-Step "Instalando dependencias del backend"
        & $activatePath
        & python -m pip install --upgrade pip
        & python -m pip install -e $BackendPath
    }
}

function Ensure-WebDependencies {
    param(
        [string]$WebPath,
        [bool]$InstallDependencies
    )

    if (-not (Test-Command -Name "npm")) {
        throw "No se ha encontrado npm en PATH."
    }

    if ($InstallDependencies) {
        Write-Step "Instalando dependencias de la web"
        Push-Location $WebPath
        try {
            & npm install
        }
        finally {
            Pop-Location
        }
    }
}

function Start-Postgres {
    param(
        [string]$RepoRoot,
        [bool]$ForceDocker
    )

    $dockerAvailable = Test-Command -Name "docker"
    $localPostgresAvailable = Test-TcpPort -TargetHost "127.0.0.1" -Port 5432

    if ($ForceDocker) {
        if (-not $dockerAvailable) {
            throw "Se ha pedido -UseDockerPostgres pero docker no esta disponible."
        }

        Write-Step "Arrancando PostgreSQL/PostGIS con docker compose"
        Push-Location $RepoRoot
        try {
            & docker compose up -d postgres
        }
        finally {
            Pop-Location
        }

        if (-not (Wait-ForPort -TargetHost "127.0.0.1" -Port 5432)) {
            throw "PostgreSQL no ha quedado accesible en el puerto 5432."
        }
        return
    }

    if ($localPostgresAvailable) {
        Write-Step "Detectado PostgreSQL escuchando en localhost:5432"
        return
    }

    if ($dockerAvailable) {
        Write-Step "No hay PostgreSQL local. Arrancando PostgreSQL/PostGIS con docker compose"
        Push-Location $RepoRoot
        try {
            & docker compose up -d postgres
        }
        finally {
            Pop-Location
        }

        if (-not (Wait-ForPort -TargetHost "127.0.0.1" -Port 5432)) {
            throw "PostgreSQL no ha quedado accesible en el puerto 5432."
        }
        return
    }

    throw "No hay PostgreSQL local en 5432 y docker no esta disponible. Inicia PostgreSQL/PostGIS manualmente o instala Docker."
}

function Start-NewTerminal {
    param(
        [string]$ShellExe,
        [string]$Title,
        [string]$Command
    )

    Start-Process -FilePath $ShellExe -ArgumentList @(
        "-NoExit",
        "-Command",
        "`$Host.UI.RawUI.WindowTitle = '$Title'; $Command"
    ) | Out-Null
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $repoRoot "backend\api"
$webPath = Join-Path $repoRoot "apps\manager-web"
$activatePath = Join-Path $backendPath ".venv\Scripts\Activate.ps1"
$shellExe = Get-ShellExecutable

Write-Step "Preparando entorno"
Ensure-EnvFile -RepoRoot $repoRoot

$installBackendDeps = (-not $SkipDependencyInstall) -and (-not (Test-Path (Join-Path $backendPath ".venv")))
$installWebDeps = (-not $SkipDependencyInstall) -and (-not (Test-Path (Join-Path $webPath "node_modules")))

Start-Postgres -RepoRoot $repoRoot -ForceDocker:$UseDockerPostgres
Ensure-BackendEnvironment -BackendPath $backendPath -InstallDependencies:$installBackendDeps
Ensure-WebDependencies -WebPath $webPath -InstallDependencies:$installWebDeps

$backendCommand = @"
Set-Location '$backendPath'
& '$activatePath'
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@

$webCommand = @"
Set-Location '$webPath'
npm run dev -- --host 0.0.0.0 --port 5173
"@

Write-Step "Abriendo terminal del backend"
Start-NewTerminal -ShellExe $shellExe -Title "Smart Mobility Backend" -Command $backendCommand

Write-Step "Abriendo terminal de la web"
Start-NewTerminal -ShellExe $shellExe -Title "Smart Mobility Manager Web" -Command $webCommand

Write-Host "" 
Write-Host "Servicios lanzados:" -ForegroundColor Green
Write-Host "  Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "  Swagger: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Health:  http://localhost:8000/api/v1/health" -ForegroundColor Green
Write-Host "  Web:     http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Uso recomendado:" -ForegroundColor Yellow
Write-Host "  pwsh -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1"
Write-Host ""
Write-Host "Opciones:" -ForegroundColor Yellow
Write-Host "  -UseDockerPostgres       Fuerza postgres por docker compose"
Write-Host "  -SkipDependencyInstall   No ejecuta instalaciones aunque falten dependencias"