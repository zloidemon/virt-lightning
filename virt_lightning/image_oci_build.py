class OCIImageBuild:
    def __init__(self, name):
        self.__name = name
        self.__labels = {}

    # --keep-git-dir
    # --checksum
    # --chown
    # --chmod
    # --link
    # --exclude
    def add(self, src, dst):
        return self

    def arg(self, key, value):
        return self

    def cmd(self, *args):
        return self

    # --from
    # --chown
    # --chmod
    # --link
    # --parents
    # --exclude
    def copy(self, src, dst):
        return self

    def entrypoint(self, entry):
        return self

    def env(self, key, value):
        return self

    def expose(self, port, protocol):
        return self

    # --platform
    # def from(self):
    #    return self

    # --interval=DURATION (default: 30s)
    # --timeout=DURATION (default: 30s)
    # --start-period=DURATION (default: 0s)
    # --start-interval=DURATION (default: 5s)
    # --retries=N (default: 3)
    def healthcheck(self):
        return self

    def label(self, key, value):
        if not isinstance(key, str):
            raise TypeError("key must be string")

        if len(key) == 0 or key == "":
            raise ValueError("key must be none zero string")

        if not isinstance(value, str):
            raise TypeError("value must be string")

        if not self.__labels.get(key, None):
            self.__labels[key] = value
        else:
            raise KeyError(f"'{key}' already exists with value: '{self.__labels[key]}'")
        return self

    def onbuilt(self, callback):
        return self

    # --mount
    # --network
    # --security
    def run(self):
        return self

    def shell(self, filename, *args):
        return self

    def stopsignal(self, signal):
        return self

    def user(self, uid, guid=None):
        return self

    def volume(self, *args):
        return self

    def workdir(self, path):
        return self
