import utime
from machine import Pin
from irq_button import IrqButton
from led_matrix_74hc595 import LedMatrix
from bitmap_font_4x7 import BitmapFont4x7
from rtc_clock import RtcClock

led_matrix = LedMatrix(
    rows=8, cols=24, data_pin=Pin(4), shift_pin=Pin(2),
    layout=(
        LedMatrix.ROW | LedMatrix.ACTIVE_LOW | LedMatrix.A2H,
        LedMatrix.COLUMN | LedMatrix.ACTIVE_HIGH | LedMatrix.H2A,
    )
)
led_matrix.start()

font = BitmapFont4x7()

def draw(hour, minute, flash_on=False, set_mode=0):
    
    n0 = minute % 10
    n1 = (minute // 10) % 10
    n2 = hour % 10
    n3 = (hour // 10) % 10
    
    led_matrix.clear()
    
    # draw minutes
    if flash_on or set_mode != RtcClock.MODE_SET_MINUTE:
        led_matrix.blit(font.get_fbuf(chr(0x30+n0)), 17, 0)
        led_matrix.blit(font.get_fbuf(chr(0x30+n1)), 12, 0)

    # draw hours
    if flash_on or set_mode != RtcClock.MODE_SET_HOUR:
        led_matrix.blit(font.get_fbuf(chr(0x30+n2)), 5, 0)
        led_matrix.blit(font.get_fbuf(chr(0x30+n3)), 0, 0)
    
    # draw colon
    if flash_on or set_mode != RtcClock.MODE_NORMAL:
        led_matrix.blit(font.get_fbuf(':'), 8, 0)


clock = RtcClock()
clock.calibrate()

# setup buttons
IrqButton(17, lambda x: clock.switch_mode())
IrqButton(16, lambda x: clock.set_inc())


try:
    while True:
        (_, _, _, _, hours, minutes, seconds, subseconds) = clock.datetime()
        flash_on = subseconds < 500

        draw(hours, minutes, flash_on, clock.mode)
        led_matrix.draw()
        utime.sleep_ms(2)
            
except KeyboardInterrupt:
    pass
finally:
    led_matrix.stop()

