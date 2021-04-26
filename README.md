# LiDns

**Liberia Dns is a python asyncio based smart DNS proxy server for a real free internet**  
LiDns resolves DNS queries to real ip or a predefined SNI proxy ip based on the prior automatically generated  
information of target website, stored in Redis db.

the main idea is:

1. your server/proxy server is flagged by Google (or other rulers of the internet)
2. as a result you will get a 403 (or anything else) error when using some google (or other rulers) backed services
3. you think of a way to get rid of the persecution of the great ruler
4. you may try tor, but its speed is low and also leads to various captcha problems
5. also, manually routing blocked ips to tor, is not convenient
6. so you can use LiDns server with a [sniproxy](https://github.com/amirdaaee/SNI-SSL-Proxy-docker)

## How does it work

### DNS server

1. A DNS lookup query is received by the server
2. Server checks if the queried domain is available in local Redis db (a.k.a. status cache)
3. if it is available in Redis:
    1. if it is flagged as a sanctionative server in Redis db, LiDns responds to the query with a pre-defined SNI proxy
       ip
    2. if not, it relays the query to the upstream DNS server (e.g. 8.8.8.8) and returns the response
4. if it is not available in Redis:
    1. LiDns queries to upstream DNS or responds the query with a pre-defined SNI proxy ip (based on the  
       configuration)
    2. it adds the domain name to Redis db (a.k.a. Inquiry cache) to be inquired by the inquirer

### Inquirer

1. waits until a record becomes available in the inquiry cache
2. sends an HTTP get request to the domain
3. fills out the status cache for the domain based on the request-response and status code

## performance

LiDns is written using asyncio coroutines to keep up performance despite third-party services time consumption.  
currently, it doesn't reliably support pypy, but it is scheduled for future upgrades.

## how to use

### cli

run `python server.py --help` to see usage

### docker

docker image is available at [docker-hub](https://hub.docker.com/r/amirdaaee/lidns)

supported environmental variables are:

- BIND_IP: equals to cli `--bind_ip`
- BIND_PORT: equals to cli `--bind_port`
- DNS_IP: equals to cli `--dns_ip`
- DNS_PORT: equals to cli `--dns_port`
- SMART_MODE: equals to cli `--smart` option. declaring this variable with **any value** will result in the starting DNS
  server in smart mode. to disable smart mode, do not declare this variable **at all**.
- REDIS_URI: equals to cli `--redis_uri`
- SNI_IP: equals to cli `--sni_ip`
- AGGRESSIVE_MODE: equals to cli `--aggressive` option. declaring this variable with **any value** will result in the
  starting smart DNS server in aggressive mode. to disable the aggressive mode, do not declare this variable **at all**.
- INQUIRY_TTL: equals to cli `--inquiry_ttl`
- NO_INQUIRER: equals to cli `--no_inquirer`
- LOG_LEVEL: equals to cli `--log`

furthermore, you can use `docker-compose.yml` for a complete deployment besides Redis and sniproxy

## v2ray/v2fly compatibility

you can use v2ray (or v2fly) proxy server to recap all services. you just need to route all DNS query requests to LiDns,
add create an internal DNS in v2ray server configuration and force outbound freedom protocol to use **ipv4**:

    {
    "dns": {
        "servers": [
          {
            "address": **LiDns ip**,
            "port": **LiDns port**
          }
        ],
        "tag": "internal_dns"
      },
      "routing": {
        "domainStrategy": "AsIs",
        "rules": [
          {
            "type": "field",
            "port": "53",
            "network": "udp",
            "outboundTag": "dns"
          }
        ]
      },
      "inbounds": [
        {
          "listen": "0.0.0.0",
          "port": 1080,
          "protocol": "http"
        }
      ],
      "outbounds": [
        {
          "protocol": "freedom",
          "settings": {
            "domainStrategy": "UseIPv4"
          },
          "tag": "direct"
        },
        {
          "protocol": "dns",
          "settings": {
            "network": "udp",
            "address": **LiDns ip**,
            "port": **LiDns port**
          },
          "tag": "dns"
        }
      ]
    }

**note**: if you can do it better, tell me in issues

**note**: if not using the aggressive mode, watch for your browser DNS cache, which is it defaults to 1 minute in
firefox and google chrome

## Contribution

Any contribution is highly appreciated