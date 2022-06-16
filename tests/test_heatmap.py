import matplotlib.pyplot as plt

from etl.transfrom import heatmap
from etl import util

def plot_heatmap(hset):
    xx, yy, z = hset
    plt.pcolormesh(xx, yy, z, cmap='RdBu', alpha=0.5)
    plt.colorbar()
    plt.show()


if __name__ == '__main__':
    target_map_id = 'Erangel_Main'
    xx_, yy_ = heatmap.ready_meshgrid(target_map_id, 100)
    z = heatmap.new_grid(xx_, yy_)
    mgset = (xx_, yy_, z)
    heatmap.add_sticker(mgset, (419200, 219200), 10000, 1)
    util.plot_map(target_map_id, 'High')
    plot_heatmap(mgset)