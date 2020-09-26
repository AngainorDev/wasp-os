# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Wasp-os system manager
~~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: wasp.system

    wasp.system is the system-wide singleton instance of :py:class:`.Manager`.
    Application must use this instance to access the system adapters provided
    by the manager.

.. data:: wasp.watch

    wasp.watch is an import of :py:mod:`watch` and is simply provided as a
    shortcut (and to reduce memory by keeping it out of other namespaces).
"""

import gc
import machine
import sys

from adapters.app import App
from adapters.wifi import Wifi
import watch
import uasyncio as asyncio

#from apps.flashlight import FlashlightApp
#from apps.heart import HeartApp
from apps.launcher import LauncherApp
from apps.pager import NotificationApp

import logging
logging.basicConfig(level=logging.DEBUG)

import lvgl as lv


class EventType():
    """Enumerated interface actions.

    MicroPython does not implement the enum module so EventType
    is simply a regular object which acts as a namespace.
    """
    DOWN = 1
    UP = 2
    LEFT = 3
    RIGHT = 4
    TOUCH = 5

    HOME = 256
    BACK = 257


class EventMask():
    """Enumerated event masks.
    """
    TOUCH = 0x0001
    SWIPE_LEFTRIGHT = 0x0002
    SWIPE_UPDOWN = 0x0004
    BUTTON = 0x0008

class Manager():
    """Wasp-os system manager

    The manager is responsible for handling top-level UI events and
    dispatching them to the foreground application. It also provides
    adapters to the application.

    The manager is expected to have a single system-wide instance
    which can be accessed via :py:data:`wasp.system` .
    """

    def __init__(self):
        self.app = None

        self.quick_ring = []
        self.launcher = App(LauncherApp())
        self.launcher_ring = []
        self.notifier = App(NotificationApp())
        self.notifications = {}

        self.blank_after = 15

        self._brightness = 2
        self._charging = True
        self._scheduled = False
        self._scheduling = False
        self.watch = watch.Watch(self._handle_touch)
        self.log = logging.getLogger('wasp')
        self.network_service = Wifi()
        self.event_mask = 0
        self.awake = asyncio.Event()
        self.tv_apps = []

    def init_apps(self):
        from apps.settings import SettingsApp
        #from apps.binclock import BinClockApp
        from apps.clock import ClockApp
        from apps.lclock import LClockApp
        from apps.lvoid import LVoidApp
        #from apps.flashlight import FlashlightApp
        # from apps.steps import StepCounterApp
        #from apps.stopwatch import StopwatchApp
        #from apps.testapp import TestApp

        #self.register(BinClockApp(), True)
        #self.register(LClockApp(), True)
        #self.register(StepCounterApp(), True)
        #self.register(StopwatchApp(), True)
        #self.register(HeartApp(), True)

        #self.register(FlashlightApp(), False)
        #self.register(SettingsApp(), False)
        #self.register(TestApp(), False)

        self.tv_apps = [[None]*2 for row in range(2)]
        valid_pos = [{'x': 0, 'y': 0}, {'x': 1, 'y': 0}, {'x': 0, 'y': 1}, {'x': 1, 'y': 1}]
        self.watch.tile_view.set_valid_positions(valid_pos, 4)

        self.tv_register(LClockApp(), 0, 0)
        self.tv_register(LVoidApp('0,1'), 0, 1)
        self.tv_register(LVoidApp('1,0'), 1, 0)
        self.tv_register(LVoidApp('1,1'), 1, 1)

        self.watch.tile_view.set_event_cb(self.tv_event)

    def tv_event(self, item, event):
        print("tvevent", item, ":", event)

    def register(self, app, quick_ring=False):
        """Register an application with the system.

        :param object app: The application to register
        """
        if quick_ring is True:
            self.quick_ring.append(App(app))
        else:
            self.launcher_ring.append(App(app))
            self.launcher_ring.sort(key=lambda x: x.NAME)

    def tv_register(self, app, row=0, col=0):
        """Register an app in the tile_view"""
        self.tv_apps[row][col] = App(app)
        try:
            self.watch.tile_view.add_element(app.lv_main)
        except Exception as e:
            print("add_element", e)
        # todo: handle padding via styles instead
        app.lv_main.set_size(220, 220)
        app.lv_main.set_pos(row * 240 + 10, col * 240 + 10)
        if 'set_scroll_propagation' in dir(app.lv_main):
            app.lv_main.set_scroll_propagation(True)

    @property
    def brightness(self):
        """Cached copy of the brightness current written to the hardware."""
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        self.watch.backlight.set(value)

    def lv_switch(self, row, col):
        app = self.tv_apps[row][col]
        if app is None:
            print("None", row, col)
        if self.app:
            if 'background' in dir(self.app):
                self.app.background()
        else:
            # System start up...
            self.watch.tft.display_wakeup()
            self.watch.backlight.set(self._brightness)

        # Clear out any configuration from the old application
        self.event_mask = 0
        self.app = app
        app.foreground()

    def switch(self, app):
        """Switch to the requested application.
        """
        if self.app:
            if 'background' in dir(self.app):
                self.app.background()
        else:
            # System start up...
            #self.watch.display.poweron()
            #self.watch.display.mute(True)
            self.watch.backlight.set(self._brightness)
            # self.watch.tft.backlight_fade(self._brightness)

        # Clear out any configuration from the old application
        self.event_mask = 0

        self.app = app
        #self.watch.display.mute(True)
        #self.watch.drawable.reset()
        #self.watch.lv.scr_load(app.scr)
        app.foreground()
        #self.watch.display.mute(False)

    def navigate(self, direction=None):
        """Navigate to a new application.

        Left/right navigation is used to switch between applications in the
        quick application ring. Applications on the ring are not permitted
        to subscribe to :py:data`EventMask.SWIPE_LEFTRIGHT` events.

        Swipe up is used to bring up the launcher. Clock applications are not
        permitted to subscribe to :py:data`EventMask.SWIPE_UPDOWN` events since
        they should expect to be the default application (and is important that
        we can trigger the launcher from the default application).

        :param int direction: The direction of the navigation
        """
        app_list = self.quick_ring

        if direction == EventType.LEFT:
            if self.app in app_list:
                i = app_list.index(self.app) + 1
                if i >= len(app_list):
                    i = 0
            else:
                i = 0
            self.switch(app_list[i])
        elif direction == EventType.RIGHT:
            if self.app in app_list:
                i = app_list.index(self.app) - 1
                if i < 0:
                    i = len(app_list)-1
            else:
                i = 0
            self.switch(app_list[i])
        elif direction == EventType.UP:
            self.switch(self.launcher)
        elif direction == EventType.DOWN:
            if self.app != app_list[0]:
                self.switch(app_list[0])
            else:
                if len(self.notifications):
                    self.switch(self.notifier)
                else:
                    # Nothing to notify... we must handle that here
                    # otherwise the display will flicker.
                    self.watch.vibrator.pulse()

        elif direction == EventType.HOME or direction == EventType.BACK:
            if self.app != app_list[0]:
                self.switch(app_list[0])
            else:
                self.pms.keep_awake(False)

    def notify(self, id, msg):
        self.notifications[id] = msg

    def unnotify(self, id):
        if id in self.notifications:
            del self.notifications[id]

    def request_event(self, event_mask):
        """Subscribe to events.

        :param int event_mask: The set of events to subscribe to.
        """
        self.event_mask |= event_mask

    def request_tick(self, period_ms=None):
        """Request (and subscribe to) a periodic tick event.
        Note: With the current simplistic timer implementation sub-second
        tick intervals are not possible.
        """
        self.app._fg_period = period_ms

    async def on_net(self):
        self.watch.rtc.sync_time()
        await asyncio.sleep(1)

    def sleep(self):
        """Enter the deepest sleep state possible.
        """
        self.awake.clear()
        self.log.debug("Sleep")
        self.watch.backlight.set(0)
        self.app.background()
        self.watch.tft.display_sleep()
        # self.watch.touch.sleep() # Todo?
        self.network_service.sleep()
        self._charging = self.watch.axp.isChargeing()

    async def wake(self, by_user):
        """Return to a running state.
        """
        self.log.debug("wake: "+str(by_user))
        if by_user:
            self.awake.set()
            self.watch.tft.display_wakeup()
            self.watch.backlight.set(self._brightness)
            self.app.foreground()
            # self.watch.touch.wake()  # Todo?
        else:
            await self.connect()

    async def connect(self):
        await self.network_service.wake()
        if self.network_service.isconnected():
            await self.on_net()
        self.network_service.sleep()

    def handle_button(self, state):
        """Process a button-press (or unpress) event.
        """
        print("handle")
        self.log.debug("handle_button")
        self.keep_awake()
        if not self.awake.is_set():
            asyncio.create_task(self.wake(by_user=True))
            return

        if bool(self.event_mask & EventMask.BUTTON):
            # Currently we only support one button
            if not self.app.press(EventType.HOME, state):
                # If app reported None or False then we are done
                return

        if state:
            self.navigate(EventType.HOME)

    def keep_awake(self):
        self.pms.keep_awake()
        pass

    def _handle_touch(self, event):
        """Process a touch event.
        """
        self.keep_awake()

        event_mask = self.event_mask
        if event[0] < 5:
            updown = event[0] == 1 or event[0] == 2
            if (bool(event_mask & EventMask.SWIPE_UPDOWN) and updown) or \
               (bool(event_mask & EventMask.SWIPE_LEFTRIGHT) and not updown):
                if self.app.swipe(event):
                    self.navigate(event[0])
            else:
                self.navigate(event[0])
        elif event[0] == 5 and self.event_mask & EventMask.TOUCH:
            self.app.touch(event)
        self.watch.touch.reset_touch_data()

    def run(self, no_except=True):

        try:
            asyncio.run(self.main_loop())
        except Exception as e:
            with open("reset_reason.txt", "w") as f:
                f.write(str(e))
            sys.print_exception(e)
            machine.reset()

    async def main_loop(self):
        from adapters.power_management_service import PMS
        self.pms = PMS(self.blank_after)
        self.init_apps()
        if not self.app:
            lv.scr_load(self.watch.scr)
            self.lv_switch(0,0)
            #self.switch(self.quick_ring[0])
        #asyncio.create_task(self.connect())
        self.pms.init()
        self.keep_awake()
        while True:
            gc.collect()
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
            print("free", gc.mem_free(), "alloc", gc.mem_alloc())
            await asyncio.sleep(5)


system = Manager()
