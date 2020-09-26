# SPDX-License-Identifier: LGPL-3.0-or-later

"""Binary Clock for the geek
**not** lvgl converted
"""

from wasp import system as wasp

import icons
import fonts.clock as digits
from widgets import BatteryMeter

DIGITS = (
        digits.clock_0,
        digits.clock_1,
        digits.clock_2,
        digits.clock_3,
        digits.clock_4,
        digits.clock_5,
        digits.clock_6,
        digits.clock_7,
        digits.clock_8,
        digits.clock_9
)

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'


class BinClockApp():
    """Simple digital clock application.
    """
    NAME = 'BinClock'
    ICON = icons.clock

    def __init__(self):
        super().__init__()
        self.meter = BatteryMeter()

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.request_tick(1000)

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.update()

    def draw(self):
        """Redraw the display from scratch."""
        draw = wasp.watch.drawable
        draw.fill()
        # draw.rleblit(digits.clock_colon, pos=(2*48, 80), fg=0xb5b6)
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.update()
        self.meter.draw()
        
    def bin_draw(self, ccolor, draw, digit, offset):    
        color = ccolor if digit & 1 else 0x2104
        draw.fill(color,offset+4,4*45+5+5,24,24)
        color = ccolor if digit & 2 else 0x2104
        draw.fill(color,offset+4,3*45+5+5,24,24)
        color = ccolor if digit & 4 else 0x2104
        draw.fill(color,offset+4,2*45+5+5,24,24)
        color = ccolor if digit & 8 else 0x2104
        draw.fill(color,offset+4,1*45+5+5,24,24)

    def bin_draw_small(self, ccolor, draw, digit, offset):    
        color = ccolor if digit & 1 else 0x2104
        draw.fill(color,offset+4,4*45+5+4+5,16,16)
        color = ccolor if digit & 2 else 0x2104
        draw.fill(color,offset+4,3*45+5+4+5,16,16)
        color = ccolor if digit & 4 else 0x2104
        draw.fill(color,offset+4,2*45+5+4+5,16,16)
        color = ccolor if digit & 8 else 0x2104
        draw.fill(color,offset+4,1*45+5+4+5,16,16)

    def update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """
        now = wasp.watch.rtc.get_localtime()
        # print("bin")
        #if now[3] == self.on_screen[3] and now[4] == self.on_screen[4]:
        if now[5] != self.on_screen[5]:
            self.meter.update()
        else:
            return False

        draw = wasp.watch.drawable
        if now[3] != self.on_screen[3]:
            digit = now[3] //10
            self.bin_draw(0x075F, draw, digit, 0)
            digit = now[3] % 10
            self.bin_draw(0x075F, draw, digit, 48)
        if now[4] != self.on_screen[4]:
            digit = now[4] //10
            self.bin_draw(0x1FE0, draw, digit, 2*48+5)
            digit = now[4] % 10
            self.bin_draw(0x1FE0, draw, digit, 3*48+5)
        if now[5] != self.on_screen[5]:
            digit = now[5] //10
            self.bin_draw_small(0xFB60, draw, digit, 4*48+5+2-8)
            digit = now[5] % 10
            self.bin_draw_small(0xFB60, draw, digit, 5*48-4-2-16)
        
        
        """
        draw.rleblit(DIGITS[now[4]  % 10], pos=(4*48, 80))
        draw.rleblit(DIGITS[now[4] // 10], pos=(3*48, 80), fg=0xbdb6)
        draw.rleblit(DIGITS[now[3]  % 10], pos=(1*48, 80))
        draw.rleblit(DIGITS[now[3] // 10], pos=(0*48, 80), fg=0xbdb6)
        """
        self.on_screen = now

        """ month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]
        draw.string('{} {} {}'.format(now[2], month, now[0]),
                0, 240, width=240)
        """
        self.meter.update()
        return True
