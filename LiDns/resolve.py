# import dns
import dns.asyncquery
import dns.message
import dns.rdtypes
import dns.rrset
from dns.rdtypes.IN import A as rdtypes_IN_A


class RealResolver:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    async def resolve(self, query):
        resp = await dns.asyncquery.udp(query, self.ip, self.port)
        return resp


class FakeResolver:
    def __init__(self, answer_ip):
        self.answer_ip = answer_ip

    def resolve(self, query):
        response = dns.message.make_response(query)
        response.answer.append(dns.rrset.RRset(response.question[0].name, 1, 1))
        response.answer[0].add(rdtypes_IN_A.A(1, 1, self.answer_ip))
        return response


def read_request_packet(packet):
    return dns.message.from_wire(packet)
