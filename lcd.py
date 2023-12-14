################################
#   Author: Salah Ud Din       #
#   GitHUb: @4yub1k            #
################################

import time
import RPi.GPIO as GPIO


class LCD:
    width = 16  # Maximum characters per line

    high = True
    low = False

    row_1 = 0x80  # LCD RAM address for the 1st line
    row_2 = 0xC0  # LCD RAM address for the 2nd line

    delay = 0.0002  # <20ms, LM016L, set it 37us.

    def __init__(self, rs=5, en=6, d4=12, d5=13, d6=16, d7=19):
        self.rs, self.en = rs, en
        self.d4, self.d5, self.d6, self.d7 = d4, d5, d6, d7
        self.cursor, self.special_char = 0, " "
        self.end_char = " "
        self.row = 0
        self.pins_list = [self.rs, self.en, self.d4, self.d5, self.d6, self.d7]
        # for more commands:
        # https://www.electronicsforu.com/technology-trends/learn-electronics/16x2-lcd-pinout-diagram
        # https://www.electronicwings.com/8051/lcd16x2-interfacing-in-4-bit-mode-with-8051
        # https://www.farnell.com/datasheets/58820.pdf
        # self.commands_list = [0x02, 0x28, 0x0C, 0x06, 0x01, 0x80]
        self.commands_list = {
            0x02: 37 / 1e6,  # 4 bit mode
            0x28: 37 / 1e6,
            0x0C: 37 / 1e6,
            0x06: 37 / 1e6,
            0x01: 37 / 1e6,
            0x80: 37 / 1e6,
        }
        self.setup_pins()  # Setup pins
        self.initialise_lcd()

    def initialise_lcd(self):
        """
        Start the lcd.
        """
        time.sleep(20 / 1e3)  # wait for 20ms, LCD ON wait more than 15ms.
        for command, time_delay in self.commands_list.items():
            self.send_command(command)
            time.sleep(time_delay)

    def setup_pins(self):
        """
        Setup output pins.
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
        for pin in self.pins_list:
            GPIO.setup(pin, GPIO.OUT)

    def send_byte_to_lcd(self, byte):
        """
        To send command to lcd, first put RS to low.
        To send data to lcd, first put RS to High.
        Send High 4 bits (nibbles) to D4, D5, D6, D7 pins,
        Set EN to High, Delay, than to low, (remember every command take sometime to finish, see datasheet and put delay)
        Then send Low nibbles to D4, D5, D6, D7 pins,
        Set EN to High, delay, then EN to low.
        """
        high_bits = byte >> 4  # High nibbles
        low_bits = byte & 0x0F  # Low nibbles

        self.send_bits(high_bits)
        self.lcd_toggle_enable()

        self.send_bits(low_bits)
        self.lcd_toggle_enable()

    def send_bits(self, byte):
        for bit, pin in enumerate(self.pins_list[2:]):  # [0 , 0, 1, 1] , [d4, d5, d6, d7]
            if byte >> bit & 0b1:
                GPIO.output(pin, True)
            else:
                GPIO.output(pin, False)

    def lcd_toggle_enable(self):
        """
        Turn EN high than, low
        """
        time.sleep(self.delay)
        for state in [True, False]:
            time.sleep(self.delay)
            GPIO.output(self.en, state)
            time.sleep(self.delay)

    def cursor_start(self, start, row, special_char=" "):
        """
        Set cursor, from where you want to print data.
        """
        self.row = row
        self.cursor, self.special_char = start, special_char

    def end_fill(self, end_char=" "):
        """
        To fill the remaining space at end of data, "testing" -> "testing         ", len() = 16
        """
        self.end_char = end_char

    def rotate_line(self, print_string, delay=0.2):
        """
        Send long strings to  lcd.
        """
        i = -1
        while True:
            output = (
                print_string[i + 1 : 17 + i]
                + print_string[17 + i : i + 1]
                + (16 - len(print_string[i + 1 : 17 + i])) * " "
                if len(print_string[i + 1 : 17 + i]) < 17
                else ""
            )
            i += 1
            if len(print_string[i + 1 : 17 + i]) <= 1:
                output = (
                    print_string[i + 1 : 17 + i]
                    + (16 - len(print_string[i + 1 : 17 + i] + print_string[0])) * " "
                    + print_string[0]
                )
                for i in range(1, 16):
                    self.print_line((16 - len(print_string[:i])) * " " + print_string[: i + 1])
                    time.sleep(delay)
                break
            self.print_line(output)
            time.sleep(delay)
            # self.clear()

    def change_lcd_mode(self, mode):
        """
        Change mode of lcd, for excecuting lcd command Put RS to "Low",
        for sending data to display put RS to "High"
        """
        GPIO.output(self.rs, mode)  # RS pin

    def print_line(self, print_string):
        """
        Send Data to lcd. First set row number to start from, then send data to that row
        of lcd.
        """
        row = self.row_1 if self.row == 0 else self.row_2
        self.send_command(row)  # RS to low, then set row number.

        # Send Data to lcd display.
        self.change_lcd_mode(self.high)  # RS to High
        print_string = f"{self.cursor * self.special_char}{print_string}"
        print_string += f"{(16 - len(print_string)) * self.end_char}"  # send exact width eg 16, else index error
        for i in range(self.width):
            self.send_byte_to_lcd(ord(print_string[i]))

    def send_command(self, command):
        """
        Send command to lcd.
        """
        self.change_lcd_mode(self.low)  # RS to low
        self.send_byte_to_lcd(command)

    def clear(self):
        """
        This will clear the lcd display.
        """
        self.send_command(0x01)  # 000001 Clear display, see datasheet.
