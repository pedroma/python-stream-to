python-stream-to
================

For now there are hard-coded IP's and device UUID's. This will change in the future. For dependencies you need:

sudo apt-get install python-requests python-twisted

Usage for this command is:

python send_to.py [file]

Twisted is used to serve the file you want to stream to your final device. The protocol used is UpnP. This is in a testing phase but the final idea is to have a nautilus script so you can send any media file (audio,image,video) to a remote device.

Also if I figure out how to make python's SimpleHTTPServer create threads I will use because using twisted for this is just overkill.

