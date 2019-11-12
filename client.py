# -*- coding: utf-8 -*-
"""
Created on Sat Nov 2 01:46:07 2019

@author: Shashwat Kathuria
"""

# Client Side Program
# Physical Layer and Data Link Layer Implementation

# Importing socket library for socket programming
import socket, random
import pylab as plt

def main():

    # Getting required input
    generator = raw_input("Enter the generator function in 0s and 1s : ")
    finalDecodedMessage = ""
    while True:

        # Configuration for socket
        s = socket.socket()
        port = 9999
        try:
            # Connecting
            s.connect(("127.0.0.1", port))
        except:
            break
        # Getting received message from server
        receivedMessage = s.recv(1024).decode()

        # Decoding message from Physical Layer which itself takes help from
        # Data Link Layer for error detection
        physicalLayer = PhysicalLayer(receivedMessage)
        decodedMessage = physicalLayer.decode(generator)

        # Printing Answer
        if decodedMessage != None:
            print("\nDecoded Frame Message     : " + str(decodedMessage))
            finalDecodedMessage += str(decodedMessage)
        else:
            print("\nError detected in data by CRC (Cyclic Redundancy Check).")

        # Plotting and showing encodings through graphs
        physicalLayer.plotManchesterEncoding()
        physicalLayer.plotOriginalEncoding()
        # Closing connection
        s.close()
        print("--------------------------------------")
    # Printing final answer
    print("\nFinal Decoded Message : " + str(finalDecodedMessage))
    print("--------------------------------------")


class PhysicalLayer():

    def __init__(self, bits):
        """Function to initialize Physical Layer Object."""

        self.message = ""
        self.bits = bits
        self.decodedMessage = ""
        self.time = list(range(len(self.bits)))
        self.manchesterEncoding = bits
        self.manchesterYVal = []
        self.originalYVal = []

    def decode(self, generator):
        """Function to decode data using Manchester Encoding.
           Generator variable used to pass onto Data Link Layer Object."""

        # Variable to keep track of decoded part of Manchester Encoding
        temp = ""
        print("\nManchester Encoding                 : \n" +  str(self.bits))

        # Getting values for manchester encoding graph plot
        yVal = [int(x) for x in list(self.bits)]
        temp = []
        for val in yVal:
            if val == 0:
                temp.append(-1)
            else:
                temp.append(1)
        yVal = temp
        self.manchesterYVal = yVal

        temp = ""
        # Decoding Manchester encoding in pairs
        for i in range(0, len(self.bits), 2):
            # Getting bits pair
            s = self.bits[i: i + 2]
            # If Low High then 1
            if s == "01":
                temp += "1"
            # If High Low then 0
            elif s == "10":
                temp += "0"

        # Storing answer
        self.bits = temp

        # Getting values for original encoding graph plot
        tempOriginalYVal = [int(x) for x in self.bits]
        for y in tempOriginalYVal:
            self.originalYVal.append(y)
            self.originalYVal.append(y)

        # Decoded to original encoding with CRC Remainder
        print("\nOriginal Encoding With CRC Remainder     : \n" + str(self.bits))

        choice = raw_input("\nDo you deliberately want to introduce errors into the frame signal to check the program?Press 1 for yes else give any other input : ")

        # Introducing Errors Deliberately if choice is 1
        if choice == "1":
            temp = list(self.bits)
            # For 5 iterations
            for i in range(5):
                index = random.randint(0, len(self.bits) - 1)
                if temp[index] == "0":
                    temp[index] = "1"
                elif temp[index] == "1":
                    temp[index] = "0"

            self.bits = "".join(temp)

            print("\nOriginal Encoding With CRC Remainder After Introducing Deliberate Errors     : \n" + str(self.bits))

        # Getting checksum
        CRCchecksum = DataLinkLayer(self.bits, generator).CRCdetectError()

        # Printing checksum
        print("\nCRC Remainder                            : \n" + str(CRCchecksum))

        # Checking further cases
        if CRCchecksum == '0' * (len(generator) - 1):
            self.bits = self.bits[:-(len(generator) - 1)]
            # Error case
            if len(self.bits) % 8 != 0:
                print("\nError detected in data. Number of bits not a multiple of 8.\n")
                return None
            # Correct case
            else:
                print("\nNo Error.")
                print("\nOriginal Encoding Without CRC Remainder : \n" + str(self.bits))
                return self.bitsToString()
        # Error case
        else:
            print("\nError detected in data. CRC Remainder is not equal to " + str('0' * (len(generator) - 1)))
            return None


    def bitsToString(self):
        """Function to convert a stream of bits into string using ascii and bit values."""

        # Lists to store bits and chars
        chars = []
        bitsArray = []

        # Storing all bits in an array
        for i in self.bits:
            bitsArray.append(int(i))

        # Converting 8 bits (each byte) into a char
        for b in range(len(bitsArray) // 8):

            # Getting 8 bits/a byte
            byte = bitsArray[b*8:(b+1)*8]
            # Converting to a char and then appending to list of chars
            # Base 2 for bit
            chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))

        # Concatenating chars and storing
        self.decodedMessage = ''.join(chars)

        # Returning answer
        return self.decodedMessage

    def plotManchesterEncoding(self):
        """Function to plot Manchester Encoding."""

        # Plotting and configuring the graph
        plt.figure("Graph")
        plt.title("Manchester Encoding")
        plt.clf()
        plt.xlim(0, len(self.time))
        plt.xlabel("Time || Manchester Encoding")
        plt.ylabel("Encoding Value")
        plt.plot(self.time, self.manchesterYVal, drawstyle='steps-post')
        plt.show()

    def plotOriginalEncoding(self):
        """Function to plot Original Encoding."""

        # Plotting and configuring the graph
        plt.figure("Graph")
        plt.title("Original Encoding")
        plt.clf()
        plt.xlim(0, len(self.time))
        plt.xlabel("Time || Original Encoding")
        plt.ylabel("Encoding Value")
        plt.plot(self.time, self.originalYVal, drawstyle='steps-post')
        plt.show()

class DataLinkLayer():
    def __init__(self, bits, generator):
        """Function to initialize Data Link Layer Object."""

        self.bits = bits
        self.keyLength = len(generator)
        self.appendedData = self.bits + "0" * (self.keyLength - 1)
        self.generator = generator

    def CRCdetectError(self):
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

    def XOR(self, messagePartition, generator):
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
