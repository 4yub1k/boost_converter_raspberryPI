################################
#   Author: Salah Ud Din       #
#   GitHUb: @4yub1k            #
################################

from spidev import SpiDev


class MCP3008:
    def __init__(self, bus=0, device=0, max_speed_hz=1_000_000):
        """
        Default Bus=0, device=0
        """
        self.spi = SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz  # 1MHz

    def read_channel(self, channel=0):
        """
        Default channel = 0
        """
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data
