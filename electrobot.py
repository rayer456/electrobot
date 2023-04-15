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
from config import config_file as CFG
import predictions
import logger as LOG


HOST = CFG['irc']['HOST']
PORT = CFG['irc']['PORT']
CHANNEL = f"#{CFG['irc']['CHANNEL']}"
ACCOUNT = CFG['irc']['BOT_ACCOUNT'] #can be anything?
CLIENT_ID = CFG['auth']['CLIENT_ID']
CLIENT_SECRET = CFG['auth']['CLIENT_SECRET']
B_ID = CFG['auth']['CHANNEL_ID']
event_host = CFG['eventsub']['HOST']


def refresh_token(refr_token, br=''):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={refr_token}"
   
    response = requests.post("https://id.twitch.tv/oauth2/token", headers=headers, data=data)
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
    
    while True:
        try:
            with open(f'tokens/token_{br}.json') as token_file:
                token = json.load(token_file)
                break
        except json.JSONDecodeError: #not readable
            LOG.logger.info("Removing bad file")
            LOG.logger.info("Run authorize.py")
            os.remove(f'tokens/token_{br}.json')
            exit() #parent will die on hourly check, if not by user
        except FileNotFoundError:
            if br == 'bot':
                LOG.logger.error("No bot token, run authorize.py")
            else:
                LOG.logger.error("No streamer token, run authorize.py")
            exit()
    
    headers = {"Authorization": f"OAuth {token['access_token']}"}
    response = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)

    match response.status_code:
        case 200: #ok, valid
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
    sock = socket.create_connection((HOST, PORT))
    IRC = context.wrap_socket(sock, server_hostname=HOST)
    IRC.setblocking(False)

    send_data(f"PASS oauth:{token_bot}")
    send_data(f"NICK {ACCOUNT}")
    send_data(f"JOIN {CHANNEL}")

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
        LOG.logger.critical("Couldn't connect to the server, closing...")
        exit()
    IRC_connect()


def send_data(command):
    IRC.send(f"{command}\n".encode('utf-8'))


def get_mods():
    headers = {
        "Authorization": f"Bearer {token_broad}", 
        "Client-Id": f"{CLIENT_ID}"
    }
    response = requests.get(f'https://api.twitch.tv/helix/moderation/moderators?broadcaster_id={B_ID}', headers=headers)
    
    mods = []
    for mod in json.loads(response.text)['data']:
        mods.append(mod['user_login'])
    mods.append(CFG['irc']['CHANNEL'])

    return mods


def event_prediction_begin(locks_at):
    send_data(f"PRIVMSG {CHANNEL} :🎰🚨🎰BETS ARE OPEN, any gamblers? modCheck 🎰🚨🎰")
    locks_at = locks_at.replace('T', ' ')[:locks_at.find('.')] #formatting
    locks_at = datetime.datetime.strptime(locks_at, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=35)

    return datetime.datetime.strftime(locks_at, "%Y-%m-%d %H:%M:%S")

    
def event_prediction_lock(outcomes):
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

    send_data(f"PRIVMSG {CHANNEL} :🎰BETS ARE CLOSED🎰 {split_string} split ({total_users} betters, pool: {total_points:,}) PauseFish")


def event_prediction_end(outcomes, e_status, winning_id):
    if e_status == "resolved":
        losing_outcomes = []
        all_losers = [] #store all losers in one place

        for outcome in outcomes:
            if outcome['id'] == winning_id:
                winning_outcome = outcome
            else:
                losing_outcomes.append(outcome)

        for i, winner in enumerate(winning_outcome['top_predictors']):
            if i != 0:
                winner_string += f", {winner['user_name']} (+{winner['channel_points_won']:,})"
            else:
                winner_string = f"GIGACHAD {winner['user_name']} (+{winner['channel_points_won']:,})"
        
        if len(winning_outcome['top_predictors']) != 0: #if no one won
            send_data(f"PRIVMSG {CHANNEL} :{winner_string}")
        
        for losing_outcome in losing_outcomes:
            for loser in losing_outcome['top_predictors']:
                all_losers.append(loser)
        
        #get 10 biggest losers
        all_losers = sorted(all_losers, key=itemgetter('channel_points_used'), reverse=True)[:10]

        for i, loser in enumerate(all_losers):
            if i != 0:
                loser_string += f", {loser['user_name']} (-{loser['channel_points_used']:,})"
            else:
                loser_string = f"xdd {loser['user_name']} (-{loser['channel_points_used']:,})"
        
        if len(all_losers) != 0: #no one lost
            send_data(f"PRIVMSG {CHANNEL} :{loser_string}")
        
    else: #canceled
        send_data(f"PRIVMSG {CHANNEL} :Prediction canceled SadgeCry") #balls


