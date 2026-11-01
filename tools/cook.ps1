param([Parameter(Mandatory=$true)][string]$UnrealRoot)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$project=Join-Path $repo 'project/ProjectPBZ/ProjectPBZ.uproject'
$editor=Join-Path $UnrealRoot 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
$projectDir=Split-Path -Parent $project
& $editor $project -run=Cook -TargetPlatform=Windows "-CookDir=$projectDir/Content/Hcx2B" "-CookDir=$projectDir/Plugins/HuaShira/Content" "-CookDir=$projectDir/Content/PBZContent" -NoDefaultMaps -NoGameAlwaysCook -unattended -nullrhi -nosplash -stdout -FullStdOutLogOutput
if($LASTEXITCODE -ne 0){throw "Cook failed: $LASTEXITCODE"}
