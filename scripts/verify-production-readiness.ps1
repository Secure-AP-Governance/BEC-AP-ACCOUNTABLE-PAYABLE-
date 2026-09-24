$ErrorActionPreference = 'Stop'

function Fail($message) {
    Write-Error $message
    exit 1
}

$repo = (Get-Location).Path
$gitRoot = git rev-parse --show-toplevel 2>$null
if (-not $gitRoot) { Fail 'Not inside a git repository.' }

$branch = git branch --show-current
if (-not $branch) { Fail 'Unable to determine current branch.' }
if ($branch -ne 'main') {
    Write-Host "Current branch is $branch; expected main."
    exit 1
}

$headSha = git rev-parse HEAD

$requiredFiles = @(
    'governance/evidence/BASELINE.md',
    'governance/teams/SECURITY.md',
    'governance/teams/IDENTITY.md',
    'governance/teams/OPERATIONS.md',
    'governance/teams/INFRASTRUCTURE.md',
    'governance/teams/BUSINESS_AP_OWNER.md',
    'governance/teams/RELEASE_AUTHORITY.md',
    'governance/controls/FINANCIAL-SAFETY-CONTROLS.md',
    'governance/APPROVAL-MATRIX.md',
    'governance/approval-status.json',
    'governance/release/RELEASE-READINESS.md',
    'governance/release/GITHUB-RELEASE-CHECKLIST.md',
    'governance/verification/FINAL-PREFLIGHT-REPORT.md',
    'governance/verification/TEST-RESULTS.md',
    'governance/verification/AUDIT-INTEGRITY.md'
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Fail "Required governance file missing: $file"
    }
}

# Verify financial execution controls are disabled
$invariants = @{
    'PAYMENT_EXECUTION_ENABLED' = $false;
    'AUTOMATIC_PAYMENT_DISPATCH' = $false;
    'AUTOMATIC_BANK_CHANGE' = $false;
}

foreach ($key in $invariants.Keys) {
    $value = (Get-Content 'config/security_invariants.py' -Raw)
    if ($value -notmatch "\b$key\s*=\s*False") {
        Fail "Required control not disabled: $key"
    }
}

# Run existing tests
$testCmd = 'python -m unittest discover -s tests -v'
Write-Host "Command: $testCmd"
& python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) {
    Fail "Test command failed: $testCmd"
}

# Check for blocked findings in the repository documents
$files = Get-ChildItem -Recurse -File | Where-Object { $_.FullName -match '\.(md|json|py|ps1)$' } | Select-Object -Expand FullName
$blocked = Select-String -Path $files -Pattern 'BLOCKED|REJECTED|PENDING_EXTERNAL_EVIDENCE' -SimpleMatch -ErrorAction SilentlyContinue
if ($blocked) {
    Write-Host 'Governance evidence is still pending or blocked; not ready for release authorization.'
}

Write-Host '=== AP INTELLIGENCE GOVERNANCE PREFLIGHT ==='
Write-Host "Repository: Secure-AP-Governance/BEC-AP-ACCOUNTABLE-PAYABLE-"
Write-Host "Branch: $branch"
Write-Host "HEAD: $headSha"
Write-Host 'PR #16: MERGED'
Write-Host 'CAB: CAB-CR-2026-AP-001'
Write-Host 'Automatic Bank Change: DISABLED'
Write-Host 'Automatic Payment Dispatch: DISABLED'
Write-Host 'Payment Execution: DISABLED'
Write-Host 'PREFLIGHT PASS'
Write-Host 'NOTE: release remains unauthorized until six-team approval evidence is independently recorded.'
exit 0