def read_data(q):
    pred_is_active = False
    while True: 
        try: 
            select.select([IRC], [], [], 4) #block until timeout, unless irc msg
            
            if q.qsize() != 0: #from livesplit or eventsub
                data = q.get() #collision?
                
                if type(data) == str: #livesplit
                    LOG.logger.debug(f"in queue from livesplit: {data}")
                    create_prediction(data)
                else: #eventsub
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
                    
            if pred_is_active:
                current_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                if current_utc >= time_35s_before_lock:
                    send_data(f"PRIVMSG {CHANNEL} :🚨30 seconds left VeryPog make your bets NOW🚨")
                    pred_is_active = False
                    
            buffer = IRC.recv(1024).decode()
            buffer = buffer.replace(' \U000e0000', '') #happens when spamming?
            msg = buffer.split() #[user, type_msg, channel, message]

            if not buffer: #empty = disconnect
                IRC_reconnect()
                continue

            if msg[0] == "PING":
                LOG.logger.info("Pinged")
                send_data(f"PONG {msg[1]}")
            elif msg[1] == "PRIVMSG": #TODO commands, modcommands, song, pb, wr
                chat_interact(buffer.splitlines())

        except ssl.SSLWantReadError: #timeout
            continue             
        except Exception:
            LOG.logger.error("Exception in read_data", exc_info=True)
        

def chat_interact(buffer):
    mods = get_mods() #easier than parsing with /tags
    for i in buffer: #possibly multiple messages
        username = i[i.find(':')+1:i.find('!')]
        chat_msg = i[i.find(':', 1)+1:]
        #print(f"{username}: {chat_msg}")

        if username in mods: #mod commands
            response = None
            match chat_msg.split():
                case ["pred", "start", name]:
                    response = create_prediction(name)
                case ["pred", "lock"]:
                    response = end_prediction("LOCK")
                case ["pred", "outcome", outcome] if 0 < int(outcome) <= 10:
                    response = resolve_prediction(int(outcome))
                case ["pred", "cancel"]: #CANCELED 
                    response = end_prediction("CANCEL")

            if response != None: send_data(f"PRIVMSG {CHANNEL} :{response}")


def update_latest_prediction():
    global pred_json

    while True:
        headers = {
            "Authorization": f"Bearer {token_broad}",
            "Client-Id": CLIENT_ID
        }
        response = requests.get(f'https://api.twitch.tv/helix/predictions?broadcaster_id={B_ID}&first=1', headers=headers)
        LOG.logger.debug("update_latest_prediction: request done")

        match response.status_code:
            case 200:
                pred_json = json.loads(response.text)
                break
            case 401: #token expired
                validate_token('broad')


def create_prediction(pred_name):
    with open('predictions/predictions.json', 'r') as file:
        preds = json.load(file)
    LOG.logger.debug("create_prediction: Read predictions.json")
    
    not_found = True
    options = ""
    for i in preds['predictions']:
        options += f"{i['name']} "
        if i['name'] == pred_name: #match
            i['data']['broadcaster_id'] = B_ID
            data = i['data']
            not_found = False
        
    if not_found:
        LOG.logger.debug("create_prediction: Non-existing prediction")
        return f"Possibilities: {options}"

    while True:
        headers = {
            "Authorization": f"Bearer {token_broad}", 
            "Client-Id": f"{CLIENT_ID}",
            "Content-Type": "application/json"
        }
        response = requests.post('https://api.twitch.tv/helix/predictions', json=data, headers=headers)

        match response.status_code:
            case 200:
                LOG.logger.debug("create_prediction: successfully created prediction")
                break
            case 400: #pred already running
                LOG.logger.error(response.text)
                return "Prediction already running"
            case 401: #expired
                validate_token('broad')
            case 429:
                LOG.logger.warning("Too many requests")
                break


