
# # !pip install pymemcache
# # !pip install faker
# import random, faker
# from pymemcache.client.base import Client
# from pymemcache.client.murmur3 import murmur3_32
# import os

# class Ring:
#     class Node:
#         def __init__(self, name, ip, port):
#             self.name = name
#             self.ip = ip
#             self.port = port
#             self.client = Client((ip, port))
#             self.keys = set() # keys of data stored in this node
#         def __str__(self):
#             return f'({self.name},{self.ip},{self.port})'
#         def __repr__(self):
#             return f'{self.name}, {self.keys}'
    
#     def __init__(self, N):
#         assert isinstance(N, int) and N>=1
#         self.size = N # a ring of 0, 1, ..., N-1
#         self.cluster = [] # sorted list of (location, node) tuple
#         self.ports_in_use = set()
#     def __repr__(self):
#         return f'Ring of size {self.size} with nodes:'+'\n'+ ',\n'.join([str(n) for n in self.cluster])
    
#     def get_hash(self, key):
#         return murmur3_32(str(key)) % self.size
    
#     def find_next_node(self, loc):
#         # given a location on the ring, find the first node encountered counterclockwise
#         # 0<=loc<=ring_size-1
#         # returns the index of the next node in self.cluster
#         # NOTE: it returns len(self.cluster) instead of 0 if loc is the largest on the ring
#         assert len(self.cluster)>0, 'No node has been added to the ring'
#         tempidx = 0 # index in the array representing the cluster
#         while loc > self.cluster[tempidx][0]:
#             tempidx += 1
#             if tempidx==len(self.cluster): # reach the end of the cluster
#                 return tempidx # return the first node
#         return tempidx
    
#     def find_node(self, name):
#         # return the index of a node in self.cluster with a certain name
#         for idx, (loc, node) in enumerate(self.cluster):
#             if node.name == name:
#                 return idx
#         assert False, f'Error: no node with name {name}'

#     def add_node(self, name, ip, port):
#         assert port not in self.ports_in_use, f'Port {port} already in use'
#         assert name not in {n[1].name for n in self.cluster}, f'Name "{name}" already exists'
#         node = self.Node(name, ip, port) # node initialization
#         self.ports_in_use.add(port)
#         # choose somewhere on the ring to place the node
#         loc = random.randint(0, self.size-1)
#         occupied = {n[0] for n in self.cluster}
#         while loc in occupied:
#             loc = random.randint(0, self.size-1)
#         # if no node has been added, just add the node to the ring at loc
#         if len(self.cluster)==0:
#             self.cluster.append((loc, node))
#         # else, identify the next node and perform rehashing, replication factor=2
#         else:
#             idx = self.find_next_node(loc) # index of the next node in self.cluster
#             self.cluster = self.cluster[:idx] + [(loc, node)] + self.cluster[idx:]
#             # notations
#             num_nodes = len(self.cluster) # number of nodes after addition
#             h = lambda k: self.get_hash(k) # hash function
#             l_n, n = loc, node # new node being added
#             l_P, P = self.cluster[(idx-1)%num_nodes] # node prior to n
#             l_N, N = self.cluster[(idx+1)%num_nodes] # next node from n
#             _,  NN = self.cluster[(idx+2)%num_nodes] # next node from N
#             # if the added node is the second one, copy all the data from the first node
#             if num_nodes==2:
#                 n.keys |= P.keys
#                 for k in n.keys:
#                     v = P.client.get(k)
#                     n.client.set(k,v)
#             # if the added node is the third one (P --> n --> N --> P):
#             elif num_nodes==3:
#                 # 1) keys in (l_N,l_P] should be deleted from N and added to n
#                 N_to_P = {k for k in P.keys if h(k)<=l_P or h(k)>l_N} if l_P<l_N else \
#                          {k for k in P.keys if l_N<h(k)<=l_P}
#                 for k in N_to_P:
#                     N.client.delete(k)
#                     v = P.client.get(k)
#                     n.client.set(k,v)
#                 N.keys -= N_to_P
#                 n.keys |= N_to_P
#                 # 2) keys in (l_P,l_n] should be deleted from P and added to n
#                 P_to_n = {k for k in N.keys if h(k)<=l_n or h(k)>l_P} if l_n<l_P else \
#                          {k for k in N.keys if l_P<h(k)<=l_n}
#                 for k in P_to_n:
#                     P.client.delete(k)
#                     v = N.client.get(k)
#                     n.client.set(k,v)
#                 P.keys -= P_to_n
#                 n.keys |= P_to_n
#             # if there are at least 3 nodes before adding the new one  (P-->n-->N-->NN)
#             else:
#                 # 1) for data in both P and N, delete them from N and add them to n
#                 keysPN = P.keys.intersection(N.keys)
#                 for k in keysPN:
#                     N.client.delete(k)
#                     v = P.client.get(k)
#                     n.client.set(k,v)
#                 N.keys -= keysPN
#                 n.keys |= keysPN
#                 # 2) for keys in (l_P, l_n], delete them from NN and add them to n
#                 P_to_n = {k for k in N.keys if h(k)<=l_n or h(k)>l_P} if l_n<l_P else \
#                          {k for k in N.keys if l_P<h(k)<=l_n}
#                 for k in P_to_n:
#                     NN.client.delete(k)
#                     v = N.client.get(k)
#                     n.client.set(k,v)
#                 NN.keys -= P_to_n
#                 n.keys  |= P_to_n
#         print(f'Node {name} added')
#         return

