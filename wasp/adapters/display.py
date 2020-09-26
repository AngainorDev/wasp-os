import st7789_lvgl


class Display:
    """Display wrapper"""

    def __init__(self, pmu):
        """Inits display"""
        # Init display
        tft = st7789_lvgl
        tft.lvgl_driver_init()
        self.tft = tft
        self.pmu = pmu
        """
        self.set_backlight_level(0)  # Turn backlight off
        self.backlight_level = 0
        self.bl_pin = Pin(12, Pin.OUT)
        self.backlight(1)  # Enable power on backlight
        """

    """
    def backlight_fade(self, val=100):
        if val > self.backlight_level:
            data = 0
            for i in range(self.backlight_level, val):
                data = i
                self.set_backlight_level(i)
            self.backlight_level = data
            return True
        elif val < self.backlight_level:
            data = 0
            for i in reversed(range(val, self.backlight_level)):
                data = i
                self.set_backlight_level(i)
            self.backlight_level = data
            return True

    def switch_scene(self):
        level = self.backlight_level
        self.backlight_fade(0)
        self.backlight_fade(level)

    def set_backlight_level(self, percent):
        if 0 <= percent <= 100:
            voltage = 800 * percent / 100
            self.__set_lcd_backlight_voltage__(2400 + voltage)
            self.backlight_level = percent
    """

    def display_off(self):
        self.tft.st7789_send_cmd(0x10)

    def display_sleep(self):
        self.tft.st7789_send_cmd(0x10)

    def display_wakeup(self):
        self.tft.st7789_send_cmd(0x11)

    """
    def backlight(self, val):
        self.bl_pin.value(val)
        self.__turn_lcd_backlight__(val)

    def __turn_lcd_backlight__(self, val):
        if val == 1:
            if 'setPowerOutPut' in self.pmu.__dict__:
                self.pmu.setPowerOutPut(axp202.AXP202_LDO2, True)
            else:
                self.pmu.enablePower(axp202.AXP202_LDO2)
        else:
            if 'setPowerOutPut' in self.pmu.__dict__:
                self.pmu.setPowerOutPut(axp202.AXP202_LDO2, False)
            else:
                self.pmu.disablePower(axp202.AXP202_LDO2)

    def __set_lcd_backlight_voltage__(self, voltage=3200):
        if voltage >= 3200:
            self.pmu.setLDO2Voltage(3200)
        elif voltage <= 2400:
            self.pmu.setLDO2Voltage(2400)
        else:
            self.pmu.setLDO2Voltage(voltage)
    """


