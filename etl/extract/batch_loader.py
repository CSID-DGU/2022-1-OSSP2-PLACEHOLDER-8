from datetime import datetime, timedelta
from typing import NewType
from tqdm import tqdm

from chicken_dinner.models.match import Match
from chicken_dinner.models.telemetry import Telemetry
from chicken_dinner.pubgapi import PUBG

from etl.extract import unit_loader

MatchData = NewType('MatchData', tuple[str, Match, Telemetry])


def samples(pubg: PUBG) -> list[str]:
    timestamp = datetime.strftime(
        datetime.utcnow() - timedelta(days=1, hours=1), '%Y-%m-%dT%H:%M:%S.%fZ',
    )
    return pubg.samples(timestamp, 'steam').match_ids


# TODO: multithreading by usage of threading.event
def batch_load(pubg: PUBG, matches: list) -> dict[str, list[MatchData]]:
    match_data_collection = dict()
    for match_id in tqdm(matches):
        match = unit_loader.match(pubg, match_id, _mid=match_id)
        telemetry = unit_loader.telemetry(match, _mid=match_id)
        match_data_collection.setdefault(match.map_id, []).append((match_id, match, telemetry))

    return match_data_collection
