import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import urllib.request

url = "http://192.168.101.100:5000/metrics-raw"

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

    cpu = data["cpu"]
    mem = data["mem"]
    disk = data["disk"]
    timestamps = data["timestamp"]
    fechas = timestamps.astype("datetime64[s]")

    plt.cla()
    plt.plot(fechas, cpu, label="CPU (%)")
    plt.plot(fechas, mem, label="Mem (%)")
    plt.plot(fechas, disk, label="Disco")

    plt.title("Monitoreo del servidor en tiempo real")
    plt.xlabel("Tiempo")
    plt.ylabel("Valores")
    plt.legend()
    plt.tight_layout()

ani = FuncAnimation(plt.gcf(), update, interval=1000)
plt.show()