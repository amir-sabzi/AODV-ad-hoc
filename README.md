# Implementation of AODV
I've implement in this project a simulation of Ad hoc On-Demand Distance Vector Routing in python multi-Thread environment.  
They can communicate and send/receive messages in this network.
## Vehicles
I designed two class, one known as "Vehicle" that has following properties:
* <b>(IP,Port)</b>: We set localhost IP (127.0.0.xxx) for each vehicle and also we dedicate a port for each vehicle to handle sockets.
* <b>UID</b>: ID of each vehicle which should be a unique positive integer.
* <b>Location</b>: A pair of (x, y) which point to the current position of a node within the field.
* <b>Radius</b>: Range of accessibility of each node.  
## Server
Though in the real world you do not have the address of your neighbors, to implement a practical model, you need to implement a server. All communications are going through the server. The server must be capable of transmitting messages considering the distance between the nodes. Each vehicle knows about the address of the server and can only send and receive messages via its link with the server. Note that the server is only a simulator for real word situation so there is no need for it in a real scenario.
