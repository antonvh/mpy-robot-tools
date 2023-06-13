# Runs the hotrod model with a bluetooth PS4 controller.
# Filters for a certain controller with mac address.

from mindstorms import MSHub, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from projects.mpy_robot_tools.serialtalk.auto import SerialTalk
from projects.mpy_robot_tools.pybricks import Motor, Port

# Create your objects here.
mshub = MSHub()
st = SerialTalk("B")
engine = Motor("E")
steer = Motor("F")

# Only allow this controller to connect
ps4 = b'70:20:84:75:69:5F'

mshub.speaker.beep()
# Find limit of front wheels
steer.run_until_stalled(-300, duty_limit=50)
steer.reset_angle(-210)
steer.reset_angle(-210) # Sometimes calling this once is not enough.
# Center front wheels
steer.run_target(300,0)

# Check whether a gamepad is connected. Returns 1 when connected
ack, connected = st.call('connected')
print(ack,connected)
if ack == "connectedack":
    if connected == 1:
        print("Gamepad connected")
        # Returns the Bluetooth address of the controller connected as index idx as a string in the format 'AA:BB:CC:11:22:33'
        ack, bluetooth_address = st.call('btaddress','B',0)
        print(bluetooth_address, " is connected")
        # Confgures the bluetooth address bluetooth_address (given as a string in the format 'AA:BB:CC:11:22:33') to be used as a filter for controllers to be connected. Dependoing on the btfilter setting, the filter will be active.
        st.call('btallow','17s',ps4)
        # Activaes the bluetooth filter. Values are 0 (not active) or 1 (active).
        filter_active = 1
        st.call('btfilter','B',filter_active)
        if bluetooth_address != ps4:
            print(bluetooth_address, ", connected but expected:", ps4)
            # Disconnectes the controller connect to index idx.
            st.call('btdisconnect','B',0)
else:
    print("LMS-ESP32 not connected over UART")
    raise SystemExit

while True:
    ack, connected = st.call('connected')
    print("waiting for connection from", ps4)
    if connected: break
    wait_for_seconds(1)

# Returns the status of the gamepad with 6 parameters: 
# myGamepad->buttons(),myGamepad->dpad(),myGamepad->axisX(),
# myGamepad->axisY(),myGamepad->axisRX(),myGamepad->axisRY())
print(st.call('gamepad'))


while True:
    # Get gamepad state with a low timeout, so we can quickly try again if comms fail.
    ack, gp = st.call('gamepad', timeout=50)
    if ack == 'gamepadack':
        fwd = gp[3]
        left = gp[4]
        engine.run(fwd * -2)
        steer.track_target(left * -0.2)
    else:
        steer.stop()
        engine.stop()
        print(ack,gp)
        

