import network
import socket
import machine
from time import sleep
import time

# Motor control pins
motor1_a = machine.Pin(2, machine.Pin.OUT)  
motor1_b = machine.Pin(3, machine.Pin.OUT)
motor1_PWM = machine.Pin(0, machine.Pin.OUT)
motor2_a = machine.Pin(4, machine.Pin.OUT)  
motor2_b = machine.Pin(5, machine.Pin.OUT)
motor2_PWM = machine.Pin(1, machine.Pin.OUT)

# Buzzer and note frequencies (in Hz)
buzzer = machine.PWM(machine.Pin(15))

NOTES = {
    'C4': 261,
    'D4': 294,
    'E4': 329,
    'F4': 349,
    'G4': 392,
    'A4': 440,
    'B4': 466,
    'C5': 523,
    'D5': 587,
    'E5': 659,
    'F5': 698,
    'G5': 784,
    'A5': 880,
    'B5': 988,
    'C6': 1047,
}

# Wi-Fi credentials
SSID = "CYBERTRON"
PASSWORD = "Mr.LamYo"

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("Connecting to Wi-Fi...")

while not wlan.isconnected():
    sleep(1)
print("Connected! IP: http://", wlan.ifconfig()[0])


# Function to control motors
def control_motors(direction):
    if direction == "centre":
        motor1_PWM.off()
        motor2_PWM.off()
    else:
        motor1_PWM.on()
        motor2_PWM.on()
    if direction == "forward":
        motor1_a.on()
        motor1_b.off()
        motor2_a.on()
        motor2_b.off()
    elif direction == "backward":
        motor1_a.off()
        motor1_b.on()
        motor2_a.off()
        motor2_b.on()
    elif direction == "left":
        motor1_a.off()
        motor1_b.on()
        motor2_a.on()
        motor2_b.off()
    elif direction == "right":
        motor1_a.on()
        motor1_b.off()
        motor2_a.off()
        motor2_b.on()
    else:  # Stop
        motor1_a.off()
        motor1_b.off()
        motor2_a.off()
        motor2_b.off()

def perform_stab():
    print("Stab action performed!")  # Replace with your motor or servo logic


# Function to play a note
def play_note(frequency, duration):
    buzzer.freq(frequency)  # Set the frequency
    buzzer.duty_u16(32768)  # Set a reasonable duty cycle (half of 65535)
    time.sleep(duration)     # Wait for the note to play
    buzzer.duty_u16(0)       # Turn off the buzzer


