#!/bin/bash
# Aegis // Shield Seed-V2 Unified Deployment Script
# Optimized for Google Cloud Run (WebSocket + Persistence)

PROJECT_ID=$(gcloud config get-value project)
SERVER_SERVICE="aegis-server"
CLIENT_SERVICE="aegis-client"
REGION="us-central1"

echo "------------------------------------------------"
echo "AEGIS // INITIATING UNIFIED CLOUD DEPLOYMENT"
echo "------------------------------------------------"

# 1. Enable APIs
echo "[1/5] Ensuring Cloud APIs are enabled..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com

# 2. Deploy Server (Backend)
echo "[2/5] Building & Deploying SERVER ($SERVER_SERVICE)..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVER_SERVICE ./server
gcloud run deploy $SERVER_SERVICE \
    --image gcr.io/$PROJECT_ID/$SERVER_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --timeout 600 \
    --session-affinity \
    --set-env-vars="FIRESTORE_COLLECTION=aegis_sessions"

# 3. Deploy Client (Frontend)
echo "[3/5] Building & Deploying CLIENT ($CLIENT_SERVICE)..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$CLIENT_SERVICE ./client
gcloud run deploy $CLIENT_SERVICE \
    --image gcr.io/$PROJECT_ID/$CLIENT_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated

# 4. Final Verification
SERVER_URL=$(gcloud run services describe $SERVER_SERVICE --platform managed --region $REGION --format 'value(status.url)')
CLIENT_URL=$(gcloud run services describe $CLIENT_SERVICE --platform managed --region $REGION --format 'value(status.url)')

echo "------------------------------------------------"
echo "AEGIS // DEPLOYMENT SUCCESSFUL"
echo "Backend Neural Link: $SERVER_URL"
echo "Frontend Dashboard: $CLIENT_URL"
echo "------------------------------------------------"
