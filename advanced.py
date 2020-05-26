from pynput.keyboard import Listener  as KeyboardListener
from pynput.mouse    import Listener  as MouseListener
from pynput.keyboard import Key
import win32api
import win32gui
import win32con
import math

log = print

COMBINATIONS = [
    Key.ctrl_l,
]

pressed_current = set()
last_position = None
window = None

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
            # log('移动目标位置', x, y)

            win32gui.SetWindowPos(
                self.handle,
                win32con.HWND_TOP,
                x,
                y,
                self.width,
                self.height,
                True
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
        window.x = rect[0]
        window.y = rect[1]
        window.width = rect[2]
        window.height = rect[3]

def window_point():
    pos = win32api.GetCursorPos()
    log('鼠标指向的位置', pos)
    handle = win32gui.WindowFromPoint(pos)
    window = Window(handle=handle)
    win32gui.EnumWindows(find_window, window)
    return window

def on_move(x, y):
    global last_position
    global window

    if Key.ctrl_l in pressed_current:
        # 缩放 150%
        x = math.floor(x / 1.5)
        y = math.floor(y / 1.5)
        log('on_move x, y', x, y)
        # log('api get last_position', last_position)
        delta_x = x - last_position[0]
        delta_y = y - last_position[1]
        last_position = (x, y)
        # log('鼠标移动了')
        window.move(delta_x, delta_y)

def on_press(key):
    global last_position
    global window
    global pressed_current

    if key == Key.ctrl_l:
        pressed_current.add(key)
        pos = win32api.GetCursorPos()
        last_position = pos
        if window is None:
            window = window_point()


def on_release(key):
    global window
    global pressed_current

    if key in pressed_current:
        pressed_current.remove(key)
        window = None


if __name__ == "__main__":
    with MouseListener(on_move=on_move) as listener:
        with KeyboardListener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
