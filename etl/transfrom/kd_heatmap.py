from math import isclose
from typing import Callable, NewType

import numpy as np
from chicken_dinner.models.match import Match
from chicken_dinner.models.telemetry import Telemetry, TelemetryObject
from scipy import interpolate

from etl import config, util
from etl.extract.batch_loader import MatchData
from etl.transfrom import heatmap

KillData = NewType('KillData', tuple[TelemetryObject, TelemetryObject])
Mgset = NewType('Mgset', tuple[np.ndarray, np.ndarray, np.ndarray])


def is_valid_kill(t: TelemetryObject):
    return True


def extract_kill_location(
    match_datas: dict[str, list[MatchData]]
) -> dict[str, list[KillData]]:
    kill_loc_collection = dict()
    for map_id, match_data_per_map in match_datas.items():
        kills = []
        for _, _, telemetry in match_data_per_map:
            kill_events = telemetry.filter_by('log_player_kill_v2')
            for event in kill_events:
                if event.killer is None:
                    continue
                elif isclose(event.killer.location.x, 0) or isclose(
                    event.victim.location.x, 0
                ):
                    continue

                killer_location, victim_location = event.killer.location, event.victim.location
                kills.append((killer_location, victim_location))
        kill_loc_collection[map_id] = kills

    return kill_loc_collection


def get_distribution_mgset(kill_loc_collection: dict[str, list[KillData]]):
    dist_mgset_collection = dict()
    for map_id, kill_loc in kill_loc_collection.items():
        linspace_x, linspace_y = heatmap.ready_meshgrid(map_id, 100)
        mggrid = heatmap.new_grid(linspace_x, linspace_y)
        sigma_mgset = linspace_x, linspace_y, mggrid
        for killer_location, victim_location in kill_loc:
            kx, ky = killer_location.x, killer_location.y
            vx, vy = victim_location.x, victim_location.y
            heatmap.add_sticker(
                sigma_mgset,
                pos=(kx, ky),
                amp=1.0,
                sigma=config.DISTRIBUTION_MAP_SIGMA,
                prob_mode=False,
            )
            heatmap.add_sticker(
                sigma_mgset,
                pos=(vx, vy),
                amp=1.0,
                sigma=config.DISTRIBUTION_MAP_SIGMA,
                prob_mode=False,
            )
        result = 1 / (np.power(sigma_mgset[2] + 1, 0.5))
        dist_mgset_collection[map_id] = (linspace_x, linspace_y, result)

    return dist_mgset_collection


def get_kd_mgset(
    kill_loc_collection: dict[str, list[KillData]], dist_mgset_collection: dict[str, Mgset]
) -> dict[str, Mgset]:
    kd_mgset_collection = dict()
    map_id_list = dist_mgset_collection.keys()
    for map_id in map_id_list:
        kill_loc = kill_loc_collection[map_id]
        dist_mgset = dist_mgset_collection[map_id]
        sigma_func = interpolate.RectBivariateSpline(*dist_mgset)

        linspace_x, linspace_y = heatmap.ready_meshgrid(map_id, 400)
        kill_mggrid = heatmap.new_grid(linspace_x, linspace_y)
        kill_mgset = (linspace_x, linspace_y, kill_mggrid)
        death_mggrid = heatmap.new_grid(linspace_x, linspace_y)
        death_mgset = (linspace_x, linspace_y, death_mggrid)
        for killer_location, victim_location in kill_loc:
            kx, ky = killer_location.x, killer_location.y
            vx, vy = victim_location.x, victim_location.y
            heatmap.add_sticker(
                kill_mgset,
                pos=(kx, ky),
                amp=1.0,
                sigma=(config.KD_MAP_SIGMA_AMP * sigma_func(kx, ky)),
            )
            heatmap.add_sticker(
                death_mgset,
                pos=(vx, vy),
                amp=1.0,
                sigma=(config.KD_MAP_SIGMA_AMP * sigma_func(vx, vy)),
            )

        result_mggrid = np.log2((kill_mggrid + 0.001) / (death_mggrid + 0.001))
        result_mggrid = np.tanh(result_mggrid)
        kd_mgset_collection[map_id] = (linspace_x, linspace_y, result_mggrid)
    return kd_mgset_collection


def get_kd_func(kd_mgset_collection: dict[str, Mgset]) -> dict[str, Callable]:
    kd_func_collection = dict()
    for map_id, kd_mgset in kd_mgset_collection.items():
        kd_func = interpolate.RectBivariateSpline(*kd_mgset)
        kd_func_collection[map_id] = kd_func
    return kd_func_collection


def calculate_heatmap(match_data_collection: dict[str, list[MatchData]]):
    # get kills on one list
    kill_loc_collection = extract_kill_location(match_data_collection)

    # DEBUG
    for a, b in kill_loc_collection.items():
        print(a, len(b))

    # using kills, get distribution-map
    dist_mgset_collection = get_distribution_mgset(kill_loc_collection)

    # DEBUG
    # for map_id, mgset in dist_mgset_collection.items():
    #     print(map_id, mgset[2])

    # using distribution-map and kills, get kill-map & death-map => kd-map
    kd_mgset_collection = get_kd_mgset(kill_loc_collection, dist_mgset_collection)

    # DEBUG
    # for map_id, mgset in kd_mgset_collection.items():
    #     print(map_id, mgset[2].shape)

    # kd-map into function using interpolation
    kd_func_collection = get_kd_func(kd_mgset_collection)

    # DEBUG
    for map_id, kd_func in kd_func_collection.items():
        print(map_id, kd_func(400000, 400000))


    return kd_func_collection
