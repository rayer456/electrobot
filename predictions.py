import socket
from time import sleep
import datetime
import json


HOST = "127.0.0.1"
PORT = 16834


def main(q):
    global auto_predictions

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.settimeout(2.0)

        while True:
            try:
                sleep(5)

                sock.send(b"getcurrentsplitname\r\n")
                split_name = sock.recv(1024).decode().rstrip() #remove \r\n
                
                sock.send(b"getcurrenttime\r\n")
                raw_time = sock.recv(1024).decode().rstrip()[:-3] #no ms

                current_time = convert_to_hms(raw_time)

                print(f"{split_name} : {current_time}")
                
                for pred in auto_predictions:
                    if pred['split_name'].lower() == split_name.lower():
                        q.put(f"start {pred['name']}")
                        print(f"Start the {pred['name']} prediction!!")
                        auto_predictions.remove(pred)


                if split_name == 'DLG' and current_time <= '0:39:10': #pace
                    #start prediction
                    print("PB??")
            except TimeoutError: #reset, add new predictions again
                get_self_starting_predictions()
                continue
            except KeyboardInterrupt:
                break


def get_self_starting_predictions():
    global auto_predictions

    with open('predictions/predictions.json', 'r') as file:
        data = json.load(file)

    auto_predictions = [] #predictions that auto start based on current split
    for p in data['predictions']:
        if p['auto_predict']['auto_start'] == True:
            auto_pred = {
                "name": p['name'],
                "split_name": p['auto_predict']['split_name']
            }
            auto_predictions.append(auto_pred)


def convert_to_hms(current_time):
    hms_list = current_time.split(':') #[1,22,33] or [4,16]
    hours_in_seconds = 0
    minutes_in_seconds = int(hms_list[-2]) * 60
    seconds = int(hms_list[-1])

    if len(hms_list) == 3: #hh:mm:ss
        hours_in_seconds = int(hms_list[0]) * 3600

    total_seconds = hours_in_seconds + minutes_in_seconds + seconds

    return str(datetime.timedelta(seconds=total_seconds))