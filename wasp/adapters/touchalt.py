from machine import Pin
from adapters import moosegesture
import logging


class TouchAlt:
    def __init__(self, focal_touch, pin_int, callback=None):
        self.focal_touch = focal_touch
        self.pin_int = pin_int
        self.points = []
        self.callback = callback
        self.log = logging.getLogger('Touch')
        self.log.setLevel(logging.DEBUG)
        # No need, we get events via lvgl
        # self.pin_int.irq(trigger=Pin.IRQ_RISING, handler=self.touch)

    def feedback_cb(self, drv, event):
        # fed from lvgl. see lv.EVENT.xx constants
        self.log.debug("feedback_cb {} {}".format(event, drv))

    def touch(self, pin):
        # No more used
        self.log.debug("Touch event")
        self.log.debug("gid {}".format(self.focal_touch.get_gesture_id()))
        """
        fingers = self.focal_touch.touched
        self.log.debug("Fingers: "+str(fingers))
        if fingers == 1:
            point = self.focal_touch.touches[0]
            self._add_point(point['x'], point['y'])
        elif fingers == 0:
            if len(self.points)>0:
                self.gesture()
            self.reset_touch_data()
        """

    def _add_point(self, x, y):
        self.log.debug("add point: " + str(x)+' '+str(y))
        self.points.append((x, y))

    def gesture(self):
        from wasp import EventType
        gesture = moosegesture.getGesture(self.points)
        gesture_detect = None
        if len(gesture) == 1:
            gesture = gesture[0]
            if gesture == 'U':
                gesture_detect = EventType.UP
            elif gesture == 'D':
                gesture_detect = EventType.DOWN
            elif gesture == 'R':
                gesture_detect = EventType.RIGHT
            elif gesture == 'L':
                gesture_detect = EventType.LEFT
        elif len(gesture) == 0:
            gesture_detect = EventType.TOUCH

        if gesture_detect and self.callback:
            self.callback((gesture_detect, self.points[-1][0], self.points[-1][1]))

    def reset_touch_data(self):
        self.points.clear()
