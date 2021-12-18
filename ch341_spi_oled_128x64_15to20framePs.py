import random
import time
import numpy as np
from matplotlib import pyplot as plt
import os
import random
import numpy as np
from fractions import Fraction
import pyautogui
from PIL import Image

## call ch341dll_wrap
from ch341dll_32bits_wrap.ch341dll_wrap  import *

###1.  init ch341 device
hd = CH341DEV(0)
hd.ch341_i2c_speed(3)
#hd.ch341_close()


###2.  init oled ----
hd.spi_oled1306_3w(0, 0x00); #// SSD1306_DISPLAYOFF
hd.spi_oled1306_3w(0, 0x10); #// SSD1306_SETDISPLAYCLOCKDIV
hd.spi_oled1306_3w(0, 0x40); #// Suggested value 0x80
hd.spi_oled1306_3w(0, 0xB0); #// SSD1306_SETMULTIPLEX
hd.spi_oled1306_3w(0, 0x81); #// 1 / 64
hd.spi_oled1306_3w(0, 0xFF); #// SSD1306_SETDISPLAYOFFSET
hd.spi_oled1306_3w(0, 0xA1); #// 0 no offset
hd.spi_oled1306_3w(0, 0xA6); #// SSD1306_SETSTARTLINE line  # 0
hd.spi_oled1306_3w(0, 0xA8); #// SSD1306_MEMORYMODE
hd.spi_oled1306_3w(0, 0x3F); #// 0x0 act like ks0108
hd.spi_oled1306_3w(0, 0xC8); #// SSD1306_SEGREMAP | 1
hd.spi_oled1306_3w(0, 0xD3); #// SSD1306_COMSCANDEC
hd.spi_oled1306_3w(0, 0x00); #// SSD1306_SETCOMPINS
hd.spi_oled1306_3w(0, 0xD5);
hd.spi_oled1306_3w(0, 0x80); #// SSD1306_SETCONTRAST
hd.spi_oled1306_3w(0, 0xD8);
hd.spi_oled1306_3w(0, 0x05); #// SSD1306_SETPRECHARGE
hd.spi_oled1306_3w(0, 0xD9);
hd.spi_oled1306_3w(0, 0xF1); #// SSD1306_SETVCOMDETECT
hd.spi_oled1306_3w(0, 0xDA);
hd.spi_oled1306_3w(0, 0x12); #// SSD1306_CHARGEPUMP
hd.spi_oled1306_3w(0, 0xDB); #// Charge pump on
hd.spi_oled1306_3w(0, 0x30); #// SSD1306_DEACTIVATE_SCROLL
hd.spi_oled1306_3w(0, 0x8D); #// SSD1306_DISPLAYALLON_RESUME
hd.spi_oled1306_3w(0, 0x14); #// SSD1306_NORMALDISPLAY}
hd.spi_oled1306_3w(0, 0xAF);  # // SSD1306_NORMALDISPLAY}
### initial done


### 2.
wdata = (ctypes.c_uint8 * 4095)()
data = (ctypes.c_uint8 * 4095)()
for ii in range(128*2):
    wdata[ii] = 0;
    data[ii] = 0;

start_time = time.time()
for ff in range(1000):
    imag = pyautogui.screenshot(); #imag.save("test.png") #imag = Image.open("heihei.png")
    im = imag.resize([128, 64]);   # im.show()
    imag_pix = im.load()
    out128x8 = np.zeros([128, 8])
    thv = 300;
    for hang8 in range(8):
        for bit_cnt in range(8):
            hang = hang8 * 8 + bit_cnt;
            for lei in range(128):
                yy = imag_pix[lei, hang]
                yys = abs(yy[0] + yy[1] + yy[2])
                if yys >= thv:
                    tmp_int =  1
                else:
                    tmp_int = 0
                out128x8[lei, hang8] += (int(tmp_int) << bit_cnt);

    for ii in range(8):
        din = [];
        #din_len = 0; # hd.spi_oled1306_3w(0, 0xB0 + ii);  # // SSD1306_NORMALDISPLAY} # hd.spi_oled1306_3w(0, 0);  # // SSD1306_NORMALDISPLAY} # hd.spi_oled1306_3w(0, 0x10);  # // SSD1306_NORMALDISPLAY}
        din.append(((0xB0 + ii) >> 1));
        din.append(0x80 & (ii << 7));
        din.append(0x10 >> 3);
        din.append(0);
        hd.ch341_oled306_3w_stream(din);

        wdata = np.zeros(round(9/8*128));
        sel_w = 0;
        for jj in range(128):
            #hd.spi_oled1306_3w(1, int(out128x8[jj,ii]));  # // SSD1306_NORMALDISPLAY}
            outdata_sel = int(out128x8[jj,ii])
            #for ii in range(8):
            shift_v = jj%8;# start from 0: #range 0~7; period = 8;
            if shift_v == 0:
                wdata[sel_w]   = (0x1 << (8 - shift_v - 1)) + ((outdata_sel & 0xff) >> (shift_v + 1));
                wdata[sel_w+1] = (outdata_sel & 0xff) << (7 - shift_v );
                sel_w += 1;

            if shift_v >= 1 and shift_v <= 6:
                wdata[sel_w]     = (int(wdata[sel_w]) & (0xff << (8 - shift_v)) & 0xff) +  (0x1 << ((8 - shift_v - 1))) + ((outdata_sel & 0xff) >> (shift_v + 1));
                wdata[sel_w + 1] = (outdata_sel & 0xff) << (7 - shift_v );
                sel_w += 1;

            if shift_v == 7:
                wdata[sel_w] = int(wdata[sel_w]) | 0x1;
                wdata[sel_w+1]  = outdata_sel & 0xff;
                sel_w += 2;
        din = [];
        for ii in range(int(9*(128/8))):
            din.append(int(wdata[ii]))
        hd.ch341_oled306_3w_stream(din);
#    print("send frame num:", ff)
    frame_times = 10;
    if (ff % frame_times == 0):
        end_time = time.time();
        print("send frame num:", ff, "time_cost:", end_time - start_time, "frame rate f/s:", round(frame_times / (end_time - start_time)))
        start_time = time.time()

hd.ch341_close();
