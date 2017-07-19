import threading
import queue

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor, task

class Server(LineReceiver):
    def __init__(self):
        self.connected = False

    def lineReceived(self,line):
        self.inq.put(line.decode("utf-8"))

    def connectionMade(self):
        self.connected = True

    def connectionLost(self,reason):
        self.connected = False
        self.loopq.stop()

class ServerFactory(Factory):
    def __init__(self,inq,outq):
        self.inq = inq
        self.outq = outq
        self.client = None

    def buildProtocol(self,addr):
        qhandler = OutQHandler(self.outq,self)
        loopq = task.LoopingCall(qhandler.handle)
        loopqDeferred = loopq.start(0.1)

        s = Server()
        s.loopq = loopq
        s.inq = self.inq
        self.client = s
        return s

    def writeClient(self,data):
        if self.client == None:
            print("Not connected")
            return
        else:
            self.client.sendLine(data.encode("utf-8"))

class OutQHandler():
    def __init__(self,outq,factory):
        self.outq = outq
        self.outq.put("Test from server")
        self.factory = factory

    def handle(self):
        #Write outgoing
        if self.factory.client == None or self.factory.client.connected == False:
            return

        while not self.outq.empty():
            try:
                item = self.outq.get(False)
            except queue.Empty:
                continue
            if item is None:
                continue
            self.factory.writeClient(item)

class server:
    def __init__(self,outq,HOST="localhost",PORT=9544):
        self.inq = queue.Queue()
        self.t = threading.Thread(target=self.start,args=(HOST,PORT,outq,self.inq),daemon=True)
        self.t.start()

    def start(self,*args,**kwargs):
        sf = ServerFactory(args[3],args[2])

        reactor.listenTCP(args[1], sf)
        reactor.run(installSignalHandlers=0)
