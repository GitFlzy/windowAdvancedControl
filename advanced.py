from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Key
from pynput.keyboard._win32 import KeyCode

import win32api
import win32gui
import win32con

import math
from ctypes import windll
import threading


# log = print

COMBINATIONS = {
    Key.ctrl_l,
    Key.alt_l,
    KeyCode(83),
}

pressed_current = set()
last_position = None
window = None
lock = threading.Lock()


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


def on_move(x, y):
    global last_position
    global window
    global COMBINATIONS
    global lock

    lock.acquire()

    if pressed_current == COMBINATIONS:
        status = windll.user32.IsZoomed(window.handle)
        if status:
            # print('当前窗口最大化了', status)
            win32gui.ShowWindow(window.handle, win32con.SW_RESTORE)
            window = window_point()
        # 缩放 150%
        x = math.floor(x / 1.5)
        y = math.floor(y / 1.5)
        # log('on_move x, y', x, y)
        # log('api get last_position', last_position)
        delta_x = x - last_position[0]
        delta_y = y - last_position[1]
        last_position = (x, y)
        # log('鼠标移动了')
        window.move(delta_x, delta_y)

    lock.release()


def on_press(key):
    global pressed_current
    global lock
    global window

    lock.acquire()

    if key in COMBINATIONS:
        pressed_current.add(key)
        # log('按下了', key)
        if pressed_current == COMBINATIONS:
            global last_position
            # log('触发快捷键，可以移动窗口')
            pos = win32api.GetCursorPos()
            last_position = pos
            # if window is None:
            window = window_point()
            # print('window', window)

    lock.release()


def on_release(key):
    global window
    global pressed_current
    global lock

    lock.acquire()

    if key in pressed_current:
        pressed_current.remove(key)
        # window = None

    lock.release()


def on_scroll(x, y, dx, dy):
    # log('位置', x, y)
    # log('dx, dy', dx, dy)
    pass


def advancedControl():
    with MouseListener(on_move=on_move) as listener:
        with KeyboardListener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


if __name__ == "__main__":
    advancedControl()
