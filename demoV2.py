import RPi.GPIO as GPIO
import time
import threading
import bme680
from sense_hat import SenseHat
print("Demo by Ayub Sultan n01492500")
sense = SenseHat()
# Initialize the BME680 sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)



# LED Control Class
class LED_TEST:
    def __init__(self, led_pin):
        self.led_pin = led_pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led_pin, GPIO.OUT)

    def turn_on(self):
        GPIO.output(self.led_pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.led_pin, GPIO.LOW)

# Sensor Reading Function
def display_data(stop_event, offset=0):
    while not stop_event.is_set():
        sensor.set_temp_offset(offset)
        sensor.get_sensor_data()
        output = '{0:.2f} C, {1:.2f} hPa, {2:.3f} %RH'.format(
            sensor.data.temperature,
            sensor.data.pressure,
            sensor.data.humidity)
        print(output)
        print('')
        time.sleep(1)

def blink_led(led, stop_event, offset=0):
    while not stop_event.is_set():
        sensor.set_temp_offset(offset)
        sensor.get_sensor_data()
        temp = sensor.data.temperature

        # Map temperature (15°C to 35°C) to blink delay (1s to 0.1s)
        # Lower temp → slower blink (higher delay)
        # Higher temp → faster blink (lower delay)
        temp = max(15, min(35, temp))  # Clamp temp between 15–35
        delay = 1.1 - ((temp - 15) / 20.0)  # Maps 15→1s, 35→0.1s

        led.turn_on()
        time.sleep(delay)
        led.turn_off()
        time.sleep(delay)

        print(f"Temp: {temp:.1f}°C, Blink Delay: {delay:.2f}s")
        
def SenseTemp(stop_event, offset=0):
    # 3x5 font patterns for digits 0–9
    digits = {
        '0': ["111", "101", "101", "101", "111"],
        '1': ["010", "110", "010", "010", "111"],
        '2': ["111", "001", "111", "100", "111"],
        '3': ["111", "001", "111", "001", "111"],
        '4': ["101", "101", "111", "001", "001"],
        '5': ["111", "100", "111", "001", "111"],
        '6': ["111", "100", "111", "101", "111"],
        '7': ["111", "001", "010", "100", "100"],
        '8': ["111", "101", "111", "101", "111"],
        '9': ["111", "101", "111", "001", "111"]
    }

    white = [255, 255, 255]
    black = [0, 0, 0]

    while not stop_event.is_set():
        sensor.set_temp_offset(offset)
        sensor.get_sensor_data()
        temp = int((sensor.data.temperature))  # Use only the integer part

        # Clamp to two-digit display (00–99)
        temp_str = str(temp)[-2:] if temp >= 10 else '0' + str(temp)

        # Create 8x8 blank grid
        pixels = [[black for _ in range(8)] for _ in range(8)]

        # Draw each digit using the 3x5 pattern
        for idx, digit in enumerate(temp_str):
            pattern = digits[digit]
            x_offset = idx * 4  # 0 for first digit, 4 for second

            for y, row in enumerate(pattern):
                for x, pixel in enumerate(row):
                    if x_offset + x < 8 and y < 5:
                        pixels[y][x_offset + x] = white if pixel == '1' else black

        # Flatten and update the display
        flat_pixels = sum(pixels, [])
        sense.set_pixels(flat_pixels)

        time.sleep(2)  # Update interval
# Demo Function Using Threads
def demo():
    print("Starting LED + Sensor demo with threads...")
    led = LED_TEST(led_pin=11)

    # Create a stop event to safely stop threads
    stop_event = threading.Event()

    # Create threads
    led_thread = threading.Thread(target=blink_led, args=(led, stop_event, 0))
    sensor_thread = threading.Thread(target=display_data, args=(stop_event,))
    sensehat_thread = threading.Thread(target=SenseTemp, args=(stop_event,))

    # Start threads
    led_thread.start()
    sensor_thread.start()
    sensehat_thread.start()


    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Demo stopped by user")
        stop_event.set()  # Signal threads to stop

    # Wait for threads to finish
    led_thread.join()
    sensor_thread.join()
    sensehat_thread.join()
def main():
    demo()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")
