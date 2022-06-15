import functools
import os
import pickle
from typing import Callable
from typing import TypeVar

from chicken_dinner.models.match import Match
from chicken_dinner.models.telemetry import Telemetry
from chicken_dinner.pubgapi import PUBG

import etl.config as config


def _is_pickle_exists(pickle_path):
    return os.path.exists(pickle_path)


def _open_obj_from_pickle(pickle_path):
    with open(pickle_path, 'rb') as pickle_file:
        obj = pickle.load(pickle_file)
    return obj


def _save_obj_as_pickle(pickle_path, obj):
    os.makedirs(os.path.dirname(pickle_path), exist_ok=True)
    with open(pickle_path, 'wb') as pickle_file:
        pickle.dump(obj, pickle_file)
    return obj


R = TypeVar('R')
def pickle_loader(_name: str):
    """[Decorator] save result as pickle.
    if pickle exists, load it or run function and save.
    match_id is needed as a function arg.

    @_name: name of pickle file
    """

    def wrapper(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def inside(*args, _mid=None):
            if _mid is None:
                return func(*args)

            pickle_path = os.path.join(config.CACHE_PATH, _mid, _name)
            if _is_pickle_exists(pickle_path):
                obj = _open_obj_from_pickle(pickle_path)
            else:
                print(f"[LOG]\tNo pickle '{_name}' in {_mid}")
                obj = _save_obj_as_pickle(pickle_path, func(*args))
            return obj

        return inside

    return wrapper


@pickle_loader('match.pickle')
def match(pubg: PUBG, match_id: str) -> Match:
    return pubg.match(match_id)


@pickle_loader('telemetry.pickle')
def telemetry(match: Match) -> Telemetry:
    return match.get_telemetry()
