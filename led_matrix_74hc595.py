import math
import framebuf
from pio_74hc595 import PIO_74HC595


reverse_lookup = bytes((
    0x00, 0x80, 0x40, 0xc0, 0x20, 0xa0, 0x60, 0xe0, 0x10, 0x90, 0x50, 0xd0, 0x30, 0xb0, 0x70, 0xf0,
    0x08, 0x88, 0x48, 0xc8, 0x28, 0xa8, 0x68, 0xe8, 0x18, 0x98, 0x58, 0xd8, 0x38, 0xb8, 0x78, 0xf8,
    0x04, 0x84, 0x44, 0xc4, 0x24, 0xa4, 0x64, 0xe4, 0x14, 0x94, 0x54, 0xd4, 0x34, 0xb4, 0x74, 0xf4,
    0x0c, 0x8c, 0x4c, 0xcc, 0x2c, 0xac, 0x6c, 0xec, 0x1c, 0x9c, 0x5c, 0xdc, 0x3c, 0xbc, 0x7c, 0xfc,
    0x02, 0x82, 0x42, 0xc2, 0x22, 0xa2, 0x62, 0xe2, 0x12, 0x92, 0x52, 0xd2, 0x32, 0xb2, 0x72, 0xf2,
    0x0a, 0x8a, 0x4a, 0xca, 0x2a, 0xaa, 0x6a, 0xea, 0x1a, 0x9a, 0x5a, 0xda, 0x3a, 0xba, 0x7a, 0xfa,
    0x06, 0x86, 0x46, 0xc6, 0x26, 0xa6, 0x66, 0xe6, 0x16, 0x96, 0x56, 0xd6, 0x36, 0xb6, 0x76, 0xf6,
    0x0e, 0x8e, 0x4e, 0xce, 0x2e, 0xae, 0x6e, 0xee, 0x1e, 0x9e, 0x5e, 0xde, 0x3e, 0xbe, 0x7e, 0xfe,
    0x01, 0x81, 0x41, 0xc1, 0x21, 0xa1, 0x61, 0xe1, 0x11, 0x91, 0x51, 0xd1, 0x31, 0xb1, 0x71, 0xf1,
    0x09, 0x89, 0x49, 0xc9, 0x29, 0xa9, 0x69, 0xe9, 0x19, 0x99, 0x59, 0xd9, 0x39, 0xb9, 0x79, 0xf9,
    0x05, 0x85, 0x45, 0xc5, 0x25, 0xa5, 0x65, 0xe5, 0x15, 0x95, 0x55, 0xd5, 0x35, 0xb5, 0x75, 0xf5,
    0x0d, 0x8d, 0x4d, 0xcd, 0x2d, 0xad, 0x6d, 0xed, 0x1d, 0x9d, 0x5d, 0xdd, 0x3d, 0xbd, 0x7d, 0xfd,
    0x03, 0x83, 0x43, 0xc3, 0x23, 0xa3, 0x63, 0xe3, 0x13, 0x93, 0x53, 0xd3, 0x33, 0xb3, 0x73, 0xf3,
    0x0b, 0x8b, 0x4b, 0xcb, 0x2b, 0xab, 0x6b, 0xeb, 0x1b, 0x9b, 0x5b, 0xdb, 0x3b, 0xbb, 0x7b, 0xfb,
    0x07, 0x87, 0x47, 0xc7, 0x27, 0xa7, 0x67, 0xe7, 0x17, 0x97, 0x57, 0xd7, 0x37, 0xb7, 0x77, 0xf7,
    0x0f, 0x8f, 0x4f, 0xcf, 0x2f, 0xaf, 0x6f, 0xef, 0x1f, 0x9f, 0x5f, 0xdf, 0x3f, 0xbf, 0x7f, 0xff,
))

