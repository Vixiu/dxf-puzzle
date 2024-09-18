import re
import threading
import cv2
import time
from pynput.mouse import  Controller, Button
import mss
import numpy as np
from pynput import keyboard
import win32gui


COLORS=[(0, 0, 0), (17, 34, 51), (34, 68, 102), (51, 102, 153), (68, 136, 204), (85, 170, 255), (102, 204, 50), (119, 238, 101), (136, 16, 152), (153, 50, 203), (170, 84, 254), (187, 118, 49), (204, 152, 100), (221, 186, 151), (238, 220, 202), (255, 254, 253)]
count=0
mouse = Controller()
flag=True
speed=9

def wait_dnf_process(process_name='地下城与勇士'):
    while True:
        hwnd = win32gui.FindWindow(process_name, None)
        if hwnd != 0:
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            return l, t
        else:
            print(f"waiting for {process_name}...")
            time.sleep(2)
def _mss(game_region):
    monitor = {
        "left": game_region[0],
        "top": game_region[1],
        "width": game_region[2]-game_region[0],
        "height": game_region[3]-game_region[1],
    }
    sct = mss.mss()

    def shot(top=0, bottom=game_region[3], left=0, right=game_region[2]):
        return cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)[top:bottom, left:right]

    return shot
def microsecond_sleep(sleep_time):
    sleep_time *= 1000
    end_time = time.perf_counter() + (sleep_time - 0.9) / 1e6  # 0.8是时间补偿，需要根据自己PC的性能去实测
    while time.perf_counter() < end_time:
        pass
def clicked(x,y):
    mouse.position = (x, y)
    microsecond_sleep(speed)
    mouse.press(Button.left)
    microsecond_sleep(speed)
    mouse.release(Button.left)
    microsecond_sleep(speed)
def kb():
# 监听键盘键入
    with keyboard.Events() as events:
        for event in events:
            # 监听esc键，释放esc键，停止监听。
            if event.key == keyboard.Key.esc:
                global flag
                flag=False
                break
        time.sleep(0.2)

def get_xy():
    with keyboard.Events() as _events:
        for _event in _events:
            if isinstance(_event, keyboard.Events.Release) and _event.key.char == 'd':
                return Controller().position

def start(xy):
    global count
    tg=(xy['identify_txy'][0]-1,xy['identify_txy'][1]-1,xy['identify_bxy'][0]+1,xy['identify_bxy'][1]+1)
    black_w=(xy['region_bxy'][0]-xy['region_txy'][0])//16
    black_h=(xy['region_bxy'][1]-xy['region_txy'][1])//12
    color_xy = {
        (COLORS[i], COLORS[kk]):( i * black_w + black_w // 2, kk * black_h + black_h // 2,(i+1,kk+1))
        for kk in range(12) for i in range(16)
    }

    w,h=tg[2]-tg[0],tg[3]-tg[1]
    ms = _mss(tg)
    th = threading.Thread(target=kb)
    th.start()
    while flag:
        img = ms()
        try:
            key = color_xy[(tuple(img[1, 1]), tuple(img[h-1, w-1]))]
        except KeyError:
            count += 1
            if count > 40:
                time.sleep(0.2)
                clicked(*xy['end'])
                time.sleep(0.1)
                clicked(*xy['start'])
                mouse.press(Button.left)
                mouse.release(Button.left)
                count = 0
            continue
        clicked(*xy['identify_txy'])
        clicked(xy['region_txy'][0]+key[0],xy['region_txy'][1]+key[1])
        count = 0



if __name__ == '__main__':
    print('-务必已管理员身份打开脚本-')
    print('-------------------------')
    print('S键-自动校准位置并开始脚本,')
    print('A键-手动校准位置并开始脚本')
    print('D键-修改速度(鼠标在拼图上闪烁请调大速度)')
    print('Esc键-退出脚本')
    base_xy={
        'start':(850,770),
        'end':(850,715),
        'identify_txy':(575,654),
        'identify_bxy':(609, 677),
        'region_txy':(537,223),
        'region_bxy':(1173,580),
    }

    with keyboard.Events() as events:
        for event in events:
            try:
                if isinstance(event, keyboard.Events.Release) and event.key.char=='a':
                    print('-------------------------------------')
                    print('请依次录入,鼠标移动到指定位置后按D键')
                    print('-------------------------------------')
                    print('> 请将鼠标移动到','“选择拼图”','按钮上,按D键 <')
                    base_xy['start']=get_xy()
                    base_xy['end'] = base_xy['start']
                    print('> 请将鼠标移动到','“色块上”','后按D键 <')
                    base_xy['identify_txy'] = get_xy()
                    print('> 请将鼠标移动到','“色块下”','后按D键 <')
                    base_xy['identify_bxy'] = get_xy()
                    print('> 请将鼠标移动到','“拼图左上”','后按D键 <')
                    base_xy['region_txy'] = get_xy()
                    print('> 请将鼠标移动到','“拼图右下”','后按D键 <')
                    base_xy['region_bxy'] = get_xy()
                    print('完成')
                    break
                elif  isinstance(event, keyboard.Events.Release) and event.key.char=='s':
                    lt = wait_dnf_process()
                    for k,v in base_xy.items():
                        base_xy[k]=tuple(i + j for i, j in zip(lt,base_xy[k]))
                    break
                elif  isinstance(event, keyboard.Events.Release) and event.key.char=='d':
                    print(f'当前{speed}毫秒,输入后回车确认:')
                    speed=float(re.sub(r'[a-zA-Z]', '', input()))
                    print('已设置',speed,'ms')
                    print('S键自动校准位置,A键手动校准位置,D键修改速度,Esc键退出脚本')
                elif event.key == keyboard.Key.esc:
                    exit(0)
            except AttributeError:
                pass
    print('开始执行,Esc键退出脚本...')
    start(base_xy)
    print('脚本退出')