def resolve_prediction(outcome):
    update_latest_prediction()
    
    #ACTIVE, RESOLVED, CANCELED, LOCKED
    if pred_json['data'][0]['status'] not in ("ACTIVE", "LOCKED"): 
        return "No active predictions"

    if not outcome <= len(pred_json['data'][0]['outcomes']):
        return f"{outcome} is not an option"

    data = {
        "broadcaster_id": B_ID,
        "id": pred_json['data'][0]['id'],
        "status": "RESOLVED",
        "winning_outcome_id": pred_json['data'][0]['outcomes'][outcome-1]['id']
    }

    while True:
        headers = {
            "Authorization": f"Bearer {token_broad}", 
            "Client-Id": f"{CLIENT_ID}",
            "Content-Type": "application/json"
        }
        response = requests.patch('https://api.twitch.tv/helix/predictions', headers=headers, json=data)

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
    update_latest_prediction()

    status = pred_json['data'][0]['status'] 
    match action:
        case "LOCK":
            if status != "ACTIVE":
                if status == "LOCKED":
                    return "Already locked"
                return "No active predictions"
        case "CANCEL":
            if status not in ("ACTIVE", "LOCKED"):
                return "No active predictions"
            
    data = {
        "broadcaster_id": B_ID,
        "id": pred_json['data'][0]['id'],
        "status": f"{action}ED" #LOCK or CANCEL
    }

    while True:
        headers = {
            "Authorization": f"Bearer {token_broad}", 
            "Client-Id": f"{CLIENT_ID}",
            "Content-Type": "application/json"
        }
        response = requests.patch('https://api.twitch.tv/helix/predictions', headers=headers, json=data)

        match response.status_code:
            case 200:
                break
            case 400:
                LOG.logger.error("end_prediction: 400 Bad Request")
                break
            case 401: #try again
                validate_token('broad')
            case 404:
                LOG.logger.error("end_prediction: 404 Not found")
                break
        

async def event_handler(q):
    global event_host
    global token_broad
    
    while True:
        try:
            async with websockets.connect((event_host)) as eventsub:
                while True:
                    buffer = await asyncio.wait_for(eventsub.recv(), 15) #no keepalive = conn died
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
                            event_host = buffer['payload']['session']['reconnect_url']
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
            continue
        except websockets.exceptions.ConnectionClosedError:
            LOG.logger.error("Eventsub: Connection closed", exc_info=True)
            continue
        except Exception:
            LOG.logger.error("Websockets error", exc_info=True)
            continue


def queue_event_object(q, buffer): #parsing data to write to chat
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

        headers = {
                "Authorization": f"Bearer {token_broad}", 
                "Client-Id": f"{CLIENT_ID}",
                "Content-Type": "application/json"
            }
        data = {
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
        response = requests.post('https://api.twitch.tv/helix/eventsub/subscriptions', headers=headers, json=data)

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


def hourly_validation():
    try:
        while True:
            time.sleep(3600) #validate every hour
            old_process = mp.active_children()[0] #indexError = no child
            old_event_process = mp.active_children()[1]
            old_prediction_process = mp.active_children()[2]
            http_code = validate_token('bot')
            http_code2 = validate_token('broad')

            if http_code == 200 and http_code2 == 200:
                LOG.logger.debug("Hourly check done")
                continue
            elif http_code == 401 or http_code2 == 401:
                LOG.logger.warning("Reconnecting...")
                old_process.terminate()
                old_event_process.terminate()
                old_prediction_process.terminate()
        
                new_process = mp.Process(target=run, daemon=True, args=(q,))
                new_process.start()

                time.sleep(4)
                event_process = mp.Process(target=eventsub, daemon=True, args=(q,))
                event_process.start()

                prediction_process = mp.Process(target=auto_predictions, daemon=True, args=(q,CFG))
                prediction_process.start()
            else:
                LOG.logger.error(f"Unknown error: code {http_code} / {http_code2}")
                break #kill self and children
    except IndexError:
        LOG.logger.error("Child process dead")
    except KeyboardInterrupt:
        LOG.logger.info("Closing bot...")
        exit()


def run(q):
    global delay, attempts
    delay = 1
    attempts = 1
    validate_token('bot')
    validate_token('broad')
    IRC_connect()
    read_data(q)


def eventsub(q):
    asyncio.run(event_handler(q))


def auto_predictions(q, CFG):
    predictions.main(q, CFG, LOG)


if __name__ == "__main__":
    q = mp.Queue()

    process = mp.Process(target=run, daemon=True, args=(q,)) #kill child if parent dies
    process.start() #child

    time.sleep(4)
    event_process = mp.Process(target=eventsub, daemon=True, args=(q,))
    event_process.start()

    prediction_process = mp.Process(target=auto_predictions, daemon=True, args=(q,CFG))
    prediction_process.start()

    hourly_validation()