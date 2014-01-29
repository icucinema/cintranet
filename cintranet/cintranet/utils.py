import socket

class IRCCatPinger(object):
    def __init__(self, ip, port):
        self.address = ip, port
        self.failed = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.address)
        except Exception, e:
            print "Uhoh, Exception!", e
            self.failed = True

    def __del__(self):
        if not self.failed:
            self.socket.close()

    def say(self, channel, message):
        if not self.failed:
            self.socket.send(u'{} {}\n'.format(channel, message))

    def tell(self, person, message):
        return self.say(person, message)
