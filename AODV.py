import socket
import time
import threading
import math
import json
import random
'''class Message:
    def __init__(self, sender_IP,receiver_IP ,seq_num,dest_seq_num,destination_IP,type, message):
        self.sender_IP = sender_IP
        self.receiver_IP = receiver_IP
        self.seq_num = seq_num
        self.dest_seq_num = dest_seq_num
        self.destination_IP = destination_IP  #if broadCast IP is 1.1.1.1
        self.type = type        #six type of messages : RREQ , RREP , data , Initialization , Initialization_Ack
                                #                        Initialization_done
        self.message = message'''
###############################    server   ###########################################
class Server(object):
    def __init__(self,n,IP,PORT,vehicles_PORT,vehicles_IP,range_of_access,width,length):
        self.vehicles_num = n
        self.UIDs = [0] * self.vehicles_num
        self.PORTs = vehicles_PORT
        self.IPs = vehicles_IP
        self.RANGE = range_of_access
        self.width = width
        self.length = length
        self.Cordinates = [(math.inf,math.inf)] * self.vehicles_num
        self.in_ports = [x + 2048 for x in self.PORTs]
        self.initial_counter = 0
        self.ack_counter1 = 0
        self.ack_counter2 = 0
        self.neighbors = []
        self.all_locations_flag = False
        for port in self.in_ports:
            recieve_thread = threading.Thread(target=self.receive, args=(port,))
            recieve_thread.daemon = True  # Daemonize thread
            recieve_thread.start()
        '''neighbor_thread = threading.Thread(target=self.find_neighbors,args=())'''
    def activation(self):
        self.send_sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(self.vehicles_num)]
        i = 0
        for s in self.send_sockets:
            s.connect((self.IPs[i], self.PORTs[i]))
            i = i + 1
    def Change_loc(self):
        self.initial_counter = 0
        self.ack_counter1 = 0
        self.ack_counter2 = 0
        self.UIDs = [0] * self.vehicles_num
        self.Cordinates = [(math.inf,math.inf)] * self.vehicles_num
        self.all_locations_flag = False
    def receive(self,port):
        recieve_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recieve_socket.bind(('127.0.0.1', port))
        recieve_socket.listen()
        Node, addr = recieve_socket.accept()
        while True :
            data = Node.recv(1024)
            #print("Server", envelope.sender_IP, envelope.receiver_IP, envelope.seq_num, envelope.dest_seq_num,
                 # envelope.destination_IP, envelope.type, envelope.message)

            envelope = data.decode('utf-8')
            envelope = envelope.split(";")

            sender_IP       = envelope[0]
            receiver_IP     = envelope[1]
            seq_num         = envelope[2]
            dest_seq_num    = envelope[3]
            dest_IP         = envelope[4]
            type            = envelope[5]
            message         = envelope[6]
            #rec_add = envelope.receiver_IP
            #source_add = envelope.sender_IP
            p = random.uniform(0, 1)
            if (p < 0):
            # drop packet
                print(sender_IP,"retransmit")
                dest_ind = self.IPs.index(sender_IP)
                send_thread = threading.Thread(target=self.send, args=(data, dest_ind))
                send_thread.daemon = True
                send_thread.start()
            else:
                if (type == "Initialization"):
                    hello_index = self.IPs.index(sender_IP)
                    self.initial_counter = self.initial_counter + 1
                    message = list(map(int, message.split(",")))  #x,y,UID
                    self.UIDs[hello_index] = message[2]
                    self.Cordinates[hello_index] = (message[0],message[1])
                    broadCast_thread = threading.Thread(target=self.Conditional_BroadCast, args=(sender_IP, data))
                    broadCast_thread.daemon = True
                    broadCast_thread.start()
                    #print(self.initial_counter)
                    if self.initial_counter == self.vehicles_num :
                        #print("now")
                        self.all_locations_flag = True
                elif(type == "Initialization_Ack" ):
                    receiver_ind = self.IPs.index(receiver_IP)
                    send_thread = threading.Thread(target=self.send, args=(data, receiver_ind))
                    send_thread.daemon = True
                    send_thread.start()
                    self.ack_counter2 = self.ack_counter2 + 1
                    #print(":",self.ack_counter1,self.ack_counter2,":")
                    if self.ack_counter2 == self.ack_counter1 :
                        for ii in range(self.vehicles_num):
                            ###############################################################################################
                            temp_type = "Initialization_done"
                            temp_sender_IP = '127.0.0.1'
                            temp_receiver_IP = self.IPs[ii]
                            temp_dest_IP = "null"
                            temp_seq_num = str(0)
                            temp_dest_seq_num = str(0)
                            temp_message = "null"
                            ################################################################################################
                            done_message = temp_sender_IP+";"+temp_receiver_IP+";"+temp_seq_num+";"+temp_dest_seq_num+";"+\
                                           temp_dest_IP+";"+temp_type+";"+temp_message
                            encoded_done  = done_message.encode('utf-8')
                            send_thread = threading.Thread(target=self.send, args=(encoded_done,ii))
                            send_thread.daemon = True
                            send_thread.start()

                else:
                    if(receiver_IP == '1.1.1.1'):
                        self.BroadCast(sender_IP,data)
                    else:

                        if self.check_range(sender_IP,receiver_IP):
                            dest_ind = self.IPs.index(receiver_IP)
                            send_thread = threading.Thread(target=self.send, args=(data, dest_ind))
                            send_thread.daemon = True
                            send_thread.start()

    def BroadCast(self,source,data):
        i = 0
        envelope = data.decode('utf-8')
        envelope = envelope.split(";")

        sender_IP       = envelope[0]
        receiver_IP     = envelope[1]
        seq_num         = envelope[2]
        dest_seq_num    = envelope[3]
        dest_IP         = envelope[4]
        type            = envelope[5]
        message         = envelope[6]
        for dest in self.IPs:
            if dest == source :
                i = i + 1
                continue
            else:
                if self.check_range(source,dest):
                    broadCast_message = sender_IP+";"+dest+";"+seq_num+";"+dest_seq_num+";"+\
                                        dest_IP+";"+type+";"+message
                    encoded_BC        = broadCast_message.encode('utf-8')
                    send_thread = threading.Thread(target=self.send, args=(encoded_BC,i))
                    send_thread.daemon = True
                    send_thread.start()
                i = i + 1


    def Conditional_BroadCast(self,source,date):
        while True :
            if self.all_locations_flag :
                i = 0
                for dest in self.IPs:
                    if dest == source :
                        i = i + 1
                        continue
                    else:
                        if self.check_range(source,dest):
                            self.ack_counter1 = self.ack_counter1 + 1
                            #print(":", self.ack_counter1, self.ack_counter2, ":")
                            send_thread = threading.Thread(target=self.send, args=(date,i))
                            send_thread.daemon = True
                            send_thread.start()
                        i = i + 1

                break

    def check_range(self,source,dest):
        source_ind = self.IPs.index(source)
        dest_ind = self.IPs.index(dest)
        source_cord = self.Cordinates[source_ind]
        dest_cord = self.Cordinates[dest_ind]
        xs = source_cord[0]
        ys = source_cord[1]
        xd = dest_cord[0]
        yd = dest_cord[1]
        d  = (xs - xd)**2 + (ys - yd)**2
        dd = (self.RANGE)**2
        if (xs > self.length or xd > self.length or yd > self.width or ys > self.width):
            return False
        elif (d < dd):
            return True
        else:
            return False

    def send(self, message, i):
        time.sleep(random.uniform(0,self.vehicles_num/6 +0.5))
        self.send_sockets[i].send(message)





    #def send_to_all(self,message):






