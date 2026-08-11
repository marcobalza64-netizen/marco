#!/usr/bin/env python3
"""
Visualizzatore spettro audio in tempo reale.
Ascolta il microfono e mostra le frequenze in un grafico colorato.
"""

from __future__ import annotations

import argparse
import queue
import sys
import threading

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    print("Manca la libreria sounddevice.")
    print("Installa le dipendenze con:")
    print("  python3 -m pip install -r requirements.txt")
    sys.exit(1)
except OSError as exc:
    print("PortAudio non trovato (serve per il microfono).")
    print(f"Dettaglio: {exc}")
    print("Mac/Windows: di solito basta  pip install -r requirements.txt")
    print("Linux: sudo apt install libportaudio2 portaudio19-dev")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.colors import LinearSegmentedColormap
except ImportError:
    print("Manca la libreria matplotlib.")
    print("Installa le dipendenze con:")
    print("  python3 -m pip install -r requirements.txt")
    sys.exit(1)


SAMPLE_RATE = 44_100
BLOCK_SIZE = 2048
N_FFT = 4096
N_BARS = 96
SMOOTHING = 0.72
MIN_FREQ = 40.0
MAX_FREQ = 16_000.0
GAIN = 2.8


def build_colormap() -> LinearSegmentedColormap:
    """Gradiente caldo/freddo per le barre dello spettro."""
    return LinearSegmentedColormap.from_list(
        "spectrum",
        [
            "#0b1d3a",
            "#1b6ca8",
            "#2ec4b6",
            "#ffd166",
            "#ef476f",
            "#ff2d95",
        ],
    )


def freq_edges(n_bars: int, sample_rate: int) -> np.ndarray:
    """Bordi delle barre su scala logaritmica (più naturale all'orecchio)."""
    return np.geomspace(MIN_FREQ, min(MAX_FREQ, sample_rate / 2 - 1), n_bars + 1)


