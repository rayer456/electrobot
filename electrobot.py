import time
import requests
import socket
import websockets
import asyncio
import ssl
import json
import multiprocessing as mp
from multiprocessing.managers import BaseManager
import select
import datetime
from operator import itemgetter

import global_hotkeys as hkeys

from config import config_file as CFG
from src import automatic_prediction
from src import Token, TokenType
from src import logger as LOG


CHANNEL = f"#{CFG['twitch']['info']['channel'].lower()}"
BOT_ACCOUNT = CFG['twitch']['info']['bot_account'] # can be anything?
CLIENT_ID = CFG['twitch']['auth']['client_id']
CHANNEL_ID = CFG['twitch']['info']['channel_id']

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
ACTION_DENIED_MESSAGE = CFG['messages']['action_denied_message']

GRANT_MODS = CFG['permissions']['grant_mods']
GRANT_VIPS = CFG['permissions']['grant_vips']

HOTKEYS_ENABLED = CFG['hotkeys']['enabled']
HOTKEYS: dict = CFG['hotkeys']

LIVESPLIT_HOST = CFG['livesplit']['host']
LIVESPLIT_PORT = CFG['livesplit']['port']


def IRC_connect():
    global IRC

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    sock = socket.create_connection((TWITCH_IRC_HOST, TWITCH_IRC_PORT))
    IRC = context.wrap_socket(sock, server_hostname=TWITCH_IRC_HOST)
    IRC.setblocking(False)

    IRC_send(f"PASS oauth:{token_bot.get_access_token()}")
    IRC_send(f"NICK {BOT_ACCOUNT}")
    IRC_send(f"JOIN {CHANNEL}")
    # requesting tags
    IRC_send("CAP REQ :twitch.tv/commands twitch.tv/tags")

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
        input()

    IRC_connect()


def IRC_send(command):
    IRC.send(f"{command}\n".encode('utf-8'))


def chat(message):
    IRC_send(f"PRIVMSG {CHANNEL} :{message}")


def event_prediction_begin(locks_at: str) -> str:
    chat(PRED_BEGIN_MESSAGE)
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

    chat(f"{PRED_LOCK_PREFIX} {split_string} split ({total_users} users, pool: {total_points:,}) {PRED_LOCK_SUFFIX}")


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
            chat(winner_string)
        
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
            chat(loser_string)
        
    elif e_status == "canceled":
        chat(PRED_CANCEL_MESSAGE)


def main():
    global delay, attempts, token_broad

    validate_utc = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=3600)
    pred_is_active = False

    while True: 
        try: 
            select.select([IRC], [], [], 4)
            
            # data from livesplit or eventsub
            if q.qsize() != 0: 
                data = q.get() # collision?
                
                if type(data) == automatic_prediction.AutomaticPrediction: 
                    LOG.logger.debug(f"in queue from livesplit: {data.split}")
                    create_prediction(data.split, "Livesplit")
                elif type(data) == dict: # type is dict 
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
                    chat(PRED_REMINDER_MESSAGE)
                    pred_is_active = False

            # checking IRC messages 
            buffer = IRC.recv(1024).decode()
            buffer = buffer.replace(' \U000e0000', '') # happens when spamming?
            msg = buffer.split()

            if not buffer: # empty = disconnect
                IRC_reconnect()
                continue
            
            attempts = 1
            delay = 1

            if msg[0] == "PING":
                LOG.logger.info("Pinged")
                IRC_send(f"PONG {msg[1]}")
            elif msg[2] == "PRIVMSG":
                chat_interact(buffer.splitlines())

        except ssl.SSLWantReadError: # timeout
            continue
        except KeyboardInterrupt:
            LOG.logger.info("Closing bot...")
            break
        except Exception:
            LOG.logger.error("Exception in read_data", exc_info=True)
    

def hourly_validation():
    http_code_bot = token_bot.validate()
    http_code_broad = token_broad.validate()
    LOG.logger.debug(f"Hourly check done: bot: {http_code_bot} | broad: {http_code_broad}")

    if http_code_bot == 401:
        LOG.logger.info("Reconnecting to IRC Chat...")
        IRC_reconnect()
        

def setup_hotkeys():
    bindings = get_hotkeys()
    hkeys.register_hotkeys(bindings)
    hkeys.start_checking_hotkeys()
    LOG.logger.info('Hotkeys registered')


def get_hotkeys() -> list:
    hotkeys_copy = HOTKEYS.copy()
    hotkeys_copy.pop('enabled')
    hotkey: str
    for hotkey in hotkeys_copy.keys():
        if '_' in hotkey:
            hotkeys_copy[hotkey.replace('_', ' ')] = hotkeys_copy.pop(hotkey)

    hotkeys = [{
        'hotkey': hotkeys_copy[hotkey],
        'on_press_callback': use_hotkeys,
        'on_release_callback': None,
        'actuate_on_partial_release': False,
        'callback_params': hotkey
    } for hotkey in hotkeys_copy]

    return hotkeys


