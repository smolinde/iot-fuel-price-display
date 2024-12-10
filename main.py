# Import required libraries
import utime, network, urequests, ujson, sys
from machine import I2C, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from time import sleep

# Automatically set I2C parameters for LCD1602 display, don't change anything here
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
SDA = machine.Pin(0)
SCL = machine.Pin(1)
I2C_CONNECTION = I2C(0, sda = SDA, scl = SCL, freq=400000)
LCD = I2cLcd(I2C_CONNECTION, I2C_CONNECTION.scan()[0], I2C_NUM_ROWS, I2C_NUM_COLS)

# Replace with your WiFi credentials
WLAN_SSID = 'WiFi Name'
WLAN_PSK = 'YourSafeWiFiPassword123!' 

# Set up WiFi
WLAN = network.WLAN(network.STA_IF)
WLAN.active(True)

# Replace the values below with your API key and a station ID of your choice 
API_KEY = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
STATION_ID = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
URL = f'https://creativecommons.tankerkoenig.de/json/detail.php?id={STATION_ID}&apikey={API_KEY}'

# Set the fuel type here (default fuel type: 'e5')
# Available fuel types: 'diesel', 'e5', 'e10'
FUEL_TYPE = 'e5'

# Set the price display banner here (16 characters or less)
BANNER = 'My Pretty Banner'

# Set the refreshing rate in seconds here (default: 300)
REFRESHING_RATE = 300

# Left-bound print function for LCD1602 display
def print_lcd(text, row):
    LCD.move_to(0, row)
    LCD.putstr(text)

# Wipes the display before finishing the program
def clean_exit():
    LCD.clear()
    sys.exit()

# Entry point
try:
    # Try to connect to pre-configured WiFi network
    WLAN.connect(WLAN_SSID, WLAN_PSK)
    for i in range(0, 30):
        LCD.clear()
        print_lcd('Connecting to', 0)
        print_lcd(f'WLAN... ({i + 1}s)', 1)
        if WLAN.isconnected() == False:
            sleep(1)
            
        else:
            break

    LCD.clear()
    if WLAN.isconnected() == False:
        print_lcd('Connection to', 0)
        print_lcd('WLAN failed', 1)
        sleep(5)
        LCD.clear()
        sys.exit()
    else:
        print_lcd('WLAN connected!', 0)
        sleep(3)
        LCD.clear()

    # Loop forever main logic of live price display
    while True:
        try:
            # Send the URL request to tankerkoenig API with a timeout of 15 seconds
            response = urequests.get(URL, timeout = 15)

            # Load response content to a dictionary if response code is 200 - OK
            if response.status_code == 200:
                LCD.clear()
                data = ujson.loads(response.text)

                # Check whether server returns an error based on provided API key and station ID
                if data['ok'] is not True:
                    print_lcd('Parameter Error', 0)
                    sleep(5)
                    clean_exit()

                # Extract and round the price
                price = round(float(data['station'][FUEL_TYPE]), 2)
                    
                # Print the final result to LCD1602 display
                # If the price is e.g. 1.7, append a '0' for appealing look
                print_lcd(BANNER, 0)
                if (price * 100 % 10 == 0):
                    print_lcd(f'{price}0 EUR/L', 1)
                else:
                    print_lcd(f'{price} EUR/L', 1)

                # wait until next update
                sleep(REFRESHING_RATE)
            
            # Display HTTP error
            else:
                LCD.clear()
                print_lcd(f'HTTP Error - {response.status_code}', 0)
                sleep(5)

        # Handle loss of internet connection or loss of WiFi network
        except OSError:
            LCD.clear()
            if WLAN.isconnected() == False:
                print_lcd('Connection to', 0)
                print_lcd('WLAN is lost!', 1)
                sleep(5)
                clean_exit()

            else:
                print_lcd('Connection to', 0)
                print_lcd('server is lost!', 1)
                sleep(5)
                LCD.clear()
                print_lcd('Trying to', 0)
                print_lcd('reconnect...', 1)

# For debugging, do not remove this!
except KeyboardInterrupt:
    clean_exit()