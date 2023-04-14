import socket
from time import sleep
from datetime import timedelta
import json


def main(q, CFG, LOG):
    global auto_predictions

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CFG['livesplit']['HOST'], CFG['livesplit']['PORT']))
            sock.settimeout(0.5)
            LOG.logger.info("Connected to Livesplit Server")

            while True:
                try:
                    sleep(1)
                    sock.send(b"getcurrentsplitname\r\n")
                    split_name = sock.recv(1024).decode().rstrip() #remove \r\n
                    
                    #sock.send(b"getcurrenttime\r\n")
                    #raw_time = sock.recv(1024).decode().rstrip()[:-3] #no ms
                    #current_time = convert_to_hms(raw_time)
                    #print(f"{split_name} : {current_time}")
                    
                    for pred in auto_predictions:
                        if pred['split_name'].lower() == split_name.lower():
                            q.put(pred['name']) #send to other process
                            auto_predictions.remove(pred)
                            LOG.logger.debug(f"Auto started at {split_name}")
                            
                    #do things based on name and/or time

                except TimeoutError: #run reset, add predictions again
                    get_self_starting_predictions()
                    continue
    except ConnectionRefusedError:
        LOG.logger.warning("Predictions will not start automatically by split")
        LOG.logger.warning("Start Livesplit Server and restart the bot")


def get_self_starting_predictions():
    global auto_predictions

    with open('predictions/predictions.json', 'r') as file:
        data = json.load(file)

    auto_predictions = [] #auto start based on current split
    for p in data['predictions']:
        if p['auto_predict']['auto_start'] == True:
            auto_pred = {
                "name": p['name'],
                "split_name": p['auto_predict']['split_name']
            }
            auto_predictions.append(auto_pred)


def convert_to_hms(raw_time):
    hms_list = raw_time.split(':') #[1,22,33] or [18,16]
    hours_in_seconds = 0
    minutes_in_seconds = int(hms_list[-2]) * 60
    seconds = int(hms_list[-1])

    if len(hms_list) == 3: #hh:mm:ss
        hours_in_seconds = int(hms_list[0]) * 3600

    total_seconds = hours_in_seconds + minutes_in_seconds + seconds
    return str(timedelta(seconds=total_seconds))