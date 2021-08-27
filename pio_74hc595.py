from rp2 import asm_pio, StateMachine, PIO

@asm_pio(
    out_shiftdir=PIO.SHIFT_RIGHT,
    out_init=(PIO.OUT_LOW),
    sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW),
    autopull=True,
)
def pio_74hc595():
    pull()
    mov(y, osr)                   # load loop counter to Y
    wrap_target()
    mov(x, y)         .side(0b10) # set X to loop counter
    
    label('loop')                 # main loop
    out(pins, 1)      .side(0b00) # shift 1 bit from OSR to the first out pin
                                  # drive SCLK pin low
    jmp(x_dec, 'loop').side(0b01) # branch to loop if X is not zero, decrement X
                                  # drive SCLK pin high
    wrap()



class PIO_74HC595:
    def __init__(self, out_base, sideset_base, freq, daisy_chain=4):
        self.sm = StateMachine(
            0,
            pio_74hc595,
            out_base=out_base,
            sideset_base=sideset_base,
            freq=freq
        )
        
        # put the loop counter into OSR so that it can be loaded to Y when SM starts
        self.sm.put(daisy_chain * 8 - 1)
    
    def start(self):
        self.sm.active(1)
        
    def stop(self):
        self.sm.active(0)
        
    def put(self, data):
        self.sm.put(data)



