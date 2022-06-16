import datetime
import chicken_dinner.models.match as Match
import chicken_dinner.models.telemetry as Telemetry
from chicken_dinner.pubgapi import PUBG
import analysis.samples.load as Load
from pymongo import MongoClient
from pymongo.cursor import CursorType
import json
import matplotlib.pyplot as plt
import analysis.utils.plot as Plot

def player_position(match):
    tel = Load.get_telemetry(match.id,match)
    chicken_player = tel.winner()[0]
    locations = tel.filter_by("log_player_position")  # 텔레메트리: 포지션으로 필터
    winner_positions = []  # 1등 경로

    start = datetime.datetime.strptime(
        tel.filter_by("log_match_start")[0].timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    # 시작 시간 설정
    for end_location in locations:
        timestamp = datetime.datetime.strptime(
            end_location.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        dt = (timestamp - start).total_seconds()
        player = end_location.character.name  # log_player_position에 기록된 플레이어의 이름
        if player == chicken_player:  # 1등만 추출
            winner_positions.append(
                {
                    "player": player,
                    "timestamp": dt,
                    "x": end_location.character.location.x/1000,
                    "y": end_location.character.location.y/1000,
                    "z": end_location.character.location.z/1000
                }
            )  # 1등 이름, 경과시간, x,y,z
    return winner_positions

def plot_positions(positions: list, color):
    try:
        for i in range(len(positions)):
            plt.plot(positions[i]['position_x'], positions[i]['position_y'], color=color, marker='o')

    except:
        for idx, pos in enumerate(positions):
            plt.plot(pos['x'], pos['y'], color=color, marker='o')

    
def circle_positions(match):
    tel = Load.get_telemetry(match.id,match)
    game_states = tel.filter_by("log_game_state_periodic")
    circle_positions = []
    start = datetime.datetime.strptime(game_states[0].timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    for game_state in game_states:
        timestamp = datetime.datetime.strptime(game_state.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        dt = (timestamp - start).total_seconds()
        if game_state.game_state.poison_gas_warning_position.x != 0:
            circle_positions.append([
                dt,
                game_state.game_state.poison_gas_warning_position.x/1000,
                game_state.game_state.poison_gas_warning_position.y/1000,
                game_state.game_state.poison_gas_warning_radius/1000,
            ])
            break
    result = list([circle_positions[0][1],circle_positions[0][2]])
    return result

def landing_position(match,name):
    tel = Load.get_telemetry(match.id,match)
    chicken_player = name
    
    #print("chicken_player: ", chicken_player)
    landing_locations = tel.filter_by("log_parachute_landing")  # 텔레메트리: 포지션으로 필터
    user_positions = []  # 1등 경로
    
    start = datetime.datetime.strptime(
        tel.filter_by("log_match_start")[0].timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    # 시작 시간 설정
    for landing_location in landing_locations:
        timestamp = datetime.datetime.strptime(
            landing_location.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        dt = (timestamp - start).total_seconds()
        player = landing_location.character.name  # log_player_position에 기록된 플레이어의 이름
        if player == chicken_player:  # 1등만 추출
            user_positions.append(
                {
                    "player": player,
                    "timestamp": dt,
                    "x": landing_location.character.location.x/1000,
                    "y": landing_location.character.location.y/1000,
                    "z": landing_location.character.location.z/1000
                }
            )  # 1등 이름, 경과시간, x,y,z
#    print(user_positions[0].keys())
    result = list([user_positions[0]['x'],user_positions[0]['y']])
    return result

def rec(circle_pos, landing_pos, map_name):
    
    client = MongoClient("mongodb://localhost:27017")
    db = client["PUBG_Analysis"]
    collection = db["Route_recommendation"]

    temp_map_id = map_name
    temp_circle_x = circle_pos[0]
    temp_circle_y = circle_pos[1]
    temp_land_x = landing_pos[0]
    temp_land_y = landing_pos[1]
    i = 1
    while True:
        my_query = {
            "$and": [
                {"map_id": temp_map_id},
                {"land_x": {"$gt": temp_land_x - 10 * i}},
                {"land_x": {"$lt": temp_land_x + 10 * i}},
                {"land_y": {"$gt": temp_land_y - 10 * i}},
                {"land_y": {"$lt": temp_land_y + 10 * i}},
                {"circle_x": {"$gt": temp_circle_x - 10 * i}},
                {"circle_x": {"$lt": temp_circle_x + 10 * i}},
                {"circle_y": {"$gt": temp_circle_y - 10 * i}},
                {"circle_y": {"$lt": temp_circle_y + 10 * i}},
            ]
        }
        temp1 = collection.find_one(my_query)
        if temp1:
            # print(i,"tr")
            temp = collection.find(my_query)
            return temp
        i += 1
        if i == 100: break
        

if __name__ == "__main__":
    api_key = None
    with open("my_api", mode="r") as api_key_file:
        api_key = api_key_file.read()

    pubg = PUBG(api_key=api_key, shard='steam')
    
    # input으로 넣는 값 예시 match_id, user_name
    match = pubg.match('2714ff31-97f5-45fc-95ea-9b35e2660fb8') 
    user_name = 'JDeark'

    map_name = match.map_id
    circle_data = circle_positions(match)
    landing_data = landing_position(match, user_name)
    position_data = player_position(match)

    most_similar_match_between_db_and_input = rec(landing_data,circle_data,map_name)
    position_list = []
    for i in range (len(most_similar_match_between_db_and_input[0]['winner_player_position'])):
        position_list.append(most_similar_match_between_db_and_input[0]['winner_player_position'][i])
   
    # Extracted Data
    # if most_similar_match_between_db_and_input == None : print("There is no similar match, there may be a few match to compare")
    # else :
    #     for x in most_similar_match_between_db_and_input:
    #         print(x)
    player_plot = plot_positions(position_data,'white')
    extracted_plot = plot_positions(position_list,"r")
 
    Plot.plot_map(map_name, "High")
    plt.show()
