import sys
sys.path.append('/home/michael/dotdashboard/lib')
import board
import busio
# import framebufferio
import adafruit_framebuf as framebufferio
import digitalio
import displayio
import rgbmatrix
# import rgbmatrix

# from adafruit_bitmap_font import bitmap_font
import adafruit_display_text

def init():

    bit_depth_value = 2
    base_width = 64
    base_height = 32
    chain_across = 1
    tile_down = 2
    serpentine_value = True

    width_value = base_width * chain_across
    height_value = base_height * tile_down
    
    
    # displayio.release_displays()
    # matrix = rgbmatrix.RGBMatrix(
    #     width=64, bit_depth=4,
    #     rgb_pins=[
    #         board.MTX_R1,
    #         board.MTX_G1,
    #         board.MTX_B1,
    #         board.MTX_R2,
    #         board.MTX_G2,
    #         board.MTX_B2
    #     ],
    #     addr_pins=[
    #         board.MTX_ADDRA,
    #         board.MTX_ADDRB,
    #         board.MTX_ADDRC,
    #         board.MTX_ADDRD
    #     ],
    #     clock_pin=board.MTX_CLK,
    #     latch_pin=board.MTX_LAT,
    #     output_enable_pin=board.MTX_OE
    # )
    # return framebufferio.FramebufferDisplay(matrix)

    displayio.release_displays()

    # send register
    B2 = digitalio.DigitalInOut(board.D10)
    R1 = digitalio.DigitalInOut(board.D11)
    G1 = digitalio.DigitalInOut(board.D27)
    B1 = digitalio.DigitalInOut(board.D7)
    R2 = digitalio.DigitalInOut(board.D8)
    G2 = digitalio.DigitalInOut(board.D9)
    CLK = digitalio.DigitalInOut(board.D17)
    STB = digitalio.DigitalInOut(board.D4)
    OE = digitalio.DigitalInOut(board.D18)

    R1.direction = digitalio.Direction.OUTPUT
    G1.direction = digitalio.Direction.OUTPUT
    B1.direction = digitalio.Direction.OUTPUT
    R2.direction = digitalio.Direction.OUTPUT
    G2.direction = digitalio.Direction.OUTPUT
    B2.direction = digitalio.Direction.OUTPUT
    CLK.direction = digitalio.Direction.OUTPUT
    STB.direction = digitalio.Direction.OUTPUT
    OE.direction = digitalio.Direction.OUTPUT

    OE.value = True
    STB.value = False
    CLK.value = False

    MaxLed = 64

    c12 = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    c13 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]

    for l in range(0, MaxLed):
        y = l % 16
        R1.value = False
        G1.value = False
        B1.value = False
        R2.value = False
        G2.value = False
        B2.value = False

        if c12[y] == 1:
            R1.value = True
            G1.value = True
            B1.value = True
            R2.value = True
            G2.value = True
            B2.value = True
        if l > (MaxLed - 12):
            STB.value = True
        else:
            STB.value = False
        CLK.value = True
        # time.sleep(0.000002) 
        CLK.value = False
    STB.value = False
    CLK.value = False

    for l in range(0, MaxLed):
        y = l % 16
        R1.value = False
        G1.value = False
        B1.value = False
        R2.value = False
        G2.value = False
        B2.value = False

        if c13[y] == 1:
            R1.value = True
            G1.value = True
            B1.value = True
            R2.value = True
            G2.value = True
            B2.value = True
        if l > (MaxLed - 13):
            STB.value = True
        else:
            STB.value = False
        CLK.value = True
        # time.sleep(0.000002)
        CLK.value = False
    STB.value = False
    CLK.value = False

    R1.deinit()
    G1.deinit()
    B1.deinit()
    R2.deinit()
    G2.deinit()
    B2.deinit()
    CLK.deinit()
    STB.deinit()
    OE.deinit()

    # This next call creates the RGB Matrix object itself. It has the given width
    # and height. bit_depth can range from 1 to 6; higher numbers allow more color
    # shades to be displayed, but increase memory usage and slow down your Python
    # code. If you just want to show primary colors plus black and white, use 1.
    # Otherwise, try 3, 4 and 5 to see which effect you like best.
    #

    # SET FOR PI ZERO PINOUTS BASED ON 
    # https://pinout.xyz/pinout/pin19_gpio10/
    # https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/wiring.md
    matrix = rgbmatrix.RGBMatrix(
        width=width_value, height=height_value, bit_depth=bit_depth_value,
        rgb_pins=[board.D11, board.D27, board.D7, board.D8, board.D9, board.D10],
        addr_pins=[board.D22, board.D23, board.D24, board.D25],
        clock_pin=board.D17, latch_pin=board.D4, output_enable_pin=board.D18,
        tile=tile_down, serpentine=serpentine_value,
        doublebuffer=True)

    # Associate the RGB matrix with a Display so that we can use displayio features
    display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)

    print("-" * 40)

    display.rotation = 0
    return display




display = init()
# mainfont = bitmap_font.load_font("/fonts/frucnorm6.bdf")

line1 = adafruit_display_text.label.Label(
    color=0x8000ff,
        text="is there anybody out there?")
line1.x = 2
line1.y = 5
line1.scale = 1
g = digitalio.Group()
g.append(line1)
display.show(g)

while True:
    display.refresh(minimum_frames_per_second=0)


