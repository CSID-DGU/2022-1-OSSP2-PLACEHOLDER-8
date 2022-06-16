import datetime
import json
import matplotlib.pyplot as plt
import os
import numpy as np
import chicken_dinner.models.match as Match
import chicken_dinner.models.telemetry as Telemetry
from chicken_dinner.pubgapi import PUBG
from random import *
#import analysis.utils.plot as Plot
#import analysis.samples.load as Load
from collections import OrderedDict
from pymongo import MongoClient
from pymongo.cursor import CursorType
import json




def db_insert(data):
    client = MongoClient("mongodb://localhost:27017")
    db = client["PUBG_Analysis"]
    collection = db["Route_recommendation"]

    file_data = OrderedDict()
    
    file_data["land_x"] = float(data[3][0]) 
    file_data["land_y"] = float(data[3][1])
    file_data["end_x"] = float(data[4][0])
    file_data["end_y"] = float(data[4][1])
    file_data["circle_x"] = float(data[5][0])
    file_data["circle_y"] = float(data[5][1])
    file_data["winner_player_position"] = []
    for i in range(len(data[6])):
        file_data["winner_player_position"].append({
            "position_x" : float(data[6][i]['x']),
            "position_y" : float(data[6][i]['y'])
        })
    match_id = str(data[7])
    map_name = str(data[8])
    file_data["match_id"] = match_id
    file_data["map_id"] = map_name
    db.Route_recommendation.insert_one(file_data)


def make_json(data):
    file_data = OrderedDict()
    
    file_data["land_x"] = float(data[3][0]) 
    file_data["land_y"] = float(data[3][1])
    file_data["end_x"] = float(data[4][0])
    file_data["end_y"] = float(data[4][1])
    file_data["circle_x"] = float(data[5][0])
    file_data["circle_y"] = float(data[5][1])
    file_data["winner_player_position"] = []
    for i in range(len(data[6])):
        file_data["winner_player_position"].append({
            "position_x" : float(data[6][i]['x']),
            "position_y" : float(data[6][i]['y'])
        })
    match_id = str(data[7])
    map_name = str(data[8])
    file_data["match_id"] = match_id
    file_data["map_id"] = map_name

    #print(json.dumps(file_data,ensure_ascii = False, indent = "\t"))

    filename = match_id + map_name
    with open(f'{filename}.json', 'w', encoding = "utf-8") as make_file:
        json.dump(file_data, make_file, ensure_ascii = False, indent = "\t")


def plot_positions(positions: list, color):
    for idx, pos in enumerate(positions):
        plt.plot(pos['x'], pos['y'], color=color, marker='o')


def open_tel(match_id):
    tel_path = os.path.join(
        r'C:\Users\juhon\Desktop\gitPUBG\PUBG_analysis\samples\samples',
        f'match_{match_id}',
        'telemetry.json',
    )
    with open(tel_path, "r") as tel_file:
        raw_json = json.load(tel_file)
    return raw_json

@Load.pickle_loader('circle_positions_v5.pickle')
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
    return circle_positions[0]

@Load.pickle_loader('landing_positions_v5.pickle')
def landing_position(match):

    tel = Load.get_telemetry(match.id,match)
    chicken_player = tel.winner()[0]
    #print("chicken_player: ", chicken_player)
    landing_locations = tel.filter_by("log_parachute_landing")  # 텔레메트리: 포지션으로 필터
    winner_positions = []  # 1등 경로

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
            winner_positions.append(
                {
                    "player": player,
                    "timestamp": dt,
                    "x": landing_location.character.location.x/1000,
                    "y": landing_location.character.location.y/1000,
                    "z": landing_location.character.location.z/1000
                }
            )  # 1등 이름, 경과시간, x,y,z
    return winner_positions

@Load.pickle_loader('ending_positions_v5.pickle')
def end_position(match):
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
    winner_positions.reverse()
    return winner_positions

def plot_landing(landing_list) :
    x = landing_list[0]['x']
    y = landing_list[0]['y']
    return x,y

def plot_ending(end_list) :
    x = end_list['x']
    y = end_list['y']
    return x,y