def bin_spectrum(magnitudes: np.ndarray, freqs: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Raggruppa i bin FFT nelle barre logaritmiche."""
    bars = np.zeros(len(edges) - 1, dtype=np.float64)
    for i in range(len(bars)):
        mask = (freqs >= edges[i]) & (freqs < edges[i + 1])
        if np.any(mask):
            bars[i] = float(np.mean(magnitudes[mask]))
    return bars


class SpectrumVisualizer:
    def __init__(self, device: int | str | None = None, list_devices: bool = False):
        if list_devices:
            print(sd.query_devices())
            sys.exit(0)

        self.device = device
        self.audio_q: queue.Queue[np.ndarray] = queue.Queue(maxsize=8)
        self.stream: sd.InputStream | None = None
        self.window = np.hanning(N_FFT).astype(np.float32)
        self.edges = freq_edges(N_BARS, SAMPLE_RATE)
        self.centers = np.sqrt(self.edges[:-1] * self.edges[1:])
        self.smoothed = np.zeros(N_BARS, dtype=np.float64)
        self.peaks = np.zeros(N_BARS, dtype=np.float64)
        self.lock = threading.Lock()
        self.cmap = build_colormap()
        self.running = True

        self.fig, self.ax = plt.subplots(figsize=(12, 6), facecolor="#070b14")
        self.ax.set_facecolor("#070b14")
        self.fig.canvas.manager.set_window_title("Spettro Audio — Microfono")

        colors = self.cmap(np.linspace(0.15, 0.95, N_BARS))
        widths = np.diff(self.edges) * 0.82
        self.bars = self.ax.bar(
            self.centers,
            np.zeros(N_BARS),
            width=widths,
            color=colors,
            align="center",
            edgecolor="none",
        )
        self.peak_line, = self.ax.plot(
            self.centers,
            np.zeros(N_BARS),
            color="#ffffff",
            linewidth=1.2,
            alpha=0.55,
            marker=".",
            markersize=3,
            linestyle="None",
        )

        self.ax.set_xscale("log")
        self.ax.set_xlim(self.edges[0], self.edges[-1])
        self.ax.set_ylim(0, 1.05)
        self.ax.set_xlabel("Frequenza (Hz)", color="#9fb3c8", fontsize=11)
        self.ax.set_ylabel("Livello", color="#9fb3c8", fontsize=11)
        self.ax.set_title(
            "Spettro audio in tempo reale",
            color="#e8eef7",
            fontsize=16,
            pad=14,
            fontweight="bold",
        )
        self.ax.tick_params(colors="#7f93a8")
        for spine in self.ax.spines.values():
            spine.set_color("#243447")
        self.ax.grid(True, which="both", axis="y", color="#1a2740", linewidth=0.7, alpha=0.8)
        self.status = self.ax.text(
            0.01,
            0.97,
            "In ascolto…",
            transform=self.ax.transAxes,
            va="top",
            ha="left",
            color="#7dffb3",
            fontsize=10,
            family="monospace",
        )
        self.fig.tight_layout()

    def _audio_callback(self, indata, frames, time_info, status) -> None:  # noqa: ARG002
        if status:
            # Non bloccare il callback audio: solo segnala.
            pass
        mono = indata[:, 0].copy()
        try:
            self.audio_q.put_nowait(mono)
        except queue.Full:
            try:
                self.audio_q.get_nowait()
            except queue.Empty:
                pass
            try:
                self.audio_q.put_nowait(mono)
            except queue.Full:
                pass

    def _compute_spectrum(self, samples: np.ndarray) -> np.ndarray:
        if len(samples) < N_FFT:
            padded = np.zeros(N_FFT, dtype=np.float32)
            padded[: len(samples)] = samples
            samples = padded
        else:
            samples = samples[-N_FFT:]

        spectrum = np.fft.rfft(samples * self.window)
        magnitudes = np.abs(spectrum) / (N_FFT / 2)
        freqs = np.fft.rfftfreq(N_FFT, d=1.0 / SAMPLE_RATE)
        bars = bin_spectrum(magnitudes, freqs, self.edges)

        # Compressione tipo dB per rendere leggibili sia sussurri che picchi.
        bars = 20.0 * np.log10(bars + 1e-8)
        bars = (bars + 70.0) / 70.0  # circa da -70 dB a 0 dB
        bars = np.clip(bars * GAIN, 0.0, 1.0)
        return bars

    def _update(self, _frame):
        chunks: list[np.ndarray] = []
        while True:
            try:
                chunks.append(self.audio_q.get_nowait())
            except queue.Empty:
                break

        if chunks:
            samples = np.concatenate(chunks).astype(np.float32)
            bars = self._compute_spectrum(samples)
            self.smoothed = SMOOTHING * self.smoothed + (1.0 - SMOOTHING) * bars
            self.peaks = np.maximum(self.peaks * 0.965, self.smoothed)
            self.status.set_text("In ascolto…  |  chiudi la finestra per uscire")
            self.status.set_color("#7dffb3")
        else:
            self.smoothed *= 0.94
            self.peaks *= 0.98
            self.status.set_text("In attesa del microfono…")
            self.status.set_color("#ffd166")

        for rect, height in zip(self.bars, self.smoothed):
            rect.set_height(float(height))
        self.peak_line.set_ydata(self.peaks)
        return (*self.bars, self.peak_line, self.status)

    def start(self) -> None:
        try:
            self.stream = sd.InputStream(
                device=self.device,
                channels=1,
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                dtype="float32",
                callback=self._audio_callback,
            )
            self.stream.start()
        except Exception as exc:  # noqa: BLE001
            print("\nImpossibile aprire il microfono.")
            print(f"Dettaglio: {exc}")
            print("\nSuggerimenti (Mac):")
            print("  1. Impostazioni di Sistema → Privacy e sicurezza → Microfono")
            print("     → abilita Terminal / iTerm / Python")
            print("  2. Elenca i dispositivi con:")
            print("       python3 spectrum_visualizer.py --list-devices")
            print("  3. Scegline uno con:")
            print("       python3 spectrum_visualizer.py --device 1")
            sys.exit(1)

        print("Spettro audio avviato. Chiudi la finestra per uscire.")
        anim = FuncAnimation(
            self.fig,
            self._update,
            interval=33,
            blit=False,
            cache_frame_data=False,
        )
        # Tieni un riferimento per evitare garbage collection.
        self._anim = anim
        try:
            plt.show()
        finally:
            self.stop()

    def stop(self) -> None:
        self.running = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualizza lo spettro audio del microfono in tempo reale."
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Indice o nome del microfono (vedi --list-devices)",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Elenca i dispositivi audio disponibili e esci",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device: int | str | None
    if args.device is None:
        device = None
    else:
        try:
            device = int(args.device)
        except ValueError:
            device = args.device

    viz = SpectrumVisualizer(device=device, list_devices=args.list_devices)
    viz.start()


if __name__ == "__main__":
    main()
