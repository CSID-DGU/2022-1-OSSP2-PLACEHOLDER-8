import pickle

import requests

from etl import config

def save_as_pickle(_o):
    with open(config.INSTANCE_PATH, 'wb') as pickle_file:
        pickle.dump(_o, pickle_file)


def upload_object(_o):
    save_as_pickle(_o)
    with open(config.INSTANCE_PATH,'rb') as pickle_file:
        files = {'file': pickle_file}
        try:
            response = requests.post(config.SERVER_URL, files=files)
            if response.ok:
                print('YAY')
            else:
                print('OH.')
        except:
            print('OOH.')