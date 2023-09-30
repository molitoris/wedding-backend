import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import pathlib
import json

class Setup(BaseModel):
    guest_list_filepath: pathlib.Path
    guest_registration_endpoint: str
    qr_code_output_path: pathlib.Path
    
    invitation_token_size: int
    invitation_data_filename: str
    invitation_data_output_path: pathlib.Path

class EmailSettings(BaseModel):
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

class ApiSettings(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

class DatabaseSettings(BaseModel):
    path: pathlib.Path
    filename: str


class Config(BaseSettings):
    setup: Setup
    email: EmailSettings
    api: ApiSettings
    db: DatabaseSettings
    frontend_base_url: str

if os.environ.get('mode', 'production') == 'production':
    file = pathlib.Path('/config/config.json')
else:
    file = pathlib.Path('/config/config_dev.json')

if not file.exists():
    raise FileNotFoundError(f'Could not find config: {file}')

with open(file=file, mode='r') as f:
    data = json.load(f)

config = Config(**data)

if __name__ == '__main__':
    print(config.model_dump())