#
import random
import faker
from pymemcache.client.base import Client
from pymemcache.client.murmur3 import murmur3_32

# Define the number of key spaces in the hash ring
NUM_KEY_SPACES = 100

class Node:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

# Global variable to keep track of the nodes in the hash ring
NODES = []

#create a dictonary of NODE_KEYS to hold the node and keys it is reponsible for
NODE_KEYS = {}

# add_node function that all the respective keys are mapped and replicated to the new node and moved to it:
def add_node(node):
    NODES.append(node)
    NODE_KEYS[node.name] = set()
    rebalance_keys(node)

def rebalance_keys(new_node):
    # Iterating over the keys assigned to the node that is being removed
    for key in range(NUM_KEY_SPACES):
        # Finding the node responsible for the key
        responsible_node = find_responsible_node(key)
        # If the responsible node is the node being removed, set the key on the new node
        if responsible_node == new_node:
            for node in NODES:
                if node != new_node and node != responsible_node:
                        client = Client((new_node.ip, new_node.port))
                        client.set(str(key), dht_getHashed(key))
                        NODE_KEYS[new_node.name].add(key)
                        # print(f"Key {key} reassigned from {node.name} to {new_node.name}")


#Reassigning all keys assigned to the current node being deleted to other available nodes.
def reassignKeys(deletingNode):
    # Finding the next two nodes in the hash ring
    next_node, next_next_node = find_next_two_nodes(deletingNode)
    # Getting the keys assigned to the current node
    keys_to_reassign = list(NODE_KEYS[deletingNode.name])
    # Removeing the current node from the node keys dictionary
    del NODE_KEYS[deletingNode.name]
    # Reassign the keys to the next two nodes in the hash ring
    for key in keys_to_reassign:
        client = Client((next_node.ip, next_node.port))
        client.set(key, dht_getHashed(key))
        NODE_KEYS[next_node.name].add(key)
        # print(f"Key {key} reassigned from {deletingNode.name} to {next_node.name}")
        # If the next node is not available, reassign the key to the next-next node
        if not client.stats():
            client = Client((next_next_node[0], next_next_node[1]))
            client.set(key, dht_getHashed(key))
            NODE_KEYS[next_next_node.name].add(key)
            # print(f"Keyy {key} reassigned from {deletingNode.name} to {next_next_node.name}")

 
def remove_node(node):
    reassignKeys(node)
    NODES.remove(node)

# Helper function to find the node responsible for a given key
def find_responsible_node(key):
    # Calculate the hash of the key
    key_hash = murmur3_32(str(key))
    # Mapped the hash to a key space in the hash ring
    key_space = key_hash % NUM_KEY_SPACES
    
    # Finding the node responsible for the key space
    responsible_node = None
    for node in NODES:
        node_key_space = murmur3_32(node.name) % NUM_KEY_SPACES
        if node_key_space <= key_space and (not responsible_node or node_key_space < murmur3_32(responsible_node.name) % NUM_KEY_SPACES):
            responsible_node = node
            # print("Responsible node:", responsible_node.name)
            return responsible_node
    # If no node is found, return first node
    if not responsible_node:
        # print("New node:", responsible_node.name)
        return NODES[0]
    

# Helper function to replicate a key-value pair to two nodes in the hash ring
def replicate_key_value(key, value):
    # Finding the two nodes responsible for the key (including the primary node)
    primary_node = find_responsible_node(key)
    node1, node2 = None, None
    for node in NODES:
        if node == primary_node:
            continue
        if not node1:
            node1 = node
        else:
            node2 = node
            break
    # Replicate the key-value pair to the two nodes
    for node in (primary_node, node1, node2):
        # create a empty new node
        if node1 and node2:
            client = Client((node.ip, node.port))
            client.set(str(key), value)
            NODE_KEYS[node.name].add(str(key))

# Helper function to read the values of a list of keys from the DHT
def read_list_func(rlist):
    # Read the values of the sampled keys from your DHT
    for key in rlist:
        value = dht_get(str(key))
        print(f"Key: {key}, Value: {value}")
    #print the node that has these keys and also where the replicas are

def read_list_test(rlist):
    values = []
    # Read the values of the sampled keys from your DHT
    for key in rlist:
        value = dht_get(str(key))
        print(f"Key: {key}, Value: {value}") 
        values.append(value)
    print()
    print("Test values for the sample keys are: ", values)
    return values


# Function to get a value for a given key from the DHT
def dht_get(key):
    # Find the node responsible for the key
    hashed_key = murmur3_32(str(key))
    node = find_responsible_node(hashed_key)
    # Get the value for the key from the node
    client = Client((node.ip, node.port))
    if client.get(str(hashed_key)) is not None:    
        return client.get(str(hashed_key)).decode('utf-8')
    else:
        return None
    
def dht_getHashed(key):
    # Find the node responsible for the key
    node = find_responsible_node(key)
    # Get the value for the key from the node
    client = Client((node.ip, node.port))
    if client.get(str(key)) is not None:    
        return client.get(str(key)).decode('utf-8')
    else:
        return None


# Function to set a value for a given key in the DHT
def dht_set(key, value):
    # Replicate the key-value pair to two nodes in the hash ring
    replicate_key_value(key, value)

# Given a node in the DHT, return the next two nodes in the DHT.
def find_next_two_nodes(node):
    node_index = NODES.index(node)
    next_node_index = (node_index + 1) % len(NODES)
    next_next_node_index = (node_index + 2) % len(NODES)
    return NODES[next_node_index], NODES[next_next_node_index]

