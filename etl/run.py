import numpy as np

import matplotlib.pyplot as plt
from chicken_dinner.models.match import Match
from chicken_dinner.models.telemetry import Telemetry
from chicken_dinner.pubgapi import PUBG

from etl.extract import batch_loader
from etl.transfrom import kd_heatmap
from etl.load import loader
from etl import util


def main():
    # Auth
    pubg = util.pubg_with_auth()
    
    # Extraction
    matches = batch_loader.samples(pubg)
    print(len(matches))
    match_data_collection = batch_loader.batch_load(pubg, matches[:50])

    # Transformation
    kd_func_collection = kd_heatmap.calculate_heatmap(match_data_collection)

    # Load
    loader.upload_object(kd_func_collection)

if __name__ == '__main__':
    main()
