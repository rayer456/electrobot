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
from operator import itemgetter
from config import config_file as CFG
import predictions


HOST = CFG['irc']['HOST']
PORT = CFG['irc']['PORT']
CHANNEL = f"#{CFG['irc']['CHANNEL']}"
ACCOUNT = CFG['irc']['BOT_ACCOUNT'] #can be anything?
CLIENT_ID = CFG['auth']['CLIENT_ID']
CLIENT_SECRET = CFG['auth']['CLIENT_SECRET']
B_ID = CFG['auth']['CHANNEL_ID']
event_host = CFG['eventsub']['HOST']
delay = 1
attempts = 1


def refresh_token(refr_token, br=''):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={refr_token}"
   
    response = requests.post("https://id.twitch.tv/oauth2/token", headers=headers, data=data)
    match response.status_code:
        case 200:
            with open(f'tokens/token_{br}.json', 'w') as file:
                file.write(response.text) #json response
            print(f"[+] 200: Stored new token in token{br}.json")
        case 400:
            print("[+] Invalid refresh token, run authorize.py")
            exit()
        case _:
            print(f"[+] {response.status_code}: Unknown error")
            exit()


def validate_token(br, q=None): #which one
    global token_bot
    global token_broad
    
    while True:
        try:
            with open(f'tokens/token_{br}.json') as token_file:
                token = json.load(token_file)
                break
        except json.JSONDecodeError: #not readable
            print("[+] Removing bad file")
            print("[+] Run authorize.py")
            os.remove(f'tokens/token_{br}.json')
            exit() #parent will die on hourly check, if not by user
        except FileNotFoundError:
            if br == 'bot':
                print("[+] No bot token, run authorize.py")
            else:
                print("[+] No streamer token, run authorize.py")
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

            print(f"\n[+] TOKEN VALIDATED")
        case 401: #unauth, expired
            print("[+] Token expired, refreshing...")
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
            print(f"[+] Unknown error /validate: code {response.status_code}")
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

    print("\n[+] Connected to IRC Chat\n")


def IRC_reconnect():
    global delay, attempts

    print("[+] Disconnected, reconnecting...")
    IRC.shutdown(2) #no more data sent/recv
    IRC.close()

    print(f"[+] Waiting {delay}s...\n")
    time.sleep(delay)
    delay *= 2 #exp backoff
    attempts += 1
    
    if attempts == 7:
        print(f"[+] Couldn't connect to the server, closing...")
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


def read_data(q): #TODO better name
    mods = get_mods() #easier than parsing with /tags
    while True: 
        try: 
            select.select([IRC], [], [], 4) #block until timeout, unless irc msg, then don't block
            
            if q.qsize() != 0: #auto pred from livesplit server or notification from eventsub
                data = q.get() #collision?
                
                if type(data) == str:
                    create_prediction(data)
                else: #dict
                    e_status = data['status'] #.end resolved/canceled
                    outcomes = data['outcomes'] #list
                    winning_id = data['winning_id']

                    if data['type'].endswith("begin"):
                        send_data(f"PRIVMSG {CHANNEL} :🎰BETS ARE OPEN🎰")
                    elif data['type'].endswith("lock"):
                        event_prediction_lock(outcomes)
                    elif data['type'].endswith("end"):
                        event_prediction_end(outcomes, e_status, winning_id)
                    
            buffer = IRC.recv(1024).decode() #non-blocking
            buffer = buffer.replace(' \U000e0000', '') #happens when spamming?
            msg = buffer.split()

            if not buffer: #empty = disconnect
                IRC_reconnect()
                continue

            if msg[0] == "PING":
                print("[+] Pinged")
                send_data(f"PONG {msg[1]}")  #user #type_msg #CHANNEL #message

            elif msg[1] == "PRIVMSG": #TODO commands, modcommands, song, pb, wr
                buffer_split = buffer.splitlines()

                for i in buffer_split:
                    username = i[i.find(':')+1:i.find('!')]
                    chat_msg = i[i.find(':', 1)+1:]
                    print(f"{username}: {chat_msg}")

                    if username in mods: #mod commands
                        response = None
                        match chat_msg.split():
                            case ["pred", "start", name]:
                                response = create_prediction(name)

                            case ["pred", "lock"]: #LOCKED
                                response = end_prediction("LOCK")
                            
                            case ["pred", "outcome", outcome] if 0 < int(outcome) <= 10:
                                response = resolve_prediction(int(outcome))
                                    
                            case ["pred", "cancel"]: #CANCELED 
                                response = end_prediction("CANCEL")

                        if response != None: send_data(f"PRIVMSG {CHANNEL} :{response}")

                    #TODO normal commands                        
        except ssl.SSLWantReadError: #happens after timeout
            continue             
        except Exception as e:
            print(f"[+] exception in read_data: {type(e)}")
        

def get_prediction():
    global pred_json

    while True:
        headers = {
            "Authorization": f"Bearer {token_broad}",
            "Client-Id": CLIENT_ID
        }
        response = requests.get(f'https://api.twitch.tv/helix/predictions?broadcaster_id={B_ID}&first=1', headers=headers)

        match response.status_code:
            case 200:
                pred_json = json.loads(response.text)
                break
            case 401: #token expired
                validate_token('broad')