###############################    vehicles   ###########################################
class Vehicles(object):
    def __init__(self,UID,ip,port,x,y,delay):
        self.UID = UID
        self.period = 1000
        self.IP = ip
        self.PORT = port
        self.x= x
        self.out_Port = self.PORT + 2048
        self.y= y
        self.delay = delay
        self.initial_Done = False
        recieve_thread = threading.Thread(target=self.receive, args=())
        recieve_thread.daemon = True  # Daemonize thread
        recieve_thread.start()
        self.seq_num = 0    # Every node maintains its monotonically increasing sequence number -> increases
                            #every time the node notices change in the neighborhood topology

        self.route_table = []           #<destination addr, next-hop addr,destination sequence number, life_time>




    def activation(self):
        self.send_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.send_socket.connect(('127.0.0.1',self.out_Port))

    def Initialization(self):
        ##############################################################################################################
        type = "Initialization"
        sender_IP = self.IP
        receiver_IP = '127.0.0.1'
        dest_IP = 'null'
        message = str(self.x)+","+str(self.y)+","+str(self.UID)   # x,y,UID
        seq_num = str(0)
        dest_seq_num = str(0)
        ##############################################################################################################
        #def __init__(self, sender_IP,receiver_IP ,seq_num,dest_seq_num,destination_IP,type, message):
        #print(sender_IP,receiver_IP,seq_num,dest,type,message)
        hello_message = sender_IP+";"+receiver_IP+";"+seq_num+";"+dest_seq_num+";"+\
                                        dest_IP+";"+type+";"+message
        encoded_hello = hello_message.encode('utf-8')
        send_thread = threading.Thread(target=self.send, args=(encoded_hello,))
        send_thread.daemon = True
        send_thread.start()


    def receive(self):
        recieve_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print()
        #print(self.UID,"  ",self.IP," ",self.PORT)
        recieve_socket.bind((self.IP, self.PORT))
        recieve_socket.listen()
        server, addr = recieve_socket.accept()
        while True :
            data = server.recv(1024)

            # def __init__(self, sender_IP,receiver_IP ,seq_num,dest_seq_num,destination_IP,type, message)
            envelope = data.decode('utf-8')
            envelope = envelope.split(";")

            sender_IP = envelope[0]
            receiver_IP = envelope[1]
            seq_num = int(envelope[2])
            dest_seq_num = int(envelope[3])
            dest_IP = envelope[4]
            type = envelope[5]
            message = envelope[6]
            print(sender_IP,receiver_IP,type,dest_IP,message)
            #print(type)
            if(sender_IP == self.IP):
                #retransmit
                print(self.IP,"trensmited")
                send_thread = threading.Thread(target=self.send, args=(data,))
                send_thread.daemon = True
                send_thread.start()
            else:
                if (type == "Initialization"):
                    ########################################## Initialization ##########################################
                    type = "Initialization_Ack"
                    receiver_IP  = sender_IP
                    dest_IP = "null"
                    seq_num = 0
                    dest_seq_num = 0
                    message = str(self.UID)
                    ######################################################################################################
                    hello_Ack = self.IP+";"+receiver_IP+";"+str(seq_num)+";"+str(dest_seq_num)+";"+\
                                            dest_IP+";"+type+";"+message
                    encoded_Ack = hello_Ack.encode('utf-8')
                    send_thread = threading.Thread(target=self.send, args=(encoded_Ack,))
                    send_thread.daemon = True
                    send_thread.start()
                if type == "Initialization_Ack":
                    self.update_or_Add_route(sender_IP,sender_IP,0)
                if type =="Initialization_done":
                    self.initial_Done = True
                ########################################## after Initialization #######################################
                    # (sender_IP,  receiver_IP ,seq_num,destination_IP,type, message)
                    # sender_IP = previous_HOP   ; seq_NUM shiould be check
                    # message = source_address
                    # now we know to send a packet to source_address we should pass it to previous_HOP
                if self.initial_Done :
                    if (type == "data"):
                        if(dest_IP == self.IP ):
                            print(message,self.IP)
                            print(time.time())
                        else:
                            #m = Message(self.IP, self.search_route(dest_add), envelope.seq_num, envelope.dest_seq_num, dest_add, "data",
                             #           envelope.message)
                            data_message =  self.IP+";"+self.search_route(dest_IP)+";"+str(seq_num)+";"+str(dest_seq_num)+";"+\
                                            dest_IP+";"+type+";"+message
                            encoded_data = data_message.encode('utf-8')
                            send_thread = threading.Thread(target=self.send, args=(encoded_data,))
                            send_thread.daemon = True
                            send_thread.start()


                    if (type == "RREQ"):
                        if(dest_IP == self.IP):                           ## I am destination
                            #temp_source_add = envelope.message
                            #temp_sender_IP = envelope.sender_IP
                            #temp_seq_num = int(envelope.seq_num)
                            #print(self.getter_seqNUM(temp_source_add))
                            #print(temp_seq_num)

                            if(self.getter_seqNUM(message) < seq_num):
                                print("iam dest :", self.IP)
                                self.update_or_Add_route(message, sender_IP, seq_num)
                                ##############################       we are dest        ###############################
                                ######################  so we should SEND RREP to source ###############################
                                RREP_dest = message
                                RREP_type = "RREP"
                                RREP_rec = sender_IP
                                RREP_send = self.IP
                                RREP_source = dest_IP
                                RREP_seq_num = str(self.seq_num)
                                RREP_dest_seq_num = str(self.getter_seqNUM(message))
                                # (self, sender_IP,receiver_IP ,seq_num,dest_seq_num,destination_IP,type, message):
                                #RREP_message = Message(RREP_send, RREP_rec, RREP_seq_num, RREP_dest_seq_num, \
                                                       #RREP_dest, RREP_type, RREP_source)
                                RREP_message =  RREP_send+";"+RREP_rec+";"+RREP_seq_num+";"+RREP_dest_seq_num+";"+ \
                                                RREP_dest+";"+RREP_type+";"+RREP_source
                                RREP_encoded = RREP_message.encode('utf-8')
                                send_thread = threading.Thread(target=self.send, args=(RREP_encoded,))
                                send_thread.daemon = True
                                send_thread.start()

                        else:                                                   ## I am NOT destination
                            #print("iam NOT dest")
                            #temp_source_add = envelope.message
                            #temp_seq_num = int(envelope.seq_num)
                            #print(self.getter_seqNUM(temp_source_add))
                            #print(temp_seq_num)
                            if( self.getter_seqNUM(message) < seq_num):
                                #temp_sender_IP = envelope.sender_IP
                                #temp_dest_seq_num = int(envelope.dest_seq_num)
                                #print("route_added_nd")
                                self.update_or_Add_route(message, sender_IP, seq_num)
                                #temp_dest_add = envelope.destination_IP
                                if(self.search_route(dest_IP) == -1) or (self.getter_seqNUM(dest_IP) < dest_seq_num):
                                    ############################## broadCast RREQ ##########################################
                                    #temp_message = Message(self.IP,'1.1.1.1',envelope.seq_num,envelope.dest_seq_num
                                                           #,envelope.destination_IP,envelope.type,envelope.message)

                                    temp_message = RREP_message =  self.IP+";"+'1.1.1.1'+";"+str(seq_num)+";"+str(dest_seq_num)+";"+\
                                                    dest_IP+";"+type+";"+message
                                    encoded_temp = temp_message.encode('utf-8')
                                    send_thread = threading.Thread(target=self.send, args=(encoded_temp,))
                                    send_thread.daemon = True
                                    send_thread.start()
                                elif(self.getter_seqNUM(dest_IP) > dest_seq_num):
                                    ########################## we have a root to dest#######################################
                                    ######################  so we should SEND RREP to source ###############################
                                    RREP_dest           = message
                                    RREP_type           = "RREP"
                                    RREP_rec            = sender_IP
                                    RREP_send           = self.IP
                                    RREP_source         = dest_IP
                                    RREP_seq_num        = str(self.getter_seqNUM(dest_IP))
                                    RREP_dest_seq_num   = str(self.getter_seqNUM(message))
                                    #(self, sender_IP,receiver_IP ,seq_num,dest_seq_num,destination_IP,type, message):
                                    #RREP_message  = Message(RREP_send,RREP_rec,RREP_seq_num,RREP_dest_seq_num,\
                                    #                        RREP_dest,RREP_type,RREP_source)
                                    RREP_message = RREP_send + ";" + RREP_rec + ";" + RREP_seq_num + ";" + RREP_dest_seq_num + ";" + \
                                                   RREP_dest + ";" + RREP_type + ";" + RREP_source
                                    RREP_encoded = RREP_message.encode('utf-8')
                                    send_thread = threading.Thread(target=self.send, args=(RREP_encoded,))
                                    send_thread.daemon = True
                                    send_thread.start()
                    if( type == "RREP"):
                        #dest_add = envelope.destination_IP
                        #source_add = envelope.message
                        #seq_num = int(envelope.seq_num)
                        #sender_add = envelope.sender_IP
                        if (dest_IP == self.IP):
                            if(self.getter_seqNUM(message) < seq_num):
                                print("route_find  :",self.IP)
                                self.update_or_Add_route(message, sender_IP, seq_num)
                                self.Start_sending_data(message,self.data)
                        else:
                            if (self.getter_seqNUM(message) < seq_num):
                                self.update_or_Add_route(message, sender_IP, seq_num)
                                #m = Message(self.IP,self.search_route(dest_add),envelope.seq_num,envelope.dest_seq_num,dest_add,"RREP",source_add)
                                m = self.IP + ";" + self.search_route(dest_IP) + ";" + str(seq_num) + ";" + str(dest_seq_num) + ";" + \
                                                   dest_IP + ";" + type + ";" + message
                                encoded_m = m.encode('utf-8')
                                send_thread = threading.Thread(target=self.send, args=(encoded_m,))
                                send_thread.daemon = True
                                send_thread.start()


    def Start_RREQ(self,destination_add,data):
        print(time.time())
        self.data = data
        if self.search_route(destination_add) != -1:
            self.Start_sending_data(destination_add, self.data)
        else:
            RREQ_dest = destination_add
            RREQ_type = "RREQ"
            RREQ_rec = '1.1.1.1'
            RREQ_send = self.IP
            RREQ_source = self.IP
            self.seq_num = self.seq_num + 1
            RREQ_seq_num = str(self.seq_num)
            RREQ_dest_seq_num = str(self.getter_seqNUM(destination_add))
            # (self, sender_IP,receiver_IP ,seq_num,dest_seq_num,destination_IP,type, message):
            #RREQ_message = Message(RREQ_send, RREQ_rec, RREQ_seq_num, RREQ_dest_seq_num, \
            #                       RREQ_dest, RREQ_type, RREQ_source)
            RREQ_message = RREQ_send + ";" + RREQ_rec + ";" + RREQ_seq_num+ ";" + RREQ_dest_seq_num+ ";" + \
                           RREQ_dest + ";" + RREQ_type+ ";" + RREQ_source
            RREQ_encoded = RREQ_message.encode('utf-8')
            #byte_array = json.dumps(RREQ_message.__dict__).encode("utf-8")
            send_thread = threading.Thread(target=self.send, args=(RREQ_encoded,))
            send_thread.daemon = True
            send_thread.start()
    def Start_sending_data(self,destination_add,data):
        data_dest = destination_add
        data_type = "data"
        data_rec = self.search_route(destination_add)
        data_send = self.IP
        data_source = self.IP
        self.seq_num = self.seq_num + 1
        data_seq_num = str(self.seq_num)
        data_dest_seq_num = str(self.getter_seqNUM(destination_add))
        # (self, sender_IP,receiver_IP ,seq_num,dest_seq_num,destination_IP,type, message):
        #data_message = Message(data_send, data_rec, data_seq_num, data_dest_seq_num, \
        #                       data_dest, data_type, data)
        data_message = data_send + ";" + data_rec + ";" + data_seq_num + ";" + data_dest_seq_num + ";" + \
                       data_dest + ";" + data_type + ";" + data + "," + data_source
        data_encoded = data_message.encode('utf-8')
        send_thread = threading.Thread(target=self.send, args=(data_encoded,))
        send_thread.daemon = True
        send_thread.start()
    def update_or_Add_route(self,destination_Add,next_HOP,seq_num):     #<destination addr,next-hop addr,destination sequence number,life_time>
        flag = True
        for entry in self.route_table:
            if(entry[0] == destination_Add):
                entry[1] = next_HOP
                entry[2] = seq_num
                entry[3] = self.period
                flag = False
        if flag :
            temp = [destination_Add,next_HOP,seq_num,self.period]
            self.route_table.append(temp)


    def search_route(self,destination_Add):
        flag = True
        for entry in self.route_table:
            if(entry[0]==destination_Add):
                return entry[1]
                flag = False
        if flag :
            return  -1

    def getter_seqNUM(self,destination_Add):
        flag = True
        for entry in self.route_table:
            if (entry[0] == destination_Add):
                return entry[2]
                flag = False
        if flag :
            return -1
    def send(self,message):
        time.sleep(self.delay)
        self.send_socket.send(message)


