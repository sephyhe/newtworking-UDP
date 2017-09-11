import sys
import socket
from struct import pack, unpack
import select

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
        
            
    r_in_port = int(port_num_list[0])
    r_out_port = int(port_num_list[1])
    cr_in_port = int(port_num_list[2])
    
    filename = port_num_list[3] 
    ip_address = '127.0.0.1'
    
    #Creating sockets and coonecting
    try:
        r_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        r_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except:
        print('Generating sockets is fail.')        
        exit()          
        
    try:
        r_in.bind((ip_address, r_in_port))
        r_out.bind((ip_address, r_out_port))
    except:
        print('Binding sockets is fail.')
        r_in.close()
        r_out.close()         
        exit()        
        
    try:
        r_out.connect((ip_address, cr_in_port))
    except:
        print('Connecting sockets is fail.')
        r_in.close()
        r_out.close()         
        exit()        
        
        
    #deal with data    
    try:
        infile = open(filename,'w')        
    except FileNotFoundError:
        print('Error' , filename, " does not exist" )
        r_in.close()
        r_out.close()         
        exit()  
        

    excepted = 0
    while True:
      
        read, write, exception = select.select([r_in],[],[]) 
        if not(read or write or exception):
            print("Time out")
            
        packet_r= r_in.recv(536)
        data_head = unpack('!Liiiq',packet_r[:24])
        magicno, datatype, seqno, datalen, checksum = data_head            
  
        if magicno != 0x497E or datatype != DATA_PACKET:
            continue

        if seqno != excepted:
            new_packet = pack('!Liii', magicno, ACKNOWLEDGEMENT_PACKET, seqno, 0)  
            r_out.send(new_packet)  
            continue
        else:
            data = unpack(str(datalen)+"s", packet_r[24:])
            text = data[0]
            print('Getting data:',text)   
            
            checkagain = hash(text) 
            
            if checkagain == checksum:
                new_packet = pack('!Liiis', magicno, ACKNOWLEDGEMENT_PACKET, seqno, 0, '') 
                print("The data was transferred correctly")
                r_out.send(new_packet)                
                excepted = 1 - excepted
                
                
                try:
                    infile.write(text)  
                    print("Saved data.")
                except:
                    print("Saving data is fail.")
                            
                if datalen == 0:
                    infile.close()
                    r_in.close()
                    r_out.close()         
                    exit()                
                
            else:
                print("The data was not transferred correctly and waiting for re-sender")            
            
                    
   
main()