# Rebuild workflow.json, import it and publish it. Restart n8n afterwards so webhooks reload.
$env:Path = 'C:\Program Files\nodejs;' + $env:APPDATA + '\npm;' + $env:Path
$env:N8N_DIAGNOSTICS_ENABLED = 'false'
Push-Location $PSScriptRoot
try {
    python build_workflow.py
    # Unpublish first: importing over a published workflow leaves the old version active.
    n8n unpublish:workflow --id=ticketTriageDemo1
    n8n import:workflow --input=workflow.json
    n8n publish:workflow --id=ticketTriageDemo1
}
finally {
    Pop-Location
}
