import functools
import os
import random
import datetime
from re import template
from django.shortcuts import render
from flask import Flask, jsonify,send_file
import matplotlib
matplotlib.use('Agg')
from io import BytesIO, StringIO
import numpy as np
import matplotlib.pyplot as plt
import click
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask.cli import with_appcontext
from scipy import interpolate
from pymongo import MongoClient
from pymongo.cursor import CursorType
from chicken_dinner.pubgapi import PUBG
from chicken_dinner.constants import COLORS
from difflib import Match
from chicken_dinner.models.telemetry import Telemetry
import PIL.Image
import urllib.request as req
import matplotlib.patches as patches  # 원 추가
from matplotlib.figure import Figure
import base64
from difflib import Match

bp = Blueprint('match', __name__, url_prefix='/match')



@bp.route('/data/<string:id>')

def search_by_circle(id):

    def pubg():
        # api_key = None
        # with open('my_api', mode='r') as api_key_file:
        #     api_key = api_key_file.read()
        #     print('Auth key:', api_key)
        api_key="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2NzNlZGFhMC1hOWZlLTAxM2EtY2I4Ni0wMTM2YWI5NGY3N2IiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjUxMjQ1ODc2LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImZyb3plbmRvZyJ9.mdDyb3P1KCBcNIk5xKeu7B7IWOIIaWpAc9JKL7TGyiY"
        return PUBG(api_key=api_key, shard='steam')
    

    map_dimensions = {
    'Desert_Main': [819200, 819200],
    'Erangel_Main': [819200, 819200],
    'Savage_Main': [409600, 409600],
    'DihorOtok_Main': [614400, 614400],
    'Range_Main': [204800, 204800],
    'Baltic_Main': [819200, 819200],
    'Summerland_Main': [204800, 204800],
    }


    def mapsize(map_name):
        map_name_list = list(map_dimensions.keys())

        map_x, map_y = 0, 0
        for i in range(len(map_name_list)):
            if map_name == map_name_list[i]:
                map_x = map_dimensions[map_name][0] / 800
                map_y = map_dimensions[map_name][1] / 800
                break
        return map_x, map_y




    def get_match(pubg: PUBG, match_id: str)->Match:
        return pubg.match(match_id)

    def get_telemetry(match: Match) -> Telemetry:
        return match.get_telemetry()
    
    def get_all_circle(circles):# 중복 자기장 포함 모든 white 자기장 정보 가져오기
        all_circle=[]
        for i in circles["white"]:
            if(i[4]>0):
                all_circle.append(i)
        return all_circle

    def get_circle_list(all_circle):#중복 자기장 제거

        k=0
        all_circle_dup=[]
        while k < len(all_circle)-1:
            if all_circle[k+1][4] -all_circle[k][4] < 0:
                all_circle_dup.append(all_circle[k+1])
            k += 1

        # all_circle_dup.insert(0, all_circle[0]) #db삽입할땐 주석첟리     
        return all_circle_dup

  

    def get_feature(match)->dict:
            
        circles1 = match.get_telemetry().circle_positions()
        all_circle1 = get_all_circle(circles1)
        circle_list1 = get_circle_list(all_circle1)
            
            
        key=["Match_ID","F_Circle_x","F_Circle_y","L_Circle_x","L_Circle_y","Map_Name","Match_Mode"]
        dict={}
        dict[key[0]]=match.id
            
            
        dict[key[1]]=circle_list1[0][1]
        dict[key[2]]=circle_list1[0][2]
        dict[key[3]]=circle_list1[-1][1]
        dict[key[4]]=circle_list1[-1][2]
        dict[key[5]]=match.map_name
        dict[key[6]]=match.game_mode
        return dict

        
    def compare_db(input_map_name,input_game_mode,input_F_Circle_x,input_F_Circle_y,input_L_Circle_x,input_L_Circle_y):

        i = 1
        while True:
            my_query = {
                "$and": [
                    {"Map_Name": input_map_name},
                    {"Match_Mode": input_game_mode},
                    {"F_Circle_x": {"$gt": input_F_Circle_x - 100 * i}},
                    {"F_Circle_x": {"$lt": input_F_Circle_x + 100 * i}},
                    {"F_Circle_y": {"$gt": input_F_Circle_y - 100 * i}},
                    {"F_Circle_y": {"$lt": input_F_Circle_y + 100 * i}},
                    {"L_Circle_x": {"$gt": input_L_Circle_x - 100 * i}},
                    {"L_Circle_x": {"$lt": input_L_Circle_x + 100 * i}},
                    {"L_Circle_y": {"$gt": input_L_Circle_y - 100 * i}},
                    {"L_Circle_y": {"$lt": input_L_Circle_y + 100 * i}},
                    
                    
                    
                ]
            }
            # temp = bool(collection.find(my_query))
            temp1 = collection.find_one(my_query)
            if temp1:
                # print(i,"tr")
                temp = collection.find(my_query)
                # for x in temp:
                #     print(x)
                return temp

                #break
            i += 1
            if i == 10000: break



    def winner_position(tel):
        """
        available only in 'solo' mode
        param:
        """
        #tel = match.get_telemetry()
        chicken_player = tel.winner()[0]
        locations = tel.filter_by('log_player_position')  # 텔레메트리: 포지션으로 필터
        locations = [location for location in locations if location.elapsed_time > 0]
        # 게임 시작 후 경과시간 0 이상인 것들만 찾기// 찾아보니까 본 게임 시작하기 전에 다같이 모여 있는 광장이 있던데 여기서 움직이는 걸 제외한 것이라고 보여요

        player_positions = []  # 1등 경로
        start = datetime.datetime.strptime(
            tel.filter_by('log_match_start')[0].timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        # 시작 시간 설정
        for location in locations:
            timestamp = datetime.datetime.strptime(location.timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            dt = (timestamp - start).total_seconds()
            player = location.character.name  # log_player_position에 기록된 플레이어의 이름
            if player == chicken_player:  # 1등만 추출
                player_positions.append(
                    {
                        'player': player,
                        'timestamp': dt,
                        'x': location.character.location.x / 1000,
                        'y': location.character.location.y / 1000,
                        'z': location.character.location.z / 1000,
                    }
                )  # 1등 이름, 경과시간, x,y,z

        return player_positions

    # 1등 플레이어만이 아니라 애가 죽인 애들 동선도 표시해야 해서 스펙트럼으로 표현하면 너무 복잡함
    def plot_positions(positions: list, spectrum_dot_mode=True):
        if spectrum_dot_mode:

            position_bundle=[]

            
            for i in range(0,len(positions),int(len(positions)/100)+1):
                position_bundle.append(positions[i:i+int(len(positions)/100)+1])
            for idx_1, pos in enumerate(position_bundle):
            
                for i in range(len(pos)):
                    plt.plot(pos[i]['x'],pos[i]['y'],color=color[idx_1], marker='o',markersize=5)
            
        else:
            axis_key_pos = {axis: [pos[axis] for pos in positions] for axis in ['x', 'y']}
            plt.plot(*axis_key_pos.values())







    client = MongoClient("mongodb://localhost:27017/")
    db = client['match_db'] # test-db라는 이름의 데이터베이스에 접속
    collection = db["circle_match"]



    color = COLORS
    idx = list(range(len(color)))
    idx_order = list(range(len(color)))
    random.shuffle(idx)


    Pubg = pubg()    
    match_id = id
    match = get_match(Pubg,match_id)
    telemetry = get_telemetry(match)
    #자기장 plot 관련
    circles = telemetry.circle_positions()
    all_circle = get_all_circle(circles)
    circle_list=get_circle_list(all_circle)
    map_x, map_y = mapsize(telemetry.map_id())
    

    #db접근 관련
    user_match=get_feature(match)
    for x in compare_db(user_match["Map_Name"],user_match["Match_Mode"],user_match["F_Circle_x"],user_match["F_Circle_y"],user_match["L_Circle_x"],user_match["L_Circle_y"]):
        search_match_id = x["Match_ID"]
    search_match=get_match(Pubg,search_match_id)
    search_telemetry=get_telemetry(search_match)
    search_circles=search_telemetry.circle_positions()
    search_all_circle = get_all_circle(search_circles)
    search_circle_list = get_circle_list(search_all_circle)

    winner_movement = winner_position(search_telemetry)
    plot_positions(winner_movement)


    def plot_map_img(map_name=None, res_option="Low"):#맵 띄우기
        url = f"https://github.com/pubg/api-assets/raw/master/Assets/Maps/{map_name}_Main_{res_option}_Res.png"
        img_np = np.array(PIL.Image.open(req.urlopen(url)))

        k=0
        while k < len(circle_list):
            plt.gca().add_patch(patches.Circle((circle_list[k][1]/map_x,circle_list[k][2]/map_y), circle_list[k][4]/map_x, color = "w", fill = False))#첫번째 매치 원
            k+=1

        k=0
        while k < len(search_circle_list):
            plt.gca().add_patch(patches.Circle((search_circle_list[k][1]/map_x,search_circle_list[k][2]/map_y), search_circle_list[k][4]/map_x, color = color[idx[1]], fill = False))#첫번째 매치 원
            k+=1

        plt.title(search_match_id)
        plt.imshow(img_np)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200)
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{data}'/>"



    return plot_map_img("Erangel", "Low")#맵