#     def remove_node(self, name):
#         idx = self.find_node(name)
#         n = self.cluster[idx][1] # the node to be removed
#         # data rehashing before deleting the node, replication_factor=2 
#         num_nodes = len(self.cluster) # before removal
#         P = self.cluster[(idx-1)%num_nodes][1] # node prior to n
#         N = self.cluster[(idx+1)%num_nodes][1] # next node from n
#         NN = self.cluster[(idx+2)%num_nodes][1] # next node from N
        
#         if num_nodes>=3: # otherwise no need to do anything
#             keysPn = P.keys.intersection(n.keys)
#             keysNn = N.keys.intersection(n.keys)
#             # 1) data in both P and n should be added to N and deleted from n
#             for k in keysPn:
#                 v = P.client.get(k)
#                 N.client.set(k,v)
#             N.keys |= keysPn
#             # 2) data in both N and n should be added to NN and deleted from n
#             for k in keysNn:
#                 v = N.client.get(k)
#                 NN.client.set(k,v)
#             NN.keys |= keysNn
            
#         n.client.close() # close the client
#         self.cluster = self.cluster[:idx] + self.cluster[idx+1:] # remove from cluster
#         self.ports_in_use.remove(n.port) # free the port

#         print(f'Node {name} removed')
#         return

#     def dht_get(self, key):
#         key = str(key)
#         hash_key = self.get_hash(key) 
#         idx = self.find_next_node(hash_key) 
#         # node1, node2: where the key-value pair was stored
#         node1 = self.cluster[idx%len(self.cluster)][1]
#         node2 = self.cluster[(idx+1)%len(self.cluster)][1]
#         # if key not in node1.keys:
#         #    raise Exception(f'Key "{key}" not found')
#         try:
#             value = node1.client.get(key)
#         except: # in case when node1 is down
#             value = node2.client.get(key)
#         return value

#     def dht_set(self, key, value):
#         # replication factor is set to 2
#         key, value = str(key),str(value)
#         hash_key = self.get_hash(key) 
#         idx = self.find_next_node(hash_key) 
#         # node1, node2: where to store the key-value pair
#         node1 = self.cluster[idx%len(self.cluster)][1]
#         node2 = self.cluster[(idx+1)%len(self.cluster)][1] 
#         node1.client.set(key, value)
#         node2.client.set(key, value)
#         node1.keys.add(key)
#         node2.keys.add(key)
#         return node1, node2

#     # Helper functions
#     def read_list_func(self, rlist):
#         # Read the values of the sampled keys from your DHT
#         for key in rlist:
#             value = self.dht_get(key)
#             print(f"Key: {key}, Value: {value}")

#     def add_fake_data(self, key_from_inclusive, key_to_exlusive):
#         # N = how many pairs to add
#         keyrange = range(key_from_inclusive, key_to_exlusive)
#         print(f"Loading {len(keyrange)} fake data points")
#         fake = faker.Faker()
#         for key in keyrange:
#             value = fake.company()
#             self.dht_set(key, value)

