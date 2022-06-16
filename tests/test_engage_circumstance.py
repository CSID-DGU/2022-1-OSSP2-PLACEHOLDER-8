from ast import AsyncFunctionDef
import gzip
import json
import os
import datetime
import numpy as np
from math import sin, cos
import PIL.Image
import os.path

import matplotlib.pyplot as plt
import matplotlib.patches as patches  # 원 추가
import math
from matplotlib.animation import FuncAnimation
import pandas as pd
import urllib.request as req

from chicken_dinner.pubgapi import PUBG

# import chicken_dinner.types as PUBGType


def plot_map_img(map_name=None, res_option='Low'):
    url = f'https://github.com/pubg/api-assets/raw/master/Assets/Maps/{map_name}_Main_{res_option}_Res.png'
    img_np = np.array(PIL.Image.open(req.urlopen(url)))
    plt.imshow(img_np)


def Winner_Kill_Position(match):
    tel = match.get_telemetry()
    chicken_player = tel.winner()[0]
    start = datetime.datetime.strptime(
        tel.filter_by('log_match_start')[0].timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'
    )
    kill_log = tel.filter_by('log_player_kill_v2')
    global kill_position
    kill_position = []

    for kill_event in kill_log:
        timestamp = datetime.datetime.strptime(kill_event.timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        dt = (timestamp - start).total_seconds()
        try:
            player = kill_event.finisher.name
        except AttributeError:
            continue
        if player == chicken_player and player == kill_event.killer.name:
            kill_position.append(
                {
                    'Killer': player,
                    'Victim': kill_event.victim.name,
                    'Time': dt,
                    'x': kill_event.finisher.location.x / 1000,
                    'y': kill_event.finisher.location.y / 1000,
                    'z': kill_event.finisher.location.z / 1000,
                    'Victim_Location_X': kill_event.victim.location.x / 1000,
                    'Victim_Location_Y': kill_event.victim.location.y / 1000,
                    'Victim_Location_Z': kill_event.victim.location.z / 1000,
                }
            )
    return kill_position


def Winner_Engage_Position(
    match, input_kill_position
):  # Engage_Victim을 구할 때 1등이 죽인 Victim들만 고려
    tel = match.get_telemetry()
    chicken_player = tel.winner()[0]  # 1등 플레이어 =chicken
    start = datetime.datetime.strptime(
        tel.filter_by('log_match_start')[0].timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'
    )
    engage_log = tel.filter_by('log_player_take_damage')

    victim_name = []  # kill_position에서 구한 victim 이름 저장할 리스트
    engage_position = {}  # 각각의 victim_name은 key, value=해당 victim의 log_player_take_damage
    for i in input_kill_position:
        victim_name.append(i.get('Victim'))  # kill_log에서 가져온 victim name 할당

    for i in range(len(victim_name)):
        engage_position[victim_name[i]] = []
    """
    victim의 개수가 2명(victim_name='a','b')이면 { 'a': [ ], 'b' : [ ] }
    engage_position['key'=victim_name]에 빈 리스트 생성
    """
    for engage_event in engage_log:  # log_player_take_damage에서 가져온 로그
        try:
            attacker_name = engage_event.attacker.name  # **같은 예외들 제외->순수 교전상황만 표시할 것
        except AttributeError:
            continue
        if (
            engage_event.victim.name in victim_name and attacker_name == chicken_player
        ):  # engage_position의 key = 공격 받은 victim.name과 같고 공격자가 1등플레이어인 상황
            engage_timestamp = datetime.datetime.strptime(
                engage_event.timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'
            )
            engage_dt = (engage_timestamp - start).total_seconds()
            engage_position[engage_event.victim.name].append(
                {
                    'Victim': engage_event.victim.name,
                    'Attacker': chicken_player,
                    'Victim': engage_event.victim.name,
                    'Time': engage_dt,
                    'x': engage_event.attacker.location.x / 1000,
                    'y': engage_event.attacker.location.y / 1000,
                    'z': engage_event.attacker.location.z / 1000,
                    'Victim_Location_X': engage_event.victim.location.x / 1000,
                    'Victim_Location_Y': engage_event.victim.location.y / 1000,
                    'Victim_Location_Z': engage_event.victim.location.z / 1000,
                }
            )  # engage_position['a']의 값으로 위와 같은 dictonary형 데이터 추가
    return engage_position


def winner_victim_engage_circumstance(
    engage_dictionary, input_kill_position
):  # 기존에 있던 winner_kill_position, engage_circle까지 한번에 들어있음.
    number_of_victims = len(engage_dictionary)
    list_victims = list(engage_dictionary.keys())

    for i in range(number_of_victims):
        engage_circle_radius = 0
        center = (0, 0)
        number_of_engagement = 0
        for engage_event in engage_dictionary[
            list_victims[i]
        ]:  # engage_event = 각각의 victim에 대한 log_player_take_damage
            winner_x, winner_y, victim_x, victim_y = (
                engage_event['x'],
                engage_event['y'],
                engage_event['Victim_Location_X'],
                engage_event['Victim_Location_Y'],
            )
            plt.scatter(winner_x, winner_y, color='b')  # winner = 항상 파란색
            plt.scatter(
                victim_x, victim_y, color=[1, (1 / number_of_victims) * i, 0.4]
            )  # Victim은 각각 색이 다름
            plt.arrow(
                winner_x, winner_y, victim_x - winner_x, victim_y - winner_y, color='white',
            )  # victim이 winner한테서 데미지 받았을 때 표시-> 오로지 winner가 공격자일때의 입장만 나옴->winner가 데미지 받은 상황은 안나옴
            engage_distance_max = (
                math.dist([winner_x, winner_y], [victim_x, victim_y]) / 2 + 2
            )  # 반지름 값
            if engage_circle_radius < engage_distance_max:  # 교전 중 서로간의 거리가 가장 멀었을 때로 반지름 설정할 것
                engage_circle_radius = engage_distance_max
            if center[0] == 0 and center[1] == 0:  # 처음 교전시 두 플로이어 간의 교전 중심은 서로의 좌표/2
                x = (winner_x + victim_x) / 2
                y = (winner_y + victim_y) / 2
            else:
                x = center[0] + (winner_x + victim_x) / 2  # 교전이 진행되면서 두 플레이어는 이동할 것.
                y = (
                    center[1] + (winner_y + victim_y) / 2
                )  # -> 교전 중심은 이전까지의 서로의 중간좌표 + 새로운 중간좌표
            number_of_engagement = number_of_engagement + 1  # 교전 횟수
            center = (x, y)
        killer_position_x, killer_position_y = (
            input_kill_position[i]['x'],
            input_kill_position[i]['y'],
        )
        victim_killed_position_x, victim_killed_position_y = (
            input_kill_position[i]['Victim_Location_X'],
            input_kill_position[i]['Victim_Location_Y'],
        )
        kill_dist = (
            math.dist(
                [killer_position_x, killer_position_y],
                [victim_killed_position_x, victim_killed_position_y],
            )
            / 2
            + 0.1
        )
        if engage_circle_radius < kill_dist:
            engage_circle_radius = kill_dist
        x = (center[0] + (winner_x + victim_x) / 2) / (number_of_engagement + 1)
        y = (center[1] + (winner_y + victim_y) / 2) / (number_of_engagement + 1)
        center = (x, y)  # 사망 당시 포지션+교전포지션에 따른 중심좌표
        plt.scatter(
            victim_killed_position_x,
            victim_killed_position_y,
            color=[1, (1 / number_of_victims) * i, 0.4],
            marker='x',
        )
        engage_circle = patches.Circle(center, engage_circle_radius, fill=False, ec='r')
        plt.gca().add_patch(engage_circle)


if __name__ == '__main__':
    api_key = None
    with open(r'.\my_api', mode='r') as api_key_file:
        api_key = api_key_file.read()

    pubg = PUBG(api_key=api_key, shard='steam')
    match = pubg.match('c4b89079-795b-49ff-a134-c02b6aa73c77')
    winner_engage_position = Winner_Engage_Position(match, Winner_Kill_Position(match))
    winner_victim_engage_circumstance(winner_engage_position, Winner_Kill_Position(match))
    plot_map_img(match.map_name, 'Low')

    plt.show()
