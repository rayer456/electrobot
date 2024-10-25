class Prediction():
    def __init__(self, split_name: str, auto_start: bool, pred_split_name: str, pred_name: str, data_to_send: dict, is_empty):
        self.split_name = split_name
        self.auto_start = auto_start
        self.pred_split_name = pred_split_name
        self.pred_name = pred_name
        self.data_to_send = data_to_send
        self.is_empty = is_empty

    def empty(split_name: str):
        return Prediction(
            split_name=split_name,
            auto_start=False,
            pred_split_name="",
            pred_name="",
            data_to_send={},
            is_empty=True
        )
    
    def pred_as_json(self) -> dict:
        return {
            "auto_start": self.auto_start,
            "split_name": self.pred_split_name,
            "data": self.data_to_send,
            "name": self.pred_name,
        }
    
    def as_json(self) -> dict:
        pred = {}
        if not self.is_empty:
            pred = self.pred_as_json()
        return {
            "prediction": pred,
            "split_name": self.split_name,
        }
    
    def reset(self):
        self.is_empty = True
        self.auto_start = False
        self.pred_split_name = ""
        self.pred_name = ""
        self.data_to_send = {}

    
    