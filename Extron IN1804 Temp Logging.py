import telnetlib
import pytz
import csv
import time
import schedule
from datetime import datetime
import threading
import os

FILENAME = 'IN1804_data_log.csv'
PASSWORD = ''
# List of devices (IP addresses or hostnames)
devices = [
    'device@address.here',
    'device@address.here',
]  # Add your devices here

edidTable = {
    '010': "640x480 60Hz",
    '011': "800x600 60Hz",
    '012': "1024x768 60Hz",
    '013': "1280x768 60Hz",
    '014': "1280x800 60Hz",
    '015': "1280x1024 60Hz",
    '016': "1360x768 60Hz",
    '017': "1366x768 60Hz",
    '018': "1440x900 60Hz",
    '019': "1400x1050 60Hz",
    '020': "1600x900 60Hz",
    '021': "1680x1050 60Hz",
    '022': "1600x1200 60Hz",
    '023': "1920x1200 60Hz",
    '024': "1920x1080 23.98Hz",
    '025': "1920x1080 24Hz",
    '026': "1920x1080 25Hz",
    '029': "1920x1080 29.97Hz",
    '030': "1920x1080 30Hz",
    '031': "1920x1080 50Hz",
    '032': "1920x1080 59.94Hz",
    '033': "1920x1080 60Hz",
    '034': "1920x1080p (progressive) @60 Hz",
    '035': "2560x1440 @60 Hz",
    '036': "2560x1600 @60 Hz",
    '037': "3840x2160 @24 Hz",
    '038': "3840x2160 @25 Hz",
    '039': "3840x2160 @30 Hz",
    '040': "3840x2160 @50 Hz",
    '041': "3840x2160 @60 Hz",
    '045': "1920x1080 60Hz",
    '046': "2048x1080 60Hz",
    '047': "2048x1080 60Hz",
    '048': "2048x1080 60Hz",
    '049': "2048x1080 60Hz",
    '050': "2048x1080 60Hz",
    '051': "2048x1080 60Hz",
    '052': "2048x1080 60Hz",
    '053': "2048x1080 60Hz",
    '054': "2048x1200 60Hz",
    '055': "2048x1536 60Hz",
    '056': "2560x1080 60Hz",
    '057': "2560x1440 60Hz",
    '058': "2560x1600 60Hz",
    '059': "3840x2160 24Hz",
    '060': "3840x2160 25Hz",
    '061': "3840x2160 30Hz",
    '062': "3840x2160 50Hz",
    '063': "3840x2160 60Hz",
    '064': "3840x2160 60Hz",
    '065': "3840x2160 60Hz",
    '066': "3840x2160 60Hz",
    '069': "4096x2160 24Hz",
    '070': "4096x2160 25Hz",
    '071': "4096x2160 30Hz",
    '073': "4096x2160 50Hz",
    '074': "4096x2160 60Hz",
    '075': "4096x2160 60Hz",
    '076': "4096x2160 60Hz",
    '201':'Custom EDID',
    '000':'Automatic',
    'E12':"Port N/A Display Off?",
    'E13':"Invalid Parameter"
}


def parse_info(data):
    #sampledata = "Vid1 Type3 Amt0 Vmt0 Hrt067.49 Vrt060.01"

    # Split the data string into individual components
    components = data.split()
    #print(f'Data: {components}')
    # Create a dictionary to map the components to their descriptions
    descriptions = {
        "Vid": "Input",
        "Type": "Type",
        "Amt": "Aud Mute",
        "Vmt": "Vid Mute",
        "Hrt": "Horz Freq",
        "Vrt": "Vert Freq"
    }

    # Create a dictionary to map type numbers to their corresponding text
    type_mapping = {
        "1": "DVI",
        "2": "HDMI",
        "3": "Displayport"
    }

    # Create a dictionary to map mute values to their corresponding text
    mute_mapping = {
        "0": "unmuted",
        "1": "muted"
    }

    # Parse the components and map them to their descriptions
    parsed_data = {}
    for component in components:
        key = component[:3]
        value = component[3:]
        if key in descriptions:
            if key == "Type":
                value = type_mapping.get(value, value)
            elif key in ["Amt", "Vmt"]:
                value = mute_mapping.get(value, value)
            parsed_data[descriptions[key]] = value

    # Print the parsed data
    #for description, value in parsed_data.items():
    #    print(f"{description}: {value}")
    #    print(parsed_data)
    return parsed_data

def monitor_telnet_output(tn, event):
    while not event.is_set():
        output = tn.read_some()
        #print(f'Monitoring output: {output}')
        if b"Password: " in output:
            print('Password is found')
            hashstring = f'{PASSWORD}\n'.encode('ascii')
            tn.write(password.encode('ascii') + hashstring)
        elif b"Login Administrator" in output:
            event.set()  # Stop monitoring once the login prompt is received
        elif b'Inf01*' in output:
            print('Model Name Detected')
        elif b'Pno' in output:
            print('Part Number')
        elif b'Bld' in output:
            print('Firmware')
        elif b'20Stat' in output:
            print('Temperature')            
    
