import sys
import uvicorn

sys.path.append('/workspaces/wedding-api/app')

from src.routes.v1 import app_v1

if __name__ == '__main__':
    uvicorn.run(app=app_v1, host='0.0.0.0', port=8000)