def create_prediction(pred_name):
    with open('predictions/predictions.json', 'r') as file:
        preds = json.load(file)

    not_found = True
    options = ""
    for i in preds['predictions']:
        options += f"{i['name']} "
        if i['name'] == pred_name: #match
            i['data']['broadcaster_id'] = B_ID
            data = i['data']
            not_found = False
        
    if not_found:
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
                break
            case 400: #pred already running
                return "Prediction already running"
            case 401: #expired
                validate_token('broad')
            case 429:
                print("[+] Too many requests")
                break


def resolve_prediction(outcome):
    get_prediction() #update global pred_json

    if pred_json['data'][0]['status'] not in ("ACTIVE", "LOCKED"): #ACTIVE, RESOLVED, CANCELED, LOCKED
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
                break
            case 400:
                print("[+] 400: Something went wrong")
                break
            case 401: #try again
                validate_token('broad')
            case 404:
                print("[+] 404: Not found")
                break


def end_prediction(action): #LOCK or CANCEL
    get_prediction()
    status = pred_json['data'][0]['status'] #ACTIVE, RESOLVED, CANCELED, LOCKED

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
        "status": f"{action}ED"
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
                print("[+] 400: Something went wrong")
                break
            case 401: #try again
                validate_token('broad')
            case 404:
                print("[+] 404: Not found")
                break
        

async def event_handler(q):
    global event_host
    global token_broad
    
    while True:
        try:
            async with websockets.connect((event_host)) as websocket:
                while True:
                    buffer = await asyncio.wait_for(websocket.recv(), 15) #no keepalive = conn died
                    buffer = json.loads(buffer) #dict

                    match buffer['metadata']['message_type']:
                        case 'session_welcome': #first msg after connecting
                            session_id = buffer['payload']['session']['id']
                            print(f"[+] welcome received: {session_id}")
                            with open(f'tokens/token_broad.json') as token_file:
                                token = json.load(token_file)
                                token_broad = token['access_token']
                                
                            event_list = ["channel.prediction.begin", "channel.prediction.lock", "channel.prediction.end"]
                            for event in event_list:
                                sub_to_event(q, session_id, event)
                            print("[+] Listening for predictions...")    
                        case 'session_keepalive': continue #every 10s
                        case 'notification':
                            print("[+] notification received")
                            queue_object(q, buffer)
                        case 'session_reconnect':
                            print("[+] reconnect received")
                            event_host = buffer['payload']['session']['reconnect_url']
                            break
                        case 'revocation':
                            event_type = buffer['payload']['subscription']['type']
                            reason = buffer['payload']['subscription']['status']
                            print(f'[+] Revoked: {event_type} reason: {reason}')
                            continue
                        case _:
                            print("[+] Unknown message")
                            exit()
        except TimeoutError: #no keepalive
            print("[+] Connection lost, reconnecting...")
            continue
        except websockets.exceptions.ConnectionClosedError:
            print("[+] Connection dropped?")
            continue
        except Exception as e:
            print(f"[+] Websockets error: {e}")
            continue



def queue_object(q, buffer): #parsing data to write to chat
    event_type = buffer['payload']['subscription']['type']
    e_status = "xdd"
    winning_id = "xdd"
    outcomes = buffer['payload']['event']['outcomes']

    if event_type.endswith("end"):
        e_status = buffer['payload']['event']['status']
        winning_id = buffer['payload']['event']['winning_outcome_id']
    
    data = {
        "type": event_type,
        "status": e_status,
        "outcomes": outcomes,
        "winning_id": winning_id
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
                break
            case 400:
                print("[+] Bad request" + response.text)
                break
            case 401:
                print("[+] Unauthorized")
                validate_token('broad', q)
            case 403:
                print("[+] Missing scopes")
                break
            case _:
                print(f"[+] Error on sub event: {response.status_code}")
                break


def waiting_process():
    try:
        while True:
            time.sleep(3600) #validate every hour
            old_process = mp.active_children()[0] #indexError = no child
            old_event_process = mp.active_children()[1]
            old_prediction_process = mp.active_children()[2]
            http_code = validate_token('bot')
            http_code2 = validate_token('broad')

            if http_code == 200 and http_code2 == 200: 
                continue
            elif http_code == 401 or http_code2 == 401: 
                print("\n[+] Reconnecting...")
                old_process.terminate()
                old_event_process.terminate()
                old_prediction_process.terminate()
        
                new_process = mp.Process(target=run, daemon=True, args=(q,))
                new_process.start()

                time.sleep(3)
                event_process = mp.Process(target=event_sub, daemon=True, args=(q,))
                event_process.start()

                prediction_process = mp.Process(target=auto_predictions, daemon=True, args=(q,CFG))
                prediction_process.start()
            else:
                print(f"[+] Unknown error: code {http_code} / {http_code2}")
                old_process.terminate()
                old_event_process.terminate()
                break
            
    except IndexError:
        print("\n[+] Child process dead")
    except KeyboardInterrupt:
        print("[+] Closing bot...")
        exit()


def run(q):
    validate_token('bot')
    validate_token('broad')
    IRC_connect()
    read_data(q)


def event_sub(q):
    asyncio.run(event_handler(q))


def auto_predictions(q, CFG):
    predictions.get_self_starting_predictions()
    predictions.main(q, CFG)


if __name__ == "__main__":
    q = mp.Queue()

    process = mp.Process(target=run, daemon=True, args=(q,)) #kill child if parent dies
    process.start() #child

    time.sleep(3)
    event_process = mp.Process(target=event_sub, daemon=True, args=(q,))
    event_process.start()

    prediction_process = mp.Process(target=auto_predictions, daemon=True, args=(q,CFG))
    prediction_process.start()

    waiting_process()