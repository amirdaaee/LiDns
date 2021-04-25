#!/usr/bin/env python
# coding=utf-8

import argparse
import asyncio
import logging
import time

from LiDns import Handlers, Resolvers, Inquirer



def main():
    logger = logging.getLogger('server')
    parser = argparse.ArgumentParser(description='Start a smart DNS proxy implemented in Python')
    parser.add_argument('--bind_ip', default='127.0.0.1', type=str, help='The ip to listen on. default:127.0.0.1',
                        metavar='ip')
    parser.add_argument('--bind_port', default=5053, type=int, help='The port to listen on. default:5053',
                        metavar='port')
    parser.add_argument('--dns_ip', default='8.8.8.8', type=str,
                        help='ip of the upstream dns server to resolve real ip (default:8.8.8.8)', metavar='ip')
    parser.add_argument('--dns_port', default='53', type=int,
                        help='port of the upstream dns server to resolve real ip (default:53)', metavar='port')
    parser.add_argument('--smart', help='smart mode', action='store_true')
    parser.add_argument('--redis_uri', help='redis standard uri (smart mode)', type=str, metavar='uri')
    parser.add_argument('--sni_ip', help='sni proxy ip (smart mode)', type=str, metavar='ip')
    parser.add_argument('--aggressive', help='resolve to sni if query in not cached yet (smart mode)',
                        action='store_true')
    parser.add_argument('--sni_ttl', help='ttl[s] for sni ip answers (smart mode) (default=24h)', default=60 * 60 * 24,
                        type=int, metavar='int')
    parser.add_argument('--inquiry_ttl', help='ttl[s] for uncached query answers (smart mode) (default=1s)',
                        default=1, type=int, metavar='int')
    parser.add_argument('--no_inquirer', help='number of inquirers in loop (smart mode) (default=2)',
                        default=2, type=int, metavar='int')
    parser.add_argument('--log', help='log level (default:INFO)', choices=['DEBUG', 'INFO', 'WARNING'],default='INFO')
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging,args.log), format='[%(levelname)s] %(name)s:\t%(message)s [%(asctime)s]')
    if args.smart:
        assert args.redis_uri, 'redis_uri should be provided in smart mode'
        assert args.sni_ip, 'sni_ip should be provided in smart mode'

    print(f"Starting nameserver on {args.bind_ip}:{args.bind_port}")
    logger.info(f"Starting nameserver on {args.bind_ip}:{args.bind_port}")
    logger.info(f"upstream DNS {args.dns_ip}:{args.dns_port}")
    logger.info(f"smart mode: {args.smart}")
    if args.smart:
        logger.info(f"redis uri: {args.redis_uri}")
        logger.info(f"number of inquirers: {args.no_inquirer}")
        logger.info(f"sni ttl: {args.sni_ttl}")
        logger.info(f"inquiry ttl: {args.inquiry_ttl}")
        logger.info(f"aggressive mode: {args.aggressive}")

    loop = asyncio.get_event_loop()
    if args.smart:
        resolver = Resolvers.SmartResolver(args.dns_ip,
                                           args.dns_port,
                                           sni_ip=args.sni_ip,
                                           redis_uri=args.redis_uri,
                                           aggressive=args.aggressive,
                                           sni_ttl=args.sni_ttl,
                                           inquiry_ttl=args.inquiry_ttl)
    else:
        resolver = Resolvers.SimpleResolver(args.dns_ip, args.dns_port)
    Handlers.UdpDnsServer.start_server(args.bind_ip, args.bind_port, resolver=resolver, loop=loop)
    for _ in range(args.no_inquirer):
        loop.create_task(Inquirer.Inquirer(args.redis_uri, loop=loop).start())
        time.sleep(0.1)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('shutting down server')
        logger.info('shutting down server')


if __name__ == '__main__':
    main()
