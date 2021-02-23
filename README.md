# Culex
Culex is a Coap to MQTT bridge for use with RIOT-os sensor nodes.  
It uses the name of the hosts to determine the MQTT topic.

It bridges coap packages to MQTT based on a host name.

`COAP POST to /temp from 'node' -> /pathprefix/node/temp in MQTT `


# COAP
It currently listens on a single coap endpoint: `coap://[::]:5863/temp` 
The port and binding interface is configurable in config.ini

# MQTT
The MQTT server to connect to is specified in the config file.

You can use the pathprefix to change the topic locations

# Known hosts.
Culex saves the IP adresses of known hosts in the config.ini file. 

If an unknown node is encountered. It is placed in the unknown hosts lists with a temporary name.

You can copy this line to known_hosts and restart culex.

# Installation instruction

Install the dependancies present in requirements.txt using pip.

The service can then be installed and started by running `./install`
This will create a service based on the culex.service.template and add it to systemd.

