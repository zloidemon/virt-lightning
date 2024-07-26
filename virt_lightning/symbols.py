import locale
from enum import Enum, unique


@unique
class SymbolsUTF(Enum):
    CHECKMARK = "✔"
    COMPUTER = "💻"
    CROSS = "✕"
    CUSTOMS = "🛃"
    EXCLAMATION = "ℹ️"
    GLOBE = "🌍"
    HOURGLASS = "⌛"
    LIGHTNING = "⚡"
    RIGHT_ARROW = "⇛"
    THUMBS_UP = "👍"
    TRASHBIN = "🗑"


class SymbolsDefault(Enum):
    CHECKMARK = "+"
    COMPUTER = "+"
    CROSS = "-"
    CUSTOMS = "+"
    EXCLAMATION = "!"
    GLOBE = "*"
    HOURGLASS = "..."
    LIGHTNING = ""
    RIGHT_ARROW = "->"
    THUMBS_UP = "+"
    TRASHBIN = "x"


def get_symbols():
    lang, encoding = locale.getlocale()

    if encoding and encoding == "UTF-8":
        return SymbolsUTF
    return SymbolsDefault
