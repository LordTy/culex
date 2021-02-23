import datetime
import logging
import configparser
import json

import asyncio

import aiocoap.resource as resource
import aiocoap

from paho.mqtt import client as mqtt_client

MQTTdefault={'username':'anonymous','password':None,'host':'localhost','port':1883}

client = mqtt_client.Client()
logging.basicConfig(level=logging.INFO)
clog = logging.getLogger("coap-server")
clog.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
known_hosts = dict()
unknown_hosts = dict()


class PrintingLogSite(aiocoap.resource.Site):
    def render(self, request):
        clog.debug("Request from {} to {}".format(request.remote, request.opt.uri_path))
        return super().render(request)

def hostsfromconfig(hosts,hdict):
    for host in hosts.split('\n'):
        if len(host)>0:
            host = host.split( );
            hdict[host[1].strip()] = host[0].strip()
    return hdict

def hoststoconfig():
    hosttext = '\n'
    for key in unknown_hosts:
        value = unknown_hosts[key]
        hosttext+= f("{value} {key}\n")
    config['HOSTS']['unknown_hosts']=hosttext
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def namefromhost(hostname):
    if hostname in known_hosts:
        clog.debug("{} known as {}".format(hostname,known_hosts[hostname]))
        return known_hosts[hostname]
    else:
        if hostname in unknown_hosts:
            clog.debug("{} known as {}".format(hostname,unknown_hosts[hostname]))
            return unknown_hosts[hostname] 
        newname = "temp{}".format((len(known_hosts)+1))
        unknown_hosts[hostname]=newname
        clog.debug("{} added as {}".format(hostname,unknown_hosts[hostname]))
        hoststoconfig()
        return newname

class TempResource(resource.Resource):
    async def render_get(self,request):
        hostname = namefromhost(request.remote.hostinfo)
        clog.info(f"get request from {request.remote.hostinfo}")
        return aiocoap.Message(content_format=0,payload='OK'.encode('utf8'));

    async def render_post(self,request):
        hostname = namefromhost(request.remote.hostinfo)
        clog.info(f"put request from {request.remote.hostinfo}")
        client.publish(f"{config['MQTT']['pathprefix']}/{hostname}/temp",payload=request.payload)
        return aiocoap.Message()

def on_connect(client, userdata, flags, rc):
    logging.info("Connected to {} with result code {}".format(client._host,str(rc)))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")


def main():
    config.read('config.ini')

    hostsfromconfig(config['HOSTS']['known_hosts'],known_hosts)
    hostsfromconfig(config['HOSTS']['unknown_hosts'],unknown_hosts)
    
    clog.info("Routes configured:")
    for hosts in known_hosts:
        clog.info(f"{hosts} as {known_hosts[hosts]}")

    client.on_connect = on_connect
    client.username_pw_set(config['MQTT'].get('username',MQTTdefault['username']),config['MQTT'].get('password',MQTTdefault['password']))
    client.connect(config['MQTT'].get('host',MQTTdefault['host']),config['MQTT'].getint('port',MQTTdefault['port']))
    client.loop_start()

    root = PrintingLogSite()
    root.add_resource(['.well-known', 'core'],
            resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['temp'], TempResource())

    clog.info("Routes configured:")
    for route in root._resources:
        clog.info(route)

    logging.info(f"Starting coap server on: [{config['COAP']['interface']}]:{config['COAP'].getint('port')}")
    asyncio.Task(aiocoap.Context.create_server_context(root,bind=(config['COAP']['interface'],config['COAP'].getint('port'))))
    asyncio.get_event_loop().run_forever()

    

if __name__ == "__main__":
    main()





