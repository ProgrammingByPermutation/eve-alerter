import ctypes
import time
from datetime import datetime, timedelta

from PIL import ImageGrab
from playsound3 import playsound
from pytesseract import pytesseract
import win32gui
from functools import partial
import cv2
import pytesseract
import numpy as np
import os

# Things to change
PILOT_MAX_TIME_IN_AREA = 20
DELAY_BETWEEN_ALERTS = 300

# Things that don't change much
my_names = ['oxcanteven', 'oxcantéven', 'gxcant&ven', 'oxcant&ven', 'oxcant', 'dxcanteven', 'canteven', 'oxtantéven', 'daddy\'s good boy', 'naddy\'s good boy']
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def get_text_from_image(raw_image, x, y, width, height, showDialog=False):
    one = np.array(raw_image)
    # two = cv2.cvtColor(one, cv2.COLOR_RGB2GRAY)
    # thresh = 255 - cv2.threshold(two, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # x, y, width, height = -1465, 706, 122, 375
    x -= 5
    y -= 5
    ROI = one[y:y + height, x:x + width]
    data = pytesseract.image_to_string(ROI, lang='eng')

    if showDialog:
        # cv2.imshow('thresh', thresh)
        cv2.imshow('ROI', ROI)
        cv2.waitKey()

    return data


def get_eve_screenshot():
    toplist, winlist = [], []

    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, toplist)

    firefox = [(hwnd, title) for hwnd, title in winlist if 'eve - ' in title.lower()]
    # just grab the hwnd for first window matching firefox
    firefox = firefox[0]
    hwnd = firefox[0]

    # win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    return ImageGrab.grab(bbox)


def get_list_of_chatters(x, y, width, height, showDialog=False):
    image = get_eve_screenshot()
    text = get_text_from_image(image, x, y, width, height, showDialog)
    return [x.strip().lower() for x in str(text).strip().split('\n') if x.strip() != '']


def update_person_alerts(people_alerts, all_people):
    for person in all_people:
        is_me = False
        for my_name in my_names:
            if my_name in person:
                is_me = True
                break

        if is_me:
            continue

        if person not in people_alerts:
            people_alerts[person] = {
                'name': person,
                'first': datetime.now(),
                'last': datetime.now(),
                'alerted': datetime.now() - timedelta(seconds=DELAY_BETWEEN_ALERTS),
                'already_alerted': False
            }
            continue

        people_alerts[person]['last'] = datetime.now()

    for person in [x for x in people_alerts.keys()]:
        info = people_alerts[person]
        if (datetime.now() - info['last']).seconds > 20:
            del people_alerts[person]


def cls():
    # print('\n' * 60)
    os.system('cls' if os.name == 'nt' else 'clear')


def output_alert_list(people_alerts):
    cls()
    test = sorted(people_alerts.values(), key=lambda item: (item['last'] - item['first']).seconds)
    for person in test:
        print(person['name'] + ': ' + str((person['last'] - person['first']).seconds))


def get_users_greater_than(people_alerts, max_seconds):
    ret = []
    for person in people_alerts:
        info = people_alerts[person]
        if info['already_alerted']:
            continue

        if (info['last'] - info['first']).seconds > max_seconds:
            info['already_alerted'] = True
            ret.append(person)

    return ret

def DetectClick(button, watchtime = 5):
    '''Waits watchtime seconds. Returns True on click, False otherwise'''
    if button in (1, '1', 'l', 'L', 'left', 'Left', 'LEFT'):
        bnum = 0x01
    elif button in (2, '2', 'r', 'R', 'right', 'Right', 'RIGHT'):
        bnum = 0x02

    time.sleep(1)
    start = time.time()
    while 1:
        if ctypes.windll.user32.GetKeyState(bnum) not in [0, 1]:
            # ^ this returns either 0 or 1 when button is not being held down
            return True
        elif time.time() - start >= watchtime:
            break
        time.sleep(0.001)
    return False


if __name__ == '__main__':
    people_alerts = {}
    last_alarm = datetime.now() - timedelta(seconds=DELAY_BETWEEN_ALERTS)
    import pyautogui

    retry = True
    while retry:
        retry = False
        print('Click upper left hand corner to capture')
        DetectClick(1, 30)
        upperLeft = pyautogui.position()
        print(upperLeft)
        print('Click bottom right hand corner to capture')
        DetectClick(1, 30)
        bottomRight = pyautogui.position()
        width = abs(bottomRight.x - upperLeft.x)
        height = abs(bottomRight.y - upperLeft.y)
        print(f'Coordinates: {bottomRight} Width: {width} Height: {height}')
        get_list_of_chatters(upperLeft.x, upperLeft.y, width, height, True)

    while True:
        try:
            # Get the list of users
            all_people = get_list_of_chatters(upperLeft.x, upperLeft.y, width, height)
            update_person_alerts(people_alerts, all_people)
            output_alert_list(people_alerts)

            # Get the users we should alert about
            alert_users = get_users_greater_than(people_alerts, PILOT_MAX_TIME_IN_AREA)
            if len(alert_users) > 0: #  and (datetime.now() - last_alarm).seconds > DELAY_BETWEEN_ALERTS
                playsound('sounds/horn.wav')
                last_alarm = datetime.now()
        except Exception as ex:
            pass

        time.sleep(1)
