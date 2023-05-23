import random
import faker
from pymemcache.client.base import Client
from pymemcache.client.murmur3 import murmur3_32

class ConsistentHashing:

    def __init__(self, nodes, replication_factor=2):
        self.replication_factor = replication_factor
        self.nodes = []
        self.keys_map = {}
        for node in nodes:
            self.add_node(node)

    def add_node(self, node):
        self.nodes.append(node)
        for i in range(self.replication_factor):
            replica_key = f"{node}-{i}"
            self.keys_map[self.hash(replica_key)] = node
        client[node] = Client(('localhost', 11211 + len(self.nodes) - 1))

    def remove_node(self, node):
        self.nodes.remove(node)
        for i in range(self.replication_factor):
            replica_key = f"{node}-{i}"
            del self.keys_map[self.hash(replica_key)]
        client.pop(node).close()

    def get_node(self, key):
        if not self.nodes:
            return None

        hash_key = self.hash(key)
        nodes_keys = sorted(self.keys_map.keys())
        for node_key in nodes_keys:
            if hash_key <= node_key:
                return self.keys_map[node_key]

        return self.keys_map[nodes_keys[0]]

    def hash(self, key):
        return murmur3_32(str(key.encode())).to_bytes(4, byteorder='big')


# stub
def dht_get(key):
    node = ch.get_node(key)
    return client[node].get(key)


# stub
def dht_set(key, value):
    node = ch.get_node(key)
    client[node].set(key, value)


# Helper function
def read_list_func(rlist):
    # Read the values of the sampled keys from your DHT
    for key in rlist:
        value = dht_get(str(key))
        print(f"Key: {key}, Value: {value}")


def add_node_cmd(name, ip, port):
    ch.add_node(name)


def remove_node_cmd():
    name = input("Enter node name: ")
    ch.remove_node(name)


def put_cmd():
    key = input("Enter key: ")
    value = input("Enter value: ")
    dht_set(key, value)


def get_cmd():
    key = input("Enter key: ")
    value = dht_get(key)
    print(f"Value: {value}")


def help_cmd():
    print("""
        Available commands:
        - add_node: add a new Memcached node
        - remove_node: remove an existing Memcached node
        - put: store a key-value pair in the DHT
        - get: retrieve the value of a key from the DHT
        - read_list: sample 10 random keys from the DHT and display their values
        - help: display this help message
        - exit: exit the interactive shell
    """)


client = {}

ch = ConsistentHashing(['m1', 'm2', 'm3', 'm4'], replication_factor=2)
fake = faker.Faker()

def main():
    print("My Memcached DHT.")

    port = 11211
    # initialize client instances
    for node in ch.nodes:
        client[node] = Client(('localhost', port))
        port += 1
        # print(client[node],ch.nodes , ch.nodes, client)

    # insert 100 key-value pairs into the DHT
    for key in range(100):
        value = fake.company()
        key_hash = murmur3_32(str(key))
        dht_set(str(key_hash), value)
        print(key, " - ", value)

    while True:
        command = input("> ").strip().lower()
        if command == "add_node":
            name = input("Enter node name: ")
            ip = input("Enter node IP address: ")
            port = input("Enter node port: ")
            add_node_cmd(name, ip, port)
        elif command == "remove_node":
            remove_node_cmd()
        elif command == "put":
            put_cmd()
        elif command == "get":
            get_cmd()
        elif command == "read_list":
            rlist = random.sample(range(100), 10)
            read_list_func(rlist)



if __name__ == "__main__":
    main()







# import random
# import faker
# from pymemcache.client.base import Client
# from pymemcache.client.murmur3 import murmur3_32

# print("IMport")

# class ConsistentHashing:
#     def __init__(self, nodes, replicas=3):
#         self.replicas = replicas
#         self.ring = dict()
#         self.nodes = set()
#         for node in nodes:
#             self.add_node(node)

#     def add_node(self, node):
#         self.nodes.add(node)
#         for i in range(self.replicas):
#             # key = self.gen_key(f"{node}:{i}")
#             key = self.gen_key(f"{str(node)}:{str(i)}")

#             self.ring[key] = node

#     def remove_node(self, node):
#         self.nodes.discard(node)
#         for i in range(self.replicas):
#             key = self.gen_key(f"{node}:{i}")
#             # key = self.gen_key(f"{str(node)}:{str(i)}")
#             if key in self.ring:
#                 del self.ring[key]
#             else:
#                 print("Key not found")

