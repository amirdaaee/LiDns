from aioudp import UDPServer

from LiDns import resolve


class UDPDNSServer:
    def __init__(self, sender, real_resolver: resolve.RealResolver, fake_resolver: resolve.FakeResolver):
        self.sender = sender
        self.real_resolver = real_resolver
        self.fake_resolver = fake_resolver

    async def on_datagram_received(self, data, addr):
        dns_response = await self.dns_response(data)
        print(addr)
        print('='*100)
        self.sender(dns_response, addr)

    async def dns_response(self, data):
        request = resolve.read_request_packet(data)
        qname = request.question[0].name.to_text(omit_final_dot=True)
        print(qname)
        if qname == 'facebook.com':
            print('fc')
            response = self.fake_resolver.resolve(request)
        else:
            print('ot')
            response = await self.real_resolver.resolve(request)
        print(response.to_text())
        return response.to_wire()


async def start_server(loop, bind_ip, bind_port, real_resolver: resolve.RealResolver,
                       fake_resolver: resolve.FakeResolver):
    udp = UDPServer()
    udp.run(bind_ip, bind_port, loop=loop)
    backend = UDPDNSServer(sender=udp.send, real_resolver=real_resolver, fake_resolver=fake_resolver)
    udp.subscribe(backend.on_datagram_received)
    return udp
