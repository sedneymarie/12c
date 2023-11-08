import smbus
import time
import RPi.GPIO as GPIO

# Define I2C parameters
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 16  # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

# LCD Commands
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94  # LCD RAM address for the 3rd line (if using a 20x4 LCD)
LCD_LINE_4 = 0xD4  # LCD RAM address for the 4th line (if using a 20x4 LCD)
LCD_CLEAR = 0x01  # Command to clear the display

# Backlight control (if supported by your LCD)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)

def lcd_init():
    # Open I2C interface
    bus = smbus.SMBus(1)  # Rev 2 Pi uses 1

    # Initializing the LCD
    lcd_byte(0x33, LCD_CMD)  # Initialize
    lcd_byte(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_byte(0x06, LCD_CMD)  # Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # Display On, Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # Data length, number of lines, font size
    lcd_byte(0x01, LCD_CLEAR)  # Clear display
    time.sleep(0.0005)

def lcd_byte(bits, mode):
    # Send byte to data pins
    bits_high = mode | (bits & 0xF0) | 0x08
    bits_low = mode | ((bits << 4) & 0xF0) | 0x08
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits | 0x04))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, (bits & ~0x04))
    time.sleep(0.0005)

def lcd_string(message, line):
    # Send string to display
    if line == 1:
        line_address = LCD_LINE_1
    elif line == 2:
        line_address = LCD_LINE_2
    elif line == 3:
        line_address = LCD_LINE_3
    elif line == 4:
        line_address = LCD_LINE_4
    else:
        return

    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line_address, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

try:
    bus = smbus.SMBus(1)  # Rev 2 Pi uses 1

    lcd_init()  # Initialize the LCD

    while True:
        lcd_string("Hello, World!", 1)  # Display on the 1st line
        time.sleep(2)
        lcd_string("LCD with I2C", 2)  # Display on the 2nd line
        time.sleep(2)
        lcd_string("Raspberry Pi", 3)  # Display on the 3rd line
        time.sleep(2)
        lcd_string("16x2 Display", 4)  # Display on the 4th line
        time.sleep(2)
        lcd_string("", 1)  # Clear the 1st line
        lcd_string("", 2)  # Clear the 2nd line
        lcd_string("", 3)  # Clear the 3rd line
        lcd_string("", 4)  # Clear the 4th line
        time.sleep(2)

except KeyboardInterrupt:
    lcd_string("Goodbye!", 1)
    time.sleep(2)
    lcd_string("", 1)
    lcd_string("", 2)
    bus.close()
