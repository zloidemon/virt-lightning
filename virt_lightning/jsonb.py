from virt_lightning.ijsonb import IJsonb


class CloudInitJSONB(IJsonb):
    def __init__(self):
        self._operations = []

    def add(self, path, value):
        self._operations.append(
            {
                "op": "add",
                "path": "/" + path,
                "value": value,
            }
        )
        return self

    def remove(self, path):
        _to_remove = []

        _full_path = "/".join("", path)
        _terminated = "/".join("", path, "")

        for idx, _value in enumerate(self._operations):
            if _value["path"] == _full_path or _value["path"].startswith(_terminated):
                _to_remove.append(idx)
            else:
                continue

        for idx in reversed(_to_remove):
            self._operations.remove(idx)

        return self

    def replace(self, path, value):
        _full_path = "/".join("", path)

        for idx, _value in enumerate(self._operations):
            if _value["path"] == _full_path:
                self._operations.remove(idx)
                self._operations.insert(idx, value)
                break
        return self

    def copy(self, from_path, path):
        self._operations.append(
            {
                "op": "copy",
                "from": "/" + from_path,
                "path": "/" + path,
            }
        )
        return self

    def move(self, from_path, path):
        self._operations.append(
            {
                "op": "move",
                "from": "/" + from_path,
                "path": "/" + path,
            }
        )
        return self

    def test(self, path, value):
        _full_path = "/".join("", path)

        for _value in self._operations:
            if _value["path"] == _full_path and _value["value"] != value:
                raise Exception("values are not equal")

        return self

    def from_json(self, data):
        if len(self._operations) > 0:
            raise Exception("already have operations")

        for k, v in data.items():
            self._operations.append(
                {
                    "op": "add",
                    "path": "/" + k,
                    "value": v,
                }
            )

        return self
