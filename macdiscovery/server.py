import socket
import argparse
import vizier.log as log
import netifaces
import json

MAX_RECEIVE_BYTES = 4096


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


def main():

    logger = log.get_logger()

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='Port on which UDP server listens.')

    args = parser.parse_args()
    port = args.port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    logger.info('Binding UDP socket to port {}.'.format(port))
    sock.bind(('0.0.0.0', port))

    while True:
        data, address = sock.recvfrom(MAX_RECEIVE_BYTES)

        logger.info('Received {} from {}'.format(data, address))
        if not data:
            continue

        try:
            request = json.loads(data)
        except Exception as e:
            logger.error(e)
            logger.error('Could not JSON-decode message ({})'.format(data))
            return

        if('method' not in request):
            logger.warning('Expected field "method" in JSON message ({})'.format(request))
        else:
            method = request['method']

        if('link' not in request):
            logger.warning('Expected field "link" in JSON message ({})'.format(request))
        else:
            link = request['link']

        if('port' not in request):
            logger.warning('Expected field "port" in JSON message ({})'.format(request))
        else:
            port = request['port']

        logger.info(request)

        response = {}

        if(method == 'get'):
            if(link == 'mac'):
                response['status'] = 200
                response['body'] = {'mac': get_mac()}

        sock.sendto(json.dumps(response).encode(encoding='UTF-8'), (address[0], port))


if __name__ == '__main__':
    main()
