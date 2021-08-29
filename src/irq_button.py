import utime
from machine import Pin

class IrqButton:
    """
    A button class that triggers an IRQ on press and debounce for a given interval.
    """
    def __init__(self, pin, callback, debounce_interval=300):
        """
        Parameters
        ---------------

        pin: Pin
            Speficy the pin object connected to the button.
        callback: Function
            The callback function when the button is pressed.
        debounce_interval: int
            Specify the debounce interval in milliseconds. The same button
            will not be triggered in this interval after triggered.

            Strictly speaking, this behavior is not "debouncing".
            For a series of press events occured in the interval,
            the callback will be called for the first event only.

            (A real debouncing should trigger the callback for the last event.)
        """
        self.button = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.callback = callback
        self.debounce_interval = debounce_interval
        self.last_trigger_tick = 0
        self.button.irq(lambda pin: self._callback(pin), Pin.IRQ_RISING)

    def _callback(self, pin):
        if self.last_trigger_tick > 0:
            # debounce
            tick = utime.ticks_ms()
            if tick - self.last_trigger_tick < self.debounce_interval:
                return

        self.last_trigger_tick = utime.ticks_ms()
        self.callback(pin)
