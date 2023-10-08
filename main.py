"""

DNS Queries have two parts:
1. header
2. question

We will:
1. create some python classes for the header and the question
2. write two functions 'header_to_bytes' and 'question_to_bytes' to convert the required info into byte strings.
3. write a 'build_query(domain_name, record_type)' function that generates a DNS query

"""

from dataclasses import dataclass # cool way to write classes that only store data, like C-like structs
import dataclasses
import struct
import random
import socket
random.seed(1)

# CONSTANTS shrouded in enigma
TYPE_A = 1
CLASS_IN = 1

@dataclass
class DNSHeader:
    id: int
    flags: int # mostly ignored
    # the following counts tell us how many records to expect in each section of a DNS packet
    num_questions: int = 0
    num_answers: int = 0
    num_authorities: int = 0
    num_additionals: int = 0

    
@dataclass
class DNSQuestion:
    name: bytes # like example.com
    type_: int # like A
    class_: int # class is always the same

def header_to_bytes(header):
    fields = dataclasses.astuple(header) # converts the dataclass items into a tuple
    # there are 6 'H's because there are 6 fields
    return struct.pack("!HHHHHH", *fields) # * is used before fields to collect (and store in a tuple) and remove the excess fields

def question_to_bytes(question):
    return question.name + struct.pack("!HH", question.type_, question.class_)

def encode_dns_name(domain_name):
    encoded = b""
    for part in domain_name.encode("ascii").split(b"."):
        encoded += bytes([len(part)]) + part
    return encoded + b"\x00"
    # so google.com gets encoded as b"\x06google\03xcom\x00"
def build_query(domain_name, record_type):
    name = encode_dns_name(domain_name)
    id_ = random.randint(0, 65535)
    RECURSION_DESIRED = 1 << 8
    header = DNSHeader(id=id_, num_questions=1, flags=RECURSION_DESIRED)
    question = DNSQuestion(name=name, type_=record_type, class_=CLASS_IN)
    return header_to_bytes(header)+question_to_bytes(question)

# Read RFC 1035 for clarification on the flags and constants used here.

query = build_query("www.example.com", 1)

# create a UDP socket
# 'socket.AF_INET' means that we're connecting to the internet
#                                                   (as opposed to a Unix domain socket 'AF_UNIX' for example)
# 'socket.SOCK_DGRAM' means "UDP"

# UDP is used as the protocol as it is commonly used in DNS name resolution.
# This is because it doens't formally establish a connection between server and client
# hence, saving time
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send our query to 8.8.8.8, port 53. Port 53 is the DNS port.
sock.sendto(query, ("8.8.8.8", 53)) # 8.8.8.8 is Google's DNS resolver

# read the response. UDP DNS responses are usually less than 512 bytes
# so reading 1024 bytes is enough
response, _ = sock.recvfrom(1024)