def use_hotkeys(action: str):
    match action.split():
        case ['lock']:
            end_prediction("LOCK", CHANNEL.removeprefix('#'))
        case ['resolve', outcome]:
            resolve_prediction(int(outcome), CHANNEL.removeprefix('#'))
        case ['cancel']:
            end_prediction("CANCEL", CHANNEL.removeprefix('#'))


def chat_interact(buffer): 
    # buffer can contain multiple messages
    for i in buffer: 
        tags = i.split()[0]

        # mod tag is always there
        is_mod = bool(int(tags[tags.find(';mod=')+5:tags.find(';mod=')+6]))

        # broadcaster tag isn't always there
        is_streamer = False
        if tags.find('broadcaster/') != -1:
            is_streamer = True

        # vip tag isn't always there
        if tags.find(';vip=') == -1:
            is_vip = False
        else:
            is_vip = bool(int(tags[tags.find(';vip=')+5:tags.find(';vip=')+6]))

        username = i[i.find(' :')+2:i.find('!')]
        chat_msg = i[i.find(f'{CHANNEL} :') + len(CHANNEL) + 2:]
        # print(f"{username}: {chat_msg}")

        # disgusting but I don't give a shit
        send_denied_message = False
        match chat_msg.split():
            case ["pred", "start", name]:
                if (GRANT_MODS and is_mod) or (GRANT_VIPS and is_vip) or is_streamer:
                    create_prediction(name, username)
                elif (not GRANT_MODS and is_mod) or (not GRANT_VIPS and is_vip):
                    send_denied_message = True

            case ["pred", "lock"]:
                if (GRANT_MODS and is_mod) or (GRANT_VIPS and is_vip) or is_streamer:
                    end_prediction("LOCK", username)
                elif (not GRANT_MODS and is_mod) or (not GRANT_VIPS and is_vip):
                    send_denied_message = True

            case ["pred", "outcome", outcome] if 0 < int(outcome) <= 10:
                if (GRANT_MODS and is_mod) or (GRANT_VIPS and is_vip) or is_streamer:
                    resolve_prediction(int(outcome), username)
                elif (not GRANT_MODS and is_mod) or (not GRANT_VIPS and is_vip):
                    send_denied_message = True
            case ["pred", "cancel"]:
                if (GRANT_MODS and is_mod) or (GRANT_VIPS and is_vip) or is_streamer:
                    end_prediction("CANCEL", username)
                elif (not GRANT_MODS and is_mod) or (not GRANT_VIPS and is_vip):
                    send_denied_message = True

            case ["!modcommands"]:
                chat(f"{username} -> pred start <name>, pred lock, pred outcome <1-10>, pred cancel")

        if send_denied_message:
            chat(f"{username} -> {ACTION_DENIED_MESSAGE}")
            LOG.logger.info(f"User {username} tried to perform an action and is not authorized\nMod: {is_mod}\nVIP: {is_vip}")


def get_latest_prediction():
    while True:
        response = requests.get(
            url=f'{TWITCH_API}/predictions', 
            headers={
                "Authorization": f"Bearer {token_broad.get_access_token()}",
                "Client-Id": CLIENT_ID
            },
            params=f'broadcaster_id={CHANNEL_ID}&first=1',
        )
        LOG.logger.debug("get_latest_prediction: request done")

        match response.status_code:
            case 200:
                pred_json = json.loads(response.text)
                return pred_json
            case 400:
                LOG.logger.error(f"get_latest_prediction: 400 Bad Request: {response.text}")
                break
            case 401: # token expired
                token_broad.validate()


def create_prediction(pred_name, username):
    with open('predictions/predictions.json', 'r') as file:
        preds = json.load(file)
    LOG.logger.debug("create_prediction: Read predictions.json")
    
    not_found = True
    options = ''
    for p in preds['predictions']:
        options += f"{p['name']} "
        if p['name'] == pred_name: # match
            p['data']['broadcaster_id'] = CHANNEL_ID
            prediction_data = p['data']
            not_found = False
        
    if not_found:
        LOG.logger.debug("create_prediction: Non-existing prediction")
        return chat(f"{username} -> Possibilities: {options}")

    while True:
        response = requests.post(
            url=f'{TWITCH_API}/predictions',  
            headers={
                "Authorization": f"Bearer {token_broad.get_access_token()}", 
                "Client-Id": CLIENT_ID,
                "Content-Type": "application/json",
            },
            json=prediction_data,
        )

        match response.status_code:
            case 200:
                LOG.logger.debug("create_prediction: successfully created prediction")
                break
            case 400: # most likely pred already running
                LOG.logger.error(f"create_prediction: 400 Bad Request: {response.text}")
                return chat(f"{username} -> Prediction already running")
            case 401: # expired
                token_broad.validate()
            case 429:
                LOG.logger.warning("Too many requests")
                break