#     def test(self):
#         # test if all keys are stored in the correct two consecutive nodes with the same value
#         num_nodes = len(self.cluster)
#         if num_nodes>1:
#             node_locations = [n[0] for n in self.cluster] # node locations on the ring
#             all_keys = [n[1].keys for n in self.cluster]
#             # dict from key to the index of the node where it resides
#             keyToNodeIdx = {kk:[] for kk in [k for ks in all_keys for k in ks]}
#             for idx, k_list in enumerate(all_keys):
#                 for k in k_list:
#                     keyToNodeIdx[k].append(idx)
#             for k, indices in keyToNodeIdx.items():
#                 assert len(indices)==2, f'More than two nodes with key {k}'
#                 # make sure i0 and i1 are adjacent
#                 i0,i1 = indices[0], indices[1]
#                 if i0*i1: # if both are nonzero
#                     assert (i0-i1)**2==1
#                 else:
#                     assert i0+i1==1 or i0+i1==len(self.cluster)-1
#                 # make sure the key is hashed to the right location
#                 if num_nodes>2:
#                     keyhash = self.get_hash(k)
#                     if {i0,i1}=={0,num_nodes-1}: # if crossing 0 on the ring
#                         assert self.cluster[-2][0]<keyhash<=self.cluster[-1][0], f'Key {k}:{keyhash} misplaced'
#                     elif i0*i1==0: # {i0,i1}=={0,1}
#                         assert keyhash<=self.cluster[0][0] or keyhash>self.cluster[-1][0] , f'Key {k}:{keyhash} misplaced'
#                     else:
#                         i = min(i0,i1)
#                         assert self.cluster[i-1][0]<keyhash<=self.cluster[i][0], f'Key {k}:{keyhash} misplaced'
#                 # make sure the values are the same
#                 v0 = self.cluster[i0][1].client.get(k)
#                 v1 = self.cluster[i1][1].client.get(k)
#                 assert v0==v1, f'Inconsistent values for key {k}'
#         print('Test passed ...')

# def system_test():
#     print("Initializing the DHT Cluster:")
#     ring = Ring(100)
#     # add m1
#     ring.add_node('m1','localhost', 11211)
#     ring.add_fake_data(0,10)
#     ring.test()
#     # add m2
#     ring.add_node('m2','localhost', 11212)
#     ring.add_fake_data(10,20)
#     ring.test()
#     # add m3
#     ring.add_node('m3','localhost', 11213)
#     ring.add_fake_data(20,30)
#     ring.test()
#     # add m4
#     ring.add_node('m4','localhost', 11214)
#     ring.add_fake_data(30,40)
#     ring.test()
#     # remove m1
#     ring.remove_node('m1')
#     ring.test()
#     # add m5
#     ring.add_node('m5','localhost', 11215)
#     ring.add_fake_data(40,50)
#     ring.test()
#     # remove m2
#     ring.remove_node('m2')
#     ring.test()  
#     # remove m3
#     ring.remove_node('m3')
#     ring.test()
#     # add back m1
#     ring.add_node('m1','localhost', 11211)
#     ring.add_fake_data(50,100)
#     ring.test()
#     # add back m2
#     ring.add_node('m2','localhost', 11212)
#     ring.add_fake_data(100,150)
#     ring.test()    
#     # remove m4
#     ring.remove_node('m4')
#     ring.test()
#     # remove m5
#     ring.remove_node('m5')
#     ring.test()
#     # remove m1
#     ring.remove_node('m1')
#     ring.test()
#     # remove m2
#     ring.remove_node('m2')
#     ring.test()

# def main():
#     print('My Memcached DHT.')
#     instructions = '''Commands (variables in angle brackets are assumed to be strings, no need to put quotations)\n1. add_node<node_name,ip,port>\n2. remove_node<node_name>\n3. get<key>\n4. put<key,value>\n5. display\n6. system_test\n7. clear\n8. menu\n9. quit'''
#     while True:
#         ring_size = input("Please specify the ring size: ")
#         try:
#             ring = Ring(int(ring_size))
#             break
#         except:
#             pass
#     print(instructions)
#     while True:
#         command = input('command: ').lower()
#         if command=='quit':
#             break
#         elif command=='system_test':
#             print('Running system test ...')
#             system_test()
#             continue
#         elif command=='clear':
#             os.system('clear')
#             continue
#         elif command=='menu':
#             print(instructions)
#             continue
#         elif command=='display':
#             print(ring)
#             continue            
#        	try:
#             cmd = command[:command.index("<")]
#             var = command[command.index('<')+1:command.index('>')]
#             if cmd=='add_node':
#                 name, ip, port = var.split(',')
#                 ring.add_node(name, ip, port)
#             elif cmd=='remove_node':
#                 ring.remove_node(var)
#             elif cmd=='get':
#                 value = ring.dht_get(var)
#                 print(f'The value for key {var} is {value}')
#             elif cmd=='put':
#                 key, value = var.split(',')
#                 n1, n2 = ring.dht_set(key, value)
#                 print(f'Pair ({var}) set in nodes {n1.name} and {n2.name}.')
#             else:
#                 print('Command not found')
#         except AssertionError as msg:
#             print(msg)
#         except:
#             print('Invalid input')

