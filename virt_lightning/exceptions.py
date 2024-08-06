class ImageNotFoundUpstreamError(Exception):
    def __init__(self, name):
        self.name = name


class VMNotFoundError(Exception):
    def __init__(self, name):
        self.name = name


class VMNotRunningError(Exception):
    def __init__(self, name):
        self.name = name


class ImageNotFoundLocallyError(Exception):
    def __init__(self, name):
        self.name = name


class CannotConnectToLibvirtError(Exception):
    pass
