# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Digital clock
~~~~~~~~~~~~~~~~

Shows a time (as HH:MM) together with a battery meter and the date.
"""

from wasp import system as wasp

import icons
import fonts.clock as digits
from widgets import BatteryMeter

import lvgl as lv

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'


class LClockApp():
    """Simple digital clock application.
    """
    NAME = 'Clock'
    ICON = icons.clock

    def __init__(self):
        super().__init__()
        # self.meter = BatteryMeter()
        self.win = lv.win(wasp.watch.tile_view)
        self.win.set_title("LVGL Clock")
        self.label_h = lv.label(lv.btn(self.win))
        self.label_h.set_text("H")
        btn_m = lv.btn(self.win)
        self.label_m = lv.label(btn_m)
        btn_m.set_y(70)
        self.label_m.set_text("M")
        btn_s = lv.btn(self.win)
        self.label_s = lv.label(btn_s)
        btn_s.set_y(130)
        self.label_s.set_text("S")                
        # self.notifier = wasp.widgets.StatusBar()
        self.on_screen = None
        self.lv_main = self.win

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.request_tick(1000)
        wasp.watch.backlight.set(wasp._brightness)

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.update()

    def draw(self):
        """Redraw the display from scratch."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.update()
        # self.meter.draw()

    def update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """
        now = wasp.watch.rtc.get_localtime()
        #now = wasp.watch.ttgowatch.rtc.datetime()
        print("lclock", now)

        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]
        #d raw.string('{} {} {}'.format(now[2], month, now[0]), 0, 180, width=240)
        # self.label.set_text('{} {} {}'.format(now[2], month, now[0]))
        if now[3] != self.on_screen[3]:
            self.label_h.set_text('{}'.format(now[3]))
        if now[4] != self.on_screen[4]:
            self.label_m.set_text('{}'.format(now[4]))
        self.label_s.set_text('{}'.format(now[5]))
        # lv.scr_load(self.scr)  # unneeded?
        # wasp.watch.backlight.set(wasp._brightness)
        self.on_screen = now

        # self.meter.update()
        # self.notifier.update()
        return True
