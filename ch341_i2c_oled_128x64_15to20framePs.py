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
device_addr = round(0x78>>1)
hd.ch341_swi2c(device_addr,0x00, 0x00); #// SSD1306_DISPLAYOFF
hd.ch341_swi2c(device_addr,0x00, 0x10); #// SSD1306_SETDISPLAYCLOCKDIV
hd.ch341_swi2c(device_addr,0x00, 0x40); #// Suggested value 0x80
hd.ch341_swi2c(device_addr,0x00, 0xB0); #// SSD1306_SETMULTIPLEX
hd.ch341_swi2c(device_addr,0x00, 0x81); #// 1 / 64
hd.ch341_swi2c(device_addr,0x00, 0xFF); #// SSD1306_SETDISPLAYOFFSET
hd.ch341_swi2c(device_addr,0x00, 0xA1); #// 0 no offset
hd.ch341_swi2c(device_addr,0x00, 0xA6); #// SSD1306_SETSTARTLINE line  # 0
hd.ch341_swi2c(device_addr,0x00, 0xA8); #// SSD1306_MEMORYMODE
hd.ch341_swi2c(device_addr,0x00, 0x3F); #// 0x0 act like ks0108
hd.ch341_swi2c(device_addr,0x00, 0xC8); #// SSD1306_SEGREMAP | 1
hd.ch341_swi2c(device_addr,0x00, 0xD3); #// SSD1306_COMSCANDEC
hd.ch341_swi2c(device_addr,0x00, 0x00); #// SSD1306_SETCOMPINS
hd.ch341_swi2c(device_addr,0x00, 0xD5);
hd.ch341_swi2c(device_addr,0x00, 0x80); #// SSD1306_SETCONTRAST
hd.ch341_swi2c(device_addr,0x00, 0xD8);
hd.ch341_swi2c(device_addr,0x00, 0x05); #// SSD1306_SETPRECHARGE
hd.ch341_swi2c(device_addr,0x00, 0xD9);
hd.ch341_swi2c(device_addr,0x00, 0xF1); #// SSD1306_SETVCOMDETECT
hd.ch341_swi2c(device_addr,0x00, 0xDA);
hd.ch341_swi2c(device_addr,0x00, 0x12); #// SSD1306_CHARGEPUMP
hd.ch341_swi2c(device_addr,0x00, 0xDB); #// Charge pump on
hd.ch341_swi2c(device_addr,0x00, 0x30); #// SSD1306_DEACTIVATE_SCROLL
hd.ch341_swi2c(device_addr,0x00, 0x8D); #// SSD1306_DISPLAYALLON_RESUME
hd.ch341_swi2c(device_addr,0x00, 0x14); #// SSD1306_NORMALDISPLAY}
hd.ch341_swi2c(device_addr,0x00, 0xAF);  # // SSD1306_NORMALDISPLAY}
### init done

## 3. copy screen to OLED ....
start_time = time.time()
for ff in range(5000):
    imag = pyautogui.screenshot()
    #imag.save("test.png")
    #imag = Image.open("heihei.png")
    im = imag.resize([128, 64]);
    # im.show()
    imag_pix = im.load()
    out128x64 = np.zeros([128, 64])
    out128x8 = np.zeros([128, 8])
    # to128x8 = np.zeros([128,8]);
    thv = 300;
    for hang8 in range(8):
        for bit_cnt in range(8):
            hang = hang8 * 8 + bit_cnt;
            for lei in range(128):
                yy = imag_pix[lei, hang]
                yys = abs(yy[0] + yy[1] + yy[2])
                if yys >= thv:
                    out128x64[lei, hang] = 1;
                tmp_int = out128x64[lei, hang];
                out128x8[lei, hang8] += (int(tmp_int) << bit_cnt);

    for ii in range(8):
        din = [];
        #hd.ch341_swi2c(device_addr,0x00, 0xB0+ii);  # //
        #hd.ch341_stream_wi2c (device_addr,din)
        #hd.ch341_swi2c(device_addr,0x00, 0);  # // SSD1306_NORMALDISPLAY}
        din.append(0x0);
        din.append(0xB0+ii);
        #din = [];
        din.append(0x0);
        din.append(0x0);
        #hd.ch341_stream_wi2c (device_addr,din)
        #hd.ch341_swi2c(device_addr,0x00, 0x10);  # // SSD1306_NORMALDISPLAY}
        #din = [];
        din.append(0x0);
        din.append(0x10);
        hd.ch341_stream_wi2c (device_addr,din)

        din = [];
        din.append(0x40);
        for jj in range(128):
            din.append(int(out128x8[jj,ii]))
        hd.ch341_stream_wi2c (device_addr,din)
        #time.sleep(0.001)
#    print("send frame num:", ff)
    frame_times = 30;
    if (ff%frame_times == 0):
        end_time = time.time();
        print("send frame num:", ff, "time_cost:", end_time - start_time , "frame rate f/s:", round(frame_times/(end_time-start_time)))
        start_time = time.time()

hd.ch341_close();