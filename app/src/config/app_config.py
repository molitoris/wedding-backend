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

    def get_invitation_file_path(self):
        return self.invitation_data_output_path.joinpath(self.invitation_data_filename)

    def get_qr_code_output_path(self) -> pathlib.Path:
        return self.qr_code_output_path

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

    def get_file_path(self):
     return self.path.joinpath(self.filename).absolute()


class Config(BaseSettings):
    setup: Setup
    email: EmailSettings
    api: ApiSettings
    db: DatabaseSettings
    frontend_base_url: str


def load_config(data=None):

    if data is not None:
        return Config(**data)

    env = os.getenv("APP_ENV", "production")

    if env == 'production':
        file = pathlib.Path('./config/config.json')
    elif env == 'testing':
        file = pathlib.Path('./config/config_testing.json')

    if not file.exists():
        raise FileNotFoundError(f'Could not find config: {file}')

    with open(file=file, mode='r') as f:
        data = json.load(f)

    return Config(**data)