def resolve_prediction(outcome, username):
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
                "Authorization": f"Bearer {token_broad.get_access_token()}", 
                "Client-Id": f"{CLIENT_ID}",
                "Content-Type": "application/json"
            }, 
            json={
                "broadcaster_id": CHANNEL_ID,
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
            case 401:
                token_broad.validate()
            case 404:
                LOG.logger.error("resolve_prediction: 404 Not found")
                break


def end_prediction(action, username):
    latest_pred = get_latest_prediction()
    status = latest_pred['data'][0]['status'] 

    match action:
        case "LOCK":
            if status != "ACTIVE":
                if status == "LOCKED":
                    return chat(f"{username} -> Already locked")
                return chat(f"{username} -> No active predictions")
        case "CANCEL":
            if status not in ("ACTIVE", "LOCKED"):
                return chat(f"{username} -> No active predictions")

    while True:
        response = requests.patch(
            url=f'{TWITCH_API}/predictions', 
            headers={
                "Authorization": f"Bearer {token_broad.get_access_token()}", 
                "Client-Id": CLIENT_ID,
                "Content-Type": "application/json"
            }, 
            json={
                "broadcaster_id": CHANNEL_ID,
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
                token_broad.validate()
            case 404:
                LOG.logger.error(f"end_prediction: 404 Not found: {response.text}")
                break
        

async def event_handler(q: mp.Queue, token_broad: Token):
    current_eventsub = TWITCH_EVENTSUB
    while True:
        try:
            async with websockets.connect((current_eventsub)) as websock:
                while True:
                    buffer = await asyncio.wait_for(websock.recv(), 15) # no keepalive = conn died
                    buffer = json.loads(buffer) # dict

                    match buffer['metadata']['message_type']:
                        case 'session_welcome': # first msg after connecting
                            LOG.logger.info("Eventsub: welcome")
                            
                            session_id = buffer['payload']['session']['id']
                            sub_to_event(session_id, "channel.prediction.begin", token_broad)
                            sub_to_event(session_id, "channel.prediction.lock", token_broad)
                            sub_to_event(session_id, "channel.prediction.end", token_broad)

                            LOG.logger.info("Listening for events...")
                        case 'session_keepalive': continue # every 10s
                        case 'notification':
                            LOG.logger.info("Eventsub: notification")
                            queue_event_object(q, buffer)
                        case 'session_reconnect':
                            LOG.logger.warning("Eventsub: reconnect")
                            # current_eventsub = buffer['payload']['session']['reconnect_url']
                            break
                        case 'revocation':
                            event_type = buffer['payload']['subscription']['type']
                            reason = buffer['payload']['subscription']['status']
                            LOG.logger.error(f'Revoked: {event_type} reason: {reason}')
                            break
                        case _:
                            LOG.logger.error(f"Unknown message: {buffer['metadata']['message_type']}")
                            input()
        except TimeoutError: # no keepalive
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


def queue_event_object(q: mp.Queue, buffer: dict): # preparing data
    event_type: str = buffer['payload']['subscription']['type']
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


def sub_to_event(session_id, event_type, token_broad: Token):
    while True:
        response = requests.post(
            url=f'{TWITCH_API}/eventsub/subscriptions', 
            headers={
                "Authorization": f"Bearer {token_broad.get_access_token()}", 
                "Client-Id": f"{CLIENT_ID}",
                "Content-Type": "application/json"
            }, 
            json={
                "type": event_type,
                "version": '1',
                "condition": {
                    "broadcaster_user_id": CHANNEL_ID
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
                token_broad.validate()
            case 403:
                LOG.logger.error("Eventsub: missing scopes")
                break
            case _:
                LOG.logger.error(f"Eventsub: {response.status_code}")
                break


def eventsub(q: mp.Queue, token_broad: Token):
    asyncio.run(event_handler(q, token_broad))


def livesplit_predictions(q):
    auto_prediction_launcher = automatic_prediction.Launcher()
    auto_prediction_launcher.launch(q, LOG, LIVESPLIT_HOST, LIVESPLIT_PORT)


if __name__ == "__main__":
    global delay, attempts

    delay = 1
    attempts = 1

    q = mp.Queue()

    # shared memory for token
    BaseManager.register('Token', Token)
    manager = BaseManager()
    manager.start()

    # weird exception thing because manager?
    try:
        token_broad: Token = manager.Token(TokenType.BROADCASTER)
        token_bot: Token = manager.Token(TokenType.BOT)
    except Exception:
        input()

    IRC_connect()

    if HOTKEYS_ENABLED:
        setup_hotkeys()

    event_process = mp.Process(target=eventsub, daemon=True, args=(q, token_broad))
    event_process.start()

    livesplit_prediction_process = mp.Process(target=livesplit_predictions, daemon=True, args=(q,))
    livesplit_prediction_process.start()

    main()
