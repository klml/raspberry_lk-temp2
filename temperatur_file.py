import glob
import time
import csv
import threading
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO

logfile = "/var/www/html/temperatur.csv"
mete_delay = 10
round_digits = 1
verbose = False


global past_temperature
past_temperature = False


# Der One-Wire EingangsPin wird deklariert und der integrierte PullUp-Widerstand aktiviert
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Nach Aktivierung des Pull-UP Widerstandes wird gewartet,
# bis die Kommunikation mit dem DS18B20 Sensor aufgebaut ist
base_dir = '/sys/bus/w1/devices/'
while True:
    try:
        device_folder = glob.glob(base_dir + '28*')[0]
        break
    except IndexError:
        sleep(0.5)
        continue
device_file = device_folder + '/w1_slave'

# Funktion wird definiert, mit dem der aktuelle Messwert am Sensor ausgelesen werden kann
def TemperaturMessung():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
# Zur Initialisierung, wird der Sensor einmal "blind" ausgelesen
TemperaturMessung()


def TemperaturAuswertung():
    lines = TemperaturMessung()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = TemperaturMessung()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


def write_log_file( current_temperature ):
    date_temperatur = [0,0]
    date_temperatur[0] = datetime.now().replace(microsecond=0).isoformat()
    date_temperatur[1] = current_temperature

    with open( logfile , 'a') as csv_file:
        csv_file_writer = csv.writer( csv_file )
        csv_file_writer.writerow( date_temperatur )


def check_delta( past_temperature ):

    current_temperature = TemperaturAuswertung()
    threading.Timer( mete_delay, check_delta, [current_temperature] ).start()
    if ( round( current_temperature, round_digits ) != round( past_temperature, round_digits ) ):
        if verbose:
            print( 'temp changed')
            print( current_temperature )
            print( past_temperature )
        write_log_file( current_temperature )

check_delta( past_temperature )