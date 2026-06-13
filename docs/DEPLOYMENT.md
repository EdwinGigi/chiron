# Deployment Guide

This guide explains how to deploy Chiron as a production GitHub App webhook server.

## Overview

Chiron is a FastAPI application. It is stateless (outside of the task queue, if implemented), meaning it scales very well in serverless or containerized environments.

## Option 1: Google Cloud Run (Recommended)

Google Cloud Run is an ideal host for Chiron because it scales to zero (cost-effective) and natively supports Docker containers.

1. **Build the Container**:
   Use the included `Dockerfile` to build the image.
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/chiron
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy chiron \
     --image gcr.io/YOUR_PROJECT_ID/chiron \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-secrets="GITHUB_APP_ID=github_app_id:latest,GITHUB_WEBHOOK_SECRET=webhook_secret:latest,GEMINI_API_KEY=gemini_api_key:latest"
   ```

3. **Update GitHub App**:
   Take the URL provided by Cloud Run and update your GitHub App's Webhook URL (append `/webhooks/github`).

## Option 2: Render / Railway

For an easier PaaS deployment without managing GCP projects:

1. Connect your GitHub repository to Render or Railway.
2. Select **Dockerfile** as the environment.
3. Add the necessary Environment Variables (`GITHUB_APP_ID`, `GITHUB_WEBHOOK_SECRET`, `GITHUB_PRIVATE_KEY_PATH` (or base64 encoded private key), `GEMINI_API_KEY`).
4. Set the start command (handled by Dockerfile by default, but essentially `uvicorn chiron.main:app --host 0.0.0.0 --port $PORT`).

## Managing the Private Key

Since the GitHub App Private Key is a `.pem` file, it can be tricky to pass as an environment variable. 
A common pattern is to base64 encode the `.pem` file, store it in an environment variable `GITHUB_PRIVATE_KEY_B64`, and have Chiron decode it on startup, or simply mount it as a secret volume in Cloud Run/Kubernetes.
