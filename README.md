# Culex
Culex is a Coap to MQTT bridge. That uses the name of the hosts to determine the MQTT topic.

It currently listens on a single coap endpoint: `coap://[]::]:5863/temp` 

# Known hosts.
Culex saves the IP adresses of known hosts in the config.ini file. 

If an unknown node is encountered. It is placed in the unknown hosts lists with a temporary name.
You can copy this line to known_hosts and restart culex.

# Installation instruction

Install the dependancies present in requirements.txt using pip.

The service can then be installed and started by running `./install`
This will create a service based on the culex.service.template and add it to systemd.

