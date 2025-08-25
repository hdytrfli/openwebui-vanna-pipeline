import os
import uvicorn

DEBUG = os.environ.get("DEBUG", False)
PORT = int(os.environ.get("PORT", 4321))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        reload=DEBUG,
        port=PORT,
    )
