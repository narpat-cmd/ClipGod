# ClipGod - Free Cloud Deployment Guide

## 1. Push to GitHub
cd E:\ClipGod
git add .
git commit -m "Initial ClipGod release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ClipGod.git
git push -u origin main

## 2. Deploy Backend Free on Render
1. Go to https://render.com -> New -> Blueprint (or Web Service).
2. Connect your ClipGod GitHub repo.
3. Render auto-detects backend/render.yaml & backend/Dockerfile.
4. Click Deploy and copy your live backend URL (e.g. https://clipgod-backend.onrender.com).

## 3. Deploy Frontend Free on Vercel
1. Go to https://vercel.com -> Add New Project -> Import ClipGod.
2. Set Root Directory to frontend.
3. Click Deploy - live in ~15 seconds.
4. Open your live Vercel site and paste your Render Backend URL in the top-right box.
