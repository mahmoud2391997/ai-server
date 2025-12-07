# Aura AI Server

FastAPI server for handling all AI features in the Aura perfume application.

## Setup

### Prerequisites
Install Python 3.11 (recommended for compatibility):
```bash
brew install python@3.11
```

### Installation
1. Remove existing venv and create new one:
```bash
cd ai-server
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
```

2. Upgrade pip and install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the server:
```bash
python run.py
```

### Quick Fix for Current Issue
If you're still having issues, try:
```bash
deactivate
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python run.py
```

The server will run on `http://localhost:8000`

## Deployment to Vercel

This application is configured for deployment on Vercel.

### Prerequisites
- A Vercel account
- Vercel CLI installed (optional): `npm i -g vercel`

### Deployment Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Deploy from command line**:
   ```bash
   vercel
   ```
   Follow the prompts to link your project or create a new one.

3. **Or deploy via Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your Git repository
   - Vercel will automatically detect the Python project and use the `vercel.json` configuration

4. **Set Environment Variables** (optional but recommended):
   In your Vercel project settings, add these environment variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (optional)

   If not set, the app will use default values from the code.

5. **Deploy**:
   - Vercel will automatically build and deploy your application
   - Your API will be available at `https://your-project.vercel.app`

### Project Structure for Vercel
- `vercel.json`: Vercel configuration file
- `api/index.py`: Entry point for Vercel serverless functions
- `app/`: Main application code
- `.vercelignore`: Files to exclude from deployment

## API Endpoints

- **AI Nose**: `POST /api/ai-nose/analyze`
- **Mood Advisor**: `POST /api/mood-advisor/analyze`
- **Skin Analyzer**: `POST /api/skin-analyzer/analyze`
- **Occasion Detector**: `POST /api/occasion-detector/analyze`
- **Style Matcher**: `POST /api/style-matcher/analyze`
- **Longevity Meter**: `POST /api/longevity-meter/analyze`
- **Perfume Memory**: `POST /api/perfume-memory/analyze`
- **Personality Map**: `POST /api/personality-map/analyze`
- **Gift Selector**: `POST /api/gift-selector/analyze`
- **Description Generator**: `POST /api/description-generator/generate`
- **Bottle Renderer**: `POST /api/bottle-renderer/render`
- **Price Optimizer**: `POST /api/price-optimizer/optimize`

## Request Format

```json
{
  "text": "User input text",
  "user_id": "optional_user_id"
}
```

## Response Format

```json
{
  "result": "AI analysis result",
  "confidence": 0.95,
  "recommendations": ["recommendation1", "recommendation2"]
}
```