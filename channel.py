import socket
import sys
from struct import pack, unpack
import select
import random

def main():
    port_num_list = sys.argv[1:]
    
    for i in port_num_list[:5]:
        
        try:
            i = int(i)
        except:
            print('The port number should be integer.')
            exit()
        
           
        if not (i in range(1024, 64001)):
            print('The port number should between 1024 and 64000.')
            exit()
        
            
    cs_in_port = int(port_num_list[0])
    cs_out_port = int(port_num_list[1])
    cr_in_port = int(port_num_list[2])
    cr_out_port = int(port_num_list[3])
    s_in_port = int(port_num_list[4])
    r_in_port = int(port_num_list[5])
        
    lost_rate = float(port_num_list[6])
    if lost_rate < 0 or lost_rate >= 1:
        print('The lost rate should between 0 and 1.')
        exit()
    
    ip_address = '127.0.0.1'   
    
    try:
        cs_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cs_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        cr_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cr_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
    except:
        print('Generating sockets is fail.')
       
        exit()   
    
    try:
        cs_in.bind((ip_address, cs_in_port))
        cs_out.bind((ip_address, cs_out_port))    
        cr_in.bind((ip_address, cr_in_port))
        cr_out.bind((ip_address, cr_out_port)) 
    except:
        print('Binding sockets is fail.')
        cr_in.close()
        cr_out.close() 
        cr_in.close()
        cr_out.close()        
        exit()        
        
        
    try:
        cs_out.connect((ip_address, s_in_port))
        cr_out.connect((ip_address, r_in_port))
    except:
        print('Connecting sockets is fail.')
        cr_in.close()
        cr_out.close() 
        cr_in.close()
        cr_out.close()        
        exit()        
    
    
    #deal with data
    while True:       
        socket_list,outputready,exceptready = select.select([cr_in, cs_in],[],[]) 
        for socket_channel in socket_list:
            
            if socket_channel == cs_in:
                print("Getting packets from sender.") 
                packet_cs = socket_channel.recv(536)
                data_head = unpack('!Liiiq',packet_cs[:24])
                magicno, datatype, seqno, datalen, checksum = data_head
                print("The packet magicoNo={}, the datatype={}, the seqNo={}, the dataLen={}, the checksum ={}"
                      .format(magicno, datatype, seqno, datalen, checksum))
                
                if magicno != 0x497E:
                    print("Lossing packet.")
                    break
                
                
                u = random.uniform(0, 1)
                print('The random lost rate is', u)
                
                if u < lost_rate:
                    print("Dropping packet.")
                    
                    
                else:                        
                    data_full = data_head + unpack(str(datalen)+"s",packet_cs[24:])                
                    print("The data is: ", data_full[5]) 
                    
                    new_packet = pack('!Liiiq' + str(datalen) + 's', magicno, datatype, seqno, datalen, checksum,data_full[5])

                    try:
                        cr_out.send(new_packet)
                        print("Sending packet to receiver.")
                        
                    except:
                        print("Sending packet is fail.")
                        exit()
                    
                    
            elif socket_channel == cr_in:
                print("Getting packets from receiver.")
                packet_cr = socket_channel.recv(528)
              
                data_head = unpack('!Liii',packet_cr[:16])
                magicno, datatype, seqno, datalen = data_head
                print("The packet magicoNo={}, the datatype={}, the seqNo={}, the dataLen={}"
                      .format(magicno, datatype, seqno, datalen))
                
                if magicno != 0x497E:
                    print("Lossing packet.")
                    break
                                
                u = random.uniform(0, 1)
                print('The random lost rate is', u)
                
                if u < lost_rate:
                    print("Dropping packet.")
                    
                else:
                    print(packet_cr[16:])   
                    if datalen == 0:
                        data_full = (magicno, datatype, seqno, datalen,'')
                        
                    else:
                        data_full = data_head + unpack(str(datalen)+"s",packet_cr[16:])
                    
                    print("The data is: ", data_full[4]) 
                    new_packet = pack('!Liii' + str(datalen) + 's', magicno, datatype, seqno, datalen, data_full[4])

                    try:
                        cs_out.send(new_packet)
                        print("Sending to sender")
                        
                    except:
                        print("Sending packet is fail.")
                        exit()
    
main()