# ClipGod - Automated Video Clipping SaaS

ClipGod is an advanced, production-ready full-stack application that ingests long-form videos (via URL or direct upload), transcribes them, analyzes for viral highlights, and formats them into engaging short-form vertical clips (9:16) for TikTok, Reels, and YouTube Shorts with custom captions and templates.

## Project Structure
- `backend/`: FastAPI Python backend with yt-dlp, FFmpeg integration, and REST API.
- `frontend/`: React + Vite + Tailwind CSS frontend with a modern dark-mode glassmorphism interface.

## Quick Start
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
