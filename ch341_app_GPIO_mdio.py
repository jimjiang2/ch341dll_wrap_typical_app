import os
import time
import random
import time
import numpy as np

## call ch341dll_wrap
from ch341dll_32bits_wrap.ch341dll_wrap  import *


### main function define , USing GPIO mode , and try to access chip LAN8720 eth 100M phy
## MDIO bus ;DataSheet   http://ww1.microchip.com/downloads/en/devicedoc/8720a.pdf
### USE D3, D5 pins of CH341A, can be adentify

hd = CH341DEV(0)

def pre_clks(cycles):
    ''''pre clks is for input 32bits 1 before MDIO frame start '''
    for ii in range(cycles):
        hd.ch341_set_output(0x0c, 0x8 + 0x20*1, 0x0  + 0x20);  ## 0x8 is D3, 0x20 is D5,
        hd.ch341_set_output(0x0c, 0x8 + 0x20*1, 0x8  + 0x20);  ##
    hd.ch341_set_output(0x0c, 0x8 + 0x20 * 1, 0x00 + 0x00);  ##0xff is for 8bits output.


def write_mdio(phy_addr,reg_addr ,wdata, print_f=1):
    ''''MDIO frame write '''
    pre_clks(33);
    # set all 0; 01, start; , again 01 to read:
    for ii in range(2):
        mdio_o = 0;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise
        mdio_o = 1;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise

    # set phy_addr = 0x1f max
    for ii in range(5):
        mdio_o = ((phy_addr & 0x1f)  >> (4-ii)) & 0x1 ;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise

    # set reg addr 0x1f
    for ii in range(5):
        mdio_o = ((reg_addr & 0x1f)  >> (4-ii)) & 0x1 ;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise
    # set all 0; 01, ;

    # TA 2 cycles
    for ii in range(1):
        hd.ch341_set_output(0x0c, 0x8 + 0x20*0 , 0x0  );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20*0 , 0x8  );  # clk_rise
    # set all 0; 01, ;
    # 16 read data 16 cycles
    get_v = 0x0;
    for ii in range(16):
        mdio_o = ((wdata & 0xffff)  >> (16-ii)) & 0x1 ;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x20*mdio_o + 0x0  );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x20*mdio_o + 0x8  );  # clk_rise
    if(print_f > 0):
        print("write reg_addr ",hex(reg_addr),"wdata:",hex(wdata))
    hd.ch341_set_output(0x0c, 0x8 + 0x20 * 0, 0x0);  #set clk to 0; mdio to z
    return 1;

def read_mdio(phy_addr,reg_addr ,print_f=1):
    ''''MDIO frame read '''
    pre_clks(33);
    # set all 0; 01, start; , again 01 to read:
    for ii in range(1):
        mdio_o = 0;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise
        mdio_o = 1;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise

    for ii in range(1):
        mdio_o = 1;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise
        mdio_o = 0;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise
    # set all 0; 01, ;
    # set phy_addr = 0x1f max
    for ii in range(5):
        mdio_o = ((phy_addr & 0x1f)  >> (4-ii)) & 0x1 ;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise

    # set reg addr 0x1f
    for ii in range(5):
        mdio_o = ((reg_addr & 0x1f)  >> (4-ii)) & 0x1 ;
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x0 + mdio_o * 0x20 );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20, 0x8 + mdio_o * 0x20);  # clk_rise
    # set all 0; 01, ;


    # TA 2 cycles
    for ii in range(1):
        hd.ch341_set_output(0x0c, 0x8 + 0x20*0 , 0x0  );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20*0 , 0x8  );  # clk_rise
    # set all 0; 01, ;
    # 16 read data 16 cycles
    get_v = 0x0;
    for ii in range(16):
        hd.ch341_set_output(0x0c, 0x8 + 0x20*0 , 0x0  );  ##0xff is for 8bits output.
        hd.ch341_set_output(0x0c, 0x8 + 0x20*0 , 0x8  );  # clk_rise
        gdata = hd.ch341_get_input ();  # clk_rise
        get_bit = (0x20 & gdata) >> 0x5;  # clk_rise
        if get_bit < 1:
            print_f = 1;
        get_v += get_bit <<(15-ii);
    if(print_f > 0):
        print("read_mdio reg_addr ",hex(reg_addr),"get_data:",hex(get_v))
    hd.ch341_set_output(0x0c, 0x8 + 0x20 * 0, 0x0);  #set clk to 0; mdio to z
    return get_v;

phy_addr = 1;
list_reg_v = [];
for ii in range(0x1f):
    xx = read_mdio(phy_addr,ii,1)
    list_reg_v.append(xx);

write_mdio(phy_addr,0,0x2100)
xx = read_mdio(phy_addr, ii, 1)
hd.ch341_close();


### RUNNING log is below #####
#C:\Python38-32\python.exe D:/my_open_pjs/python_ch341/ch341_app_GPIO_mdio.py
#Ch341dll_wrap is loaded!!! only work for python 32bits version !!!
#Open USB CH341Dev Index= 0 ok!!!!!!!
#set I2C speed to  3 (3=750Khz, 2=400k, 1=100k, 0=20k
#read_mdio reg_addr  0x0 get_data: 0x2100
#read_mdio reg_addr  0x1 get_data: 0x7809
#read_mdio reg_addr  0x2 get_data: 0x7
#read_mdio reg_addr  0x3 get_data: 0xc0f1
#read_mdio reg_addr  0x4 get_data: 0x1e1
#read_mdio reg_addr  0x5 get_data: 0x1
#read_mdio reg_addr  0x6 get_data: 0x0
#read_mdio reg_addr  0x7 get_data: 0xffff
#read_mdio reg_addr  0x8 get_data: 0xffff
#read_mdio reg_addr  0x9 get_data: 0xffff
#read_mdio reg_addr  0xa get_data: 0xffff
#read_mdio reg_addr  0xb get_data: 0xffff
#read_mdio reg_addr  0xc get_data: 0xffff
#read_mdio reg_addr  0xd get_data: 0xffff
#read_mdio reg_addr  0xe get_data: 0xffff
#read_mdio reg_addr  0xf get_data: 0x0
#read_mdio reg_addr  0x10 get_data: 0x40
#read_mdio reg_addr  0x11 get_data: 0x0
#read_mdio reg_addr  0x12 get_data: 0x60e1
#read_mdio reg_addr  0x13 get_data: 0xffff
#read_mdio reg_addr  0x14 get_data: 0x0
#read_mdio reg_addr  0x15 get_data: 0x0
#read_mdio reg_addr  0x16 get_data: 0x0
#read_mdio reg_addr  0x17 get_data: 0x0
#read_mdio reg_addr  0x18 get_data: 0xffff
#read_mdio reg_addr  0x19 get_data: 0xffff
#read_mdio reg_addr  0x1a get_data: 0x0
#read_mdio reg_addr  0x1b get_data: 0xb
#read_mdio reg_addr  0x1c get_data: 0x0
#read_mdio reg_addr  0x1d get_data: 0x10
#read_mdio reg_addr  0x1e get_data: 0x0
#write reg_addr  0x0 wdata: 0x2100
#read_mdio reg_addr  0x1e get_data: 0x0
#Close USB CH341Dev Index= 0 ok!!!!!!!
