from enum import Enum
import requests
import json
import os

from config import config_file as CFG
from src import logger as LOG


CLIENT_ID = CFG['twitch']['auth']['client_id']
CLIENT_SECRET = CFG['twitch']['auth']['client_secret']

TWITCH_AUTH_API = 'https://id.twitch.tv/oauth2'


class TokenType(Enum):
    BOT = 'bot'
    BROADCASTER = 'broadcaster'


class Token():
    def __init__(self, token_type: TokenType):
        try:
            with open(f'tokens/token_{token_type.value}.json') as file:
                token_file = json.load(file)
        except json.JSONDecodeError: # not readable
            LOG.logger.error("Unreadable file, removing bad file")
            if token_type == TokenType.BOT:
                LOG.logger.info("Run authorize.py to authorize your bot account then restart the bot")
            else:
                LOG.logger.info("Run authorize.py to authorize your streamer account then restart the bot")
            
            os.remove(f'tokens/token_{token_type.value}.json')
        except FileNotFoundError:
            if token_type == TokenType.BOT:
                LOG.logger.error("Missing bot token, run authorize.py to authorize your bot account then restart the bot")
            else:
                LOG.logger.error("Missing streamer token, run authorize.py to authorize your streamer account then restart the bot")

        self.access_token: str = token_file['access_token']
        self.refresh_token: str = token_file['refresh_token']
        self.token_type: TokenType = token_type

        # initial validation
        self.validate()
    
    def refresh(self):
        response = requests.post(
            url=f'{TWITCH_AUTH_API}/token', 
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }, 
            data=f"grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={self.refresh_token}"
        )

        match response.status_code:
            case 200:
                with open(f'tokens/token_{self.token_type.value}.json', 'w') as file:
                    file.write(response.text)
                LOG.logger.debug(f"Stored new token in token_{self.token_type.value}.json")
            case 400:
                LOG.logger.error("Invalid refresh token, run authorize.py")
                input()
            case _:
                LOG.logger.error(f"{response.status_code}: Unknown error")
                input()


    def validate(self) -> int:
        response = requests.get(
            url=f'{TWITCH_AUTH_API}/validate', 
            headers={
                "Authorization": f"OAuth {self.access_token}"
            }
        )

        match response.status_code:
            case 200:
                LOG.logger.info(f"{self.token_type.value.capitalize()} Token validated")
            case 401: # access token expired
                LOG.logger.info(f"{self.token_type} Token expired, refreshing...")

                self.refresh()
                with open(f'tokens/token_{self.token_type.value}.json', 'r') as file:
                    token = json.load(file)

                self.access_token = token['access_token']
            case _:
                LOG.logger.error(f"Unknown error validate_token: {response.status_code}: {response.text}")
                input()

        return response.status_code
    

    def get_access_token(self):
        return self.access_token
