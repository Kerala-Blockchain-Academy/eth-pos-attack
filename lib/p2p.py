import socket
import threading
import json
from lib.slot import Slot
from lib.PoS import Block


class Peer2Peer():
    def __init__(self,sport,master):
        self.sport = sport
        self.master = master
        self.active = False
        self.connections = []
        self.mempool = []
        self.blocks = []
        #run up the server
        self.start_threat()
        self.querynodestart()


        self.chance = 0
        self.current_slot=-10
        self.malicious_block=None
       
        
    def start_threat(self):
        listener = threading.Thread(target=self.listen,daemon=True,args=(self.sport,))
        listener.start()
        
    def send(data,addr):
        if type(data)==dict:data = json.dumps(data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.sendto(data.encode(),addr)
        
    def broadcast(self,data):
        self.querynodes()
        if type(data)==dict:data = json.dumps(data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(self.connections)
        for i in self.connections:
            if i[1]!=int(self.sport):
                sock.sendto(data.encode(),i)

    def addconnections(self,addr):
        if addr not in self.connections:
            self.connections.append(addr)

    def setconnections(self,d):
        temp = []
        for i in  d:
            temp.append(tuple(i))
        self.connections = temp

    def cast_vote(self,hash=0):
        vote={'by':self.sport,'slot':Slot.get_slot(),'hash':hash}
        self.broadcast(vote)
        
    def querynodes(self):
        data = {'query':'node_discovery',
            'from':{'port':self.sport}
            }

        if self.sport!=5000:
            Peer2Peer.send(data,self.master)

    def queryend(self):
        data = {'query':'node_termination',
            'from':{'port':self.sport}
            }

        if self.sport!=5000:
            Peer2Peer.send(data,self.master)

    def querynodestart(self):
        data = {'query':'node_start',
            'from':{'port':self.sport}
            }

        if self.sport!=5000:
            Peer2Peer.send(data,self.master)
        else:
            self.connections.append(self.master)

    def listen(self,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', port))
        print('Listening udp on ',port)

        while True:
            data,addr = sock.recvfrom(2024)
            d = json.loads(str(data.decode()))
            if 'query' in d :
                if d['query'] == "node_discovery":
                    addr = (addr[0],int(d['from']['port']))
                    self.addconnections(addr)
                    self.broadcast({'nodes':self.connections})

                elif d['query'] == "node_start":
                    addr = (addr[0],int(d['from']['port']))
                    self.addconnections(addr)
                    self.broadcast({'nodes':self.connections,'slot':Slot.get_slot()})

                elif d['query'] == "node_termination":
                    addr = (addr[0],int(d['from']['port']))
                    if addr in self.connections: self.connections.remove(addr) 
                    self.broadcast({'nodes':self.connections})
                
            elif 'nodes' in d:
                self.setconnections(d['nodes'])
                if 'slot' in d:
                    Slot.slotcount = int(d['slot'][0])
                    Slot.second = int(d['slot'][1])
                
            elif 'validator' in d:
                if d['validator'][1] == int(self.sport):
                    print("[!]I am the validator")

                    self.validator = int(self.sport)
                    

                    if self.chance <1:
                        block =  Block.create_block(self,Slot.get_slot()[0])

                        #crate block if i am the validator
                        self.broadcast(block)
                        self.blocks.append(block)

                        self.mempool = []
                        self.chance+=1
                    else:
                        self.malicious_block =  Block.create_block(self,Slot.get_slot()[0])
                        self.current_slot = Slot.get_slot()[0]


            elif 'header' in d:
                d['validated'].append(self.sport)
                self.blocks.append(d)
               
                self.mempool = []
                self.cast_vote(d['header']['hash'])
                
                
                    
            elif 'by' in d:
                try:
                    for i in self.blocks:
                        if d['hash'] == i['header']['hash']:  
                            block = i
                            block['validated'].append(d['by'])
                            
                            if len(block['validated'])>=int(len(self.connections)):
                                self.chain.append(block)
                                print('[!]Chain Created')
                                print(json.dumps(self.chain, indent=4))

                    if self.blocks == [] and self.active :
                        print('[!]Voting parent block')
                        self.chain[-1]['validated'].append(d['by'])
                except:
                    pass
                    


            elif 'nonce' in d:
                d['nonced'] = d['nonce']
                del d['nonce']
                self.broadcast(d)
                self.mempool.append(d)

            elif 'nonced' in d:
                self.mempool.append(d)

            else:
                print(d)
