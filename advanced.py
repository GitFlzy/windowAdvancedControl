from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import (
    Key,
    # KeyCode,
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
    {Key.ctrl_l, Key.alt_l},
    # {Key.ctrl_l, Key.alt_l, KeyCode(83)},
]

global_enable_control = False
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
    def __init__(self, handle=0):
        self.handle = handle
        self.zoom_speed = 4
        self.update()

    def maximized(self):
        status = windll.user32.IsZoomed(self.handle)
        return status

    def move(self, vector):
        delta_x, delta_y = vector[0], vector[1]

        if not is_desktop(self.handle):
            self.x += delta_x
            self.y += delta_y
            # log('原来的位置', self.x, self.y)
            # log('移动窗口到', x, y)

            win32gui.MoveWindow(
                self.handle,
                self.x,
                self.y,
                self.width,
                self.height,
                True
            )

    def zoom_in(self):
        self.width += self.zoom_speed
        self.height += self.zoom_speed
        self.repaint()

    def zoom_out(self):
        self.width -= self.zoom_speed
        self.height -= self.zoom_speed
        self.repaint()

    def repaint(self):
        win32gui.SetWindowPos(
            self.handle,
            win32con.HWND_NOTOPMOST,
            self.x,
            self.y,
            self.width,
            self.height,
            win32con.SWP_NOMOVE
        )

    def update(self):
        # rect 存放左上角和右下角的坐标
        rect = win32gui.GetWindowRect(self.handle)
        # log('窗口信息', rect)
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2] - rect[0]
        self.height = rect[3] - rect[1]


def find_top_window(handle, window):
    hwd = window.handle
    if win32gui.IsChild(handle, hwd) or handle == hwd:
        window.handle = handle
        window.update()


def window_point():
    pos = win32api.GetCursorPos()
    # log('鼠标指向的位置', pos)
    handle = win32gui.WindowFromPoint(pos)
    window = Window(handle=handle)
    win32gui.EnumWindows(find_top_window, window)
    return window


# def restore_window_size(window):
#     # global global_window
#     handle = window.handle
#     maximized = windll.user32.IsZoomed(handle)
#     if maximized:
#         # print('当前窗口最大化了', status)
#         win32gui.ShowWindow(handle, win32con.SW_RESTORE)
#         window = window_point()

#     return window


def transform_to_real_coordinate(x, y):
    # 缩放 150%
    x = math.floor(x / 1.5)
    y = math.floor(y / 1.5)
    return (x, y)


def update_last_position(pos):
    global global_last_position
    global_last_position = pos


def get_vector(x, y):
    global global_last_position

    delta_x = x - global_last_position[0]
    delta_y = y - global_last_position[1]
    return (delta_x, delta_y)


def acquire_vector(x, y):
    (x, y) = transform_to_real_coordinate(x, y)
    vector = get_vector(x, y)
    pos = (x, y)
    update_last_position(pos)

    return vector


def on_move(x, y):
    # return
    global global_window
    global global_lock
    global global_enable_control

    global_lock.acquire()

    if global_enable_control and not global_window.maximized():
        vector = acquire_vector(x, y)
        global_window.move(vector)

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
        global global_enable_control
        global global_current

        global_current.add(key)
        if (pressed_comb(global_current, GLOBAL_COMBINATIONS) and
           not global_enable_control):
            global global_window

            # log('触发快捷键，可以移动窗口')
            pos = win32api.GetCursorPos()
            update_last_position(pos)
            global_window = window_point()
            global_enable_control = True

    global_lock.release()


def on_release(key):
    global global_current
    global global_lock
    global global_enable_control

    global_lock.acquire()

    if key in global_current:
        # print('删除了', key)
        global_current.remove(key)
        global_enable_control = False

    global_lock.release()


def is_zoom_in(x, y):
    return (x, y) == (0, 0)


def is_zoom_out(x, y):
    return (x, y) == (0, -1)


def on_scroll(x, y, dx, dy):
    global global_window
    global global_lock
    global global_enable_control

    global_lock.acquire()

    if not global_enable_control:
        global_lock.release()
        return

    if is_zoom_in(dx, dy):
        # log('放大窗口')
        global_window.zoom_in()
    elif is_zoom_out(dx, dy):
        # log('缩小窗口')
        global_window.zoom_out()

    global_lock.release()


def advancedControl():
    with MouseListener(on_move=on_move, on_scroll=on_scroll) as listener:
        with KeyboardListener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


if __name__ == "__main__":
    # print(HotKey.parse('<ctrl>+<alt>+h'))
    advancedControl()
