import utime
from machine import RTC

class RtcClock:

    """
    An adjustable clock based on the rp2040 RTC.
    """

    # clock mode
    MODE_NORMAL = 0
    MODE_SET_HOUR = 1
    MODE_SET_MINUTE = 2
    
    def __init__(self):
        self.rtc = RTC()
        self.initial_ticks = 0
        self.mode = RtcClock.MODE_NORMAL
        self.set_hour = 0
        self.set_minute = 0
    
    def calibrate(self):
        """Adjust the sub-second counter accoring to the RTC.
        """
        second = self.rtc.datetime()[6]
        while True:
            new_second = self.rtc.datetime()[6]
            if new_second == second:
                utime.sleep_ms(1)
            else:
                self.initial_ticks = utime.ticks_ms()
                break
    
    def datetime(self):
        """
        Get the current time.

        Since rp2040 RTC does not return subseconds by default, this method uses `utime.ticks_ms()` to provide milliseconds.
        Before calling `datetime()`, `calibrate()` must be called to make sure the millisecond value is accurate.
        """
        (years, months, days, weekdays, hours, minutes, seconds, _) = self.rtc.datetime()
        subseconds = (utime.ticks_ms() - self.initial_ticks) % 1000
        
        if self.mode == RtcClock.MODE_NORMAL:
            return (years, months, days, weekdays, hours, minutes, seconds, subseconds)
        else:
            # if in SET mode, return set_horu and set_minute instead, to prevent the hours and minutes change during SET process.
            return (years, months, days, weekdays, self.set_hour, self.set_minute, 0, subseconds)
        
    def switch_mode(self):
        """
        Switch the clock mode.

        Calling this method will switch the clock from NORMAL -> SET_HOUR -> SET_MINUTE -> NORMAL...
        """
        if self.mode == RtcClock.MODE_NORMAL:
            self.mode = RtcClock.MODE_SET_HOUR

            # When entering SET mode, copy the current hours and minutes to `set_hour` and `set_minute` for adjustment
            current_time = self.rtc.datetime()
            self.set_hour = current_time[4]
            self.set_minute = current_time[5]
        elif self.mode == RtcClock.MODE_SET_HOUR:
            self.mode = RtcClock.MODE_SET_MINUTE
        else:
            self.mode = RtcClock.MODE_NORMAL

            # When leaving SET mode, set the RTC using the adjusted time
            current_time = list(self.rtc.datetime())
            current_time[4] = self.set_hour
            current_time[5] = self.set_minute
            current_time[6] = 0
            self.rtc.datetime(current_time)
            self.initial_ticks = utime.ticks_ms()
            
    def set_inc(self):
        """
        Increase hour or minute in SET mode.
        Call this in SET mode to advance the hour or minute.
        """
        if self.mode == RtcClock.MODE_SET_HOUR:
            self.set_hour += 1
            if self.set_hour == 24:
                self.set_hour = 0
        elif self.mode == RtcClock.MODE_SET_MINUTE:
            self.set_minute += 1
            if self.set_minute == 60:
                self.set_minute = 0
        
