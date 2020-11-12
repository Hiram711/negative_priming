#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : Hiram
# @Date    : 2020/11/10
# @File    : main.py
# @Project : negative_priming

import os
import locale
from psychopy import core, visual, gui, event
from psychopy.tools.filetools import fromFile, toFile
from datetime import datetime
import sys
import random
import pandas as pd
from process_data import process_data


def get_config():
    # 读取配置文件
    try:
        config = fromFile('config.pickle')
    except Exception as e:
        config = {'姓名': 'user01', '性别': ['男', '女'], '年龄': 18, '测试次数': 100}
    finally:
        now = datetime.now()
        config['测试时间'] = now.strftime('%Y-%m-%d %H:%M:%S')
    # 获取用户输入
    try:
        dlg = gui.DlgFromDict(config, title='请输入测试相关信息', order=['姓名', '性别', '年龄', '测试次数', '测试时间'],
                              fixed=['测试次数', '测试时间'])
        if dlg.OK:
            assert config['性别'] in ['男', '女']  # 判断输入是否有误，有误则抛出异常
            assert isinstance(config['年龄'], int)
            assert isinstance(config['测试次数'], int)
            toFile('config.pickle', config)
            return config
        else:
            core.quit()
            sys.exit()
    except Exception as e:
        print(e)
        print('输入有误，请重新启动程序后输入')
        core.quit()
        sys.exit()


def show_stim(window, stim, wait_time):
    """
    用此函数控制屏幕中心的显示stim

    :parameters:
    window : visual.Window.__class__
        显示窗口

    stim： TextStim.__class__
        Class of text stimuli to be displayed in a :class:`~psychopy.visual.Window

    wait_time ： int
        显示时间，秒为单位

    """
    event.clearEvents('all')
    if stim:
        stim.draw()
    timer = core.CountdownTimer(wait_time)
    window.flip()
    while timer.getTime() > 0:
        pass


def show_cross(window, wait_time):
    """
    用此函数控制屏幕中心的十字显示
    """
    stim = visual.TextStim(window, text="+", color='black', colorSpace='rgb255', units='pix', pos=(0, 0), height=60)
    show_stim(window, stim, wait_time)


def show_mosaic(window, wait_time):
    """用此函数显示马赛克
    """
    image = os.path.join(os.getcwd(), 'assets', 'mosaic.png')
    stim = visual.ImageStim(window, image=image, units='pix', pos=(0, 0), size=(60.0, 60.0))
    show_stim(window, stim, wait_time)


def show_arrows(window, arrow, wait_time):
    """
    用此函数控制屏幕中心的箭头显示,注意此函数仅用于显示，不参与交互

    :parameters:

    arrow： str,Valid values are:'>>','<<'
        显示什么样的箭头

    """
    stim = visual.TextStim(window, text=arrow, color='black', colorSpace='rgb255', units='pix', pos=(0, 0), height=60)
    show_stim(window, stim, wait_time)


# 所有可能的箭头顺序
stimList = [{'first': i, 'second': j} for i in ['>>', '<<'] for j in ['>>', '<<']]


# 测试生成器，times代表要进行多少次测试
def trials(times):
    i = 0
    while i < times:
        i = i + 1
        yield random.choice(stimList)


key_dict = {'<<': 'left', '>>': 'right'}


def interact(window, stim, wait_time):
    global key_dict
    event.clearEvents('all')
    stim.draw()
    timer = core.CountdownTimer(wait_time)
    window.flip()
    run_out_of_time = True
    while timer.getTime() > 0:
        for key in event.getKeys():
            if key in ['left', 'right']:
                resp_time = wait_time - timer.getTime()
                resp_action = key
                resp_result = '正确' if key_dict.get(stim.text) == key else '错误'
                run_out_of_time = False
                break
            elif key in ['q', 'escape']:
                resp_time = None
                resp_action = 'quit'
                resp_result = '退出'
                run_out_of_time = False
                break
        if not run_out_of_time:
            break
    window.flip()
    if run_out_of_time:
        resp_time = None
        resp_action = None
        resp_result = '超时'
    return resp_time, resp_action, resp_result


def save_data(config, data):
    locale.setlocale(locale.LC_ALL, '')
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, 'data', '_'.join([config.get('姓名'), config.get('性别'), str(config.get('年龄'))]))
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    filename = os.path.join(data_dir, datetime.strptime(config.get('测试时间'), '%Y-%m-%d %H:%M:%S')
                            .strftime('%Y%m%d%H%M%S') + '.csv')
    df = pd.DataFrame(data, columns=['order', 'first', 'second', 'resp_time', 'resp_action', 'resp_result'])
    df.to_csv(filename, index=False)
    return df


if __name__ == '__main__':
    config = get_config()
    window = visual.Window(fullscr=False, size=(1024, 768), color=(1, 1, 1), units='pix')  # 创建window
    # ‘显示程序介绍页面，可以根据需要通过替换幻灯片中的文字后保存为intro.png进行替换
    intro_image = os.path.join(os.getcwd(), 'assets', 'intro.png')
    visual.ImageStim(window, image=intro_image, units='pix', pos=(0, 0), size=(1024, 768)).draw()
    window.flip()
    # 按空格开始
    event.waitKeys(keyList=["space"])
    result = []
    order = 1
    for trial in trials(config.get('测试次数')):
        stim = visual.TextStim(window, text='第{}次测试'.format(order), color='black',
                               colorSpace='rgb255', units='pix', pos=(-400, 200), height=30)
        stim.draw()
        show_cross(window, 1000 / 1000)  # 第一次显示十字，过1秒
        show_arrows(window, trial.get('first'), 1000 / 1000)  # 第一次显示箭头，过1秒
        show_mosaic(window, 1000 / 1000)  # 箭头替换为马赛克，过1秒
        show_cross(window, 1000 / 1000)  # 第二次显示十字，过1秒
        stim = visual.TextStim(window, text=trial.get('second'), color='black',
                               colorSpace='rgb255', units='pix', pos=(0, 0), height=60)
        resp_time, resp_action, resp_result = interact(window, stim, 3000 / 1000)  # 第二次显示箭头，等3秒，期间如果有按左右方向键则返回，否则超时
        result.append([order, trial.get('first'), trial.get('second'), resp_time, resp_action, resp_result])
        if resp_action == 'quit':
            break
        order = order + 1

    df = save_data(config, result)  # 保存数据
    rs = process_data(df)  # 简单处理数据
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, 'data', '_'.join([config.get('姓名'), config.get('性别'), str(config.get('年龄'))]))
    rs_filename = os.path.join(data_dir, datetime.strptime(config.get('测试时间'), '%Y-%m-%d %H:%M:%S')
                               .strftime('%Y%m%d%H%M%S') + '_result.csv')
    rs.to_csv(rs_filename, index=False)  # 将处理结果保存到CSV

    # 关闭窗口
    window.close()
    core.quit()
