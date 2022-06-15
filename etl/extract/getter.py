import functools
import os
import pickle
from typing import Callable

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


def pickle_loader(_name: str):
    """
    [Decorator] save result as pickle
    if pickle exists load else run func
    param:
    _name - file name
    _mid - match id
    *args - function arguments 
    """

    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        def inside(*args, **kwargs):
            _mid = kwargs.get('match_id')
            if _mid is None:
                return func(*args)

            pickle_path = os.join(config.CACHE_PATH, _mid, _name)
            if _is_pickle_exists(pickle_path):
                obj = _open_obj_from_pickle(_mid, _name)
            else:
                print(f"[LOG]\tNo pickle '{_name}' in {_mid}")
                obj = _save_obj_as_pickle(_mid, _name, func(*args))
            return obj

        return inside

    return wrapper


@pickle_loader('match.pickle')
def get_match(pubg: PUBG, match_id: str) -> Match:
    return pubg.match(match_id)


@pickle_loader('telemetry.pickle')
def get_telemetry(match: Match) -> Telemetry:
    return match.get_telemetry()
