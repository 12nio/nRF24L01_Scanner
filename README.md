# 2.4GHz RF Band Scanner

This project implements a 2.4GHz band scanner using a Raspberry Pi Pico, an NRF24L01 transceiver, and an SSD1306 OLED display.

The scanner operates by measuring **time-domain channel occupancy**. It iterates through all 126 available 2.4GHz channels (2400-2525 MHz) and, for each channel, repeatedly samples the NRF24L01's **Received Power Detector (RPD)** register. The percentage of samples where the **Carrier Detect (CD)** flag (RPD register, bit 0) is active is calculated.

This occupancy percentage is then visualized as a real-time bar graph on the SSD1306 display, providing a clear view of activity and interference across the 2.4GHz spectrum.

## Hardware Requirements

* **Microcontroller:** Raspberry Pi Pico
* **Transceiver:** NRF24L01
* **Display:** SSD1306 I2C OLED (128x64)

## Software & Dependencies

* [MicroPython](https://micropython.org/) (flashed on the Raspberry Pi Pico)
* `main.py`: Main application logic.
* `icons.py`: Bitmap data for the intro screen icon.
* `ssd1306.py`: MicroPython driver for the SSD1306 display.
    * *Source:* [micropython-lib/ssd1306.py](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py)
* `nrf24l01.py`: MicroPython driver for the NRF24L01 transceiver.
    * *Source:* [micropython-lib/nrf24l01.py](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/radio/nrf24l01/nrf24l01.py)

## Wiring Configuration

### NRF24L01 (SPI 0)

| Module Pin | Pico Pin (GPIO) | Description |
| :--- | :--- | :--- |
| MISO | GP4 | SPI0 MISO |
| MOSI | GP3 | SPI0 MOSI |
| SCK | GP2 | SPI0 SCK |
| CSN | GP6 | Chip Select (CSN) |
| CE | GP5 | Chip Enable (CE) |
| VCC | 3V3 | 3.3V Power |
| GND | GND | Ground |

### SSD1306 (I2C 0)

| Module Pin | Pico Pin (GPIO) | Description |
| :--- | :--- | :--- |
| SDA | GP0 | I2C0 SDA |
| SCL | GP1 | I2C0 SCL |
| VCC | 3V3/5V | Power |
| GND | GND | Ground |

## BUTTON

| Pico Pin (GPIO) | Description | 
| :--- | :--- |
| 14 | Button 1 (Increment) |
| 15 | Button 2 (Select) |

## Usage

1.  Ensure your Raspberry Pi Pico is flashed with MicroPython.
2.  Upload all required files (`main.py`, `icons.py`, `ssd1306.py`, `nrf24l01.py`) to the root directory of the Pico.
3.  Power the device. It will display an introductory screen and then immediately begin scanning. The OLED display will show channel selection menu and (if all channels selected as 'xxx') a live graph of channel occupancy from channel 0 to 125.
