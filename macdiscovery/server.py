import asyncio
import udpprotocol as udp
import socket
import argparse
import vizier.log as log
import netifaces
import json

global logger
logger = log.get_logger()


def get_mac():
    """Gets the MAC address for the robot from the network config info.

    Returns:
        str: A MAC address for the robot.

    Example:
        >>> print(get_mac())
        AA:BB:CC:DD:EE:FF

    """

    interface = [x for x in netifaces.interfaces() if 'wlan' in x or 'wlp' in x][0]
    return netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']


def handler(transport, message, address):

    try:
        request = json.loads(message)
    except Exception as e:
        logger.error(e)
        logger.error('Could not JSON-decode message ({})'.format(message))
        return

    if('method' not in request):
        logger.warning('Expected field "method" in JSON message ({})'.format(message))
    else:
        method = request['method']

    if('link' not in request):
        logger.warning('Expected field "link" in JSON message ({})'.format(message))
    else:
        link = request['link']

    if('port' not in request):
        logger.warning('Expected field "port" in JSON message ({})'.format(message))
    else:
        port = request['port']

    logger.info(request)

    response = {}

    if(method == 'get'):
        if(link == 'mac'):
            response['status'] = 200
            response['body'] = {'mac': get_mac()}

    transport.sendto(json.dumps(response).encode(encoding='UTF-8'), (address[0], port))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='Port on which UDP server listens.')

    args = parser.parse_args()
    port = args.port

    loop = asyncio.get_event_loop()

    listen = loop.create_datagram_endpoint(lambda: udp.UdpProtocol(handler), local_addr=('0.0.0.0', port), family=socket.AF_INET)
    transport, protocol = loop.run_until_complete(listen)

    loop.run_forever()


if __name__ == '__main__':
    main()
