import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import urllib.request

url = "http://192.168.101.100:5000/tx-rx-raw"

def update(frame):
    # Descargar CSV en memoria
    with urllib.request.urlopen(url) as response:
        raw = response.read().decode("utf-8")

    # Convertir string CSV → array NumPy
    data = np.genfromtxt(
        raw.splitlines(),
        delimiter=";",
        names=True,
        dtype=None,
        encoding="utf-8"
    )

    # Normalizar si solo hay 1 fila
    if data.shape == ():
        data = np.array([data])

    bytes_rx = data["bytes_rx"]
    bytes_tx = data["bytes_tx"]
    timestamps = data["timestamp"]
    fechas = timestamps.astype("datetime64[s]")

    plt.cla()
    plt.plot(fechas, bytes_rx, label="Received B")
    plt.plot(fechas, bytes_tx, label="Transmitted B")

    plt.title("Monitoreo transmisión y recibo de Bytes")
    plt.xlabel("Hora")
    plt.ylabel("B")
    plt.legend()
    plt.tight_layout()

ani = FuncAnimation(plt.gcf(), update, interval=1000)
plt.show()