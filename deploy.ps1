# Aegis // Shield Seed-V2 Deployment Script (PowerShell Version)
# Optimized for Google Cloud Run (WebSocket + Persistence)

$ProjectID = gcloud config get-value project
$ServerService = "aegis-server"
$ClientService = "aegis-client"
$Region = "us-central1"

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "AEGIS // INITIATING UNIFIED CLOUD DEPLOYMENT" -ForegroundColor Cyan
Write-Host "------------------------------------------------" -ForegroundColor Cyan

# 1. Enable APIs
Write-Host "[1/5] Ensuring Cloud APIs are enabled..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com

# 2. Deploy Server (Backend)
Write-Host "[2/5] Building & Deploying SERVER ($ServerService)..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$ProjectID/$ServerService" ./server
gcloud run deploy $ServerService `
    --image "gcr.io/$ProjectID/$ServerService" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --timeout 600 `
    --session-affinity `
    --set-env-vars="FIRESTORE_COLLECTION=aegis_sessions"

# 3. Deploy Client (Frontend)
Write-Host "[3/5] Building & Deploying CLIENT ($ClientService)..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$ProjectID/$ClientService" ./client
gcloud run deploy $ClientService `
    --image "gcr.io/$ProjectID/$ClientService" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated

# 4. Final Verification
$ServerURL = gcloud run services describe $ServerService --platform managed --region $Region --format 'value(status.url)'
$ClientURL = gcloud run services describe $ClientService --platform managed --region $Region --format 'value(status.url)'

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "AEGIS // DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
Write-Host "Backend Neural Link: $ServerURL" -ForegroundColor White
Write-Host "Frontend Dashboard: $ClientURL" -ForegroundColor White
Write-Host "------------------------------------------------" -ForegroundColor Cyan
