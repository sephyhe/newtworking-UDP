import sys
import socket
from struct import pack, unpack
import select
import time



def main():
    
    ACKNOWLEDGEMENT_PACKET = 1
    DATA_PACKET = 0 
    
    port_num_list = sys.argv[1:]    
    
    for i in port_num_list[:3]:
        
        try:
            i = int(i)
        except:
            print('The port number should be integer.')
            exit()
        
           
        if not (i in range(1024, 64001)):
            print('The port number should between 1024 and 64000')
            exit()
            
    s_in_port = int(port_num_list[0])
    s_out_port = int(port_num_list[1])
    cs_in_port = int(port_num_list[2])
    
    filename = port_num_list[3]
    ip_address = '127.0.0.1' 
    
   
   #Creating sockets and coonecting
    try:
        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except:
        print('Generating sockets is fail.')        
        exit()        
    
    try:
        s_in.bind((ip_address, s_in_port))
        s_out.bind((ip_address, s_out_port))
    except:
        print('Binding sockets is fail.')
        s_in.close()
        s_out.close()         
        exit()         
        
    try:
        s_out.connect((ip_address, cs_in_port))
    except:
        print('Connecting sockets is fail.')
        s_in.close()
        s_out.close()         
        exit()        
    
    
    #deal with data
    try:
        infile = open(filename,'r')
        print("File opened")
    except FileNotFoundError:
        print('Error,' , filename, " does not exist" )
        s_in.close()
        s_out.close()         
        exit()    
        
    next_value = 0
    exit_flag = False
    magicno = 0x497E
    packet_count = 0
    
    while exit_flag == False:
        data = infile.read(512)
        datalen = len(data)
                
        if datalen == 0 or data == '':
            checksum = hash(data)
            packet_s = pack("!Liiiq"+str(datalen)+"s", magicno, DATA_PACKET, next_value, datalen, checksum, '')
            exit_flag = True
        else:
            checksum = hash(data)
            packet_s = pack("!Liiiq"+str(datalen)+"s", magicno, DATA_PACKET, next_value, datalen, checksum, data)
                      
        while True:
            s_out.send(packet_s)
            print("Sending packets")
            
            packet_count += 1
            s_in.settimeout(1)
          
            try:
                packet_s_in = s_in.recv(528)
                data = unpack("!Liii", packet_s_in[:16])
                
                if packet_s_in == None:
                    continue
                
                magicno, datatype, seqno, datalen= data
                   
                if magicno != 0x497E or datatype != ACKNOWLEDGEMENT_PACKET or datalen != 0 or seqno != next_value:
                    continue
               
                elif seqno == next_value:
                    next_value = 1 - next_value
                    if exit_flag == True:
                        infile.close()
                        s_in.close()
                        s_out.close() 
                        print("There are {} packets sent.".format(packet_count))
                        return
                        
                    else:
                        break            
                    
                
            except socket.timeout:
                print("time out")
                
                
main()
    