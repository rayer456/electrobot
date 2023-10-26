import os
import socket
import requests
import webbrowser
import json
import tomli_w
from config import config_file as CFG
import logger as LOG


HOST = CFG['socket']['HOST']
PORT = CFG['socket']['PORT']
CLIENT_ID = CFG['auth']['CLIENT_ID']
CLIENT_SECRET = CFG['auth']['CLIENT_SECRET']
REDIRECT_URI = CFG['auth']['REDIRECT_URI']
BOT_SCOPE = CFG['scopes']['BOT_SCOPE']
BROAD_SCOPE = CFG['scopes']['BROAD_SCOPE']
CHANNEL = CFG['irc']['CHANNEL']

TOKEN_URL = 'https://id.twitch.tv/oauth2/token'
AUTHORIZE_URL = 'https://id.twitch.tv/oauth2/authorize'
TWITCH_API = 'https://api.twitch.tv/helix'


def get_code(type_token):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        LOG.logger.debug(f"Authorize: Listening on {HOST} on port {PORT}")

        if type_token == 'bot':
            authorize(BOT_SCOPE)
        else: #broad
            authorize(BROAD_SCOPE)
        LOG.logger.info("Browser opened, displaying authorization page")

        conn = sock.accept()[0] #blocking socket
        with conn:
            while True:
                data = conn.recv(1024).decode('utf-8') #waiting
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
                else:
                    secret = y[y.find('=')+1:y.find('&')]
                    
                LOG.logger.info("Authorized")
                get_token(secret, type_token)
                break


def authorize(scope):
    link = f'{AUTHORIZE_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={scope}&force_verify=true'
    webbrowser.open(link)


def get_token(code, type_token):
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

            with open(f'tokens/token_{type_token}.json', 'w') as file: 
                file.write(response.text)

            if type_token == 'broad':
                data = json.loads(response.text)
                set_channel_id(data['access_token'])

            LOG.logger.info("Stored tokens")
            print("\n[+] All done!")
        case 400:
            LOG.logger.error("Token: Invalid client_id or code or grant_type")
        case 403:
            LOG.logger.error("Token: Invalid client secret")
        case _:
            LOG.logger.error(f"Token {response.status_code}: {response.text}")


def set_channel_id(token_broad):
    response = requests.get(
        url=f'{TWITCH_API}/users?login={CHANNEL}', 
        headers={
            "Authorization": f"Bearer {token_broad}", 
            "Client-Id": f"{CLIENT_ID}"
        }
    )

    match response.status_code:
        case 200:
            data = json.loads(response.text)
            CFG['auth']['CHANNEL_ID'] = data['data'][0]['id']

            with open('config/config.toml', 'wb') as file:
                tomli_w.dump(CFG ,file)
        case _:
            LOG.logger.error(f'Set_channel_id: {response.status_code}: {response.text}')


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
        get_code('bot')
    else:
        get_code('broad')
    input()