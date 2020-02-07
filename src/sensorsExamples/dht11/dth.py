import mraa
import time

class DHT(object):
    DHT_TYPE = {
        'DHT11': '11',
        'DHT22': '22'
    }

    MAX_CNT = 320
    PULSES_CNT = 41


    def __init__(self, dht_type, pin):        
        if dht_type != self.DHT_TYPE['DHT11'] and dht_type != self.DHT_TYPE['DHT22']:
            print('ERROR: Please use 11|22 as dht type.')
            exit(1)
        self.dht_type = dht_type
        #self.pin = GPIO(pin, GPIO.OUT)
        self.pin = mraa.Aio(pin)
        #self.pin.dir(mraa.DIR_OUT)
        self._last_temp = 0.0
        self._last_humi = 0.0

    @property
    def dht_type(self):
        return self._dht_type

    @dht_type.setter
    def dht_type(self, type):
        self._dht_type = type

    def _read(self):
        # Send Falling signal to trigger sensor output data
        # Wait for 20ms to collect 42 bytes data
        #self.pin.dir(mraa.DIR_OUT)

        #self.pin.write(1)
        #time.sleep(.2)

        #self.pin.write(0)
        #time.sleep(.018)

        #self.pin.dir(mraa.DIR_IN)
        # a short delay needed
        #for i in range(10):
        #    pass

        # pullup by host 20-40 us
        count = 0
        while self.pin.read():
            count += 1
            if count > self.MAX_CNT:
                # print("pullup by host 20-40us failed")
                return None, "pullup by host 20-40us failed"

        pulse_cnt = [0] * (2 * self.PULSES_CNT)
        fix_crc = False
        for i in range(0, self.PULSES_CNT * 2, 2):
            while not self.pin.read():
                pulse_cnt[i] += 1
                if pulse_cnt[i] > self.MAX_CNT:
                    # print("pulldown by DHT timeout %d" % i)
                    return None, "pulldown by DHT timeout %d" % i

            while self.pin.read():
                pulse_cnt[i + 1] += 1
                if pulse_cnt[i + 1] > self.MAX_CNT:
                    # print("pullup by DHT timeout %d" % (i + 1))
                    if i == (self.PULSES_CNT - 1) * 2:
                        # fix_crc = True
                        # break
                        pass
                    return None, "pullup by DHT timeout %d" % i


        total_cnt = 0
        for i in range(2, 2 * self.PULSES_CNT, 2):
            total_cnt += pulse_cnt[i]

        # Low level ( 50 us) average counter
        average_cnt = total_cnt / (self.PULSES_CNT - 1)
        # print("low level average loop = %d" % average_cnt)
       
        data = ''
        for i in range(3, 2 * self.PULSES_CNT, 2):
            if pulse_cnt[i] > average_cnt:
                data += '1'
            else:
                data += '0'
        
        data0 = int(data[ 0: 8], 2)
        data1 = int(data[ 8:16], 2)
        data2 = int(data[16:24], 2)
        data3 = int(data[24:32], 2)
        data4 = int(data[32:40], 2)

        if fix_crc and data4 != ((data0 + data1 + data2 + data3) & 0xFF):
            data4 = data4 ^ 0x01
            data = data[0: self.PULSES_CNT - 2] + ('1' if data4 & 0x01 else '0')

        if data4 == ((data0 + data1 + data2 + data3) & 0xFF):
            if self._dht_type == self.DHT_TYPE['DHT11']:
                humi = int(data0)
                temp = int(data2)
            elif self._dht_type == self.DHT_TYPE['DHT22']:
                humi = float(int(data[ 0:16], 2)*0.1)
                temp = float(int(data[17:32], 2)*0.2*(0.5-int(data[16], 2)))
        else:
            # print("checksum error!")
            return None, "checksum error!"

        return humi, temp

    def read(self, retries = 15):
        for i in range(retries):
            humi, temp = self._read()
            if not humi is None:
                break
        if humi is None:
            return self._last_humi, self._last_temp
        self._last_humi,self._last_temp = humi, temp
        return humi, temp

#for pin in range(0, 50):
#	try:
#		print(pin)
#		x = mraa.Gpio(pin)
#		t = x.read()
sensor = DHT("11", 0)
humi, temp = sensor.read()
print('DHT{0}, humidity {1:.1f}%, temperature {2:.1f}*'.format(sensor.dht_type, humi, temp))
#	except Exception as e:
#		pass