#     def get_node(self, key):
#         if not self.ring:
#             return None
#         key_hash = self.gen_key(key)
#         for node_hash in sorted(self.ring.keys()):
#             if node_hash >= key_hash:
#                 return self.ring[node_hash]
#         return self.ring[min(self.ring.keys())]

#     def gen_key(self, key):
#         key_str = str(key) # Convert key to a string
#         return murmur3_32(str(key_str.encode()))






# class MemcachedDHT:
#     def __init__(self, nodes):
#         self.hash_ring = ConsistentHashing(nodes)
#         self.replication_factor = 2
#         self.nodes = set(nodes)
#         self.clients = {}
#         for node in self.nodes:
#             self.clients[node] = Client((node.ip, node.port))

#     def add_node(self, node):
#         self.hash_ring.add_node(node.ip + ":" + str(node.port))
#         self.nodes.add(node.ip + ":" + str(node.port))
#         self.clients[node.ip + ":" +
#                      str(node.port)] = Client((node.ip, node.port))

#     def remove_node(self, node):
#         #remove the node if it exisit else print key not found in ring 
#         if node.ip + ":" + str(node.port) in self.hash_ring.ring.values():
#             self.hash_ring.remove_node(node.ip + ":" + str(node.port))
#             self.nodes.discard(node.ip + ":" + str(node.port))
#             self.clients[node.ip + ":" + str(node.port)].close()
#             del self.clients[node.ip + ":" + str(node.port)]
#         else:
#             print(f"Node {node.ip}:{node.port} not found in the ring.")


#     def get_nodes_for_key(self, key):
#         nodes = set()
#         node = self.hash_ring.get_node(key)
#         nodes.add(node)
#         for i in range(self.replication_factor - 1):
#             node = self.hash_ring.get_node(str(i) + key)
#             nodes.add(node)
#         return list(nodes)

#     def dht_get(self, key):
#         nodes = self.get_nodes_for_key(key)
#         for node in nodes:
#             value = self.clients[node].get(str(key))
#             if value is not None:
#                 return value
#         return None

#     def dht_set(self, key, value):
#         nodes = self.get_nodes_for_key(key)
#         for node in nodes:
#             self.clients[node].set(str(key), value)


# class Node:
#     def __init__(self, name, ip, port):
#         self.name = name
#         self.ip = ip
#         self.port = port


# def main():
#     print("My Memcached DHT.")

#     # Add Memcached Instances
#     print("Initializing the DHT Cluster:")
#     nodes = [Node('m1', 'localhost', 11211), Node('m2', 'localhost', 11212), Node('m3', 'localhost', 11213),
#              Node('m4', 'localhost', 11214)]
#     dht = MemcachedDHT(nodes)

#     # Write 100 key-value pairs to the dht
#     print("Writing 100 key-value pairs to the DHT...")

#     # fake = faker.Faker()
#     # for i in range(100):
#     #     key = fake.word()
#     #     value = fake.sentence()
#     #     dht.dht_set(key, value)
#     #     print(key ," - ", value)
#     fake = faker.Faker()
#     for key in range(100):
#         value = fake.company()
#         key_hash = murmur3_32(str(key))
#         dht.dht_set(str(key_hash), value)
#         print(key ," - ", value)

#     # Verify the data is stored in the DHT
#     print("Verifying the data is stored in the DHT...")
#     for i in range(100):
#         key = fake.word()
#         value = dht.dht_get(key)
#         if value is None:
#             print(f"Key {key} not found in the DHT!")
#         else:
#             print(f"Key {key} maps to value '{value}' .")

#     # Remove a Memcached Instance and rehash the keys
#     print("Removing a Memcached instance and rehashing the keys...")
#     dht.remove_node(nodes[3])
#     for i in range(100):
#         key = fake.word()
#         value = dht.dht_get(key)
#         if value is None:
#             print(f"Key {key} not found in the DHT!")
#         else:
#             print(f"Key {key} maps to value '{value}'.")

#     # Add a new Memcached Instance and rehash the keys
#     print("Adding a new Memcached instance and rehashing the keys...")
#     new_node = Node('m5', 'localhost', 11215)
#     dht.add_node(new_node)