class UID_IP(object):
    def __init__(self,UIDs,IPs):
        self.UIDs = UIDs
        self.IPs  = IPs
    def UID2IP(self,UID):
        index = self.UIDs.index(UID)
        return self.IPs[index]
    def IP2UID(self,IP):
        index = self.IPs.index(IP)
        return self.UIDs[index]







##################################      main    #####################################################################


range_of_availability = int(input())
[length_of_battlefield , width_of_battledfield] = list(map(int, input().split()))
number_of_vehicles = int(input())
list_of_vehicles = []
IP_of_server = '127.0.0.1'
PORT_OF_server = 2048
UIDs = []
IPs  = []
for i in range(number_of_vehicles):
            [UID,IP,PORT,x,y,delay] = input().split()
            #print([UID,IP,PORT,x,y,delay])
            list_of_vehicles.append(Vehicles(int(UID),IP,int(PORT),int(x),int(y),float(delay) ))
            UIDs.append(int(UID))
            IPs.append(IP)
UidIp = UID_IP(UIDs,IPs)

list_of_UIDs = []
list_of_PORTs = []
list_of_IPs = []
for Vehicle in list_of_vehicles:
        list_of_IPs.append(Vehicle.IP)
        list_of_PORTs.append(Vehicle.PORT)
s = Server(number_of_vehicles,IP_of_server,PORT_OF_server,list_of_PORTs,list_of_IPs,range_of_availability\
           ,width_of_battledfield,length_of_battlefield)
