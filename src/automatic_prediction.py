import socket
from time import sleep
from datetime import timedelta
import json


class Launcher():
    def __init__(self):
        self.default_predictions = self.get_auto_predictions()

    def get_auto_predictions(self) -> list[dict]:
        with open('predictions/predictions.json', 'r') as file:
            data = json.load(file)

        # auto start based on current split
        return [
            {
            "name": p['name'],
            "split_name": p['split_name']
            }
            for p in data['predictions']
            if p['auto_start']
        ]


    def launch(self, q, LOG, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, port))
                sock.settimeout(0.5)
                LOG.logger.info("Connected to Livesplit Server")

                self.auto_predictions = self.default_predictions
                while True:
                    try:
                        sleep(1.5)
                        sock.send(b"getcurrentsplitname\r\n")
                        split_name = sock.recv(1024).decode().rstrip() #remove \r\n
                        
                        #sock.send(b"getcurrenttime\r\n")
                        #raw_time = sock.recv(1024).decode().rstrip()[:-3] #no ms
                        #current_time = convert_to_hms(raw_time)
                        #print(f"{split_name} : {current_time}")
                        
                        for pred in self.auto_predictions:
                            if pred['split_name'].lower() == split_name.lower():
                                q.put(AutomaticPrediction(pred['name'])) #send to other process
                                self.auto_predictions.remove(pred)
                                LOG.logger.info(f"Auto started at {split_name}")
                                
                        #do things based on name and/or time
                    except TimeoutError: 
                        # inactive timer
                        self.auto_predictions = self.default_predictions
                        continue
        except ConnectionRefusedError:
            LOG.logger.warning("Predictions will not start automatically by split, start Livesplit Server and restart the bot")
        except ConnectionAbortedError:
            LOG.logger.error("Connection to Livesplit Server was aborted, will continue without automatic predictions")

    def convert_to_hms(self, raw_time):
        hms_list = raw_time.split(':') #[1,22,33] or [18,16]
        hours_in_seconds = 0
        minutes_in_seconds = int(hms_list[-2]) * 60
        seconds = int(hms_list[-1])

        if len(hms_list) == 3: #hh:mm:ss
            hours_in_seconds = int(hms_list[0]) * 3600

        total_seconds = hours_in_seconds + minutes_in_seconds + seconds
        return str(timedelta(seconds=total_seconds))
    

class AutomaticPrediction():
    def __init__(self, split):
        self.split = split