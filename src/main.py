import uvicorn

from src.routes.v1 import app_v1

if __name__ == '__main__':
    uvicorn.run(app=app_v1, host='0.0.0.0', port=8000)
