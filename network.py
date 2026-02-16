import socket
import json
import threading
import time
from typing import Optional, Callable, Set
from constants import DEFAULT_PORT, NET_BUFFER_SIZE, DISCOVERY_PORT, DISCOVERY_INTERVAL

class NetworkManager:
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.is_host = False
        self.on_data_received: Optional[Callable[[dict], None]] = None
        self.on_connection_established: Optional[Callable[[], None]] = None
        self.on_connection_lost: Optional[Callable[[], None]] = None
        self.running = False
        
        # Discovery state
        self.discovery_socket: Optional[socket.socket] = None
        self.discovery_running = False
        self.found_hosts: Set[str] = set()
        self.on_host_discovered: Optional[Callable[[str], None]] = None

    def start_server(self):
        """Starts a TCP server and listens for a single connection."""
        self.stop() # Ensure previous session is fully cleaned up
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(1)
        self.is_host = True
        self.running = True
        
        # Accept connection in a separate thread to avoid blocking the main game loop
        thread = threading.Thread(target=self._accept_connection, daemon=True)
        thread.start()
        print(f"Server started on port {self.port}. Waiting for connection...")

    def _accept_connection(self):
        try:
            self.client_socket, addr = self.server_socket.accept()
            print(f"Connected by {addr}")
            if self.on_connection_established:
                self.on_connection_established()
            self._listen_for_data()
        except Exception as e:
            print(f"Error accepting connection: {e}")
            self.running = False
            if self.on_connection_lost:
                self.on_connection_lost()

    def connect_to_server(self, host_ip: str):
        """Connects to a host server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host_ip, self.port))
            self.is_host = False
            self.running = True
            
            # Listen for data in a separate thread
            thread = threading.Thread(target=self._listen_for_data, daemon=True)
            thread.start()
            print(f"Connected to server at {host_ip}")
            if self.on_connection_established:
                self.on_connection_established()
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            if self.on_connection_lost:
                self.on_connection_lost()
            return False

    def _listen_for_data(self):
        while self.running:
            try:
                data = self.client_socket.recv(NET_BUFFER_SIZE)
                if not data:
                    print("Connection closed by peer")
                    self.running = False
                    break
                
                message = json.loads(data.decode('utf-8'))
                if self.on_data_received:
                    self.on_data_received(message)
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.running = False
                break
        
        # When loop finishes (running=False or break), notify connection lost
        if self.on_connection_lost:
            self.on_connection_lost()

    def send_data(self, data: dict):
        """Sends a JSON-encoded dictionary to the connected peer."""
        if self.client_socket and self.running:
            try:
                message = json.dumps(data).encode('utf-8')
                self.client_socket.sendall(message)
            except Exception as e:
                print(f"Error sending data: {e}")
                self.running = False

    def start_discovery_beacon(self):
        """Broadcasts a beacon to the local network to announce presence."""
        if self.discovery_running:
            return
        self.discovery_running = True
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        thread = threading.Thread(target=self._run_beacon, daemon=True)
        thread.start()
        print("Discovery beacon started.")

    def _run_beacon(self):
        message = b"GOBANG_HOST"
        while self.discovery_running:
            try:
                self.discovery_socket.sendto(message, ('<broadcast>', DISCOVERY_PORT))
                time.sleep(DISCOVERY_INTERVAL)
            except Exception as e:
                print(f"Error sending discovery beacon: {e}")
                break

    def start_discovery_listener(self):
        """Listens for discovery beacons from other hosts."""
        if self.discovery_running:
            return
        self.discovery_running = True
        self.found_hosts.clear()
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Handle Windows specific bind for broadcase/discovery
        try:
            self.discovery_socket.bind(('', DISCOVERY_PORT))
        except Exception as e:
            print(f"Error binding discovery listener: {e}")
            self.discovery_running = False
            return
            
        thread = threading.Thread(target=self._run_listener, daemon=True)
        thread.start()
        print("Discovery listener started.")

    def _run_listener(self):
        self.discovery_socket.settimeout(1.0)
        while self.discovery_running:
            try:
                data, addr = self.discovery_socket.recvfrom(1024)
                if data == b"GOBANG_HOST":
                    ip = addr[0]
                    if ip not in self.found_hosts:
                        self.found_hosts.add(ip)
                        if self.on_host_discovered:
                            self.on_host_discovered(ip)
            except socket.timeout:
                continue
            except Exception as e:
                if self.discovery_running:
                    print(f"Error in discovery listener: {e}")
                break

    def stop_discovery(self):
        """Stops discovery beacon or listener."""
        self.discovery_running = False
        if self.discovery_socket:
            self.discovery_socket.close()
            self.discovery_socket = None
        print("Discovery stopped.")

    def stop(self):
        """Closes all sockets and stops threads."""
        self.running = False
        self.stop_discovery()
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

    @staticmethod
    def get_local_ip():
        """Returns the local IP address of the machine."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
