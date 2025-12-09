import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import urllib.request

url = "http://servidor-diaz.local:5000/disk-raw"  # CSV: timestamp;disk;read_bps;write_bps

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
        encoding="utf-8",
        invalid_raise=False  # ignora líneas con errores, como header
    )

    # Normalizar si solo hay 1 fila
    if data.shape == ():
        data = np.array([data])

    disk = data["disk"]
    read_bps = data["read_bps"]
    write_bps = data["write_bps"]
    timestamps = data["timestamp"]
    fechas = timestamps.astype("datetime64[s]")

    plt.cla()
    plt.plot(fechas, read_bps, label="Disk Read (bytes/s)")
    plt.plot(fechas, write_bps, label="Disk Write (bytes/s)")
    plt.plot(fechas, disk, label="Disk Used (%)")

    plt.title("Monitoreo de Disco en tiempo real")
    plt.xlabel("Tiempo")
    plt.ylabel("Bytes / s / Uso")
    plt.legend()
    plt.tight_layout()

ani = FuncAnimation(plt.gcf(), update, interval=1000)
plt.show()