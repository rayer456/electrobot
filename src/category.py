class Category():
    def __init__(self, active: bool, game_name: str, category: str, split_predictions: list):
        self.active = active
        self.game_name = game_name
        self.category = category # should maybe be called "name"?
        self.split_predictions = split_predictions

    #TODO maybe add a function that takes a function as argument and applies it on every prediction?

    def as_json(self) -> dict:
        return {
            "active": self.active,
            "category": self.category,
            "game_name": self.game_name,
            "split_names": [pred.as_json() for pred in self.split_predictions],
        }


