import zenoh

class Telemetry:
    def __init__(self, key: str):
        self.key = key
        self.session = zenoh.open(zenoh.Config())
        self.pub = self.session.declare_publisher(self.key)

# TODO finish implementing