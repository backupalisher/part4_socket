import socketio
from requests_html import HTMLSession
import json
from env import *


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


def get_html(ip_address, urls_list, device_id):
    html_code = ''
    for url in urls_list.split(','):
        r = session.get(ip_address + url.strip())
        r.html.render()
        html_code += ip_address + url.strip()
        html_code += r.html.html

    html_data = ' '.join(format(ord(x), 'b') for x in html_code)
    return html_data


def send_device_data(check_address, ip_address, url_list, parser_class, device_id):
    if check_address:
        print(check_address, ip_address, url_list, parser_class, device_id)
        code_data = get_html(ip_address, url_list, device_id)
        sio.emit('put', json.dumps({'client_init': 'parse_init',
                                    'device_id': device_id,
                                    'data': code_data,
                                    'parser_class': parser_class}), namespace='/put')
    else:
        sio.emit('put', json.dumps({'device_error': 404,
                                    'device_id': device_id,
                                    'error': 'Not connection'}), namespace='/put')


def message_received(event):
    print(f"Message {event} received")


@sio.on('get', namespace='/get')
def msg_get(eve):
    print('message received with "get"', eve)


@sio.on('put', namespace='/put')
def msg_put(eve):
    print('message received with "put"', eve)


@sio.on('get', namespace='/put')
def msg_get_put(eve):
    j_data = json.loads(eve)
    if 'getDevices' in j_data['server_init'] and (j_data['company_id'] == COMPANY_ID):
        check_address = check_ping(j_data['devices'][0]['url'])
        send_device_data(check_address,
                         j_data['devices'][0]['url'],
                         j_data['devices'][0]['url_list'],
                         j_data['devices'][0]['parser_class'],
                         j_data['devices'][0]['id'])


@sio.on('connect', namespace='/put')
def on_connect():
    print("Connect...")


@sio.on('disconnect', namespace='/put')
def on_disconnect():
    print(f"Disconnected from server")


if __name__ == '__main__':
    sio.connect('https://socket.api.part4.info:8443/put', namespaces=['/get', '/put'])
    emit_times = 0
    is_emit = True
    data = f'{{"getCompany": {COMPANY_ID}}}'
    while is_emit:
        sio.emit('put', data, namespace='/put', callback=message_received)
        emit_times += 1
        print(emit_times)
        if emit_times > 0:
            is_emit = False
    sio.wait()
