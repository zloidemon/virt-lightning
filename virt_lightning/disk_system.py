from virt_lightning.idisk import IDisk


class DiskSystem(IDisk):
    def __init__(self, conn):
        self.conn = conn

    def init(self, domain):
        pass
