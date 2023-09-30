from math import sqrt
import asyncio
from flask import Flask, render_template, request, jsonify, Response
import json
import time
import os

if not os.path.exists('path.txt'):
    with open('path.txt', 'w') as f:
        f.write('path/to/mod/logicdebugger.json')
    print("Please insert the path to the folder where the Logic Debugger mod is stored into path.txt. (The mod id is 3043605075)\nby default on Windows, the mod will be stored at C:/Program Files (x86)/Steam/steamapps/workshop/content/387990/3043605075/")
    exit()
with open('path.txt', 'r') as f:
    path = f.read().strip()

all_data = {}
colors = []
tick_cutoff = None


def get_json():
    global all_data, colors, tick_cutoff
    fail = True
    while fail:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            fail = False
        except:
            time.sleep(0.1)
    tick = data['tick']
    print(tick)
    if tick_cutoff is None:
        tick_cutoff = tick
    tickstream = data['tickstream']
    colors = data['colors']
    # tick specifies the tick of the last element in the tickstream
    # tickstream is a list of lists
    first_tick = tick - len(tickstream) + 1
    for i in range(len(tickstream)):
        if first_tick + i < tick_cutoff:
            continue
        print(first_tick + i, tick_cutoff)
        all_data[first_tick + i] = tickstream[i]


recording = False


def get_data():
    global all_data
    dat = []
    for tick in all_data:
        dat.append([int(g) for g in all_data[tick]])
    return dat


def get_data_colored():
    global all_data
    dat = []
    for tick in all_data:
        dat.append([gen_style(i, g) for i, g in enumerate(all_data[tick])])
    return dat


def gen_style(i, g):
    color = '#'+colors[i]
    style = ''
    if g == 0:
        style = f'background-color: #ffffff;'
    else:
        style = f'background-color: {color};'
    style += f'border: 2px solid {color};'
    return style


def run_in_thread():
    print("Starting thread")
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/record')
    def record():
        global recording, all_data, tick_cutoff
        all_data = {}
        tick_cutoff = None
        recording = True
        return "Recording"

    @app.route('/stop')
    def stop():
        global recording
        recording = False
        return "Stopped"

    @app.route('/data')
    def data():
        dat = get_data()
        return jsonify(dat)

    @app.route('/show_data')
    def show_data():
        return render_template('data.html', data=get_data_colored())

    app.run(debug=True, use_reloader=False)


async def run_data_collection():
    global recording, all_data
    while True:
        if recording:
            get_json()
        await asyncio.sleep(0.1)


async def main():
    global recording, all_data
    await asyncio.gather(
        asyncio.to_thread(run_in_thread),
        run_data_collection()
    )

if __name__ == '__main__':
    asyncio.run(main())
