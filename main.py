import time
from os import times

import cv2
import os


import pydirectinput as pyautogui
import mss
import numpy as np
XZPT=cv2.imread(r'C:\Users\xtiao\Desktop\59.PNG')
COLORS=[(0, 0, 0), (17, 34, 51), (34, 68, 102), (51, 102, 153), (68, 136, 204), (85, 170, 255), (102, 204, 50), (119, 238, 101), (136, 16, 152), (153, 50, 203), (170, 84, 254), (187, 118, 49), (204, 152, 100), (221, 186, 151), (238, 220, 202), (255, 254, 253)]

def split_image(image:np.ndarray, grid_size=(16, 12))->dict:
    """
    
    :param image:
    :param grid_size: 
    :return: 
    """
    # 读取图片
    dt={}

    img_height, img_width, _ = image.shape

    # 计算每块的宽度和高度
    block_width = img_width // grid_size[0]
    block_height = img_height // grid_size[1]
    w2=block_width//2
    h2=block_height//2
    # 分割并保存每一块
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            x_start = i * block_width
            y_start = j * block_height
            x_end = x_start + block_width
            y_end = y_start + block_height
            dt[(x_start + w2, y_start + h2)]= image[y_start:y_end, x_start:x_end]
    return dt
def init_location():
    result = cv2.matchTemplate(_mss((0, 0, 1920, 1080))(), XZPT, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >0.95:
        return (max_loc[0]-245,max_loc[1]-39,100,75),(max_loc[0]-250,max_loc[1]-447)
    else:
        raise ValueError('--')
def _mss(game_region):
    monitor = {
        "left": game_region[0],
        "top": game_region[1],
        "width": game_region[2],
        "height": game_region[3],
    }
    sct = mss.mss()

    def shot(top=0, bottom=game_region[3], left=0, right=game_region[2]):
        return cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)[top:bottom, left:right]

    return shot
def clicked(x,y,button):
    pyautogui.mouseDown(x,y,button=button)
  #  time.sleep(0.1)
    pyautogui.mouseUp(x, y, button=button)


time.sleep(2)
#identify_area,click_xy=init_location()
identify_area,click_xy=(717, 573, 100, 75) ,(712, 165)
ms=_mss(identify_area)



img = cv2.imread(r'C:\Users\xtiao\Desktop\output\sprite_interface2_arcadecenter_puzzle.NPK\puzzle_illust.img\1.PNG')

spl=split_image(img).copy()
index=None
while True:
    for k,i in spl.items():
        im=ms()
        result = cv2.matchTemplate(im, i, cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.99:
            clicked(identify_area[0],identify_area[1], button='left')
            clicked(k[0]+click_xy[0],k[1]+click_xy[1],button='left')
            spl.pop(k)
            break
