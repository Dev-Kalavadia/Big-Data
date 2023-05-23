from kazoo.client import KazooClient
import time
from tabulate import tabulate
from termcolor import colored
import threading
import signal
import sys
import random

# Flag to indicate if the program should stop
running = True

# Function to handle Ctrl+C (KeyboardInterrupt)
def signal_handler(sig, frame):
    global running
    print("Ctrl+C detected. Stopping threads...")
    running = False
    sys.exit(0)


class Philosopher:
    def __init__(self, name, state):
        self.name = name
        self.state = state

    def take_chopsticks(self):
        if self.state == "hungry":
            left_path = "/chopstick{}".format(int(self.name[-1]) % 5)
            right_path = "/chopstick{}".format((int(self.name[-1]) + 1) % 5)

            while True:
                # Get left chopstick state from ZooKeeper
                left_chopstick = zk.get(left_path)[0]
                # Get right chopstick state from ZooKeeper
                right_chopstick = zk.get(right_path)[0]

                if left_chopstick == b"available" and right_chopstick == b"available":
                    self.state = "eating"
                    # Update left chopstick state in ZooKeeper
                    zk.set(left_path, b"unavailable")
                    # Update right chopstick state in ZooKeeper
                    zk.set(right_path, b"unavailable")
                    break
                else:
                    # Wait for both chopsticks to become available
                    time.sleep(0.1)

    def release_chopsticks(self):
        self.state = "thinking"
        left_path = "/chopstick{}".format(int(self.name[-1]) % 5)
        right_path = "/chopstick{}".format((int(self.name[-1]) + 1) % 5)

        # Update left chopstick state in ZooKeeper
        zk.set(left_path, b"available")
        # Update right chopstick state in ZooKeeper
        zk.set(right_path, b"available")


def philosopher_watch_func(event):
    philosopher_name = event.path.split("/")[-1]
    philosopher = philosophers[philosopher_name]
    state = event.data.decode()

    if state == "hungry":
        philosopher.take_chopsticks()


def waiter_watch_func(event):
    state = event.data.decode()

    if state == "unavailable":
        for philosopher in philosophers.values():
            if philosopher.state == "hungry":
                philosopher.take_chopsticks()


def philosopher_thread_func(philosopher):
    while running:
        # Randomly alternate between thinking and hungry states
        time.sleep(random.randint(1, 5))
        philosopher.state = "hungry"

        # Try to take chopsticks
        philosopher.take_chopsticks()

        # Eat for a random amount of time
        if philosopher.state == "eating":
            # Color the philosopher who is eating
            philosopher_color = colored(philosopher.name, "green")
            philosopher_table = []
            for p in philosophers.values():
                # Color eating philosophers
                state = colored(p.state, "green" if p.state ==
                                "eating" else "white")
                philosopher_table.append([p.name, state])
            table = tabulate(philosopher_table, headers=[
                             "Philosopher", "State"], tablefmt="grid")
            print(table)
            print("{} is eating".format(philosopher_color))
            time.sleep(random.randint(1, 5))

            # Release chopsticks and go back to thinking
            philosopher.release_chopsticks()
            print("{} is thinking".format(philosopher.name))
            philosopher_table = []
            for p in philosophers.values():
                # Color eating philosophers
                state = colored(p.state, "green" if p.state ==
                                "eating" else "white")
                philosopher_table.append([p.name, state])
            table = tabulate(philosopher_table, headers=[
                             "Philosopher", "State"], tablefmt="grid")
            print(table)

            if not running:
                break


if __name__ == "__main__":
    # Register signal handler for Ctrl+C (KeyboardInterrupt)
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize ZooKeeper client and establish a connection
    from kazoo.client import KazooClient
    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()

    # Create 10 chopstick nodes with initial state "available"
    for i in range(10):
        zk.ensure_path("/chopstick{}".format(i))
        zk.set("/chopstick{}".format(i), b"available")

    # Create 5 philosopher nodes with initial state "thinking" and watch them for changes using philosopher_watch_func
    philosophers = {}
    for i in range(5):
        name = "Philosopher{}".format(i+1)
        philosopher = Philosopher(name, "thinking")
        philosophers[name] = philosopher
        path = "/{}".format(name)
        zk.ensure_path(path)
        zk.set(path, b"thinking")
        zk.get(path, watch=philosopher_watch_func)

        # Start philosopher thread
        threading.Thread(target=philosopher_thread_func,
                         args=(philosopher,)).start()

    # Create a waiter node with initial state "available" and watch it for changes using waiter_watch_func
    zk.ensure_path("/waiter")
    zk.set("/waiter", b"available")
    zk.get("/waiter", watch=waiter_watch_func)

    # Loop indefinitely, sleeping for 1 second at each iteration
    while running:
        time.sleep(1)
