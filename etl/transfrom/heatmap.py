import numpy as np
from chicken_dinner.constants import map_dimensions

from etl import config


def ready_meshgrid(map_id: str, num_split: int):
    x_size, y_size = map_dimensions[map_id]
    x_range = (0, x_size)
    y_range = (0, y_size)

    x = np.linspace(*x_range, num_split)
    y = np.linspace(*y_range, num_split)
    xx, yy = np.meshgrid(x, y, indexing='xy', sparse=True)
    return xx, yy


def new_grid(xx, yy):
    return (xx + yy) * 0


def _sticker(xx, yy, pos: tuple, sigma: float):
    """
    add gaussian kernel sticker
    """
    pos_x, pos_y = pos
    dist = (xx - pos_x) ** 2 + (yy - pos_y) ** 2
    sticker_map = np.exp(-dist / (2 * (sigma ** 2)))
    return sticker_map


def add_sticker(mgset: tuple, pos: tuple, sigma: float, amp: float, prob_mode: bool = True):
    xx, yy, z = mgset
    if prob_mode:
        amp /= np.sqrt(2 * np.pi) * sigma
    z += _sticker(xx, yy, pos, sigma) * amp
