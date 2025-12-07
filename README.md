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