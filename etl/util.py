import os

import matplotlib.pyplot as plt
import numpy as np
import PIL.Image as Image
from chicken_dinner.assets.maps import MAP_ASSET_PATH
from chicken_dinner.constants import map_dimensions
from chicken_dinner.pubgapi import PUBG

from etl import config


def pubg_with_auth():
    api_key = None
    with open(config.APIKEY_PATH, mode='r') as api_key_file:
        api_key = api_key_file.read()
        print('Auth Key:', api_key)

    return PUBG(api_key=api_key, shard='steam')


def plot_map(map_id: str = None, res_option: str = 'Low'):
    for b, f in [
        ('Heaven', 'Haven'),
        ('Tiger', 'Taego'),
        ('Baltic', 'Erangel'),
        ('Chimera', 'Paramo'),
    ]:
        map_id = map_id.replace(b, f)
    map_path = os.path.join(MAP_ASSET_PATH, f'{map_id}_{res_option}_Res.png')
    img_np = np.array(Image.open(map_path))
    size_x, size_y, _ = img_np.shape
    plt.imshow(img_np, extent=(0, *map_dimensions[map_id], 0))