class LedMatrix:
    
    # flags to indicate the matrix layout
    ROW = 0b0
    COLUMN = 0b1
    ACTIVE_LOW = 0b00
    ACTIVE_HIGH = 0b10
    A2H = 0b000
    H2A = 0b100
    
    
    def __init__(
        self,
        rows,
        cols,
        data_pin,
        shift_pin,
        layout=None
    ):
        """
        Parameters
        --------------

        rows: int
            Number of rows in the matrix.

        cols: int
            Number of columns in the matrix.

        data_pin: Pin
            Specify the data pin

        shift_pin: Pin
            Specify the shift pin. The latch pin must be the next pin.
            For example, if `shift_pin=Pin(3)`, then latch pin is automatically `Pin(4)`

        layout: 2-tuple of the combinations of the flags
            Specify the layout of the matrix.

            e.g. The deafult value is
                (ROW | ACTIVE_LOW | A2H, COLUMN | ACTIVE_HIGH | A2H)
            
            * ROW comes first, then COLUMN: 
              => Data is sent to the row register first, then daisy-chained to the column registers
            * rows are active-low, while columsn are active-high
            * rows are connected in the order of Q_A ~ Q_H, i.e. the top-most row is connected to Q_A of 74HC595,
              and the bottom-most row is connected to Q_H of 74HC595
              columns are in Q_A ~ Q_H too, i.e the left-most row is Q_A
        
        """
        if rows > 32:
            raise ValueError('Maximum 32 rows are supported.')
        
        if rows % 8:
            print('WARNING: Number of rows is not a multiple of 8. The first row should be connected to the Q_A of the first 74HC595.')
            
        if layout is None:
            layout = (
                LedMatrix.ROW | LedMatrix.ACTIVE_LOW | LedMatrix.A2H,
                LedMatrix.COLUMN | LedMatrix.ACTIVE_HIGH | LedMatrix.A2H,
            )
        
        self.rows = rows
        self.cols = cols
        self.row_bytes = math.ceil(rows / 8)
        self.col_bytes = math.ceil(cols / 8)
        self.layout = layout
        
        # byte array for storing the frame buffer
        self.buf = bytearray(self.rows * self.col_bytes)

        # FrameBuffer object for drawing methods
        self.fbuf = framebuf.FrameBuffer(self.buf, self.cols, self.rows, framebuf.MONO_HLSB)
        
        # Create the state machine. 30,000Hz is a proper frequency to produce a stable display.
        # Frequency greater than 80,000Hz will produce a flickering display.
        self.sm = PIO_74HC595(
            out_base=data_pin,
            sideset_base=shift_pin,
            freq=30_000,
            daisy_chain=self.row_bytes + self.col_bytes
        )
        
    def start(self):
        """
        Start the state machine.
        """
        self.sm.start()
        
    def stop(self):
        """
        Stop the state machine.
        """
        self.sm.stop()
        
    def draw(self):
        """
        Draw the frame buffer to the LED matrix.
        """

        # size of the data for one row
        data_size = self.row_bytes + self.col_bytes

        # since sm.put() function sends a 32-bit word a time, the row data needs to be padded to a multiple of 4
        padded_data_size = math.ceil(data_size / 4) * 4

        for i in range(self.rows):
            # row data
            data = bytearray(padded_data_size)
          
            # start byte of the row data, skip the left padding
            idx = padded_data_size - data_size
            
            # handle row/column corresponding to the layout
            for e in self.layout:

                # generate row data (row selector)
                if e & 1 == LedMatrix.ROW:
                    if e & 4 ==LedMatrix.A2H:
                        row_selector = 1 << (self.rows - i - 1)
                    else:
                        row_selector = 1 << i
                    if e & 2 == LedMatrix.ACTIVE_LOW:
                        row_selector = ~row_selector
                    
                    data[idx:idx + self.row_bytes] = row_selector.to_bytes(self.row_bytes, 'big')
                    idx += self.row_bytes
                        
                # generate column data
                if e & 1 == LedMatrix.COLUMN:
                    row_data = self.buf[self.col_bytes * i:self.col_bytes * (i+1)]
                    # reverse bits
                    if e & 4 == LedMatrix.H2A:
                        row_data = bytearray(reverse_lookup[c] for c in reversed(row_data))
                    
                    if e & 2 == LedMatrix.ACTIVE_LOW:
                        row_data = bytearray(~c for c in row_data)
                        
                    data[idx:idx + self.col_bytes] = row_data
                    idx += self.col_bytes
                    
            # send the row data to the state machine
            idx = padded_data_size
            while idx > 0:
                w = int.from_bytes(data[idx-4:idx], 'big')
                self.sm.put(w)
                idx -= 4
                
    def clear(self):
        self.fbuf.fill(0)
        
    def fill(self):
        self.fbuf.fill(1)
        
    def pixel(self, x, y, c=1):
        self.fbuf.pixel(x, y, c)
        
    def hline(self, x, y, w, c=1):
        self.fbuf.hline(x, y, w, c)
        
    def vline(self, x, y, h, c=1):
        self.fbuf.vline(x, y, h, c)
        
    def line(self, x1, y1, x2, y2, c=1):
        self.fbuf.line(x1, y1, x2, y2)
        
    def rect(self, x, y, w, h, c=1):
        self.fbuf.rect(x, y, w, h, c)
        
    def fill_rect(self, x, y, w, h, c=1):
        self.fbuf.fill_rect(x, y, w, h, c)
        
    def text(self, s, x, y, c=1):
        self.fbuf.text(s, x, y, c)
        
    def scroll(self, xstep, ystep):
        self.fbuf.scroll(xstep, ystep)
        
    def blit(self, fbuf, x, y, key=0):
        self.fbuf.blit(fbuf, x, y, key)


