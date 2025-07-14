#!/usr/bin/env python3
"""
TCP/IP Implementation from Scratch
Understanding the fundamental concepts through practical code

Author: Educational Implementation
Purpose: Learn how TCP/IP actually works by building it
"""

import socket
import struct
import time
import random
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# ============================================================================
# FOUNDATION: TCP/IP is built on these core concepts
# ============================================================================

class PacketType(Enum):
    """Types of packets in our simplified TCP"""
    SYN = 1      # Synchronize - start connection
    ACK = 2      # Acknowledge - confirm receipt
    SYN_ACK = 3  # Synchronize + Acknowledge
    DATA = 4     # Data packet
    FIN = 5      # Finish - close connection

@dataclass
class TCPHeader:
    """
    TCP HEADER STRUCTURE (what's actually in every TCP packet)
    This is the REAL foundation of TCP!
    """
    source_port: int      # 16 bits - where packet comes from
    dest_port: int        # 16 bits - where packet goes to
    sequence_num: int     # 32 bits - packet order number
    ack_num: int          # 32 bits - next expected packet number
    flags: PacketType     # 8 bits - what type of packet
    window_size: int      # 16 bits - how many packets can be sent
    checksum: int         # 16 bits - error detection
    data: bytes           # Variable - the actual data

    def to_bytes(self) -> bytes:
        """Convert header to bytes (what actually goes on the wire)"""
        return struct.pack(
            '!HHLLBBHH',  # Network byte order format
            self.source_port,
            self.dest_port, 
            self.sequence_num,
            self.ack_num,
            self.flags.value,
            self.window_size,
            self.checksum,
            len(self.data)
        ) + self.data

    @classmethod
    def from_bytes(cls, data: bytes) -> 'TCPHeader':
        """Parse bytes back into header (receive packets)"""
        header_size = struct.calcsize('!HHLLBBHH')
        header_data = struct.unpack('!HHLLBBHH', data[:header_size])
        payload = data[header_size:]
        
        return cls(
            source_port=header_data[0],
            dest_port=header_data[1],
            sequence_num=header_data[2],
            ack_num=header_data[3],
            flags=PacketType(header_data[4]),
            window_size=header_data[5],
            checksum=header_data[6],
            data=payload
        )

# ============================================================================
# CORE CONCEPT 1: SEGMENTATION
# Why? Large data must be split into smaller chunks for network transmission
# ============================================================================

class DataSegmenter:
    """
    SEGMENTATION: Breaking large data into smaller pieces
    This is fundamental to how TCP works!
    """
    
    def __init__(self, max_segment_size: int = 1024):
        self.max_segment_size = max_segment_size
    
    def segment_data(self, data: bytes) -> List[bytes]:
        """Split large data into network-sized chunks"""
        segments = []
        for i in range(0, len(data), self.max_segment_size):
            segment = data[i:i + self.max_segment_size]
            segments.append(segment)
        
        print(f"📦 Segmented {len(data)} bytes into {len(segments)} segments")
        return segments
    
    def reassemble_data(self, segments: List[bytes]) -> bytes:
        """Put segments back together in correct order"""
        result = b''.join(segments)
        print(f"🔧 Reassembled {len(segments)} segments into {len(result)} bytes")
        return result

# ============================================================================
# CORE CONCEPT 2: SEQUENCE NUMBERS
# Why? To ensure packets arrive in correct order and detect lost packets
# ============================================================================

class SequenceManager:
    """
    SEQUENCE NUMBERS: How TCP ensures correct ordering
    Every byte gets a number!
    """
    
    def __init__(self):
        # Start with random number (security)
        self.next_seq = random.randint(1000, 9999)
        self.expected_seq = 0
    
    def get_next_sequence(self, data_length: int) -> int:
        """Get sequence number for next packet"""
        current_seq = self.next_seq
        self.next_seq += data_length
        return current_seq
    
    def is_sequence_valid(self, received_seq: int) -> bool:
        """Check if received packet has expected sequence number"""
        return received_seq == self.expected_seq
    
    def update_expected_sequence(self, data_length: int):
        """Update what sequence number we expect next"""
        self.expected_seq += data_length

# ============================================================================
# CORE CONCEPT 3: ACKNOWLEDGMENTS
# Why? To confirm packets were received and trigger retransmission if lost
# ============================================================================

