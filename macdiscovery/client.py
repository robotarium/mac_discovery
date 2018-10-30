import socket
import struct
import argparse
import vizier.log as log
import json
import time

MAX_RECEIVE_BYTES = 4096


def main():

    logger = log.get_logger()

    parser = argparse.ArgumentParser()
    parser.add_argument('ip', type=str, help='IP on which to bind UDP socket')
    parser.add_argument('recv_port', type=int, help='Port on which UDP server listens.')
    parser.add_argument('send_port', type=int, help='Port on which UDP message are sent')
    parser.add_argument('quiesce', type=int, help='How many intervals to continue when no new MACs are received.')
    parser.add_argument('--mac_list', type=str, help='Previous MAC list')
    parser.add_argument('-i', type=int, default=1, help='Interval at which to send UDP messages')

    args = parser.parse_args()
    ip = args.ip
    recv_port = args.recv_port
    send_port = args.send_port
    quiesce = args.quiesce
    interval = args.i

    previous_macs = {}

    if(args.mac_list):
        try:
            f = open(args.mac_list, 'r')
            previous_macs = json.load(f)
        except Exception as e:
            logger.error('Could not open supplied MAC list file ({}).'.format(args.mac_list))
            logger.error(e)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    group = socket.inet_aton('239.255.255.250')
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    logger.info('Binding UDP socket to address {}:{}.'.format(ip, recv_port))
    sock.bind((ip, recv_port))

    message = json.dumps({"method": "get", "link": "mac", "port": recv_port}).encode(encoding='UTF-8')
    received = []
    macs = set()
    prev_mac_count = len(macs)

    q = 0
    while q < quiesce:

        sock.sendto(message, ('<broadcast>', send_port))
        data, address = sock.recvfrom(MAX_RECEIVE_BYTES)

        logger.debug('Received {} from {}'.format(data, address))
        if not data:
            continue

        try:
            js = json.loads(data)
        except Exception as e:
            log.warning(e)
            logger.warning('Could not JSON-decode message ({}).'.format(data))

        if('body' in js):
            if('mac' in js['body']):
                mac = js['body']['mac']
                macs.add(mac)
                #macs.append(mac)
            else:
                logger.warning('Expected field "mac" in JSON message.')
                continue
        else:
            logger.warning('Expected field "body" in JSON message.')
            continue

        # If we didn't add anything new
        if(prev_mac_count >= len(macs)):
            q += 1
        else:
            q = 0

        prev_mac_count = len(macs)
        time.sleep(interval)

    for x in received:
        try:
            js = json.loads(x)
        except Exception as e:
            log.warning(e)
            logger.warning('Could not JSON-decode message ({}).'.format(x))

        if('body' in js):
            if('mac' in js['body']):
                mac = js['body']['mac']
                macs.append(mac)
            else:
                logger.warning('Expected field "mac" in JSON message.')
                continue
        else:
            logger.warning('Expected field "body" in JSON message.')
            continue

    logger.info('Received MACs: {}'.format(macs))

    old_macs = set(previous_macs.keys())
    new_macs = macs.difference(old_macs)

    macs = list(macs)
    # print(previous_macs)
    ids = set(range(200))
    ids = ids.difference(old_macs)
    ids = list(ids)
    ids = ids[:len(new_macs)]

    # print(old_macs)
    # print(new_macs)

    mapping = dict(zip(new_macs, ids))
    mapping.update(previous_macs)
    logger.info(mapping)
    sock.close()


if __name__ == '__main__':
    main()