s.activation()
for v in list_of_vehicles :
    v.activation()
#for v in list_of_vehicles :
  #  v.Initialization()
x = 0
'''while True :
    for v in list_of_vehicles:
        if (v.initial_Done):
            x = x + 1
    if(x == number_of_vehicles):
        break
    else:
        x = 0'''
for v in list_of_vehicles :
    v.delay = random.uniform(2,6)
print("phase2")
text_file = open("senario32.txt", "r")
lines = text_file.readlines()
for line in lines :
    splited_line = line.split()
    if(splited_line[0] == "ChangeLoc") :
        s.Change_loc()  ##### remove location and UID of vehicles in Server
        if(len(splited_line) == 1 ):
            #change location randomly
            print("random")
        else:
            new_locs = []
            UIDs     = []
            for loc in splited_line[1:] :
                loc = loc.split("-")
                UID = int(loc[0])
                x   = int(loc[1])
                y   = int(loc[2])
                print(UID,x,y)
                temp= ((x,y))
                UIDs.append(UID)
                new_locs.append(temp)
            #change location to new_loc
            for vehicle in list_of_vehicles: ######change location of vehicles
                vehicle.route_table = []
                vehicle.initial_Done = False
                id = vehicle.UID
                index = UIDs.index(id)
                vehicle.x = new_locs[index][0]
                vehicle.y = new_locs[index][1]
            for vehicle in list_of_vehicles:
                vehicle.Initialization()
            while True:
                for v in list_of_vehicles:
                    if (v.initial_Done):
                        x = x + 1
                if (x == number_of_vehicles):
                    break
                else:
                    x = 0
    elif(splited_line[0] == "SendMessage"):
        temp = splited_line[1].split("-")
        source_UID = int(temp[0])
        dest_UID   = int(temp[2])
        message    = temp[1]
        #translate_UID_to_IP
        dest_IP = UidIp.UID2IP(dest_UID)
        # call send function
        for v in list_of_vehicles :
            if(v.UID == source_UID):
                v.Start_RREQ(dest_IP,message)

    elif(splited_line[0] == "Wait"):
        delay = int(splited_line[1])
        time.sleep(delay)
print("x")
i = 0
while True:
    i = i + 1