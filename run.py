import sys
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    # Check if we're in the correct virtual environment
    if not os.path.exists("venv") and "VIRTUAL_ENV" not in os.environ:
        print("Warning: Not running in a virtual environment.")
        print("Please activate your virtual environment first:")
        print("  source venv/bin/activate  (on Linux/macOS)")
        print("  venv\\Scripts\\activate    (on Windows)")
        print("Then install dependencies with:")
        print("  pip install -r requirements.txt")
    
    # Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    # Run the FastAPI app with uvicorn
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=True,  # Enable hot reloading for development
            log_level="info"
        )
    except ModuleNotFoundError as e:
        print(f"Module not found: {e}")
        print("Please make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)