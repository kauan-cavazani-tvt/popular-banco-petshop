import json

def getConfig(probability):
    with open('src/config/probabilities.json', 'r') as f:
        config = json.load(f)
        return config[probability]