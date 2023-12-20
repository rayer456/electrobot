import os
import socket
import requests
import webbrowser
import json
import tomli_w

from src import logger as LOG
from src import TokenType
from config import config_file as CFG


HOST = CFG['socket']['host']
PORT = CFG['socket']['port']
CLIENT_ID = CFG['twitch']['auth']['client_id']
CLIENT_SECRET = CFG['twitch']['auth']['client_secret']
REDIRECT_URI = CFG['twitch']['auth']['redirect_uri']
BOT_SCOPE = CFG['twitch']['scopes']['bot_scope']
BROAD_SCOPE = CFG['twitch']['scopes']['broad_scope']
CHANNEL = CFG['twitch']['info']['channel'].lower()

TOKEN_URL = 'https://id.twitch.tv/oauth2/token'
AUTHORIZE_URL = 'https://id.twitch.tv/oauth2/authorize'
TWITCH_API = 'https://api.twitch.tv/helix'


def get_code(type_token: TokenType):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        LOG.logger.debug(f"Authorize: Listening on {HOST} on port {PORT}")

        if type_token == TokenType.BOT:
            authorize(BOT_SCOPE)
        elif type_token == TokenType.BROADCASTER:
            authorize(BROAD_SCOPE)
        LOG.logger.info("Browser opened, displaying authorization page")

        conn = sock.accept()[0] # blocking socket
        with conn:
            while True:
                data = conn.recv(1024).decode('utf-8') # waiting
                if not data:
                    LOG.logger.error("Connection dropped?")
                    break

                conn.send('HTTP/1.0 200 OK\n'.encode('utf-8'))
                conn.send('Content-Type: text/html\n'.encode('utf-8'))
                conn.send('\n'.encode('utf-8'))
                conn.send("""
                    <html>
                    <body>
                    <h1>You can close this tab</h1>
                    </body>
                    </html>
                """.encode('utf-8'))
                
                # grab parameters
                y = data.splitlines()[0].split()[1] 
                if y[y.find('?')+1:y.find('=')] == "error":
                    LOG.logger.error(f'Message: {y}')
                    input()
                    exit()
                else:
                    secret = y[y.find('=')+1:y.find('&')]
                    
                LOG.logger.info("Authorized")
                get_token(secret, type_token)
                break


def authorize(scope):
    link = f'{AUTHORIZE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={scope}&force_verify=true'
    webbrowser.open(link)


def get_token(code: str, type_token: TokenType):
    response = requests.post(
        url=TOKEN_URL, 
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        }, 
        data=f'client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={REDIRECT_URI}',
    )
    LOG.logger.info("Token requested...")

    match response.status_code:
        case 200:
            if not os.path.exists('tokens'):
                os.makedirs('tokens')

            with open(f'tokens/token_{type_token.value}.json', 'w') as file: 
                file.write(response.text)

            if type_token == TokenType.BROADCASTER:
                data = json.loads(response.text)
                set_channel_id(data['access_token'])

            LOG.logger.info("Stored tokens")
            print("\n[+] All done!")
        case 400:
            LOG.logger.error(f"Token {response.status_code}: {response.text}")
        case 403:
            LOG.logger.error("Token: Invalid client secret")
        case _:
            LOG.logger.error(f"Token {response.status_code}: {response.text}")


def set_channel_id(access_token):
    response = requests.get(
        url=f'{TWITCH_API}/users?login={CHANNEL}', 
        headers={
            "Authorization": f"Bearer {access_token}", 
            "Client-Id": f"{CLIENT_ID}"
        }
    )

    match response.status_code:
        case 200:
            data = json.loads(response.text)
            CFG['twitch']['info']['channel_id'] = data['data'][0]['id']

            with open('config/config.toml', 'wb') as file:
                tomli_w.dump(CFG ,file)
        case _:
            LOG.logger.error(f'set_channel_id: {response.status_code}: {response.text}')


if __name__ == "__main__":
    print('[+] This script will open your browser to authorize a bot or streamer Twitch account.')
    print('[+] Run this script twice to authorize both a bot/streamer account, both are necessary.\n')

    print('[+] Make sure you are logged in on the correct account each time\n')

    print("[+] Type 'bot' to authorize your bot account")
    print("[+] This account will be used to type in chat\n")

    print("[+] Type 'streamer' to authorize your streamer account")
    print("[+] This is necessary for the prediction functionalities\n")

    choice = ''
    while choice not in ['bot', 'streamer']:
        choice = input("[+] bot or streamer?\t")

    if choice == 'bot':
        get_code(TokenType.BOT)
    else:
        get_code(TokenType.BROADCASTER)
    input()