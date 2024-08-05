from virt_lightning.idisk import IDisk


class DiskSystem(IDisk):
    def __init__(self, conn, storage, network):
        self.conn = conn
        self.storage = storage
        self.network = network

    #
    # NOTE: Заглушка для интерфейса диска
    #
    def init(self, domain):
        pass
