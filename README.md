# TCP-IP
implementing the core of the tcp/ip prootocole --> understand it how it works ^_^



LAYER 1: PHYSICAL LAYER
Based on:

Electrical signals (voltage levels: 0V = 0, 5V = 1)
Electromagnetic waves (radio, WiFi, fiber optic light)
Hardware specifications (cable types, connector shapes)
Physics laws (signal propagation, interference, attenuation)

Real example: Your Ethernet cable carries electrical pulses at specific voltages

LAYER 2: DATA LINK LAYER
Based on:

MAC addresses (hardware addresses burned into network cards)
Frame structure (fixed format for organizing bits)
Error detection (checksums, CRC algorithms)
Medium access control (who can talk when on shared medium)

Real example: Ethernet frames with source/destination MAC addresses

LAYER 3: NETWORK LAYER (IP)
Based on:

IP addresses (32-bit numbers like 192.168.1.1)
Routing tables (databases of network paths)
Packet headers (source IP, destination IP, protocol)
Hop-by-hop forwarding (each router decides next step)

Real example: Your router has a table saying "192.168.1.0/24 → local, 0.0.0.0/0 → ISP"


LAYER 4: TRANSPORT LAYER (TCP/UDP)
Based on:

Port numbers (16-bit numbers 0-65535)
State machines (CLOSED → SYN_SENT → ESTABLISHED → CLOSED)
Sequence numbers (32-bit counters for packet ordering)
Sliding window algorithm (mathematical flow control)
Timers and retransmission (timeout mechanisms)

Real example: TCP tracks "I sent packet #1000, waiting for ACK #1001"


LAYER 5: APPLICATION LAYER
Based on:

Protocol specifications (HTTP RFC, SMTP RFC documents)
Text formatting (ASCII, UTF-8 character encoding)
Request/response patterns (client asks, server responds)
State protocols (login sessions, cookies)

Real example: HTTP uses text commands like "GET /index.html HTTP/1.1"


TCP is based on:

Sliding Window Protocol (mathematical algorithm)
Sequence arithmetic (modular arithmetic for wraparound)
Exponential backoff (retransmission timing)
Checksum algorithms (error detection math)

IP is based on:

Longest prefix matching (routing algorithm)
Classless Inter-Domain Routing (CIDR) (subnet math)
Time-to-Live (TTL) (loop prevention counter)

DNS is based on:

Hierarchical tree structure (distributed database)
Caching algorithms (performance optimization)
Hash functions (domain name to IP mapping)


Each layer is built on the layer below it:
Applications (HTTP, FTP) → Text protocols & standards
         ↓
TCP/UDP → Mathematical algorithms & state machines  
         ↓
IP → Routing tables & addressing schemes
         ↓
Ethernet → Frame formats & MAC addresses
         ↓
Physical → Electrical/optical signals


