# -*- coding: utf-8 -*-
"""
Created on Sat Nov 2 01:39:40 2019

@author: Shashwat Kathuria
"""

# Server Side Program
# Physical Layer and Data Link Layer Implementation

# Importing socket library for socket programming
import socket

def main():

    # Configuration for socket
    s = socket.socket()
    port = 9999
    s.bind(("", port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Socket created and binded to port number " + str(port))

    s.listen(5)
    print("Socket listening.")

    # Getting required inputs and printing examples
    fullMessage = raw_input("\nEnter the message you want to send : ")
    print("\n-------------------------------------------------------------------\n")
    print("Example of a generator function = x^3 + x + x^0 = \"1\" + \"0\" + \"1\" + \"1\" = 1011")
    print("Example of a generator function = x^2 + x = \"1\" + \"0\" + \"0\" = 110")
    print("\n-------------------------------------------------------------------\n")
    generator = raw_input("\n\nEnter the generator function in (0s, 1s) : ")

    print("\nWaiting for client...")
    # Listening for connections
    framesToSend = [fullMessage[i:i+4] for i in range(0, len(fullMessage), 4)]

    for i in range(len(framesToSend)):
        messageToSend = framesToSend[i]
        print("\nSending Frame Number " + str(i))
        # Connection information
        c, addr = s.accept()
        print("\nClient connection received " + str(addr))

        # Encoding data
        encodedMessage = PhysicalLayer(messageToSend).encode(generator)
        print("\nEncoded input to    : " + str(encodedMessage))

        # Sending encoded data
        c.send(encodedMessage.encode())

        print("--------------------------------------")
        # Closing connection
        c.close()



class PhysicalLayer():

    def __init__(self, message):
        """Function to initialize Physical Layer Object."""

        self.message = message
        self.bits = ""
        self.encodedMessage = ""

    def encode(self, generator):
        """Function to encode data using Manchester Encoding.
           Generator variable used to pass onto Data Link Layer Object."""

        # Converting self.message to self.bits
        self.stringToBits()
        # Printing bits of original message
        print("\nOriginal Message Bits                 : \n" + str(self.bits))

        # Getting checksum of CRC from Data Link Layer
        checksum = DataLinkLayer(self.bits, generator).encodeWithCRC()

        print("\nCRC Value                             : \n" + str(checksum))

        self.bits = self.bits + checksum

        # Implementing manchester encoding
        for bit in self.bits:
            # High to Low on 0
            if bit == "0":
                self.encodedMessage += "10"
            # Low to High on 1
            elif bit == "1":
                self.encodedMessage += "01"

        # Printing Values
        print("\nOriginal Message Bits With CRC Value  : \n" + str(self.bits))
        print("\nManchester Encoding                   : \n" + str(self.encodedMessage))

        # Returning final encoded message
        return self.encodedMessage

    def stringToBits(self):
        """Function to convert a string into stream of bits using ascii and bit values."""

        # List to store bits
        temp = []

        # Converting each character to a byte(8 bits)
        for c in self.message:

            # Getting bit value and ignoring initial 0b in the starting
            bits = bin(ord(c))[2:]

            # Including starting 0s
            bits = '00000000'[len(bits):] + bits

            # Appending to temp list
            temp.extend([int(b) for b in bits])

        # Concatenating all bits one by one in temp list to self.bits
        self.bits = ""
        for b in temp:
            self.bits += str(b)


class DataLinkLayer():

    def __init__(self, bits, generator):
        """Function to initialize Data Link Layer Object."""

        self.bits = bits
        self.keyLength = len(generator)
        self.appendedData = self.bits + "0" * (self.keyLength - 1)
        self.generator = generator


    def encodeWithCRC(self):
        """Function to encode data using CRC(Cyclic Redundancy Checksum)."""


        divisor = self.generator
        divident = self.appendedData

        # Number of bits to be xored
        numBits = len(self.generator)

        # Subpart substring
        subpartSubstring = self.appendedData[0 : numBits]

        while numBits < len(self.appendedData):

            # If Leftmost bit is 1
            if subpartSubstring[0] == '1':

                # Using self.generator and appending a data bit at the end
                subpartSubstring = self.XOR(self.generator, subpartSubstring) + self.appendedData[numBits]
            # Else if leftmost bit is 0
            else:
                # Using all '0's generator
                subpartSubstring = self.XOR('0'*numBits, subpartSubstring) + divident[numBits]

            # increment numBits to move further
            numBits += 1

        # For the last nth bits, otherwise out of bound occurs due to numBits
        # If Leftmost bit is 1
        if subpartSubstring[0] == '1':

            # Using self.generator
            subpartSubstring = self.XOR(divisor, subpartSubstring)
        # Else if leftmost bit is 0
        else:

            # Using all '0's generator
            subpartSubstring = self.XOR('0' * numBits, subpartSubstring)

        # Returning checksum answer
        checksum = subpartSubstring
        return checksum

    def XOR(self, generator, messagePartition):
        """Function to xor a messagePartition and generator.
           Also cutting of first bit of xor."""

        # Variable required
        self.xor = ""
        # Iterating through bits at respective positions
        for bit1, bit2 in zip(messagePartition, generator):
            # XORing
            if bit1 == bit2:
                self.xor = self.xor + "0"
            else:
                self.xor = self.xor + "1"

        # Returning answer
        return self.xor[1 : ]

# Calling main function
if __name__ == "__main__":
    main()