def sim_msd(match1_data, match2_data) :
    temp_sum1,temp_sum2,sum = 0,0,0 
    count = 0
    match1_circle_x = match1_data[2][0]
    match1_circle_y = match1_data[2][1]
    match2_circle_x = match2_data[2][0]
    match2_circle_y = match2_data[2][1]

    for i in range(2):
        for j in range(2):
            temp_sum1 += pow((int)(match1_data[i][j]-match2_data[i][j]),2) / 4
            count += 1
    temp_sum2 += (pow((int)(match1_circle_x-match2_circle_x),2) + pow((int)(match1_circle_y-match2_circle_y),2))/2
    sum = temp_sum1 *0.7 + temp_sum2*0.3
    return 1 / (1 + (sum / count))

def regionalization(data):
    temp_x = 0
    temp_y = 0 
    for i in range(10):
        if data[0] > i * 80 and data[0] < (i + 1) * 80 : 
            temp_x = i
    for j in range(10):
        if data[1] > j * 80 and data[1] < (j + 1) * 80 : 
            temp_y = j
    #print("X, Y 구역: ", temp_x , temp_y)
    return [temp_x, temp_y]

def plot_recommendation(data,color):
    land_x, land_y = data[0] * 80 + 40, data[0] * 80 + 40 
    end_x, end_y = data[1] * 80 + 40, data[1] * 80 + 40
    dx = end_x - land_x
    dy = end_y - land_y
    #print("x : ", land_x,"y : ",land_y)
    plt.arrow(land_x, land_y, dx, dy,color = color)
    return 0


if __name__ == "__main__":
    api_key = None
    with open("my_api", mode="r") as api_key_file:
        api_key = api_key_file.read()
        #print(api_key)

    pubg = PUBG(api_key=api_key, shard='steam')
    samples = pubg.samples().match_ids[:200]
    print(len(samples))
    i=1
    compare_list=[]
    source_list=[]
    for s in samples:
        match = pubg.match(s)
        if match.map_id != 'Desert_Main':
            #print('Nah.', match.game_mode, match.map_id)
            continue
        
        print(match.id, 'is working!')
        map_id: str = match.map_id.replace(" ", "_")
        for b, f in [('Heaven', 'Haven'), ('Tiger', 'Taego')]:
            map_id = map_id.replace(b, f)
        sample_length = len(samples)
        i = i + 1
        circle_data = circle_positions(match.id, match)
        landing_data = landing_position(match.id, match)
        end_data = end_position(match.id, match)[0]
        move_data = end_position(match.id, match)

        land = list(plot_landing(landing_data))
        end = list(plot_ending(end_data))
        circle = list([circle_data[1],circle_data[2]])
        region_land = regionalization(land)
        region_end = regionalization(end)
        region_circle = regionalization(circle)

        
        if region_land != region_end:
            compare_list.append([region_land,region_end,region_circle,land,end,circle,move_data,match.id,match.map_id]) #, tel
            
    length = len(compare_list) 
    similar_position=[]
    count=[0 for i in range(length)]
    for i in range(length) :
        for j in range(length):
            if i != j : 
                similarity = round(sim_msd(compare_list[i],compare_list[j]),5)
                #print("similarity: ",similarity)
                if similarity >= 0.5 :
                    #print("input : ", compare_list[i])
                    count[i] +=1
                #print(i, " : ", j, " = ", similarity)
    result=[]

    for i in range(len(count)):
        if count[i] >= 10 :
            similar_position.append(compare_list[i])
    for value in similar_position:
        if value not in result:
            result.append(value)
    for i in range(len(result)):
        random_R = random()
        random_G = random()
        random_B = random()

        color=[random_R, random_G, random_B]
       
        land_x = result[i][3][0]  
        land_y = result[i][3][1] 
        end_x = result[i][4][0] 
        end_y = result[i][4][1]  
        circle_x = result[i][5][0] 
        circle_y = result[i][5][1]  
        dx = end_x - land_x
        dy = end_y - land_y 
        center = (circle_x, circle_y)
        winner_movement = result[i][6]
        plot_positions(winner_movement,color=color)
        plt.plot(land_x,land_y,color=color,marker="o",linewidth=3)
        plt.plot(end_x,end_y,color=color,marker="x",linewidth=3)
        plt.arrow(land_x, land_y, dx, dy,color = color,linewidth=3)
        circle = plt.Circle(center, 200, fill=False, ec=color,linewidth=3)
        plt.gca().add_patch(circle)
       
        #make_json(result[i])
        db_insert(result[i])
    Plot.plot_map(map_id, "High")
    plt.show()
    

