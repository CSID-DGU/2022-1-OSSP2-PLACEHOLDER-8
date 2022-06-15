from chicken_dinner.pubgapi import PUBG

from etl import config

def pubg_with_auth():
    api_key = None
    with open(config.APIKEY_PATH, mode='r') as api_key_file:
        api_key = api_key_file.read()
        print('Auth Key:', api_key)
    
    return PUBG(api_key=api_key, shard='steam')