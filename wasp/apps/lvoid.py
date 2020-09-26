# SPDX-License-Identifier: LGPL-3.0-or-later
"""Empty demo app
"""

from wasp import system as wasp

import icons

import lvgl as lv


class LVoidApp():
    """Demo app
    """
    NAME = 'Void'
    ICON = icons.clock

    def __init__(self, title):
        super().__init__()
        self.cont = lv.cont(wasp.watch.tile_view)
        # self.win.set_title(title)
        # self.title = title
        btn = lv.btn(self.cont)
        btn.set_y(10)
        btn.set_x(10)
        # So the button can be used to swipe
        wasp.watch.tile_view.add_element(btn)
        self.label_h = lv.label(btn)
        self.label_h.set_text(title)

        btn2 = lv.btn(self.cont)
        btn2.set_y(100)
        btn2.set_x(10)
        # So the button can be used to swipe
        wasp.watch.tile_view.add_element(btn2)
        self.label_h2 = lv.label(btn2)
        self.label_h2.set_text(title)

        self.lv_main = self.cont
        self.count = 1

    def foreground(self):
        """Activate the application."""
        self.draw()
        wasp.request_tick(1000)
        wasp.watch.backlight.set(wasp._brightness)

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.count +=1
        if self.count > 255:
            self.count = 0
        self.update()

    def draw(self):
        """Redraw the display from scratch."""
        self.update()

    def update(self):
        """Update the display (if needed).
        """
        self.label_h2.set_text(str(self.count))
        print("void", self.title, self.count)
        return True
