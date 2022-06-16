import numpy as np

import matplotlib.pyplot as plt

from etl.extract import batch_loader
from etl.transfrom import kd_heatmap
from etl.load import loader
from etl import util

def plot_heatmap(hset):
    xx, yy, z = hset
    plt.pcolormesh(xx, yy, z, cmap='RdBu', alpha=0.5)
    plt.colorbar()
    plt.show()

if __name__ == '__main__':
    pubg = util.pubg_with_auth()
    matches = batch_loader.samples(pubg)
    
    print(len(matches))
    match_data_collection = batch_loader.batch_load(pubg, matches[:3])

    # DEBUG
    for a, b in match_data_collection.items():
        print(a, len(b))

    kd_func_collection = kd_heatmap.calculate_heatmap(match_data_collection)

    loader.upload_object(kd_func_collection)