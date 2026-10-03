@echo off
rem Start n8n locally for the ticket triage demo. UI: http://localhost:5678
set "PATH=C:\Program Files\nodejs;%APPDATA%\npm;%PATH%"
set N8N_DIAGNOSTICS_ENABLED=false
set N8N_VERSION_NOTIFICATIONS_ENABLED=false
set N8N_TEMPLATES_ENABLED=false
set N8N_PERSONALIZATION_ENABLED=false
set N8N_HOST=localhost
set N8N_PORT=5678
set GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
n8n start
