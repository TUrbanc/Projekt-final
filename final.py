import numpy as np
import pyqtgraph as pg
import pyaudio
import sys
import socket

# Konstante
CHUNK = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FRAME_INTERVAL = 30  # Milisekunde
DEVICE_INDEX = 2

# Posiljanje esp-ju
def send_rgb_to_esp(rgb):
    UDP_IP = "192.168.217.206"
    UDP_PORT = 5555

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    rgb_str = ','.join(map(str, rgb))
    message = rgb_str.encode()

    sock.sendto(message, (UDP_IP, UDP_PORT))
    sock.close()


win = pg.plot()
win.setWindowTitle('Real-time Audio Spectrum Analyzer')
win.setLabel('left', 'Amplitude')
win.setLabel('bottom', 'Frequency', units='Hz')

audio_data = np.zeros(CHUNK)

p = pyaudio.PyAudio()

def update():
    global audio_data
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    audio_data = np.concatenate((audio_data[len(data):], data))
    spectrum = np.abs(np.fft.fft(audio_data))
    win.plot(x=np.linspace(0, RATE, len(spectrum) // 2), y=spectrum[:len(spectrum) // 2], clear=True)

    # Filtriranje
    spec_20_40 = spectrum[int(20 / RATE * len(spectrum)):int(40 / RATE * len(spectrum))]
    spec_40_60 = spectrum[int(40 / RATE * len(spectrum)):int(60 / RATE * len(spectrum))]
    spec_60_80 = spectrum[int(60 / RATE * len(spectrum)):int(80 / RATE * len(spectrum))]


    # Preverjanje amplitud / jakosti pri filtriranih vrednostih

    if np.max(spec_20_40) > 3000000:
        print("20 - 40 Hz")
        rgb_values = [0, 0, 255]

    elif np.max(spec_40_60) > 3000000:
        print("40 - 60 Hz")
        rgb_values = [0, 0, 130]

    elif np.max(spec_60_80) > 3000000:
        print("60 - 80 Hz")
        rgb_values = [0, 0, 30]

    else:
        print("other")
        rgb_values = [0, 0, 0]
        
    send_rgb_to_esp(rgb_values)
    app.processEvents()


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=DEVICE_INDEX)

app = pg.mkQApp()
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(FRAME_INTERVAL)

if __name__ == '__main__':
    if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        pg.QtGui.QGuiApplication.instance().exec_()