class AckManager:
    """
    ACKNOWLEDGMENTS: How TCP confirms packet delivery
    Every packet must be acknowledged!
    """
    
    def __init__(self):
        self.pending_acks: Dict[int, float] = {}  # seq_num -> timestamp
        self.received_packets: Dict[int, bytes] = {}  # seq_num -> data
    
    def send_ack(self, seq_num: int, data_length: int) -> TCPHeader:
        """Send acknowledgment for received packet"""
        ack_header = TCPHeader(
            source_port=8080,
            dest_port=8081,
            sequence_num=0,
            ack_num=seq_num + data_length,  # Next expected sequence
            flags=PacketType.ACK,
            window_size=1024,
            checksum=0,
            data=b''
        )
        print(f"📨 Sending ACK for sequence {seq_num}")
        return ack_header
    
    def wait_for_ack(self, seq_num: int, timeout: float = 2.0) -> bool:
        """Wait for acknowledgment of sent packet"""
        self.pending_acks[seq_num] = time.time()
        
        # Simulate waiting for ACK
        time.sleep(0.1)  # Network delay
        
        # Check if ACK received within timeout
        if time.time() - self.pending_acks[seq_num] > timeout:
            print(f"❌ Timeout waiting for ACK {seq_num}")
            return False
        
        print(f"✅ ACK received for sequence {seq_num}")
        del self.pending_acks[seq_num]
        return True

# ============================================================================
# CORE CONCEPT 4: FLOW CONTROL (WINDOWING)
# Why? To prevent overwhelming the receiver with too much data
# ============================================================================

class FlowController:
    """
    FLOW CONTROL: Managing data flow speed
    Don't send faster than receiver can process!
    """
    
    def __init__(self, initial_window: int = 3):
        self.window_size = initial_window
        self.packets_in_flight = 0
    
    def can_send_packet(self) -> bool:
        """Check if we can send another packet"""
        return self.packets_in_flight < self.window_size
    
    def packet_sent(self):
        """Track that a packet was sent"""
        self.packets_in_flight += 1
        print(f"📤 Packet sent. In flight: {self.packets_in_flight}/{self.window_size}")
    
    def packet_acked(self):
        """Track that a packet was acknowledged"""
        self.packets_in_flight = max(0, self.packets_in_flight - 1)
        print(f"📥 Packet ACKed. In flight: {self.packets_in_flight}/{self.window_size}")
    
    def adjust_window(self, new_size: int):
        """Adjust window size based on network conditions"""
        self.window_size = new_size
        print(f"🎛️ Window size adjusted to {self.window_size}")

# ============================================================================
# CORE CONCEPT 5: CONNECTION MANAGEMENT (3-WAY HANDSHAKE)
# Why? To establish synchronized connection before data transfer
# ============================================================================

class ConnectionManager:
    """
    CONNECTION MANAGEMENT: The famous 3-way handshake
    This is how TCP establishes connections!
    """
    
    def __init__(self):
        self.state = "CLOSED"
        self.seq_manager = SequenceManager()
    
    def initiate_connection(self) -> TCPHeader:
        """Step 1: Send SYN packet"""
        self.state = "SYN_SENT"
        syn_packet = TCPHeader(
            source_port=8080,
            dest_port=8081,
            sequence_num=self.seq_manager.get_next_sequence(0),
            ack_num=0,
            flags=PacketType.SYN,
            window_size=1024,
            checksum=0,
            data=b''
        )
        print("🤝 Step 1: Sending SYN packet")
        return syn_packet
    
    def handle_syn(self, syn_packet: TCPHeader) -> TCPHeader:
        """Step 2: Respond with SYN-ACK"""
        self.state = "SYN_RECEIVED"
        syn_ack_packet = TCPHeader(
            source_port=8081,
            dest_port=8080,
            sequence_num=self.seq_manager.get_next_sequence(0),
            ack_num=syn_packet.sequence_num + 1,
            flags=PacketType.SYN_ACK,
            window_size=1024,
            checksum=0,
            data=b''
        )
        print("🤝 Step 2: Sending SYN-ACK packet")
        return syn_ack_packet
    
    def handle_syn_ack(self, syn_ack_packet: TCPHeader) -> TCPHeader:
        """Step 3: Send final ACK"""
        self.state = "ESTABLISHED"
        ack_packet = TCPHeader(
            source_port=8080,
            dest_port=8081,
            sequence_num=self.seq_manager.get_next_sequence(0),
            ack_num=syn_ack_packet.sequence_num + 1,
            flags=PacketType.ACK,
            window_size=1024,
            checksum=0,
            data=b''
        )
        print("🤝 Step 3: Sending final ACK - Connection ESTABLISHED!")
        return ack_packet

