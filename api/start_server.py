import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Environment variables ayarla
os.environ['SECRET_KEY'] = '18mart_portal_super_secret_key_2024'
os.environ['ALGORITHM'] = 'HS256'
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

print('Environment variables set:')
print(f'SECRET_KEY: {os.getenv("SECRET_KEY")}')
print(f'ALGORITHM: {os.getenv("ALGORITHM")}')
print(f'ACCESS_TOKEN_EXPIRE_MINUTES: {os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")}')

# Server'ı başlat
import uvicorn

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
