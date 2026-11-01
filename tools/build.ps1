param([Parameter(Mandatory=$true)][string]$UnrealRoot)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$project=Join-Path $repo 'project/ProjectPBZ/ProjectPBZ.uproject'
$batch=Join-Path $UnrealRoot 'Engine/Build/BatchFiles/Build.bat'
& $batch ProjectPBZEditor Win64 Development "-Project=$project" -WaitMutex -NoHotReloadFromIDE
if($LASTEXITCODE -ne 0){throw "Editor build failed: $LASTEXITCODE"}
