from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import (
    Key,
    KeyCode,
    # HotKey,
)

import win32api
import win32gui
import win32con

import math
from ctypes import windll
import threading


log = print

GLOBAL_COMBINATIONS = [
    {Key.ctrl_l, Key.alt_l, KeyCode(83)},
]

global_enable_move = False
global_current = set()
global_last_position = None
global_window = None
global_lock = threading.Lock()


def is_desktop(handle):
    # log('窗口的句柄', handle)
    # 桌面没有标题
    text = win32gui.GetWindowText(handle)
    if text == '':
        # log('标题', text)
        return True
    else:
        return False


class Window(object):
    def __init__(self, handle=0, x=0, y=0, width=0, height=0):
        self.handle = handle
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def maximized(self):
        status = windll.user32.IsZoomed(self.handle)
        return status

    def move(self, delta_x, delta_y):
        if not is_desktop(self.handle):
            x = delta_x + self.x
            y = delta_y + self.y
            # log('原来的位置', self.x, self.y)
            # log('移动窗口到', x, y)

            win32gui.SetWindowPos(
                self.handle,
                win32con.HWND_NOTOPMOST,
                x,
                y,
                self.width,
                self.height,
                win32con.SWP_NOSIZE
            )
            self.update(x, y)

    def update(self, x, y):
        self.x = x
        self.y = y


def find_window(handle, window):
    hwd = window.handle
    if win32gui.IsChild(handle, hwd) or handle == hwd:
        rect = win32gui.GetWindowRect(handle)
        window.handle = handle
        window.y = rect[1]
        window.x = rect[0]
        window.width = rect[2]
        window.height = rect[3]


def window_point():
    pos = win32api.GetCursorPos()
    # log('鼠标指向的位置', pos)
    handle = win32gui.WindowFromPoint(pos)
    window = Window(handle=handle)
    win32gui.EnumWindows(find_window, window)
    return window


def restore_window_size(window):
    # global global_window
    handle = window.handle

    status = windll.user32.IsZoomed(handle)
    if status:
        # print('当前窗口最大化了', status)
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        window = window_point()

    return window


def on_move(x, y):
    # return
    global global_last_position
    global global_window
    global global_lock
    global global_enable_move

    global_lock.acquire()

    if global_enable_move and not global_window.maximized():
        # 缩放 150%
        x = math.floor(x / 1.5)
        y = math.floor(y / 1.5)
        delta_x = x - global_last_position[0]
        delta_y = y - global_last_position[1]
        global_last_position = (x, y)
        # log('鼠标移动了')
        global_window.move(delta_x, delta_y)

    global_lock.release()


def pressed_comb(current, COMBINATIONS):
    for combs in COMBINATIONS:
        if current == combs:
            return True
    return False


def on_press(key):
    global GLOBAL_COMBINATIONS
    global global_lock

    global_lock.acquire()

    if any([key in combs for combs in GLOBAL_COMBINATIONS]):
        global global_enable_move
        global global_current

        global_current.add(key)
        if (pressed_comb(global_current, GLOBAL_COMBINATIONS) and
           not global_enable_move):
            global global_last_position
            global global_window

            # log('触发快捷键，可以移动窗口')
            pos = win32api.GetCursorPos()
            global_last_position = pos
            global_window = window_point()
            global_enable_move = True
            # print('触发热键')

    global_lock.release()


def on_release(key):
    # global global_window
    global global_current
    global global_lock
    global global_enable_move

    global_lock.acquire()

    if key in global_current:
        # print('删除了', key)
        global_current.remove(key)
        global_enable_move = False
        # global_window = None

    global_lock.release()


def on_scroll(x, y, dx, dy):
    # log('位置', x, y)
    # log('dx, dy', dx, dy)
    pass


def advancedControl():
    with MouseListener(on_move=on_move) as listener:
        with KeyboardListener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


if __name__ == "__main__":
    # print(HotKey.parse('<ctrl>+<alt>+h'))
    advancedControl()