def query_device(device, password):
    #print(f'Running Query on {device}')
    hashstring = f'{password}\n'.encode('ascii')
    try:
        tn = telnetlib.Telnet(device)
        #print(f'Telnet connection established: {tn}')
        password_prompt_count = 0

        # Create an event to stop the monitoring thread
        stop_event = threading.Event()

        # Start the monitoring thread
        #print('Monitoring Thread')
        monitor_thread = threading.Thread(target=monitor_telnet_output, args=(tn, stop_event))
        #print('Monitoring Thread Start')
        monitor_thread.start()
        tn.write(hashstring)
        tn.write(hashstring)
        
        # Wait for the login prompt to be received
        #print('Monitoring Thread Join')
        monitor_thread.join()
        tn.write(b"w1CV\n")
        verbose = tn.read_some().decode('ascii').strip()
        # Send commands
        tn.write(b"1I\n")
        name = tn.read_some().decode('ascii').strip()
        #print(f'Device name: {name}')
        tn.write(b"*Q\n")
        firmware = tn.read_some().decode('ascii').strip()
        #print(f'Firmware: {firmware}')
        tn.write(b"N\n")
        model = tn.read_some().decode('ascii').strip()
        #print(f'Model: {model}')
        tn.write(b"w20STAT\n")
        temperature_celsius = tn.read_some().decode('ascii').strip()
        #print(f'Temperature (Celsius): {temperature_celsius}')
        # Convert temperature to Fahrenheit
        temperature_fahrenheit = round((float(temperature_celsius) * 9/5) + 32, 1)
        #print(f'Temperature (Fahrenheit): {temperature_fahrenheit}')
        
        tn.write(b"V\n")
        volume = tn.read_some().decode('ascii').strip()
        #print(volume)
        tn.write(b"!\n")
        avInput = tn.read_some().decode('ascii').strip()
        #print(f'AV Input: {avInput}')
        
        tn.write(b"w0LS\n")
        signalDetect = tn.read_some().decode('ascii').strip()
        signals = signalDetect.split("*")
        
        tn.write(b"Z\n")
        audioMute = tn.read_some().decode('ascii').strip()
        
        dataTx = f'{avInput}*\\\n'.encode('ascii')
        tn.write(dataTx)
        inputStatus = tn.read_some().decode('ascii').strip()
        if '0' in inputStatus:inputStatus = 'No Signal'
        if '2' in inputStatus:inputStatus = 'HDMI'
        if '3' in inputStatus:inputStatus = 'DisplayPort'
        if '1' in inputStatus:inputStatus = 'DVI'
       
        dataTx = f'{avInput}*\\\n'.encode('ascii')
        tn.write(dataTx)
        signalStatus = tn.read_some().decode('ascii').strip()
        
        dataTx = f'{avInput}*I\n'.encode('ascii')
        tn.write(dataTx)
        signalInfo = tn.read_some().decode('ascii').strip()
        signalDict = parse_info(signalInfo)
        #signalDict = ["Active" if '1' in x else "No signal" for x in signalDict]
        
        
        dataTx = f'wA{avInput}EDID\n'.encode('ascii')
        tn.write(dataTx)
        inputEdid = tn.read_some().decode('ascii').strip()       
        inputEdid = edidTable[inputEdid]
        
        
        dataTx = f'w{avInput}APIX\n'.encode('ascii')
        tn.write(dataTx)
        inputRes = tn.read_some().decode('ascii').strip()
        
 
        dataTx = f'w{avInput}ALIN\n'.encode('ascii')
        tn.write(dataTx)
        inputRes = f'{inputRes}x{tn.read_some().decode("ascii").strip()}'
        print(f'{inputRes}')
 
        dataTx = f'w{1}RATE\n'.encode('ascii')
        tn.write(dataTx)
        resolution1 = edidTable[tn.read_some().decode('ascii').strip()]      

        dataTx = f'w{2}RATE\n'.encode('ascii')
        tn.write(dataTx)
        resolution2 = edidTable[tn.read_some().decode('ascii').strip()]
        
        tn.write(b"w3CV\n")
        tn.close()

        pst_timezone = pytz.timezone('America/Los_Angeles')
        timestamp = datetime.now(pst_timezone).strftime('%Y-%m-%d %H:%M:%S')
        file_exists = os.path.isfile(FILENAME)
        # Write to CSV file
        with open(FILENAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                # Write header row if file does not exist
                writer.writerow(['Timestamp', 'Name', 'Device', 'Model', 'Firmware','Temp (F)','AV Input','Input Type', 'Input EDID Set','Active Res', 'In1 Signal','In2 Signal','In3 Signal', 'In4 Signal', 'Volume', 'Audio Mute','Video Mute','Horz Freq', 'Vert Freq', 'Output 1 Res','Output 2 Res'])
                
            print (timestamp, name, device, model, firmware, temperature_fahrenheit)
            writer.writerow([timestamp, name, device, model, firmware, temperature_fahrenheit, avInput,inputStatus,inputEdid, inputRes, signals[0],signals[1],signals[2],signals[3],volume,signalDict['Aud Mute'],signalDict['Vid Mute'],float(signalDict['Horz Freq']), float(signalDict['Vert Freq']),resolution1,resolution2])

    except Exception as e:
        print(f"Failed to query {device}: {e}")
        

def job():
    pst_timezone = pytz.timezone('America/Los_Angeles')
    RunTime = timestamp = datetime.now(pst_timezone).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print (f'Running Query {RunTime}')
    for device in devices:
        query_device(device,PASSWORD)

# Schedule the job every 5 minutes
job()
schedule.every(5).minutes.do(job)

print("Starting the script. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)