# if __name__ == "__main__":
# 	main()





from email.charset import add_codec
import random
import faker
from pymemcache.client.base import Client
from pymemcache.client.murmur3 import murmur3_32

class ConsistentHashing:
    def __init__(self, nodes, ring_size , replicas=1, ):
        self.replicas = replicas
        self.ring = []
        self.replication_factor = 2
        self.nodes = set()
        self.clients = {}
        self.ring_size = ring_size
        for node in nodes:
            self.add_node(node)
        

    def add_node(self, node):
        for n in self.nodes:
            if n.port == node.port or n.name == node.name:
                print("Node already exists! Try again")
                return
        print("New Node details; ", node.name, node.ip, node.port)
        self.nodes.add(node)
        self.clients[node] = Client((node.ip, node.port))

        newNode_idx = random.randint(1, self.ring_size)

        while newNode_idx in {presentNodes[0] for presentNodes in self.ring}:
            newNode_idx = random.randint(1,self.ring_size)
            print("newNode_idx", newNode_idx)

        self.ring.append((newNode_idx, node))
        



        # data_to_move = {}

        # for key in range(100):
        #     nodes_for_key = self.get_nodes_for_key(str(key))
        #     print("All nodes for key {}: {}".format(key, nodes_for_key))

        #     if len(nodes_for_key) < 2:
        #         continue

        #     replica_node = nodes_for_key[1]
        #     if node == replica_node:
        #         data_to_move[key] = self.clients[node].get(str(key))

        # for key in data_to_move:
        #     self.clients[node].set(str(key), data_to_move[key])
        #     print("Data moved: key={}, value={}".format(key, data_to_move[key]))

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self.gen_key(f"{node}:{i}")
            print("key in remove node", key)
            if key in self.ring:
                del self.ring[key]
                print("Removed node in hashing")
            else:
                print("Key not found")
        self.nodes.discard(node)
        self.clients[node].close()
        del self.clients[node]
        
    def get_node(self, key):
        if not self.ring:
            return None
        key_hash = self.gen_key(key)
        for node_hash in sorted(self.ring[1]):
            if node_hash >= key_hash:
                return self.ring[node_hash]
        return self.ring[min(self.ring)]
    
    # write a function to get the next node in the ring (position/index)
    def get_next_node(self, currentIdx):
        if currentIdx == len(self.ring) - 1:
            return 0
        else:
            return currentIdx + 1

    def gen_key(self, key):
        key_str = str(key)  # Convert key to a string
        return murmur3_32(str(key_str.encode()))
        # return murmur3_32(str(key_str.encode())).to_bytes(4, byteorder='big')
    
    def print_ring(self):
        print(self.ring)
        for node in self.ring:
            print(f"Node: {node} Name: {self.ring[node].name}")



    def get_nodes_for_key(self, key):
        nodes = set()
        node = self.get_node(int(key))
        nodes.add(node)
        hashed_key = murmur3_32(str(key))
        for i in range(1, self.replication_factor):
            replica_key = self.gen_key(str(hashed_key) + str(i))
            replica_node = self.get_node(int(replica_key))
            print(f"Replica node on get_node {i} for key {key}: {replica_node.name}")
            nodes.add(replica_node)
            print("replica_node is " , replica_node.name)
        print(f"All nodes for key {key}: {list(nodes)}")
        for node in nodes:
            print(node.name)
        return list(nodes)


    def dht_get(self, key):
        hashed_key = murmur3_32(str(key))
        nodes = self.get_nodes_for_key(hashed_key)
        for node in nodes:
            if node is None:
                print("Node not found in the DHT!")
                return None
            value = self.clients[node].get(str(hashed_key)).decode('utf-8')
            if value is not None:
                return value
                
        print(f"Key - {hashed_key} not found in the DHT!")

    def dht_set(self, key, value):
        nodes = self.get_nodes_for_key(str(key))
        for node in nodes:
            self.clients[node].set(str(key), value)


    def viewNodes(self):
        print("viewNodes")
        for node in self.nodes:
            print(node.name, node.ip, node.port)
            self.print_node_data(node)
        self.print_ring()
    
    def print_node_data(self, node):
        data = {}
        for key in range(100):
            value = self.get_nodes_for_key(str(key))
            if value:
                data[key] = [n.name for n in value]  # Change the values to node names
        print(f"Node {node.name} ({node.ip}:{node.port}) holds the following data:")
        for key, value in data.items():
            print(f"\t{key}: {value}")

