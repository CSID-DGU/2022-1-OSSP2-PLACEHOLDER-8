from datetime import datetime, timedelta

from chicken_dinner.models.match import Match
from chicken_dinner.models.telemetry import Telemetry
from chicken_dinner.pubgapi import PUBG

from etl.extract import unit_loader


def samples(pubg: PUBG) -> list:
    timestamp = datetime.strftime(
        datetime.utcnow() - timedelta(days=1),
        '%Y-%m-%dT%H:%M:%S.%fZ',
    )
    return pubg.samples(timestamp, 'steam').match_ids


def batch_load(pubg: PUBG, matches: list) -> list:
    data = []
    for match_id in matches:
        match = unit_loader.match(pubg, match_id, _mid=match_id)
        telemetry = unit_loader.telemetry(match, _mid=match_id)
        data.append((match_id, match, telemetry))
    
    return data