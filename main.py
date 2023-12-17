import RPi.GPIO as GPIO

from time import perf_counter as pf
from mcp3008 import MCP3008
from time import sleep
from wiringpi import Serial
# from lcd import LCD

GPIO.setmode(GPIO.BCM)
adc_mcp3008 = MCP3008(max_speed_hz=1_000_000)
serial = Serial("/dev/serial0", 9600)

# lcd = LCD(29, 31, 37, 40, 38, 36)  # Board
# lcd = LCD(5, 6, 26, 21, 20, 16)  # BCM
# lcd.cursor_start(0, 0)


class BoostConverter:
    ###########################################
    # Title: Boost Converter , PID controller #
    # Author: Salah Ud Din                    #
    # GitHub: https://github.com/4yub1k       #
    ###########################################
    input_voltage = 5
    voltage_range = 0
    duty = 50
    set_voltage = 9
    error = 0.0
    total_error = 0.0
    rate_error = 0.0
    previous_error = 0.0
    previous_time = 0.0
    kp, ki, kd = 0.1, 0.6, 0.01
    # kp, ki, kd = 2, 5, 1

    def initial_pwm(self):
        """
        Initial PWM, and pins.
        Uncomment voltage_pin, to set the output voltage, using voltage dividers or any crkt.
        """
        pwm_pin = 18				                # PWM pin connected to LED.
        pwm_freq = 100_000                          # frequency of PMW.
        # voltage_pin = 12                            # Voltage range pin.
        # GPIO.setwarnings(False)			        # disable warnings.
        # GPIO.setmode(GPIO.BOARD)		            # set pin numbering system.
        GPIO.setup(pwm_pin, GPIO.OUT)               # Set pin 12 output.
        # GPIO.setup(voltage_pin, GPIO.IN)            # Set pin 12 output. Voltage range set pin
        self.pwm = GPIO.PWM(pwm_pin, pwm_freq)	    # create PWM instance with frequency.
        self.pwm.start(0)				            # start PWM of required Duty Cycle.

    def change_pwm(self, duty):
        """
        Update the duty cycle.
        """
        duty = abs(duty)
        if duty >= 0 and duty <= 100:
            self.pwm.ChangeDutyCycle(duty)
            self.duty = duty

    def average_voltage(self, adc, channel_pin):
        """
        Calculate the votage, avaerage of 100 vaules.
        """
        sum_voltage = 0
        for _ in range(99):
            value = adc.read_channel(channel=channel_pin)
            sum_voltage += value * (3.3 / 1023.0) * 41.005
        return sum_voltage / 50

    def read_voltage(self, adc, channel=1):
        """
        Read Single value from channel, of MCP.
        """
        # Roundind value to fix the set point.
        return round(adc.read_channel(channel) * (3.3 / 1023.0) * 25.514)

    def set_voltage_range(self, set_voltage):
        """
        Set new voltage value.
        """
        self.set_voltage = set_voltage

    def pid_control(self):
        """
        PID Controller Method.
        """
        # Find the Voltage.
        an = adc_mcp3008.read_channel(channel=0)
        current_voltage = round(an * (3.3 / 1023.0) * 40.829)

        # Time calculation.
        current_time = pf()
        time_passed = current_time - self.previous_time

        # PID function.
        error = self.set_voltage - current_voltage
        self.total_error += error * time_passed
        self.rate_error = (error - self.previous_error) / time_passed

        output = (self.kp * error) + (self.ki * self.total_error) + (self.kd * self.rate_error)

        self.previous_error, self.previous_time = error, current_time
        return [output, current_voltage, error]


def main():
    boost_converter = BoostConverter()
    # voltage = boost_converter.read_voltage(adc_mcp3008, channel=1)
    # boost_converter.set_voltage_range(voltage)
    # print(boost_converter.set_voltage)
    boost_converter.initial_pwm()

    """Input your Voltage setpoint on pin 12 (BCM)"""
    boost_converter.set_voltage = 12

    # Infinite loop
    while True:
        output = boost_converter.pid_control()
        boost_converter.change_pwm(output[0])
        print(f"O={output[0]:.2f}, Vo={output[1]:.2f}, Vset={boost_converter.set_voltage}, E={output[2]}, D={boost_converter.duty}")
        # lcd.print_line(an)
        # Serial.puts(serial, f"{an}\r")


# Command line execution
if __name__ == "__main__":
   main()
   pwm.stop()
   GPIO.clean()
