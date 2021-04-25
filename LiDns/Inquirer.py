import asyncio
import logging

import aiohttp
import aioredis
from aiohttp import web

from LiDns import Resolvers

_Inquirer_NUM = 0


class Inquirer:
    def __init__(self, redis_uri, loop=None):
        global _Inquirer_NUM
        _Inquirer_NUM += 1
        self.logger = logging.getLogger(f'inquirer-{_Inquirer_NUM}')
        self.DIRECT_KEY = Resolvers.SmartResolver.DIRECT_KEY
        self.PROXY_KEY = Resolvers.SmartResolver.PROXY_KEY
        self.INQUIRY_KEY = Resolvers.SmartResolver.INQUIRY_KEY
        self.INQUIRY_CACHE_KEY = Resolvers.SmartResolver.INQUIRY_CACHE_KEY
        self.loop = loop or asyncio.get_event_loop()
        self.redis_client: aioredis.Redis = self.loop.run_until_complete(aioredis.create_redis(redis_uri))

    async def start(self):
        self.logger.info('inquirer started')
        while True:
            query = await self.redis_client.rpop(self.INQUIRY_KEY, encoding='utf8')
            if query:
                self.logger.info(f'got {query} to inquire')
                await self.redis_client.srem(self.INQUIRY_CACHE_KEY, query)
                self.logger.debug(f'remove {query} from INQUIRY_CACHE_KEY in {self.INQUIRY_CACHE_KEY}')
                await self.inquire(query)
                await asyncio.sleep(0.1)

            else:
                await asyncio.sleep(1)

    async def inquire(self, query: str, schema=None):
        url = query.rstrip('.')
        schema_ = schema or 'https://'
        self.logger.debug(f'checking {schema_}{url}')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{schema_}{url}') as resp:
                    status = await self.check_respone(resp)
                    if status == 'direct':
                        await self.redis_client.sadd(self.DIRECT_KEY, query)
                        self.logger.info(f'added {query} to direct set {self.DIRECT_KEY}')
                    else:
                        await self.redis_client.sadd(self.PROXY_KEY, query)
                        self.logger.info(f'added {query} to proxy set {self.PROXY_KEY}')
        except web.HTTPException:
            self.logger.error(f'error getting {schema_}{url}', stack_info=True)
            if not schema:
                self.logger.debug(f'inquiring http://{url} because of error in https:// inquiring')
                await self.inquire(query, 'http://')

    async def check_respone(self, response):
        self.logger.debug(f'get status code {response.status}')
        if response.status == 403:
            resp = await response.text()
            if 'Your client does not have permission to get URL' in resp:
                return 'proxy'
        return 'direct'
