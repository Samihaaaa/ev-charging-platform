"""
Minimal FastAPI app to test basic connectivity without database operations.
This helps isolate whether the issue is with FastAPI itself or database operations.
"""

from fastapi import FastAPI

# Create minimal app without database operations
app = FastAPI(title="Minimal Test API")

@app.get("/")
def root():
    return {"message": "Minimal API running - no database"}

@app.get("/health")
def health():
    return {"status": "healthy", "database": "disconnected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
