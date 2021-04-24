#!/usr/bin/env python
# coding=utf-8

import argparse
import asyncio

from LiDns import request, resolve


# todo: add

def main():
    parser = argparse.ArgumentParser(description='Start a smart DNS proxy implemented in Python')
    parser.add_argument('--bind_ip', default='127.0.0.1', type=str, help='The ip to listen on. default:127.0.0.1',
                        metavar='ip')
    parser.add_argument('--bind_port', default=5053, type=int, help='The port to listen on. default:5053',
                        metavar='port')
    parser.add_argument('--upstream_dns_ip', default='8.8.8.8', type=str,
                        help='ip of the upstream dns server to resolve real ip (default:8.8.8.8)', metavar='ip')
    parser.add_argument('--upstream_dns_port', default='53', type=int,
                        help='port of the upstream dns server to resolve real ip (default:53)', metavar='port')
    parser.add_argument('--smart', action='store_true', help='start server in smart mode')
    parser.add_argument('--redis_uri', help='redis standard uri (smart mode)', type=str, metavar='uri')
    parser.add_argument('--sni_ip', help='sni proxy ip (smart mode)', type=str, metavar='ip')

    args = parser.parse_args()
    # if args.smart:
    #     assert args.redis_uri, 'redis_uri should be provided in smart mode'
    #     assert args.sni_ip, 'sni_ip should be provided in smart mode'
    print(f"Starting nameserver on {args.bind_ip}:{args.bind_port}")
    loop = asyncio.get_event_loop()
    real_resolver = resolve.RealResolver(args.upstream_dns_ip, args.upstream_dns_port)
    fake_resolver = resolve.FakeResolver(args.sni_ip)
    loop.run_until_complete(request.start_server(loop, args.bind_ip, args.bind_port, real_resolver=real_resolver,
                                                 fake_resolver=fake_resolver))
    loop.run_forever()


if __name__ == '__main__':
    main()
