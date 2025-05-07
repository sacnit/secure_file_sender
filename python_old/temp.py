import urwid
from twisted.internet import reactor, protocol, endpoints
from twisted.protocols.basic import LineReceiver

class MyClientProtocol(LineReceiver):
    def connectionMade(self):
        self.factory.window.update_status("Connected to server.")

    def lineReceived(self, line):
        self.factory.window.add_message(f"Received: {line.decode()}")

    def connectionLost(self, reason):
        self.factory.window.update_status(f"Disconnected: {reason.getErrorMessage()}")

class MyClientFactory(protocol.ClientFactory):
    protocol = MyClientProtocol

    def __init__(self, window):
        self.window = window
        window.factory = self

    def clientConnectionFailed(self, connector, reason):
        self.window.update_status(f"Connection failed: {reason.getErrorMessage()}")

class MyApplicationWindow:
    def __init__(self):
        self.status_text = urwid.Text("Not connected.")
        self.message_list = urwid.SimpleListWalker([])
        self.list_box = urwid.ListBox(self.message_list)
        self.edit_box = urwid.Edit("Send: ")
        self.connect_button = urwid.Button("Connect", on_press=self.connect)

        layout = urwid.Frame(
            header=urwid.Pile([self.status_text, self.connect_button]),
            body=self.list_box,
            footer=self.edit_box
        )
        self.loop = urwid.MainLoop(layout, palette=None, event_loop=urwid.TwistedEventLoop())
        self.factory = None # Will be set when factory is created

    def update_status(self, text):
        self.status_text.set_text(text) # Direct UI update within Twisted's loop

    def add_message(self, message):
        self.message_list.append(urwid.Text(message))
        self.list_box.set_focus(len(self.message_list) - 1) # Direct UI update

    def connect(self, button):
        host = "localhost"
        port = 12345
        point = endpoints.TCP4ClientEndpoint(reactor, host, port)
        d = point.connect(MyClientFactory(self))
        d.addErrback(lambda failure: self.update_status(f"Error connecting: {failure.getErrorMessage()}"))

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key == 'enter':
            text = self.edit_box.get_edit_text()
            if self.factory and self.factory.transport and text:
                self.factory.transport.writeLine(text.encode())
                self.add_message(f"Sent: {text}")
                self.edit_box.set_edit_text("")
        return True

    def run(self):
        pass # No need to run the Urwid loop separately

if __name__ == '__main__':
    window = MyApplicationWindow()
    reactor.callWhenRunning(window.loop.run) # Start the Urwid loop via the reactor
    reactor.run()