import asyncio
from abc import abstractmethod


class UdpServer(asyncio.protocols.DatagramProtocol):
    transport = None
    __name__ = 'UdpServer'

    def __init__(self, **kwargs):
        pass

    @classmethod
    def start_server(cls, bind_ip, bind_port, loop=None, **kwargs):
        loop = loop or asyncio.get_event_loop()
        factory = lambda: cls._factory(cls, **kwargs)
        transport, protocol = loop.run_until_complete(
            loop.create_datagram_endpoint(factory, local_addr=(bind_ip, bind_port))
        )
        return transport, protocol

    @staticmethod
    def _factory(cls, **kwargs):
        return cls(**kwargs)

    def connection_made(self, transport: asyncio.transports.DatagramTransport):
        self.transport = transport

    def datagram_received(self, data, addr):
        loop = asyncio.get_event_loop()
        loop.create_task(self.handle_inbound_packet(data, addr))

    @abstractmethod
    async def handle_inbound_packet(self, data, addr):
        raise NotImplementedError('handle_inbound_packet is not defined')


class UdpDnsServer(UdpServer):
    __name__ = 'UdpDnsServer'

    def __init__(self, resolver):
        super(UdpDnsServer, self).__init__()
        self.resolver = resolver

    async def handle_inbound_packet(self, data, addr):
        response = await self.resolver.resolve(data)
        self.transport.sendto(response, addr)


class UdpClient(asyncio.protocols.DatagramProtocol):
    transport = None
    response = None

    def __init__(self, message, end_point=None, **kwargs):
        self.message = message
        self.end_point = end_point
        type(kwargs)

    @classmethod
    async def send(cls, remote_ip, remote_port, message, **kwargs):
        loop = asyncio.get_running_loop()
        end_point = loop.create_future()
        factory = lambda: cls._factory(cls, message, end_point, **kwargs)
        transport, protocol = await loop.create_datagram_endpoint(
            factory, remote_addr=(remote_ip, remote_port)
        )
        try:
            await end_point
        finally:
            transport.close()
        return end_point.result()

    @staticmethod
    def _factory(cls, message, end_point, **kwargs):
        return cls(message, end_point, **kwargs)

    def connection_made(self, transport: asyncio.transports.DatagramTransport):
        self.transport = transport
        self.transport.sendto(self.message)

    def datagram_received(self, data, addr):
        self.response = data
        self.transport.close()

    def connection_lost(self, exc):
        self.end_point.set_result(self.response)
