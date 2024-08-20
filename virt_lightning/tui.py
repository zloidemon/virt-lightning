import curses
from curses import panel


class Menu:
    def __init__(self, items, stdscreen):
        self.window = stdscreen.subwin(0, 0)
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

        self.position = 0
        self.offset_top = 3
        self.offset_left = 5
        self.items = items

    def __move(self, key):
        if key == curses.KEY_UP:
            self.position -= 1
        elif key == curses.KEY_DOWN:
            self.position += 1
        else:
            raise Exception(f"wrong key: {key}")

        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def __setup(self):
        self.panel.top()
        self.panel.show()
        self.window.clear()

    def __terminate(self):
        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    def __restore_shell(self):
        self.window.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def loop(self):
        self.__setup()

        while True:
            self.window.refresh()
            self.window.border(0)
            curses.doupdate()

            for index, item in enumerate(self.items):
                match index:
                    case self.position:
                        mode = curses.A_REVERSE
                    case _:
                        mode = curses.A_NORMAL

                entry, _ = item

                self.window.addstr(
                    self.offset_top + index,
                    self.offset_left,
                    entry.name,
                    mode,
                )

            match self.window.getch():
                case curses.KEY_UP | curses.KEY_DOWN as key:
                    self.__move(key)
                case curses.KEY_ENTER | curses.KEY_NEWLINE:
                    self.__restore_shell()

                    if len(self.items) > 0 and self.position < len(self.items):
                        item, callback = self.items[self.position]
                        callback(item)
                    else:
                        break
                case curses.KEY_Q:
                    break
                case _:
                    pass

        self.__terminate()


class VirtTUI:
    def __init__(self, stdscreen, entries, callback):
        self.screen = stdscreen
        curses.use_default_colors()
        curses.curs_set(0)

        curses.KEY_Q = ord("q")
        curses.KEY_NEWLINE = ord("\n")

        menu_items = [(obj, callback) for obj in entries]

        if len(menu_items) > 0:
            main_menu = Menu(menu_items, self.screen)
            main_menu.loop()


def menu(entries, callback):
    curses.wrapper(VirtTUI, sorted(entries), callback)
