import json

class ProductRepository:
    def load_data(self):
        with open("trademark_sample.json", "r") as f:
            data = json.load(f)
        return data
