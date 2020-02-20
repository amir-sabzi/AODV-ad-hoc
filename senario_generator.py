import random
import math
number_nodes = int(input("enter number of nodes: "))
u = int(math.log(number_nodes,4))
devide = int(math.pow(2,u))
l            = int(input("length of battleField: "))
d            = int(input("range of access (should be greater than "+ str(l/devide)+ ")"))
s          = input("source UID: ")
dest       = input("destination UID :")
area_length = l/devide
number_of_regions = (devide)**2
#print(number_of_regions)
number_of_node_in_each_region = int(number_nodes/number_of_regions)
f = 0
list_out = []
h_list  = []
for i in range(devide):
    for j in range(devide):
        for k in range(number_of_node_in_each_region):
            if (f == number_nodes):
                break
            temp = [f+1,random.uniform(i*area_length,(i+1)*area_length),\
                    random.uniform(j*area_length,(j+1)*area_length)]
            h  = [str(int(temp[1])),str(int(temp[2])) ]
            h_list.append(h)
            temp2 = str(temp[0])+"-"+str(int(temp[1]))+"-"+str(int(temp[2]))
            list_out.append(temp2)
            f = f + 1

list_out.insert(0,"ChangeLoc")
message = ["SendMessage",s+"-"+"hello"+"-"+dest]
print(*list_out, sep=' ')
print(*message, sep=' ')
out2 = []
for i in range(number_nodes):
    temp = [str(i+1) , "127.0.0."+str(i+2) , str(3000+i+1),h_list[i][0],h_list[i][1],str(int(random.uniform(1,4)))]
    print(*temp, sep=' ')

