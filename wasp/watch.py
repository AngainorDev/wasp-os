from machine import I2C, SPI, Pin
import draw565
from drivers import axp202c as axp202
#from drivers.focaltouch import FocalTouch
import ft6x36
#from drivers.st7789 import ST7789_SPI
from adapters.touchalt import TouchAlt
from adapters.vibrator import Vibrator
from adapters.backlight import Backlight
from adapters.battery import Battery
from adapters.rtc import RTC
from adapters.display import Display

import lvgl as lv
import st7789_lvgl


class Watch:

    def __init__(self, touch_callback=None):

        self.i2c0 = I2C(1, scl=Pin(22), sda=Pin(21))
        # self.i2c1 = I2C(1,scl=Pin(32), sda=Pin(23))
        self.axp = self.init_axp(self.i2c0)
        self.backlight = Backlight(self.axp)
        self.vibrator = self.init_vibrator()
        self.ir = self.init_ir()

        """
        self.display = self.init_display()
        self.drawable = draw565.Draw565(self.display)
        self.drawable.reset()
        self.drawable.string("booting", 10, 10)
        """
        # To be renamed to display, temporarily changed to avoid collisions and harmonise interface
        self.tft = Display(self.axp)
        # We need this for lvgl
        self.touch = self._init_touch(touch_callback)
        # Init lvgl
        self.scr = None
        self.tile_view = None
        self.lvgl_ticker = None
        self.init_lvgl()
        self.backlight.set(30)
        self.boot_screen()
        self.init_tile_view()
        self.rtc = RTC(self.i2c0)
        self.battery = Battery(self.axp)
        # self.accel = BMA421(self.i2c1)

    def init_lvgl(self):
        import lvesp32
        self.lvgl_ticker = lvesp32
        lv.init()
        disp_buf1 = st7789_lvgl.lv_disp_buf_t()
        buf1_1 = bytes(240 * 100)  # Could be smaller but we have some space on esp32
        disp_buf1.init(buf1_1, None, len(buf1_1) // 4)
        disp_drv = st7789_lvgl.lv_disp_drv_t()
        disp_drv.init()
        disp_drv.buffer = disp_buf1
        disp_drv.flush_cb = st7789_lvgl.driver_flush
        disp_drv.hor_res = 240
        disp_drv.ver_res = 240
        disp_drv.register()
        # Now the touch
        indev_drv = self.touch.focal_touch.lv_indev_drv_t()
        indev_drv.init()
        indev_drv.type = lv.INDEV_TYPE.POINTER
        indev_drv.read_cb = self.touch.focal_touch.touch_driver_read
        indev_drv.feedback_cb = self.touch.feedback_cb
        indev_drv.register()

    def boot_screen(self):
        scr = lv.obj()
        win = lv.win(scr)
        win.set_title("LVGL - Booting...")
        self.scr = scr
        lv.scr_load(self.scr)

    def init_tile_view(self):
        scr = lv.obj()
        tv = lv.tileview(scr)
        tv.set_edge_flash(True)
        self.tile_view = tv
        """
        # Attempt to get tileview recognizing gestures, did not work.
        scr.set_gesture_parent(False)
        tv.set_gesture_parent(False)
        """
        self.scr = scr

    def init_axp(self, bus):
        axp = axp202.PMU(bus)
        # change power off time to 4s?
        # Turn off the charging instructions
        axp.setChgLEDMode(axp202.AXP20X_LED_OFF)
        # Turn off external enable
        axp.disablePower(axp202.AXP202_EXTEN)
        axp.enablePower(axp202.AXP202_LDO2)
        axp.enablePower(axp202.AXP202_DCDC3)
        axp.clearIRQ()
        return axp

    def init_ir(self):
        ir = Pin(13, Pin.OUT)
        ir.off()
        return ir

    def init_vibrator(self):
        vibrator = Vibrator(Pin(4, Pin.OUT))
        return vibrator

    """
    def init_display(self):
        
        spi = SPI(2, baudrate=32000000, polarity=1, phase=0, bits=8, firstbit=0, sck=Pin(18,Pin.OUT),mosi=Pin(19,Pin.OUT))
        spi.init()
        display = ST7789_SPI(240, 240, spi,
                             cs=Pin(5,Pin.OUT),dc=Pin(27,Pin.OUT))
        display.rotate(0)
        display.fill(0)
        return display
    """

    def _init_touch(self, touch_callback):
        """
        ft = FocalTouch(i2c)
        return Touch(ft, Pin(38, Pin.IN), touch_callback)
        """
        ft6x36.lvgl_touch_init()
        return TouchAlt(ft6x36, Pin(38, Pin.IN), touch_callback)
