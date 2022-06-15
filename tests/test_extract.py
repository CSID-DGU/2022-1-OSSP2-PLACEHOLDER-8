from datetime import datetime, timedelta

from chicken_dinner.models.match import Match
from chicken_dinner.models.telemetry import Telemetry
from chicken_dinner.pubgapi import PUBG

from etl.extract import unit_loader
from etl import util


if __name__ == '__main__':
    pubg = util.pubg_with_auth()
    timestamp = datetime.strftime(
        datetime.utcnow() - timedelta(days=1),
        '%Y-%m-%dT%H:%M:%S.%fZ',
    )
    matches = pubg.samples(timestamp, 'steam').match_ids
    print(len(matches))
    for match_id in reversed(matches):
        match = unit_loader.match(pubg, match_id, _mid=None)
        print(match.created_at)
    telemetry = unit_loader.telemetry(match, _mid=match_id)
    