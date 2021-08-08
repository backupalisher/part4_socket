import socketio
from requests_html import HTMLSession
import json
from env import *
import datetime
import urllib3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("start-maximized")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-extensions")
options.add_argument("--enable-javascript")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--window-size=1366,768")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)

sio = socketio.Client(engineio_logger=False, ssl_verify=False)
session = HTMLSession(verify=False)
session.browser

# Время для проверки соединения с адресатом (sec.)
check_timeout = 8
urllib3.disable_warnings()


def check_ping(ip):
    try:
        if session.get(ip, timeout=check_timeout):
            return True
    except:
        return False


def get_html(ip_address, urls_list):
    html_code = ''
    for url in urls_list.split(','):
        driver.get(ip_address + url.strip())
        WebDriverWait(driver, timeout=1).until(lambda d: d.find_element_by_tag_name("div"))
        time.sleep(5)
        html_code += driver.page_source

    html_data = ' '.join(format(ord(x), 'b') for x in html_code)
    # обратно преобразовать в html
    # ''.join([chr(int(s, 2)) for s in out.split()])
    return html_data


def send_device_data(check_address, ip_address, url_list, parser_class, device_id):
    d_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ")
    if check_address:
        code_data = get_html(ip_address, url_list)

        sio.emit('put', json.dumps({'client_init': 'parse_init',
                                    'device_id': device_id,
                                    'data': code_data,
                                    'parser_class': parser_class}), namespace='/put')
        print(d_time + str(f"{{'client_init': 'parse_init', "
                           f"'device_id': {device_id}, "
                           f"'ip_address': {ip_address}, "
                           f"'parser_class': {parser_class}}}"))
    else:
        sio.emit('put', json.dumps({'device_error': 404,
                                    'device_id': device_id,
                                    'error': 'Not connection'}), namespace='/put')
        print(d_time + str(f"{{'device_error': 404, "
                           f"'device_id': {device_id},"
                           f"'error': 'Not connection'}}"))


def message_received(event):
    pass
    # print(f"Message {event} received")


@sio.on('get', namespace='/get')
def msg_get(eve):
    pass
    # print('message received with "get"', eve)


@sio.on('put', namespace='/put')
def msg_put(eve):
    pass
    # print('message received with "put"', eve)


@sio.on('get', namespace='/put')
def msg_get_put(eve):
    j_data = json.loads(eve)
    d_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ")
    print(d_time + str(j_data))
    try:
        if 'getDevices' in j_data['server_init'] and (j_data['company_id'] == COMPANY_ID):
            check_address = check_ping(j_data['devices'][0]['url'])
            send_device_data(check_address,
                             j_data['devices'][0]['url'],
                             j_data['devices'][0]['url_list'],
                             j_data['devices'][0]['parser_class'],
                             j_data['devices'][0]['id'])
    except:
        pass


@sio.on('connect', namespace='/put')
def on_connect():
    print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ") + "  Connected")


@sio.on('disconnect', namespace='/put')
def on_disconnect():
    print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ") + "  Disconnected from server")


def init_socket():
    try:
        sio.connect(URL_CLIENT_ENDPOINT, namespaces=['/get', '/put'])
    except:
        pass
    emit_times = 0
    is_emit = True
    data = f'{{"getCompany": {COMPANY_ID}}}'
    while is_emit:
        sio.emit('put', data, namespace='/put', callback=message_received)
        emit_times += 1
        print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ") + 'Emit counts  ' + str(emit_times))
        if emit_times > 0:
            is_emit = False
