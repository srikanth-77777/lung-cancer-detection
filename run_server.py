import os
from dotenv import load_dotenv

# Download model weights from cloud storage if not present locally
from download_models import ensure_models
ensure_models()

from waitress import serve
from app import app

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Read host and port from environment or default
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    
    print(f"================================================================")
    print(f"Starting Production WSGI Server (Waitress)...")
    print(f"Application: Lung Cancer AI Diagnostic System")
    print(f"Address: http://{host}:{port}")
    print(f"================================================================")
    
    # Run the Waitress WSGI server (1 thread to save RAM)
    serve(app, host=host, port=port, threads=1)
