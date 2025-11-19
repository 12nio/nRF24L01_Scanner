from machine import Pin, I2C, SPI, Timer
from ssd1306 import SSD1306_I2C
import nrf24l01
import icons
import framebuf
import utime
import math

LED_PIN = 25
I2C0_PORT = 0
I2C0_SDA = 0
I2C0_SCL = 1
SSD1306_WIDTH = 128
SSD1306_HEIGHT = 64
SPI_MISO = 4
SPI_MOSI = 3
SPI_SCK = 2
SPI_CSN = 6
SPI_CE = 5
BTN_1 = 14
BTN_2 = 15
CHANNELS = range(126)
NRF_RPD = 0x09
SAMPLES = 150

led = Pin(LED_PIN, Pin.OUT, value=1)

def led_callback(t):
    global led
    led.toggle()

timer = Timer()
timer.init(period=250, mode=Timer.PERIODIC, callback=led_callback)

def display_intro(oled):
    icon_antena = framebuf.FrameBuffer(icons.ANTENA, 48, 48, framebuf.MONO_HLSB)
    oled.blit(icon_antena, 40, 16)
    oled.text("2.4GHz Scanner", 8, 0)
    oled.text("@12nio", 40, 8)
    oled.show()

def scan_channel(nrf, ch):
    res = 0
    nrf.set_channel(ch)
    utime.sleep_us(150)
    for i in range(SAMPLES):
        rpd = nrf.reg_read(NRF_RPD)
        if rpd & 1:
            res += 1
    return res


if __name__ == "__main__":
    print("[*] 2.4 GHz Scanner")

    btn1 = Pin(BTN_1, Pin.IN, Pin.PULL_UP)
    btn2 = Pin(BTN_2, Pin.IN, Pin.PULL_UP)

    print("[*] Initializing SSD1306...")
    i2c = I2C(I2C0_PORT, sda=Pin(I2C0_SDA), scl=Pin(I2C0_SCL), freq=200000)
    print(f"\tI2C devices found: {i2c.scan()}")
    oled = SSD1306_I2C(SSD1306_WIDTH, SSD1306_HEIGHT, i2c)
    print(f"\tSSD1306 (width:{SSD1306_WIDTH}, height:{SSD1306_HEIGHT}) initialized in SDA:{I2C0_SDA}, SCL:{I2C0_SCL} ")
    oled.contrast(12)
    display_intro(oled)

    print("[*] Initializing nRF24L01...")
    spi = SPI(0, baudrate=10_000_000, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=Pin(SPI_MISO))
    csn = Pin(SPI_CSN, mode=Pin.OUT, value=1) 
    ce = Pin(SPI_CE, mode=Pin.OUT, value=0)
    nrf = nrf24l01.NRF24L01(spi, csn, ce)
    pipes = [b"0Node", b"1Node"]
    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(0, pipes[1])
    nrf.set_power_speed(nrf24l01.POWER_3, nrf24l01.SPEED_2M)
    nrf.start_listening()
    print("\t NRF24L01 listening")
    utime.sleep_ms(250)
    
    custom_channels_str = ['xxx' for i in range(5)]
    custom_channels = [-1]*5
    for i in range(5):
        oled.fill(0)
        oled.text("Select Channels", 0, 0)
        for j in range(5):
            oled.text(custom_channels_str[j], j*26, 8)
            if i == j:
                oled.hline(j*26, 16, 26, 1)
        oled.text(custom_channels_str[i], 51, 25)
        oled.text("all channels xxx for 0-125", 0,48)
        oled.text("for 0-125 range", 0, 56)
        oled.show()
        while btn2.value() == 1:
            if btn1.value() == 0:
                if custom_channels[i] == -1:
                    custom_channels[i] = 0
                custom_channels[i] += 1
                custom_channels[i] %= 126
                if len(str(custom_channels[i])) == 3:
                    custom_channels_str[i] = str(custom_channels[i])
                else:
                    custom_channels_str[i] = f"{(3-len(str(custom_channels[i])))*'0'}{custom_channels[i]}"
            oled.rect(51, 25, 26, 7, 0, True)
            oled.text(custom_channels_str[i], 51, 25)
            oled.show()
            utime.sleep_ms(75)
        utime.sleep_ms(250)

    if any([False if i == -1 else True for i in custom_channels]):
        CHANNELS = [ch for ch in custom_channels if ch != -1]
        custom_channels_str = [ch for ch in custom_channels_str if ch != 'xxx']
        
    density_per_channel = [0 for i in range(len(CHANNELS))]

    while True:
        oled.fill(0)
        oled.text("Scanning...", 0, 0)
        if len(CHANNELS) <= 5:
            for i, ch in enumerate(custom_channels_str):
                oled.text(ch, i*26, 8)
        else:
            oled.text("0", 0, 8)
            oled.text("125", 104, 8)
        
        for i, ch in enumerate(CHANNELS):
            res = scan_channel(nrf, ch)
            density_per_channel[i] = (res/SAMPLES) * 100

        for i, ch, in enumerate(CHANNELS):
            if len(CHANNELS) <= 5:
                oled.rect(i*26, 17, 24, math.trunc(density_per_channel[i]*(47/100)), 1)
            else:
                oled.vline(ch, 16, math.trunc(density_per_channel[i]*(48/100)), 1)

        oled.show()
