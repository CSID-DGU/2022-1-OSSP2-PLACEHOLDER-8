from datetime import datetime, timedelta

from chicken_dinner.models.match import Match
from chicken_dinner.models.telemetry import Telemetry
from chicken_dinner.pubgapi import PUBG

from etl.extract import unit_loader, batch_loader
from etl import util


if __name__ == '__main__':
    pubg = util.pubg_with_auth()
    matches = batch_loader.samples(pubg)
    
    print(len(matches))
    result = batch_loader.batch_load(pubg, matches[:10])