from virt_lightning.idisk import IDisk


class DiskSystem(IDisk):
    def __init__(self, conn, storage):
        self.conn = conn
        self.storage = storage

    #
    # NOTE: Заглушка для интерфейса диска
    #
    def init(self, domain):
        pass