#     for i in range(100):
#         key = fake.word()
#         value = dht.dht_get(key)
#         if value is None:
#             print(f"Key {key} not found in the DHT!")
#         else:
#             print(f"Key {key} maps to value '{value}'.")

#     # Close Memcached Clients
#     for client in dht.clients.values():
#         client.close()


# if __name__ == "__main__":
#     main()





# you need to install pymemcache
from email.charset import add_codec
import random
import faker
from pymemcache.client.base import Client
from pymemcache.client.murmur3 import murmur3_32


class ConsistentHashing:
    def __init__(self, nodes, replicas=1):
        self.replicas = replicas
        self.ring = dict()
        self.replication_factor = 2
        self.nodes = set()
        for node in nodes:
            self.add_node(node)
        self.replication_factor = 2
        self.clients = {}


    def add_node(self, node):
        self.nodes.add(node)
        for i in range(self.replicas):
            key = self.gen_key(f"{node}:{i}")
            print("key in add node", key)
            self.ring[key] = node

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
        

    def get_node(self, key):
        if not self.ring:
            return None
        key_hash = self.gen_key(key)
        for node_hash in sorted(self.ring.keys()):
            if node_hash >= key_hash:
                return self.ring[node_hash]
        return self.ring[min(self.ring.keys())]
    
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



        
    

    def add_node(self, node):
        # check  if the new node port and name are unique
        # if not unique print error message
        for n in self.nodes:
            if n.port == node.port or n.name == node.name:
                print("Node already exists! Try again")
                return
        print("New Node details; ", node.name, node.ip, node.port)
        self.hash_ring.add_node(node)
        self.nodes.add(node)
        self.clients[node] = Client((node.ip, node.port))
        data_to_move = {}
        for key in range(100):
            nodes_for_key = self.get_nodes_for_key(str(key))
            print("All nodes for key {}: {}".format(key, nodes_for_key))

            if len(nodes_for_key) < 2:
                continue

            replica_node = nodes_for_key[1]
            if node == replica_node:
                data_to_move[key] = self.clients[node].get(str(key))

        for key in data_to_move:
            self.clients[node].set(str(key), data_to_move[key])
            print("Data moved: key={}, value={}".format(key, data_to_move[key]))




    # def add_node(self, node):
    #     print("New Node details; ", node.name, node.ip, node.port)
    #     self.hash_ring.add_node(node)
    #     self.nodes.add(node)
    #     self.clients[node] = Client((node.ip, node.port))

    #     # Replicate data to new node
    #     for key in self.hash_ring.ring:
    #         nodes_for_key = self.hash_ring.get_node(key)
    #         if node in nodes_for_key:
    #             continue
    #         for n in nodes_for_key:
    #             if n != node:
    #                 value = self.clients[n].get(key)
    #                 if value:
    #                     self.clients[node].set(key, value, self.replication_factor)
    #                 break





    def remove_node(self, node):
        # remove the node if it exisit else print key not found in ring
        # self.hash_ring.remove_node(node.ip + ":" + str(node.port))
        self.hash_ring.remove_node(node)
        self.nodes.discard(node)
        self.clients[node].close()
        del self.clients[node]

    def get_nodes_for_key(self, key):
        nodes = set()
        node = self.hash_ring.get_node(int(key))
        nodes.add(node)
        hashed_key = murmur3_32(str(key))
        for i in range(1, self.replication_factor):
            replica_key = self.hash_ring.gen_key(str(hashed_key) + str(i))
            replica_node = self.hash_ring.get_node(int(replica_key))
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
        self.hash_ring.print_ring()
    
    # def print_node_data(self, node):
    #     client = Client((node.ip, node.port))
    #     data = {}
    #     for key in range(100):
    #         value = self.get_nodes_for_key(str(key))
    #         if value:
    #             data[key] = value
    #     print(f"Node {node.name} ({node.ip}:{node.port}) holds the following data:")
    #     for key, value in data.items():
    #         print(f"\t{key}: {value.value}")
    def print_node_data(self, node):
        client = Client((node.ip, node.port))
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
    print("My Memcached DHT.")

    print("Initializing the DHT Cluster:")
    nodes = [Node('m1', 'localhost', 11211), Node('m2', 'localhost', 11212), Node('m3', 'localhost', 11213),
             Node('m4', 'localhost', 11214)]
    dht = MemcachedDHT(nodes)

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
