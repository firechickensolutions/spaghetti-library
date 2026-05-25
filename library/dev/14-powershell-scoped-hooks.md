# Scoped PowerShell Hooks

**Language(s):** PowerShell

**Rework-prevention rationale:** Prevents untestable coupling and complexity underestimation by isolating shell preferences, location changes, and native executable failure checks inside the hook boundary so the calling process state is not mutated.

**Canonical source:** Don Jones, Richard Siddaway, and Jeffery Hicks, *PowerShell in Depth, Second Edition*, Manning (chapters on errors, scopes, and providers); Microsoft, *PowerShell Documentation*, `about_Automatic_Variables`, `about_Preference_Variables`, `Push-Location`, `Pop-Location` (learn.microsoft.com/powershell).

## Trigger condition

Halt and read this entry when writing a PowerShell hook that changes `$ErrorActionPreference`, changes directories, calls native executables, or checks command success with `$?`.

## Before

```powershell
$ErrorActionPreference = "Stop"   # mutates caller's global preference
cd C:\work\repo                   # mutates caller's working directory

npm run build

if ($?) {                         # $? checks the last cmdlet, not the native executable
    Write-Host "ok"
}
```

## After

```powershell
param (
    [Parameter(Mandatory = $true)]
    [string]$WorkspacePath
)

Set-StrictMode -Version Latest

$savedPreference = $ErrorActionPreference
$ErrorActionPreference = "Stop"
Push-Location $WorkspacePath -StackName "ForgeHookStack"

try {
    & npm run build 2>&1

    if ($LASTEXITCODE -ne 0) {
        throw "npm run build failed with exit code $LASTEXITCODE"
    }

    Write-Verbose "Build succeeded."
}
catch {
    $err = $_    # clone immediately: subsequent commands overwrite $_
    Write-Error "Hook failed: $($err.Exception.Message)"
    exit 1
}
finally {
    Pop-Location -StackName "ForgeHookStack"
    $ErrorActionPreference = $savedPreference
}
```

**Critical distinctions:**

| Pattern | What it checks | Correct for |
|---|---|---|
| `$?` | Last PowerShell cmdlet pipe success | Cmdlets (`Get-Item`, `Copy-Item`, etc.) |
| `$LASTEXITCODE` | Exit code of the last native executable | `node`, `npm`, `git`, `gcc`, compiled tools |
| `$ErrorActionPreference = "Stop"` | Converts non-terminating PS errors to terminating | Must be scoped: save and restore in `finally` |
| `Push-Location` / `Pop-Location` | Manages working directory as a stack | Any hook that must `cd` without mutating the caller |

**`$_` clone rule:** inside a `catch` block, assign `$_ ` to a local variable immediately. Any subsequent PowerShell command (including `Write-Error`) can overwrite `$_` with a new error object, hiding the original exception.

**Fail-open hooks:** if the hook is advisory (logging, telemetry, non-blocking), end with `exit 0` in the `finally` block regardless of errors. If the hook is a gate (must block on failure), rethrow or `exit 1`.
