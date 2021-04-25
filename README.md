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
   1. if it is flagged as a sanctionative server in Redis db, LiDns responds to the query with a pre-defined SNI proxy ip  
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
run `python server.py --help` to see usage