import socketio
import gzip
from requests_html import HTMLSession
import json
from env import *

sio = socketio.Client(engineio_logger=True, ssl_verify=False)


def get_html(ip_address, url_list):
    session = HTMLSession(verify=False)
    html_code = ''
    for url in url_list:
        r = session.get(ip_address + url)
        r.html.render()
        html_code += r.html.html
    return html_code


def send_device_data(ip_address, url_list, parser_class, device_id):
    print(ip_address, url_list, parser_class, device_id)
    html_code = get_html(ip_address, url_list)
    sio.emit('put', {'client_init': 'parse_init',
                     'device_id': device_id,
                     'html_data': html_code,
                     'parser_class': parser_class})


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
        send_device_data(j_data['devices'][0]['url'],
                         j_data['devices'][0]['url_list'],
                         j_data['devices'][0]['parser_class'],
                         j_data['devices'][0]['id'])
        print(j_data)


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
    data = '{"getCompany": 32}'
    while is_emit:
        sio.emit('put', data, namespace='/put', callback=message_received)
        emit_times += 1
        print(emit_times)
        if emit_times > 0:
            is_emit = False
    sio.wait()
