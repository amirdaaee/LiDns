import asyncio
import logging
from abc import abstractmethod

import aioredis
import dnslib

from LiDns.Handlers import UdpClient


class Resolver:

    def __init__(self, upstream_dns_ip, upstream_dns_port):
        self.upstream_dns_ip = upstream_dns_ip
        self.upstream_dns_port = upstream_dns_port

    @abstractmethod
    async def resolve(self, packet):
        raise NotImplementedError('')

    async def resolve_upstream(self, packet):
        response = await UdpClient.send(self.upstream_dns_ip, self.upstream_dns_port, packet)
        return dnslib.DNSRecord.parse(response)


class SimpleResolver(Resolver):

    async def resolve(self, packet):
        response = await self.resolve_upstream(packet)
        return response.pack()


class SmartResolver(Resolver):
    __name__ ='SmartResolver'
    redis_client: aioredis.Redis
    DIRECT_KEY = 'direct'
    PROXY_KEY = 'proxy'
    INQUIRY_KEY = 'inquiry'
    INQUIRY_CACHE_KEY = 'inquiry_cache'

    def __init__(self, upstream_dns_ip, upstream_dns_port, sni_ip, redis_uri, aggressive, sni_ttl, inquiry_ttl):
        super(SmartResolver, self).__init__(upstream_dns_ip, upstream_dns_port)
        loop = asyncio.get_event_loop()
        self.sni_ip = sni_ip
        self.redis_client = loop.run_until_complete(aioredis.create_redis(redis_uri))
        self.aggressive = aggressive
        self.sni_ttl = sni_ttl
        self.inquiry_ttl = inquiry_ttl

    async def resolve(self, packet):
        logger = logging.getLogger(f'{self.__name__}({asyncio.tasks.current_task().get_name()})')
        query = dnslib.DNSRecord.parse(packet)
        if query.q.qtype == dnslib.QTYPE.A:
            qname = str(query.q.qname)
            logger.debug(f'query name: {qname}')
            cache, inquiry_stat = await self.cache_works(qname)
            logger.debug(f'cache stat: {cache}')
            logger.debug(f'inquiry stat: {inquiry_stat}')
            if cache == 'direct':
                response = await self.resolve_upstream(packet)
            else:
                response = self.resolve_sni(query)
            if inquiry_stat:
                self.modify_ttl(response, self.inquiry_ttl)

        else:
            logger.debug('query is not A type')
            response = await self.resolve_upstream(packet)

        return response.pack()

    async def cache_works(self, key):
        if await self.redis_client.sismember(self.DIRECT_KEY, key):
            ret = 'direct'
            inquery_stat = False
        elif await self.redis_client.sismember(self.PROXY_KEY, key):
            ret = 'proxy'
            inquery_stat = False
        else:
            if not await self.redis_client.sismember(self.INQUIRY_CACHE_KEY, key):
                await self.redis_client.sadd(self.INQUIRY_CACHE_KEY, key)
                await self.redis_client.lpush(self.INQUIRY_KEY, key)
            ret = 'proxy' if self.aggressive else 'direct'
            inquery_stat = True

        return ret, inquery_stat

    def resolve_sni(self, query: dnslib.DNSRecord):
        resp = query.reply()
        resp.add_answer(dnslib.RR(query.q.qname, query.q.qtype, rdata=dnslib.A(self.sni_ip), ttl=self.sni_ttl))
        return resp

    @staticmethod
    def modify_ttl(query: dnslib.DNSRecord, ttl):
        for rr in query.rr:
            rr.ttl = ttl
