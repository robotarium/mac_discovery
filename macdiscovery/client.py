import asyncio
import udpprotocol as udp
import socket
import struct
import argparse
import vizier.log as log
import json
import queue
import time
import concurrent.futures

global logger
logger = log.get_logger()

global message_q
message_q = queue.Queue()

global message


def handler(transport, message, address):
    print(message)
    message_q.put((message, address))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='Port on which UDP server listens.')
    parser.add_argument('duration', type=int, help='How long to listen.')

    args = parser.parse_args()
    port = args.port
    duration = args.duration

    loop = asyncio.get_event_loop()

    listen = loop.create_datagram_endpoint(lambda: udp.UdpProtocol(handler), local_addr=('0.0.0.0', port), family=socket.AF_INET)
    transport, protocol = loop.run_until_complete(listen)

    sock = transport.get_extra_info('socket')
    group = socket.inet_aton('239.255.255.250')
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(loop.run_forever)

    message = json.dumps({"method": "get", "link": "mac", "port": port}).encode(encoding='UTF-8')

    start = time.time()
    while True:
        logger.info('Sending message')
        transport.sendto(message, ('<broadcast>', 5001))

        if(time.time() - start > duration):
            break

        time.sleep(1)

    received = {}
    while True:
        try:
            m = message_q.get_nowait()
            print(m)
        except Exception:
            break

    transport.close()
    loop.stop()
    print('here')
    executor.shutdown(wait=False)
    print('here')
    future.result()


if __name__ == '__main__':
    main()
