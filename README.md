# Target Clicker Game

A real-time target clicking game built with React, TypeScript, and Flask.

## Development Setup

1. Install backend dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
npm install
```

3. Start the Flask backend:
```bash
python app.py
```

4. Start the Vite development server:
```bash
npm run dev
```

## Deployment Instructions

### Backend Deployment (Railway)

1. Create a Railway account at https://railway.app
2. Install the Railway CLI and login:
```bash
npm i -g @railway/cli
railway login
```

3. Create a new project:
```bash
railway init
```

4. Add PostgreSQL:
- Go to your project in Railway dashboard
- Click "New" and select "Database" -> "PostgreSQL"
- Railway will automatically add the DATABASE_URL to your environment variables

5. Deploy the backend:
```bash
railway up
```

6. Note down your Railway deployment URL (e.g., https://your-app.railway.app)

### Frontend Deployment (Vercel)

1. Create a Vercel account at https://vercel.com
2. Install the Vercel CLI and login:
```bash
npm i -g vercel
vercel login
```

3. Create a .env.production file with your Railway backend URL:
```
VITE_API_URL=https://your-app.railway.app
```

4. Deploy to Vercel:
```bash
vercel
```

5. Follow the prompts to deploy your project

## Environment Variables

### Backend (Railway)
- `DATABASE_URL`: Automatically set by Railway when adding PostgreSQL

### Frontend (Vercel)
- `VITE_API_URL`: Your Railway backend URL

## Features
- Real-time target clicking game
- Moving targets that get smaller and faster as score increases
- Global leaderboard with top scores
- Responsive design
- Error handling and loading states