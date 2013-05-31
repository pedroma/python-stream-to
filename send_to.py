#!/usr/bin/python
import sys, requests, urllib2, subprocess, os

RENDERER_IP = "192.168.1.102"
LOCAL_IP = "192.168.1.56"
UPNP_RENDERER_PORT = "40168"

#AVTRANSPORT_URI = "http://127.0.0.1:58609/AVTransport/97281f3d-39b4-57f4-e8b3-956f1beb3a7c/control.xml"
#AVTRANSPORT_URI = "http://%s:%s/AVTransport/0996dd70-8dee-cceb-ae2f-ae6e0b8545b4/control.xml"%(RENDERER_IP,UPNP_RENDERER_PORT)
AVTRANSPORT_URI = "http://%s:%s/dev/cc282d09-8983-820a-ffff-ffff84d46d21/svc/upnp-org/AVTransport/action"%(RENDERER_IP,UPNP_RENDERER_PORT)

TWISTED_SERVE_PATH = os.path.expanduser("~/.config/twisted")
PIDFILE = "%s/twistd.pid"%TWISTED_SERVE_PATH

HEADERS = {
    "Content-type":"text/xml;charset=\"utf-8\"",
    "Connection": "Keep-Alive",
    "Soapaction":"", # set this before making the request
}

STOP_PAYLOAD = """
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <u:Stop xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
            <InstanceID>0</InstanceID>
        </u:Stop>
    </s:Body>
</s:Envelope>
"""

SET_FILE_PAYLOAD = """
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
            <InstanceID>0</InstanceID>
            <CurrentURI>http://%s:8000/%s</CurrentURI>
            <CurrentURIMetaData></CurrentURIMetaData>
        </u:SetAVTransportURI>
    </s:Body>
</s:Envelope>
"""

PLAY_PAYLOAD = """
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
        <u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
            <InstanceID>0</InstanceID>
            <Speed>1</Speed>
        </u:Play>
    </s:Body>
</s:Envelope>
"""

def start_twisted():
    if not os.path.exists(TWISTED_SERVE_PATH):
        os.makedirs(TWISTED_SERVE_PATH)
    subprocess.call(["/usr/bin/twistd","--pidfile",PIDFILE,"web","--path",TWISTED_SERVE_PATH,"--port","8000"])

def main(play_file):
    play_file_base = os.path.basename(play_file)
    if os.access(PIDFILE,os.F_OK):
        pidfile = open(PIDFILE,"r")
        pid = pidfile.readline()
        pidfile.close()
        if os.path.exists("/proc/%s"%pid):
            print "Twisted is running"
        else:
            start_twisted()
    else:
        start_twisted()

    if not os.path.islink("%s/%s"%(TWISTED_SERVE_PATH,play_file_base)):
        os.symlink(os.path.abspath(play_file), "%s/%s"%(TWISTED_SERVE_PATH,play_file_base))

    HEADERS.update({"Soapaction":"\"urn:schemas-upnp-org:service:AVTransport:1#Stop\""})
    requests.post(AVTRANSPORT_URI, headers=HEADERS,data=STOP_PAYLOAD) # STOP playing
    HEADERS.update({"Soapaction":"\"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI\""})
    requests.post(AVTRANSPORT_URI, headers=HEADERS,data=SET_FILE_PAYLOAD%(LOCAL_IP,urllib2.quote(play_file_base)))
    HEADERS.update({"Soapaction":"\"urn:schemas-upnp-org:service:AVTransport:1#Play\""})
    requests.post(AVTRANSPORT_URI, headers=HEADERS,data=PLAY_PAYLOAD)


if __name__ == "__main__":
   main(sys.argv[1])