class Node:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

def read_list_func(rlist, dht):
    # Read the values of the sampled keys from your DHT
    for key in rlist:
        value = dht.dht_get(str(key))
        print(f"Key: {key}, Value: {value}")


def help_cmd():
    print("""
        Available commands:
        - add node: add a new Memcached node
        - remove_node: remove an existing Memcached node
        - put: store a key-value pair in the DHT
        - get: retrieve the value of a key from the DHT
        - read list: sample 10 random keys from the DHT and display their values
        - help: display this help message
        - exit: exit the interactive shell
    """)

def main():
    ring_size = 100 
    print("Initializing the DHT Cluster:")
    nodes = [Node('m1', 'localhost', 11211), Node('m2', 'localhost', 11212), Node('m3', 'localhost', 11213),
             Node('m4', 'localhost', 11214)]
    dht = ConsistentHashing(nodes, ring_size)

    # Write 100 key-value pairs to Memcached (you add more if you want)
    print("Writing 100 key-value pairs to Memcached...")
    fake = faker.Faker()
    for key in range(100):
        value = fake.company()
        key_hash = murmur3_32(str(key))
        dht.dht_set(str(key_hash), value)
        print(key, " - ", value)


    # Sample 10 random keys to read from Memcached to test the system
    read_list = random.sample(range(100), 10)
    print("My Memcache DHT")

    # Verify the data is stored in the DHT
    print("Verifying the data is stored in the DHT...")
    for key in read_list:
        value = dht.dht_get(str(key))
        if value is None:
            print(f"Key - {key} not found in the DHT!")
        else:
            print(f"Key - {key} maps to value '{value}'")

    # Check the status of the value
    # read_list_func(read_list, dht)  # Check the content of the cache

    # # Simulating the failure of a node m1
    # # remove_node('m1')

    # read_list_func(read_list, dht)  # Check the content of the cache
    # # Simulating the addition of a new node m5

    # # add_node('m5', 'localhost', 11215)
    # read_list_func(read_list, dht)  # Check the content of the cache

    while True:
        command = input("> ").strip().lower()
        if command == "add node":
            name = input("Enter node name: ")
            ip = input("Enter node IP address: ")
            port = input("Enter node port: ")

            node = Node(name, ip, port)
            nodes.append(node)

            dht.add_node(node)
        elif command == "remove node":
            node_name = input(
                "Enter name of node to remove: Use 'view nodes' if unsure: ")
            for node in nodes:
                if node.name == node_name:
                    node_to_remove = node
                    dht.remove_node(node_to_remove)
                else:
                    print("Node not found")
        elif command == "set":
            dht.dht_set()
        elif command == "get":
            key = input("Enter key: ")
            value = dht.dht_get(key)
            #handle dht.dht_get(key) key that if it returns None and print no such key error message
            if value is None:
                print("No such key")
            else:
                print(f"Value: {value}")
        elif command == "read list":
            # code to get the first 1o from read_list
            read_list = random.sample(range(100), 10)

            for key in read_list:
                value = dht.dht_get(str(key))
                if value is None:
                    print(f"Key - {key} not found in the DHT!")
                else:
                    print(f"Key - {key} maps to value '{value}' .")
        elif command == "view nodes":
            dht.viewNodes()
        elif command == "help":
            help_cmd()
        elif command == "scan node":
            node_name = input(
                "Enter name of node to scan: Use 'view nodes' if unsure: ")
            for node in nodes:
                if node.name == node_name:
                    node_to_scan = node
            dht.print_node_data(node_to_scan)
        elif command == "verify data":
            for key in read_list:
                value = dht.dht_get(str(key))
                if value is None:
                    print(f"Key - {key} not found in the DHT!")
                else:
                    print(f"Key - {key} maps to value '{value}'")

if __name__ == "__main__":
    main()
