param(
  [string]$Source = "z_files/tests_results/backend.log",
  [string]$Target = "z_files/tests_results/backend_clean.log"
)

$content = Get-Content $Source -ErrorAction Stop
$cleaned = $content | ForEach-Object { $_ -replace "`e\[[0-9;]*[A-Za-z]", "" }
$cleaned | Set-Content $Target

Write-Host "Clean log written to $Target"