# ============================================================================
# PUTTING IT ALL TOGETHER: SIMPLIFIED TCP IMPLEMENTATION
# ============================================================================

class SimpleTCP:
    """
    COMPLETE TCP IMPLEMENTATION
    This shows how all the concepts work together!
    """
    
    def __init__(self, port: int):
        self.port = port
        self.segmenter = DataSegmenter()
        self.seq_manager = SequenceManager()
        self.ack_manager = AckManager()
        self.flow_controller = FlowController()
        self.connection_manager = ConnectionManager()
    
    def establish_connection(self) -> bool:
        """Perform 3-way handshake"""
        print("\n🚀 Starting 3-way handshake...")
        
        # Step 1: Send SYN
        syn = self.connection_manager.initiate_connection()
        
        # Step 2: Simulate receiving SYN-ACK
        syn_ack = self.connection_manager.handle_syn(syn)
        
        # Step 3: Send final ACK
        final_ack = self.connection_manager.handle_syn_ack(syn_ack)
        
        return self.connection_manager.state == "ESTABLISHED"
    
    def send_data(self, data: bytes) -> bool:
        """Send data using TCP reliability mechanisms"""
        if self.connection_manager.state != "ESTABLISHED":
            print("❌ Connection not established!")
            return False
        
        print(f"\n📤 Sending {len(data)} bytes of data...")
        
        # Step 1: Segment the data
        segments = self.segmenter.segment_data(data)
        
        # Step 2: Send each segment with TCP reliability
        for i, segment in enumerate(segments):
            # Flow control - wait if window is full
            while not self.flow_controller.can_send_packet():
                print("⏳ Window full, waiting...")
                time.sleep(0.1)
            
            # Create data packet
            seq_num = self.seq_manager.get_next_sequence(len(segment))
            data_packet = TCPHeader(
                source_port=self.port,
                dest_port=8081,
                sequence_num=seq_num,
                ack_num=0,
                flags=PacketType.DATA,
                window_size=1024,
                checksum=0,
                data=segment
            )
            
            print(f"📦 Sending segment {i+1}/{len(segments)} (seq: {seq_num})")
            
            # Send packet
            self.flow_controller.packet_sent()
            
            # Wait for ACK
            if self.ack_manager.wait_for_ack(seq_num):
                self.flow_controller.packet_acked()
                print(f"✅ Segment {i+1} acknowledged")
            else:
                print(f"❌ Segment {i+1} failed - would retransmit")
                return False
        
        print("🎉 All data sent successfully!")
        return True

# ============================================================================
# DEMONSTRATION: HOW TCP/IP ACTUALLY WORKS
# ============================================================================

def demonstrate_tcp_concepts():
    """
    PRACTICAL DEMONSTRATION
    This shows TCP/IP concepts in action!
    """
    
    print("=" * 70)
    print("🌐 TCP/IP IMPLEMENTATION DEMONSTRATION")
    print("=" * 70)
    
    # Create TCP instance
    tcp = SimpleTCP(port=8080)
    
    # Establish connection
    if tcp.establish_connection():
        print("✅ Connection established successfully!")
        
        # Send some data
        message = b"Hello, TCP/IP! This is a longer message that will be segmented into multiple packets to demonstrate how TCP handles large data transfers with reliability, flow control, and proper sequencing."
        
        success = tcp.send_data(message)
        
        if success:
            print("\n🎯 WHAT JUST HAPPENED:")
            print("1. 3-way handshake established connection")
            print("2. Data was segmented into smaller packets")
            print("3. Each packet was sequenced and sent")
            print("4. Flow control prevented overwhelming receiver")
            print("5. Acknowledgments confirmed delivery")
            print("6. This is exactly how real TCP works!")
    
    print("\n" + "=" * 70)
    print("🎓 EDUCATIONAL INSIGHTS")
    print("=" * 70)
    print("TCP/IP is built on these FUNDAMENTAL concepts:")
    print("• SEGMENTATION: Break large data into small packets")
    print("• SEQUENCING: Number packets to ensure correct order")
    print("• ACKNOWLEDGMENTS: Confirm packet delivery")
    print("• FLOW CONTROL: Prevent overwhelming the receiver")
    print("• CONNECTION MANAGEMENT: Establish reliable sessions")
    print("• ERROR DETECTION: Checksums and retransmission")
    print("\nEvery time you browse the web, send email, or use any")
    print("internet service, THIS is what's happening underneath!")

