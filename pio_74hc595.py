from rp2 import asm_pio, StateMachine, PIO

@asm_pio(
    out_shiftdir=PIO.SHIFT_RIGHT,
    out_init=(PIO.OUT_LOW),
    sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW),
    autopull=True,
)
def pio_74hc595():
    pull()                          # pul the number of bits
    mov(y, osr)                     # load the nubmer of bits to Y

    wrap_target()
    mov(x, y)                       # set X to loop counter
    
    label('loop')                   # loop for DATA pin
    out(pins, 1)      .side(0b00)   # send 1 bit to DATA pin / set SHIFT pin low
    jmp(x_dec, 'loop').side(0b01)   # if not all bits sent, then loop / set SHIFT pin high to trigger the shift

    pull()            .side(0b10)   # row completed, manual pull to discard unused data / set LATCH pin high
    wrap()



class PIO_74HC595:
    """
    A class that controls 74HC595 using PIO.
    """
    def __init__(self, out_base, sideset_base, freq, daisy_chain=4):
        self.sm = StateMachine(
            0,
            pio_74hc595,
            out_base=out_base,
            sideset_base=sideset_base,
            freq=freq
        )
        
        # put the number of bits into OSR so that it can be loaded to Y when SM starts
        self.sm.put(daisy_chain * 8 - 1)
    
    def start(self):
        self.sm.active(1)
        
    def stop(self):
        self.sm.active(0)
        
    def put(self, data):
        self.sm.put(data)