def dht_get_replicas(key):
    # Find the node responsible for the key
    node = find_responsible_node(key)
    # Find the next two nodes in the hash ring
    nodes = find_next_two_nodes(node)
    # Get the values for the key from the nodes
    values = []
    for node in nodes:
        client = Client((node.ip, node.port))
        value = client.get(str(key))
        if value is not None:
            values.append(value)
    return values

def print_node_table():
    viewNodes()
    # For debugging purposes
    # print("Keys stored in each node:")
    # print("{:<20} {:<10} {}".format('Node IP', 'Node Port', 'Keys'))
    # print("{:<20} {:<10} {}".format('-' * 20, '-' * 10, '-' * 50))
    # for node, keys in NODE_KEYS.items():
    #     key_list = ', '.join(map(str, keys))
    #     print("{:<20} {:<10} {}".format(node.ip, node.port, key_list))


def viewNodes():
    print("Nodes in the DHT:")
    for node in NODES:
        print(f"Node {node.name} ({node.ip}:{node.port})")

def test():
    print("Testing the DHT...")
    # Write 100 key-value pairs to Memcached (you add more if you want)
    for key in range(100):
        dht_set(key, f"Value for key {key}")
    
    # Select 10 random keys and read their values from the DHT for both scenarios the 10 keys have to be sane to verify 
    rlist = random.sample(range(100), 10)
    # Read the values of the sampled keys from your DHT
    print()
    print("Initial test round: Sample Keys set to", rlist) 
    intial = read_list_test(rlist)
    
    # Scenario 1: One of the servers drops
    # Remove a node from the DHT
    print()
    print("Scenario 1: One of the servers drops")
    node_name = "m1"
    for node in NODES:
        if node.name == node_name:
            node_to_remove = node
            remove_node(node_to_remove)
    # Read the values of the sampled keys from your DHT
    scenario1 = read_list_test(rlist)

    # Scenario 2: A new server is added
    # Add a new node to the DHT
    print()
    print("Scenario 2: A new server is added")
    newNode = Node('m5', 'localhost', 11215)
    add_node(newNode)
    # Read the values of the sampled keys from your DHT
    scenario2 = read_list_test(rlist)

    # Automating the test function to confirm whether the test passes or not
    print("Performing Autocheck")
    if intial == scenario1 and intial == scenario2:
        print("Test passed")
    else:   
        print("Test failed")


def help_cmd():
    print("""
    Welcome to DHT interactive shell
        Available commands:
        - add node: add a new Memcached node
        - remove node: remove an existing Memcached node
        - set: store a key-value pair in the DHT
        - get: retrieve the value of a key from the DHT
        - read list: sample 10 random keys from the DHT and display their values
        - test: Automate the testing function to decide whether the test passes or not
        - view nodes: display the nodes in the DHT
        - help: display this help message
        - exit: exit the interactive shells
    """)

# Main function to run the simulation
def main():
    print("My Memcached DHT.")
    # Add Memcached Instances
    print("Initializing the DHT Cluster:")
    addNodes = [Node('m1', 'localhost', 11211), Node('m2', 'localhost', 11212), Node('m3', 'localhost', 11213),
             Node('m4', 'localhost', 11214)]
    
    for node in addNodes:
        add_node(node)

    # Write 100 key-value pairs to Memcached (you add more if you want
    fake = faker.Faker()
    for key in range(100):
        value = fake.company()
        key_hash = murmur3_32(str(key))
        dht_set(str(key_hash), value)
        print(key, " - ", value)

    # Sample 10 random keys to read from Memcached to test the system
    read_list = random.sample(range(100), 10)
    print("My Memcache DHT")

    # Verify the data is stored in the DHT
    print("Verifying the data is stored in the DHT...")
    for key in read_list:
        value = dht_get(str(key))
        if value is None:
            print(f"Key - {key} not found in the DHT!")
        else:
            print(f"Key - {key} maps to value '{value}'")

    help_cmd()

    # Interactive shell
    while True:
        command = input("> ").strip().lower()
        if command == "add node":
            
            name = input("Enter node name: ")
            ip = input("Enter node IP address: ")
            port = input("Enter node port: ")
            node = Node(name, ip, port)
            flag = False
            for n in NODES:
                if n.name == node.name or n.port == node.port:
                    print(f"Error: Node {node.name} already exists or port must be in use! Try again")
                    flag = True
                    break
            if flag:
                continue
            add_node(node)
            print("Node was successfully added")    
        elif command == "remove node":
            node_name = input("Enter name of node to remove: Use 'view nodes' if unsure: ")
            removeflag = False
            for node in NODES:
                if node.name == node_name:
                    node_to_remove = node
                    remove_node(node_to_remove)
                    print("Node has been sucessfully removed")
                    removeflag = True
                    break
            if not removeflag:
                print("Node not found")  
        elif command == "set":
            key = input("Enter key to be added: ")
            value = input("Enter value to be added: ")
            key_hash = murmur3_32(str(key))
            dht_set(str(key_hash), value)
            # dht.dht_set()
        elif command == "get":
            key = input("Enter key: ")
            value = dht_get(key)
            if value is None:
                print("No such key")
            else:
                print(f"Value: {value}")
        elif command == "read list":
            # code to get the first 1o from read_list
            read_list = random.sample(range(100), 10)

            for key in read_list:
                value = dht_get(str(key))
                if value is None:
                    print(f"Key - {key} not found in the DHT!")
                else:
                    print(f"Key - {key} maps to value '{value}'.")
        # elif command == "view ring":
        #     print_node_table()
        elif command == "help":
            help_cmd()
        elif command == "view nodes":
            viewNodes()
        elif command == "test":
            test()
        elif command == "exit":
            break
        else:
            print("Invalid command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    main()