# HTML for the web interface
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Jousting Robot Controller</title>
    <style>
        body {
            text-align: center;
            background-color: #99CCFF;
        }
        
        #joystick-container {
            position: absolute;
            width: 350px;
            height: 350px;
            margin: 50px auto;
            background: #b3b3b3;
            border-radius: 50%;
            border: 2px solid #aaa;
        }
        
        #joystick {
            position: absolute;
            width: 100px;
            height: 100px;
            background: #007bff; /* Change color */
            border-radius: 50%;
            top: 125px; /* Centered within #joystick-container */
            left: 125px;
            touch-action: none;
        }
        
        #stabButton {
            position: absolute;
            width: 300px;
            height: 100px;
            background: #007bff;
            border: 2px solid black;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            top: 50px;
            left: 550px; /* Position on the page */
        }
      
        #retreatButton {
            position: absolute;
            width: 300px;
            height: 100px;
            background: #007bff;
            border: 2px solid black;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            top: 150px;
            left: 550px; /* Position on the page */
        }
      
        #soundButton {
            position: absolute;
            width: 300px;
            height: 100px;
            background: #007bff;
            border: 2px solid black;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            top: 275px;
            left: 550px; /* Position on the page */
        }
        
        #stabButton:hover {
            background: #0056b3;
        }
        
        #retreatButton:hover {
            background: #0056b3;
        }

        #soundButton:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div id="joystick-container">
        <div id="joystick"></div>
    </div>
    <button id="stabButton">Stab!</button>
    <button id="retreatButton">Retreat!</button>
    <button id="soundButton">Sound</button>
    <p id="status">Status: Waiting...</p>

    <script>
        document.addEventListener("DOMContentLoaded", () => {
            const joystick = document.getElementById("joystick");
            const container = document.getElementById("joystick-container");
            const status = document.getElementById("status");
            const stabButton = document.getElementById("stabButton");
            const retreatButton = document.getElementById("retreatButton");
            const soundButton = document.getElementById("soundButton");

            const containerRect = container.getBoundingClientRect();
            const joystickRadius = joystick.offsetWidth / 2;
            const containerRadius = container.offsetWidth / 2;

            let isDragging = false;

            joystick.addEventListener("pointerdown", () => isDragging = true);
            joystick.addEventListener("pointerup", resetJoystick);
            joystick.addEventListener("pointermove", (e) => isDragging && moveJoystick(e));
          
            stabButton.addEventListener("click", sendStabCommand);
            retreatButton.addEventListener("click", sendRetreatCommand);
            soundButton.addEventListener("click", sendSoundCommand);

            function resetJoystick() {
                isDragging = false;
                joystick.style.left = `${containerRadius - joystickRadius}px`;
                joystick.style.top = `${containerRadius - joystickRadius}px`;
                updateStatus("center");
            }

            function moveJoystick(event) {
                const x = event.clientX - containerRect.left;
                const y = event.clientY - containerRect.top;

                const dx = x - containerRadius, dy = y - containerRadius;
                const distance = Math.min(Math.hypot(dx, dy), containerRadius - joystickRadius);
                const angle = Math.atan2(dy, dx);

                joystick.style.left = `${Math.cos(angle) * distance + containerRadius - joystickRadius}px`;
                joystick.style.top = `${Math.sin(angle) * distance + containerRadius - joystickRadius}px`;

                const direction = getDirection(dx, dy);
                updateStatus(direction);
                sendCommand(direction);
            }

            function getDirection(dx, dy) {
                const threshold = containerRadius / 3;
                if (Math.abs(dx) < threshold && Math.abs(dy) < threshold) return "center";
                return Math.abs(dy) > Math.abs(dx) ? (dy > 0 ? "down" : "up") : (dx > 0 ? "right" : "left");
            }

            function updateStatus(direction) {
                status.textContent = `Status: Moving ${direction}`;
            }

            function sendCommand(direction) {
                fetch(`/${direction}`).catch(console.error);
            }

            function sendStabCommand() {
                fetch(`/stab`).then(() => {
                    updateStatus("stab!");
                }).catch(console.error);
            }

            function sendRetreatCommand() {
                fetch(`/retreat`).then(() => {
                    updateStatus("retreat!");
                }).catch(console.error);
            }

            function sendSoundCommand() {
                fetch(`/sound`).then(() => {
                    updateStatus("sound!");
                }).catch(console.error);
            }
        });
    </script>
</body>
</html>
"""

# Start web server
addr = socket.getaddrinfo("0.0.0.0", 8080)[0][-1]  # Port set to 8080
server = socket.socket()
server.bind(addr)
server.listen(1)
print("Listening on", addr)

# List of notes and durations for the song
song = [
    ('C4', 0.4),
    ('D4', 0.4),
    ('E4', 0.4),
    ('F4', 0.4),
    ('G4', 0.4),
    ('A4', 0.4),
    ('B4', 0.4),
    ('C5', 0.4),
    ('C4', 0.4),
]

while True:
    client, addr = server.accept()
    print("Client connected from", addr)
    request = client.recv(1024)
    request_str = str(request)
    print("Request:", request_str)

    # Serve the web page
    if '/stab' in request_str:
        perform_stab()
        client.send('HTTP/1.1 200 OK\n\nStab command received!')

    elif '/retreat' in request_str:
        control_motors("backward")
        client.send('HTTP/1.1 200 OK\n\nRetreat command received!')

    elif '/sound' in request_str:
        for note, duration in song:
            play_note(NOTES[note], duration)
        client.send('HTTP/1.1 200 OK\n\nSound command received!')

    elif '/' in request_str:
        # Default action
        client.send('HTTP/1.1 200 OK\n\n' + HTML)
    
    client.close()

