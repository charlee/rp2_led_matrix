import framebuf

class BitmapFont4x7:
    """
    BitmapFont4x7 relies on `font4x7.bin` font file.
    `font4x7.bin` contains glyphs for ASCII 00~7F, each glyph occupies 8 bytes.

    [row1, row2, row3, row4, row5, row6, row7, 0x00]

    The most significant 4 bits of each row byte contain the glyph data, while 
    the least significant 4 bites are 0. So the data of a glyph is:

         glyph   unused
        -----------------
        _ _ _ _ 0 0 0 0     # row1
        _ _ _ _ 0 0 0 0     # row2
        _ _ _ _ 0 0 0 0     # row3
        _ _ _ _ 0 0 0 0     # row4
        _ _ _ _ 0 0 0 0     # row5
        _ _ _ _ 0 0 0 0     # row6
        _ _ _ _ 0 0 0 0     # row7
        0 0 0 0 0 0 0 0     # unused

    The reason for using a whole byte for each row is that FrameBuffer requires
    at least 1 byte to represent a row.

    """
    def __init__(self):
        with open('font4x7.bin', 'rb') as f:
            self.data = f.read()

    def get_fbuf(self, c):
        """
        Returns a 8x8 MONO_HLSB FrameBuffer that contains the glyph data at the top-left corner.
        The return value can be drawn on another MONO_HLSB FrameBuffer using the .blit() method.

        Example:

        ```
        canvas = framebuf.FrameBuffer(bytearray(8 * 8), 8, 8)
        font = BitmapFont4x7()
        c = font.get_fbuf('H')
        canvas.blit(c, 0, 0, 0)
        ```

        """
        idx = ord(c)
        data = bytearray(self.data[idx*8:idx*8+8])
        return framebuf.FrameBuffer(data, 8, 8, framebuf.MONO_HLSB)

