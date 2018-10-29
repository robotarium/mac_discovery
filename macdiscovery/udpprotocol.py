import asyncio
import vizier.log as log


class UdpProtocol:

    def __init__(self, handler):
        # Handler must be a function that accepts transport data, addr
        self.handler = handler
        self.logger = log.get_logger()

        # Set when a connection is made
        self.transport = None

    def connection_made(self, transport):
        self.logger.info('Connection established.')
        self.transport = transport

    def connection_lost(self, exc):
        self.logger.info('Connection lost.  Closing the asyncio event loop.')
        loop = asyncio.get_event_loop()
        loop.stop()

    def datagram_received(self, data, addr):
        message = data.decode(encoding='UTF-8')
        self.logger.info('Message ({0}) received from address ({1}).'.format(message, addr))
        self.handler(self.transport, message, addr)

    def error_received(self, exc):
        print('Error received:', exc)
