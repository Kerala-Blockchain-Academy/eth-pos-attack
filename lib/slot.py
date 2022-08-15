from re import T
import sched, time
import threading
from lib.PoS import Block

class Slot:
    s = sched.scheduler(time.time, time.sleep)
    slotcount = 0
    second = 20
    

    def slotfun(cls,sc):
        if cls.second==20:
            cls.slotcount+=1
            cls.second=0    
            cls.peer.active=True
            cls.peer.blocks=[]
        elif cls.second==10 and cls.peer.blocks==[] and cls.peer.active:
            #if no block were found upvote the previous block
            print('vote for parent')
            cls.peer.chain[-1]['validated'].append(cls.peer.sport)
            cls.peer.cast_vote()

        cls.second+=1
        if cls.peer.sport == 5000 and cls.second==2:
            validator = Block.find_proposer(cls.peer.connections)
            cls.peer.broadcast({"validator":validator})


        if cls.peer.current_slot+1==cls.slotcount:
            print('time to broadcast malicious block')
            cls.peer.malicious_block['validated'].append(cls.peer.sport)
            cls.peer.broadcast(cls.peer.malicious_block)
            cls.peer.blocks(cls.peer.malicious_block)
            cls.peer.mempool=[]
            cls.peer.current_slot=-10

            

        print("Slot=>",cls.slotcount," ",cls.second,end="\r")
        sc.enter(1, 1,cls.slotfun, (cls,sc,))

    def shoot(cls):
        cls.s.enter(0, 1, cls.slotfun, (cls,cls.s,))
        cls.s.run()

    @classmethod
    def start_slot(cls,peer):
        cls.peer = peer
        listener = threading.Thread(target=cls.shoot,args=(cls,),daemon=True)
        listener.start()

    @classmethod
    def get_slot(cls):
        return cls.slotcount,cls.second

