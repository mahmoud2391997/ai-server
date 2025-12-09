import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Disable proxy for edge_tts and external API calls before importing app
# This must be done before edge_tts initializes its HTTP client
os.environ.setdefault('NO_PROXY', '*')
os.environ.setdefault('no_proxy', '*')
# Unset proxy variables to prevent httpx/requests from using them
for proxy_var in ['HTTP_PROXY', 'http_proxy', 'HTTPS_PROXY', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(proxy_var, None)

from app.main import app

if __name__ == "__main__":
    import logging
    # Configure logging to show INFO level and above
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )