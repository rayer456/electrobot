import os
import time
import requests
import socket
import websockets
import asyncio
import ssl
import json
import multiprocessing as mp
import select
import datetime
from operator import itemgetter
import global_hotkeys as hkeys

from config import config_file as CFG
from src import automatic_prediction
from src import logger as LOG


CHANNEL = f"#{CFG['twitch']['info']['channel']}"
ACCOUNT = CFG['twitch']['info']['bot_account'] # can be anything?
CLIENT_ID = CFG['twitch']['auth']['client_id']
CLIENT_SECRET = CFG['twitch']['auth']['client_secret']
B_ID = CFG['twitch']['info']['channel_id']

TWITCH_AUTH_API = 'https://id.twitch.tv/oauth2'
TWITCH_API = 'https://api.twitch.tv/helix'
TWITCH_EVENTSUB = 'wss://eventsub.wss.twitch.tv/ws'
TWITCH_IRC_HOST = 'irc.chat.twitch.tv'
TWITCH_IRC_PORT = 6697

PRED_BEGIN_MESSAGE = CFG['messages']['pred_begin_message']
PRED_REMINDER_MESSAGE = CFG['messages']['pred_reminder_message']
PRED_LOCK_PREFIX = CFG['messages']['pred_lock_prefix']
PRED_LOCK_SUFFIX = CFG['messages']['pred_lock_suffix']
PRED_WINNER_PREFIX = CFG['messages']['pred_winner_prefix']
PRED_LOSER_PREFIX = CFG['messages']['pred_loser_prefix']
PRED_CANCEL_MESSAGE = CFG['messages']['pred_cancel_message']

ENABLE_HOTKEYS = CFG['hotkeys']['enabled']

LIVESPLIT_HOST = CFG['livesplit']['host']
LIVESPLIT_PORT = CFG['livesplit']['port']


def refresh_token(refr_token, br=''):
    response = requests.post(
        url=f'{TWITCH_AUTH_API}/token', 
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }, 
        data=f"grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={refr_token}"
    )

    match response.status_code:
        case 200:
            with open(f'tokens/token_{br}.json', 'w') as file:
                file.write(response.text) #json response
            LOG.logger.debug(f"200: Stored new token in token{br}.json")
        case 400:
            LOG.logger.error("Invalid refresh token, run authorize.py")
            exit()
        case _:
            LOG.logger.error("{response.status_code}: Unknown error")
            exit()


def validate_token(br, q=None):
    global token_bot
    global token_broad
    
    # open token file
    while True:
        try:
            with open(f'tokens/token_{br}.json') as token_file:
                token = json.load(token_file)
                break
        except json.JSONDecodeError: #not readable
            LOG.logger.error("Unreadable file, removing bad file")
            if br == 'bot':
                LOG.logger.info("Run authorize.py to authorize your bot account then restart the bot")
            else:
                LOG.logger.info("Run authorize.py to authorize your streamer account then restart the bot")
            
            os.remove(f'tokens/token_{br}.json')
            input()
        except FileNotFoundError:
            if br == 'bot':
                LOG.logger.error("Missing bot token, run authorize.py to authorize your bot account then restart the bot")
            else:
                LOG.logger.error("Missing streamer token, run authorize.py to authorize your streamer account then restart the bot")
            input()
    
    # validate token
    response = requests.get(
        url=f'{TWITCH_AUTH_API}/validate', 
        headers={
            "Authorization": f"OAuth {token['access_token']}"
        }
    )

    match response.status_code:
        case 200:
            if br == 'bot':
                token_bot = token['access_token'] #read from token
            else: #broad
                token_broad = token['access_token']
                if q != None: 
                    q.put(token_broad)

            LOG.logger.info("TOKEN VALIDATED")
        case 401: #unauth, expired
            LOG.logger.info("Token expired, refreshing...")
            refresh_token(token['refresh_token'], br) #refreshing json

            with open(f'tokens/token_{br}.json') as token_file:
                token = json.load(token_file)

            if br == 'bot':
                token_bot = token['access_token']
            else: #broad
                token_broad = token['access_token']
                if q != None: 
                    q.put(token_broad)
        case _:
            LOG.logger.error(f"Unknown error validate_token: {response.status_code}")
            exit()

    return response.status_code


def IRC_connect():
    global IRC

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    sock = socket.create_connection((TWITCH_IRC_HOST, TWITCH_IRC_PORT))
    IRC = context.wrap_socket(sock, server_hostname=TWITCH_IRC_HOST)
    IRC.setblocking(False)

    irc_send(f"PASS oauth:{token_bot}")
    irc_send(f"NICK {ACCOUNT}")
    irc_send(f"JOIN {CHANNEL}")

    LOG.logger.info("Connected to IRC Chat")


def IRC_reconnect():
    global delay, attempts

    LOG.logger.warning("Disconnected, reconnecting...")
    IRC.shutdown(2) #no more data sent/recv
    IRC.close()

    LOG.logger.warning(f"Waiting {delay}s...")
    time.sleep(delay)
    delay *= 2 #exp backoff
    attempts += 1
    
    if attempts == 7:
        LOG.logger.critical("Couldn't connect to the IRC server, closing...")
        exit()

    IRC_connect()


def irc_send(command):
    IRC.send(f"{command}\n".encode('utf-8'))


def chat(message):
    irc_send(f"PRIVMSG {CHANNEL} :{message}")


def get_mods() -> list:
    response = requests.get(
        url=f'{TWITCH_API}/moderation/moderators?broadcaster_id={B_ID}', 
        headers={
            "Authorization": f"Bearer {token_broad}", 
            "Client-Id": f"{CLIENT_ID}",
        }
    )

    mods = [mod['user_login'] for mod in json.loads(response.text)['data']]
    mods.append(CHANNEL)

    return mods


def event_prediction_begin(locks_at: str) -> str:
    irc_send(f"PRIVMSG {CHANNEL} :{PRED_BEGIN_MESSAGE}")
    locks_at = locks_at.replace('T', ' ')[:locks_at.find('.')]
    locks_at = datetime.datetime.strptime(locks_at, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=35)

    return datetime.datetime.strftime(locks_at, "%Y-%m-%d %H:%M:%S")

    
def event_prediction_lock(outcomes: list):
    total_users, total_points = 0, 0

    for outcome in outcomes:
        total_users += outcome['users']
        total_points += outcome['channel_points']

    for i, outcome in enumerate(outcomes):
        split = outcome['channel_points'] / total_points * 100 #zerodiv exc if no one bet
        if i != 0:
            split_string += f"/{round(split)}"
        else:
            split_string = f"{round(split)}"

    irc_send(f"PRIVMSG {CHANNEL} :{PRED_LOCK_PREFIX} {split_string} split ({total_users} users, pool: {total_points:,}) {PRED_LOCK_SUFFIX}")


def event_prediction_end(outcomes: list, e_status: str, winning_id: str):
    if e_status == "resolved":
        losing_outcomes = []
        all_losers = []

        for outcome in outcomes:
            if outcome['id'] == winning_id:
                winning_outcome = outcome
            else:
                losing_outcomes.append(outcome)

        for i, winner in enumerate(winning_outcome['top_predictors']):
            if i != 0:
                winner_string += f", {winner['user_name']} (+{winner['channel_points_won']:,})"
            else:
                winner_string = f"{PRED_WINNER_PREFIX} {winner['user_name']} (+{winner['channel_points_won']:,})"
        
        # at least 1 winner
        if len(winning_outcome['top_predictors']) != 0: 
            irc_send(f"PRIVMSG {CHANNEL} :{winner_string}")
        
        for losing_outcome in losing_outcomes:
            for loser in losing_outcome['top_predictors']:
                all_losers.append(loser)
        
        # get 10 biggest losers
        all_losers = sorted(all_losers, key=itemgetter('channel_points_used'), reverse=True)[:10]
        for i, loser in enumerate(all_losers):
            if i != 0:
                loser_string += f", {loser['user_name']} (-{loser['channel_points_used']:,})"
            else:
                loser_string = f"{PRED_LOSER_PREFIX} {loser['user_name']} (-{loser['channel_points_used']:,})"
        
        # at least 1 loser
        if len(all_losers) != 0: 
            irc_send(f"PRIVMSG {CHANNEL} :{loser_string}")
        
    elif e_status == "canceled":
        irc_send(f"PRIVMSG {CHANNEL} :{PRED_CANCEL_MESSAGE}")


def main():
    global delay, attempts

    validate_utc = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=3600)
    mods = get_mods()
    pred_is_active = False

    while True: 
        try: 
            select.select([IRC], [], [], 4)
            
            # data from livesplit or eventsub
            if q.qsize() != 0: 
                data = q.get() # collision?
                
                if type(data) == automatic_prediction.AutomaticPrediction: 
                    LOG.logger.debug(f"in queue from livesplit: {data.split}")
                    create_prediction(data.split)
                else: # type is dict 
                    e_status = data['status'] #.end resolved/canceled
                    outcomes = data['outcomes']
                    winning_id = data['winning_id']

                    if data['type'].endswith("begin"):
                        pred_is_active = True
                        time_35s_before_lock = event_prediction_begin(data['locks_at'])
                    elif data['type'].endswith("lock"):
                        pred_is_active = False
                        event_prediction_lock(outcomes)
                    elif data['type'].endswith("end"):
                        pred_is_active = False
                        event_prediction_end(outcomes, e_status, winning_id)
            
            # token validation check
            current_utc = datetime.datetime.now(datetime.UTC)
            if current_utc >= validate_utc:
                hourly_validation()
                validate_utc = current_utc + datetime.timedelta(seconds=3600)

            # reminder check
            if pred_is_active:
                if current_utc.strftime("%Y-%m-%d %H:%M:%S") >= time_35s_before_lock:
                    irc_send(f"PRIVMSG {CHANNEL} :{PRED_REMINDER_MESSAGE}")
                    pred_is_active = False

            # checking IRC messages 
            buffer = IRC.recv(1024).decode()
            buffer = buffer.replace(' \U000e0000', '') #happens when spamming?
            msg = buffer.split() #[user, type_msg, channel, message]

            if not buffer: # empty = disconnect
                IRC_reconnect()
                continue
            
            attempts = 1
            delay = 1

            if msg[0] == "PING":
                LOG.logger.info("Pinged")
                irc_send(f"PONG {msg[1]}")
            elif msg[1] == "PRIVMSG":
                chat_interact(buffer.splitlines(), mods)

        except ssl.SSLWantReadError: #timeout
            continue
        except KeyboardInterrupt:
            LOG.logger.info("Closing bot...")
            break
        except Exception:
            LOG.logger.error("Exception in read_data", exc_info=True)
    

def hourly_validation():
    http_code = validate_token('bot')
    http_code2 = validate_token('broad')

    if http_code == 200 and http_code2 == 200:
        LOG.logger.debug("Hourly check done")
    elif http_code == 401:
        LOG.logger.info("Reconnecting...")
        IRC_reconnect()
    elif http_code2 == 401:
        pass
    else:
        LOG.logger.error(f"hourly_validation: code {http_code} / {http_code2}")
        

def setup_hotkeys():
    bindings = get_hotkeys()
    hkeys.register_hotkeys(bindings)
    hkeys.start_checking_hotkeys()
    LOG.logger.info('Hotkeys registered')


def get_hotkeys() -> list:
    while True:
        try:
            with open('config/bindings.json', 'r') as file:
                bindings = json.load(file)
            
            hotkeys = [{
                'hotkey': binding['hotkey'],
                'on_press_callback': use_hotkeys,
                'on_release_callback': None,
                'actuate_on_partial_release': False,
                'callback_params': binding['action']
            } for binding in bindings]

            return hotkeys
        
        except FileNotFoundError:
            default_bindings = [
                {
                    'hotkey': 'control + 1',
                    'action': 'resolve 1',
                },
                {
                    'hotkey': 'control + 2',
                    'action': 'resolve 2',
                },
                {
                    'hotkey': 'control + 3',
                    'action': 'resolve 3',
                },
                {
                    'hotkey': 'control + 4',
                    'action': 'resolve 4',
                },
                {
                    'hotkey': 'control + 5',
                    'action': 'lock',
                },
                {
                    'hotkey': 'control + 6',
                    'action': 'cancel',
                },
            ]
            with open('config/bindings.json', 'w') as file:
                file.write(json.dumps(default_bindings))


def use_hotkeys(action: str):
    match action.split():
        case ['lock']:
            end_prediction("LOCK")
        case ['resolve', outcome]:
            resolve_prediction(int(outcome))
        case ['cancel']:
            end_prediction("CANCEL")


def chat_interact(buffer, mods): 
    for i in buffer: #possibly multiple messages
        username = i[i.find(':')+1:i.find('!')]
        chat_msg = i[i.find(':', 1)+1:]
        #print(f"{username}: {chat_msg}")

        if username in mods:
            match chat_msg.split():
                case ["pred", "start", name]:
                    create_prediction(name)
                case ["pred", "lock"]:
                    end_prediction("LOCK")
                case ["pred", "outcome", outcome] if 0 < int(outcome) <= 10:
                    resolve_prediction(int(outcome), username)
                case ["pred", "cancel"]:
                    end_prediction("CANCEL")
                case ["!modcommands"]:
                    chat(f"{username} -> pred start <name>, pred lock, pred outcome <1-10>, pred cancel")


def get_latest_prediction():
    while True:
        response = requests.get(
            url=f'{TWITCH_API}/predictions', 
            headers={
                "Authorization": f"Bearer {token_broad}",
                "Client-Id": CLIENT_ID
            },
            params=f'broadcaster_id={B_ID}&first=1',
        )
        LOG.logger.debug("get_latest_prediction: request done")

        match response.status_code:
            case 200:
                pred_json = json.loads(response.text)
                return pred_json
            case 400:
                LOG.logger.error(f"get_latest_prediction: 400 Bad Request: {response.text}")
                break
            case 401: #token expired
                validate_token('broad')


def create_prediction(pred_name):
    with open('predictions/predictions.json', 'r') as file:
        preds = json.load(file)
    LOG.logger.debug("create_prediction: Read predictions.json")
    
    not_found = True
    options = ''
    for p in preds['predictions']:
        options += f"{p['name']} "
        if p['name'] == pred_name: # match
            p['data']['broadcaster_id'] = B_ID
            prediction_data = p['data']
            not_found = False
        
    if not_found:
        LOG.logger.debug("create_prediction: Non-existing prediction")
        return chat(f"Possibilities: {options}")

    while True:
        response = requests.post(
            url=f'{TWITCH_API}/predictions',  
            headers={
                "Authorization": f"Bearer {token_broad}", 
                "Client-Id": CLIENT_ID,
                "Content-Type": "application/json",
            },
            json=prediction_data,
        )

        match response.status_code:
            case 200:
                LOG.logger.debug("create_prediction: successfully created prediction")
                break
            case 400: #pred already running
                LOG.logger.error(f"create_prediction: 400 Bad Request: {response.text}")
                return chat("Prediction already running")
            case 401: #expired
                validate_token('broad')
            case 429:
                LOG.logger.warning("Too many requests")
                break


def resolve_prediction(outcome, username=None):
    latest_pred = get_latest_prediction()
    
    #ACTIVE, RESOLVED, CANCELED, LOCKED
    if latest_pred['data'][0]['status'] not in ("ACTIVE", "LOCKED"): 
       return chat(f"{username} -> No active predictions")

    if not outcome <= len(latest_pred['data'][0]['outcomes']):
        return chat(f"{username} -> {outcome} is not an option")

    while True:
        response = requests.patch(
            url=f'{TWITCH_API}/predictions', 
            headers={
                "Authorization": f"Bearer {token_broad}", 
                "Client-Id": f"{CLIENT_ID}",
                "Content-Type": "application/json"
            }, 
            json={
                "broadcaster_id": B_ID,
                "id": latest_pred['data'][0]['id'],
                "status": "RESOLVED",
                "winning_outcome_id": latest_pred['data'][0]['outcomes'][outcome-1]['id']
            }
        )

        match response.status_code:
            case 200:
                LOG.logger.debug("resolve_prediction: successfully resolved prediction")
                break
            case 400:
                LOG.logger.error("resolve_prediction: 400 Bad Request")
                break
            case 401: #try again
                validate_token('broad')
            case 404:
                LOG.logger.error("resolve_prediction: 404 Not found")
                break


def end_prediction(action):
    latest_pred = get_latest_prediction()
    status = latest_pred['data'][0]['status'] 

    match action:
        case "LOCK":
            if status != "ACTIVE":
                if status == "LOCKED":
                    return chat("Already locked")
                return chat("No active predictions")
        case "CANCEL":
            if status not in ("ACTIVE", "LOCKED"):
                return chat("No active predictions")

    while True:
        response = requests.patch(
            url=f'{TWITCH_API}/predictions', 
            headers={
                "Authorization": f"Bearer {token_broad}", 
                "Client-Id": CLIENT_ID,
                "Content-Type": "application/json"
            }, 
            json={
                "broadcaster_id": B_ID,
                "id": latest_pred['data'][0]['id'],
                "status": f"{action}ED" #LOCK or CANCEL
            }
        )

        match response.status_code:
            case 200:
                break
            case 400:
                LOG.logger.error(f"end_prediction: 400 Bad Request: {response.text}")
                break
            case 401:
                validate_token('broad')
            case 404:
                LOG.logger.error(f"end_prediction: 404 Not found: {response.text}")
                break
        

async def event_handler(q):
    global token_broad

    current_eventsub = TWITCH_EVENTSUB
    while True:
        try:
            async with websockets.connect((current_eventsub)) as websock:
                while True:
                    buffer = await asyncio.wait_for(websock.recv(), 15) #no keepalive = conn died
                    buffer = json.loads(buffer) #dict

                    match buffer['metadata']['message_type']:
                        case 'session_welcome': #first msg after connecting
                            LOG.logger.info("Eventsub: welcome")
                            with open(f'tokens/token_broad.json') as token_file:
                                token = json.load(token_file)
                                token_broad = token['access_token']
                                
                            event_list = ["channel.prediction.begin", "channel.prediction.lock", "channel.prediction.end"]
                            for event in event_list:
                                sub_to_event(q, buffer['payload']['session']['id'], event)

                            LOG.logger.info("Listening for events...")
                        case 'session_keepalive': continue #every 10s
                        case 'notification':
                            LOG.logger.info("Eventsub: notification")
                            queue_event_object(q, buffer)
                        case 'session_reconnect':
                            LOG.logger.warning("Eventsub: reconnect")
                            #current_eventsub = buffer['payload']['session']['reconnect_url']
                            break
                        case 'revocation':
                            event_type = buffer['payload']['subscription']['type']
                            reason = buffer['payload']['subscription']['status']
                            LOG.logger.error(f'Revoked: {event_type} reason: {reason}')
                            break
                        case _:
                            LOG.logger.error(f"Unknown message: {buffer['metadata']['message_type']}")
                            exit()
        except TimeoutError: #no keepalive
            LOG.logger.warning("Connection lost, reconnecting...", exc_info=True)
            current_eventsub = TWITCH_EVENTSUB
            continue
        except websockets.exceptions.ConnectionClosedError:
            LOG.logger.error("Eventsub: Connection closed", exc_info=True)
            current_eventsub = TWITCH_EVENTSUB
            continue
        except Exception:
            LOG.logger.error("Websockets error", exc_info=True)
            continue


def queue_event_object(q: mp.Queue, buffer): #parsing data to write to chat
    event_type = buffer['payload']['subscription']['type']
    outcomes = buffer['payload']['event']['outcomes']
    e_status = ""
    winning_id = ""
    locks_at = ""

    if event_type.endswith("end"):
        e_status = buffer['payload']['event']['status']
        winning_id = buffer['payload']['event']['winning_outcome_id']

    elif event_type.endswith("begin"):
        locks_at = buffer['payload']['event']['locks_at']
    
    data = {
        "type": event_type,
        "status": e_status,
        "outcomes": outcomes,
        "winning_id": winning_id,
        "locks_at": locks_at
    }
    q.put(data)


def sub_to_event(q, session_id, event_type):
    global token_broad

    while True:
        if q.qsize() != 0:
            token_broad = q.get() #after 401, not initial connect

        response = requests.post(
            url=f'{TWITCH_API}/eventsub/subscriptions', 
            headers={
                "Authorization": f"Bearer {token_broad}", 
                "Client-Id": f"{CLIENT_ID}",
                "Content-Type": "application/json"
            }, 
            json={
                "type": event_type,
                "version": '1',
                "condition": {
                    "broadcaster_user_id": B_ID
                },
                "transport": {
                    "method": "websocket",
                    "session_id": session_id
                }
            }
        )

        match response.status_code:
            case 202:
                LOG.logger.info("Eventsub: Subbed to event")
                break
            case 400:
                LOG.logger.error(f"Eventsub: Bad request: {response.text}")
                break
            case 401:
                LOG.logger.warning("Eventsub: Unauthorized")
                validate_token('broad', q)
            case 403:
                LOG.logger.error("Eventsub: missing scopes")
                break
            case _:
                LOG.logger.error(f"Eventsub: {response.status_code}")
                break


def eventsub(q):
    asyncio.run(event_handler(q))


def livesplit_predictions(q):
    auto_prediction_launcher = automatic_prediction.Launcher()
    auto_prediction_launcher.launch(q, LOG, LIVESPLIT_HOST, LIVESPLIT_PORT)


if __name__ == "__main__":
    global delay, attempts

    delay = 1
    attempts = 1
    q = mp.Queue()
    
    validate_token('bot')
    validate_token('broad')
    IRC_connect()

    if ENABLE_HOTKEYS:
        setup_hotkeys()

    event_process = mp.Process(target=eventsub, daemon=True, args=(q,))
    event_process.start()

    livesplit_prediction_process = mp.Process(target=livesplit_predictions, daemon=True, args=(q,))
    livesplit_prediction_process.start()

    main()