# ============================================================================
# BONUS: REAL NETWORK PROGRAMMING EXAMPLE
# ============================================================================

def create_real_tcp_server():
    """
    REAL TCP SERVER using Python's socket library
    This is how you'd actually implement TCP in practice
    """
    
    print("\n🔧 REAL TCP SERVER IMPLEMENTATION")
    print("-" * 50)
    
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(1)
    
    print("🏃 TCP Server listening on port 9999")
    print("💡 Run this in terminal to connect:")
    print("   telnet localhost 9999")
    print("   (or use another terminal with the client code)")
    
    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"📞 Connection from {address}")
            
            # Receive data
            data = client_socket.recv(1024)
            print(f"📨 Received: {data.decode()}")
            
            # Send response
            response = b"Hello from TCP server! Your message was received."
            client_socket.send(response)
            
            client_socket.close()
            
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down")
    finally:
        server_socket.close()

def create_real_tcp_client():
    """
    REAL TCP CLIENT
    This connects to the server above
    """
    
    print("\n🔧 REAL TCP CLIENT IMPLEMENTATION")
    print("-" * 50)
    
    # Create TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server (3-way handshake happens here!)
        client_socket.connect(('localhost', 9999))
        print("✅ Connected to server")
        
        # Send data
        message = b"Hello from TCP client!"
        client_socket.send(message)
        print(f"📤 Sent: {message.decode()}")
        
        # Receive response
        response = client_socket.recv(1024)
        print(f"📥 Received: {response.decode()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client_socket.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def demonstrate_full_tcp_stack():
    """
    COMPLETE TCP/IP STACK DEMONSTRATION
    Shows every layer working together
    """
    print("\n🌐 COMPLETE TCP/IP STACK IMPLEMENTATION")
    print("=" * 60)
    
    # Layer 4: Transport (TCP)
    print("\n🚚 LAYER 4: TRANSPORT LAYER")
    tcp = SimpleTCP(port=8080)
    
    # Layer 3: Network (IP) - Simplified
    print("\n🌍 LAYER 3: NETWORK LAYER (IP)")
    source_ip = "192.168.1.100"
    dest_ip = "192.168.1.200"
    print(f"   Source IP: {source_ip}")
    print(f"   Destination IP: {dest_ip}")
    print(f"   Routing: Direct delivery (same subnet)")
    
    # Layer 2: Data Link (Ethernet) - Simplified
    print("\n🔗 LAYER 2: DATA LINK LAYER")
    source_mac = "00:1B:44:11:3A:B7"
    dest_mac = "00:1B:44:11:3A:B8"
    print(f"   Source MAC: {source_mac}")
    print(f"   Destination MAC: {dest_mac}")
    print(f"   Frame type: Ethernet II")
    
    # Layer 1: Physical - Conceptual
    print("\n⚡ LAYER 1: PHYSICAL LAYER")
    print("   Medium: Copper cable (CAT6)")
    print("   Encoding: Manchester encoding")
    print("   Speed: 1 Gbps")
    print("   Bits transmitted as electrical signals")
    
    # Now run the full stack
    print("\n🎯 FULL STACK IN ACTION:")
    if tcp.establish_connection():
        message = b"Hello from complete TCP/IP stack!"
        tcp.send_data(message)
        
        print("\n📊 WHAT HAPPENED AT EACH LAYER:")
        print("🔴 Application: Created message")
        print("🟠 Transport: TCP segmented, sequenced, acknowledged")
        print("🟡 Network: IP routed packet to destination")
        print("🟢 Data Link: Ethernet framed with MAC addresses")
        print("🔵 Physical: Bits transmitted as electrical signals")

def create_complete_tcp_server():
    """
    PRODUCTION-READY TCP SERVER
    This is how real servers work
    """
    import select
    import errno
    
    class CompleteTCPServer:
        def __init__(self, host='localhost', port=8080):
            self.host = host
            self.port = port
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setblocking(False)  # Non-blocking
            self.clients = {}
            self.running = True
            
        def start(self):
            """Start server with proper error handling"""
            try:
                self.socket.bind((self.host, self.port))
                self.socket.listen(128)  # Backlog queue
                print(f"🚀 Production TCP Server on {self.host}:{self.port}")
                
                while self.running:
                    self.handle_connections()
                    
            except Exception as e:
                print(f"❌ Server error: {e}")
            finally:
                self.cleanup()
                
        def handle_connections(self):
            """Handle multiple connections efficiently"""
            ready_sockets = [self.socket]
            ready_sockets.extend(self.clients.keys())
            
            try:
                readable, _, exceptional = select.select(ready_sockets, [], ready_sockets, 1.0)
                
                for sock in readable:
                    if sock is self.socket:
                        # New connection
                        self.accept_connection()
                    else:
                        # Existing client data
                        self.handle_client_data(sock)
                        
                for sock in exceptional:
                    self.cleanup_client(sock)
                    
            except select.error as e:
                if e[0] != errno.EINTR:
                    print(f"❌ Select error: {e}")
                    
        def accept_connection(self):
            """Accept new client connection"""
            try:
                client_socket, address = self.socket.accept()
                client_socket.setblocking(False)
                self.clients[client_socket] = {
                    'address': address,
                    'buffer': b'',
                    'connected_at': time.time()
                }
                print(f"📞 New client: {address}")
                
            except socket.error as e:
                if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                    print(f"❌ Accept error: {e}")
                    
        def handle_client_data(self, client_socket):
            """Handle data from existing client"""
            try:
                data = client_socket.recv(4096)
                if data:
                    client_info = self.clients[client_socket]
                    client_info['buffer'] += data
                    
                    # Process complete messages
                    self.process_client_buffer(client_socket)
                else:
                    # Client disconnected
                    self.cleanup_client(client_socket)
                    
            except socket.error as e:
                if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                    print(f"❌ Client error: {e}")
                    self.cleanup_client(client_socket)
                    
        def process_client_buffer(self, client_socket):
            """Process complete messages from client buffer"""
            client_info = self.clients[client_socket]
            buffer = client_info['buffer']
            
            # Simple HTTP request processing
            if b'\r\n\r\n' in buffer:
                request = buffer.split(b'\r\n\r\n')[0].decode('utf-8', errors='ignore')
                print(f"📨 Request from {client_info['address']}: {request.split()[0:2]}")
                
                # Send HTTP response
                response = self.create_http_response(request)
                try:
                    client_socket.send(response.encode())
                except socket.error:
                    pass
                    
                # Clear buffer
                client_info['buffer'] = b''
                
                # Close connection (HTTP/1.0 behavior)
                self.cleanup_client(client_socket)
                
        def create_http_response(self, request):
            """Create proper HTTP response"""
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Complete TCP Server</title></head>
            <body>
                <h1>🎯 Complete TCP/IP Implementation</h1>
                <p><strong>Server Time:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Active Connections:</strong> {len(self.clients)}</p>
                <p><strong>Your Request:</strong></p>
                <pre>{request}</pre>
                <p>This response traveled through all TCP/IP layers!</p>
            </body>
            </html>
            """
            
            response = f"HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: text/html\r\n"
            response += f"Content-Length: {len(html)}\r\n"
            response += f"Connection: close\r\n"
            response += f"\r\n{html}"
            
            return response
            
        def cleanup_client(self, client_socket):
            """Clean up client connection"""
            if client_socket in self.clients:
                address = self.clients[client_socket]['address']
                del self.clients[client_socket]
                print(f"📴 Client disconnected: {address}")
                
            try:
                client_socket.close()
            except:
                pass
                
        def cleanup(self):
            """Clean up server resources"""
            for client_socket in list(self.clients.keys()):
                self.cleanup_client(client_socket)
            self.socket.close()
            print("🛑 Server shutdown complete")
    
    # Run the complete server
    server = CompleteTCPServer()
    server.start()

# Enhanced main function
def main():
    """Enhanced main with all features"""
    print("=" * 70)
    print("🌐 COMPLETE TCP/IP IMPLEMENTATION")
    print("=" * 70)
    
    choice = input("""
Choose demonstration:
1. Educational TCP concepts
2. Complete TCP/IP stack
3. Production TCP server
4. Real networking examples
5. All demonstrations

Enter choice (1-5): """).strip()
    
    if choice == "1":
        demonstrate_tcp_concepts()
    elif choice == "2":
        demonstrate_full_tcp_stack()
    elif choice == "3":
        create_complete_tcp_server()
    elif choice == "4":
        create_real_tcp_server()
    elif choice == "5":
        demonstrate_tcp_concepts()
        demonstrate_full_tcp_stack()
        print("\n🚀 Starting production server...")
        create_complete_tcp_server()
    else:
        print("Invalid choice, running basic demonstration...")
        demonstrate_tcp_concepts()

if __name__ == "__main__":
    main()