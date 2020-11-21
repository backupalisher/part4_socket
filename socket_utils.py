import socketio
from requests_html import HTMLSession
import json
from env import *
import datetime

sio = socketio.Client(engineio_logger=False, ssl_verify=False)
session = HTMLSession(verify=False)
session.browser

# Время для проверки соединения с адресатом
check_timeout = 8


def check_ping(ip):
    try:
        if session.get(ip, timeout=check_timeout):
            return True
    except:
        return False


def get_html(ip_address, urls_list):
    html_code = ''
    for url in urls_list.split(','):
        r = session.get(ip_address + url.strip())
        r.html.render()
        html_code += ip_address + url.strip()
        html_code += r.html.html

    html_data = ' '.join(format(ord(x), 'b') for x in html_code)
    return html_data


def send_device_data(check_address, ip_address, url_list, parser_class, device_id):
    d_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ")
    if check_address:
        # print(f"{check_address}, {ip_address}, {url_list}, {parser_class}, {device_id}")
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
    print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ") + "  Connect...")


@sio.on('disconnect', namespace='/put')
def on_disconnect():
    print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S - ") + "  Disconnected from server")


def init_socket():
    sio.connect('https://socket.api.part4.info:8443/put', namespaces=['/get', '/put'])
    emit_times = 0
    is_emit = True
    data = f'{{"getCompany": {COMPANY_ID}}}'
    while is_emit:
        sio.emit('put', data, namespace='/put', callback=message_received)
        emit_times += 1
        print('Emit counts  ' + str(emit_times))
        if emit_times > 0:
            is_emit = False
