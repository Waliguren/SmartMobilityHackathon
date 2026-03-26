param(
    [switch]$UseDockerPostgres,
    [switch]$SkipDependencyInstall
)

$ErrorActionPreference = "Stop"
$script:ResolvedDatabaseUrl = $null
$script:DatabaseModeLabel = "postgres"
$script:UseDockerForWeb = $false

function Write-Step {
    param([string]$Message)
    Write-Host "[smart-mobility] $Message" -ForegroundColor Cyan
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[smart-mobility] $Message" -ForegroundColor Yellow
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
        if (-not $InstallDependencies) {
            Write-Warn "No existe backend\\api\\.venv. Se ignorara -SkipDependencyInstall para preparar el backend."
            $InstallDependencies = $true
        }
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

    $npmAvailable = Test-Command -Name "npm"
    $dockerAvailable = Test-Command -Name "docker"
    $nodeModulesPath = Join-Path $WebPath "node_modules"

    if (-not $npmAvailable) {
        if (-not $dockerAvailable) {
            throw "No se ha encontrado npm en PATH ni Docker disponible. Instala Node.js o Docker."
        }
        Write-Warn "npm no encontrado en PATH. Se usara Docker para las dependencias y dev server."
        $script:UseDockerForWeb = $true
        return
    }

    if ((-not $InstallDependencies) -and (-not (Test-Path $nodeModulesPath))) {
        Write-Warn "No existe apps\\manager-web\\node_modules. Se ignorara -SkipDependencyInstall para preparar la web."
        $InstallDependencies = $true
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

function Get-LocalPostgresService {
    $serviceNames = @("postgresql*", "postgres*", "pgsql*")
    $services = @(Get-Service -Name $serviceNames -ErrorAction SilentlyContinue)
    if ($services.Count -gt 0) {
        return $services[0]
    }

    return $null
}

function Ensure-LocalPostgres {
    $localPostgresAvailable = Test-TcpPort -TargetHost "127.0.0.1" -Port 5432
    if ($localPostgresAvailable) {
        Write-Step "Detectado PostgreSQL escuchando en localhost:5432"
        return $true
    }

    $service = Get-LocalPostgresService
    if ($null -eq $service) {
        return $false
    }

    if ($service.Status -ne "Running") {
        Write-Step "Intentando arrancar el servicio local de PostgreSQL: $($service.Name)"
        Start-Service -Name $service.Name
    }

    if (Wait-ForPort -TargetHost "127.0.0.1" -Port 5432) {
        Write-Step "PostgreSQL local arrancado mediante servicio de Windows"
        return $true
    }

    return $false
}

function Get-SqliteDatabaseUrl {
    param(
        [string]$RepoRoot
    )

    $sqlitePath = Join-Path $RepoRoot "backend\api\smartmobility-dev.db"
    $normalized = $sqlitePath.Replace("\", "/")
    return "sqlite:///$normalized"
}

function Start-Postgres {
    param(
        [string]$RepoRoot,
        [bool]$ForceDocker
    )

    $dockerAvailable = Test-Command -Name "docker"
    $localPostgresAvailable = Ensure-LocalPostgres

    if ($ForceDocker) {
        if (-not $dockerAvailable) {
            if ($localPostgresAvailable) {
                Write-Step "Docker no esta disponible. Se usara PostgreSQL local en su lugar"
                return
            }

            $script:ResolvedDatabaseUrl = Get-SqliteDatabaseUrl -RepoRoot $RepoRoot
            $script:DatabaseModeLabel = "sqlite"
            Write-Warn "Se ha pedido -UseDockerPostgres pero no hay Docker ni PostgreSQL local. Se usara SQLite solo para desarrollo."
            return
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

    $script:ResolvedDatabaseUrl = Get-SqliteDatabaseUrl -RepoRoot $RepoRoot
    $script:DatabaseModeLabel = "sqlite"
    Write-Warn "No hay PostgreSQL local ni Docker. Se usara SQLite solo para desarrollo."
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
if ('$($script:ResolvedDatabaseUrl)' -ne '') { `$env:DATABASE_URL = '$($script:ResolvedDatabaseUrl)' }
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@

if ($script:UseDockerForWeb) {
    $webCommand = @"
Set-Location '$repoRoot'
docker compose up manager-web
"@
    Write-Step "Docker sera usado para la web (Node.js no esta instalado localmente)"
} else {
    $webCommand = @"
Set-Location '$webPath'
npm run dev -- --host 0.0.0.0 --port 5173
"@
}

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
Write-Host "  DB mode: $script:DatabaseModeLabel" -ForegroundColor Green
Write-Host ""
Write-Host "Uso recomendado:" -ForegroundColor Yellow
Write-Host "  pwsh -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1"
Write-Host ""
Write-Host "Opciones:" -ForegroundColor Yellow
Write-Host "  -UseDockerPostgres       Fuerza postgres por docker compose"
Write-Host "  -SkipDependencyInstall   No ejecuta instalaciones aunque falten dependencias"