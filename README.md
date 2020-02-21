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
## Scenario
Scenarios are input commands which are used to instruct the server how to behave. For example, if you want a node to start sending a message after T seconds, you have to write it down in the scenario section like the following example.  
```
ChangeLoc UID-x1-y1 UID-x2-y2 ...
SendMessage sourceUID-Message-destUID
Wait T
```
also we should have an input file for initialization of nodes. to facilitate making input for the code, I've provide a simple code (Scenario_generator.py) that generate random senario and input for testing. you can see examples of input and scenario in the repasitory.

