#!/usr/bin/env python3
"""
Spettro Frequenza — visualizzatore audio scenografico in tempo reale.
Ascolta il microfono, regola la sensibilità e mostra lo spettro animato.

Avvio:
  python3 spectrum_visualizer.py
  oppure doppio clic su avvia.command / avvia.bat / avvia.sh
"""

from __future__ import annotations

import argparse
import queue
import sys

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
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.widgets import Slider
except ImportError:
    print("Manca la libreria matplotlib.")
    print("Installa le dipendenze con:")
    print("  python3 -m pip install -r requirements.txt")
    sys.exit(1)


SAMPLE_RATE = 44_100
BLOCK_SIZE = 2048
N_FFT = 4096
N_BARS = 72
SMOOTHING = 0.68
MIN_FREQ = 40.0
MAX_FREQ = 16_000.0
DEFAULT_SENSITIVITY = 1.35  # 1.0 = neutro; >1 più sensibile
FLOOR_DB = -68.0


def stage_colormap() -> LinearSegmentedColormap:
    """Palette da bassi freddi ad acuti caldi (look da palco)."""
    return LinearSegmentedColormap.from_list(
        "stage",
        [
            "#062033",
            "#0e6b8a",
            "#1ad4b0",
            "#f2d06b",
            "#ff7a45",
            "#ff3d6e",
        ],
    )


def freq_edges(n_bars: int, sample_rate: int) -> np.ndarray:
    return np.geomspace(MIN_FREQ, min(MAX_FREQ, sample_rate / 2 - 1), n_bars + 1)


def bin_spectrum(magnitudes: np.ndarray, freqs: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Raggruppa i bin FFT in barre logaritmiche (veloce)."""
    idx = np.digitize(freqs, edges) - 1
    bars = np.zeros(len(edges) - 1, dtype=np.float64)
    counts = np.zeros(len(edges) - 1, dtype=np.int32)
    valid = (idx >= 0) & (idx < len(bars))
    np.add.at(bars, idx[valid], magnitudes[valid])
    np.add.at(counts, idx[valid], 1)
    nonzero = counts > 0
    bars[nonzero] /= counts[nonzero]
    return bars


class SpectrumVisualizer:
    def __init__(
        self,
        device: int | str | None = None,
        list_devices: bool = False,
        sensitivity: float = DEFAULT_SENSITIVITY,
    ):
        if list_devices:
            print(sd.query_devices())
            sys.exit(0)

        self.device = device
        self.sensitivity = float(np.clip(sensitivity, 0.2, 4.0))
        self.audio_q: queue.Queue[np.ndarray] = queue.Queue(maxsize=8)
        self.stream: sd.InputStream | None = None
        self.window = np.hanning(N_FFT).astype(np.float32)
        self.edges = freq_edges(N_BARS, SAMPLE_RATE)
        self.centers = np.sqrt(self.edges[:-1] * self.edges[1:])
        self.x_line = np.arange(N_BARS, dtype=np.float64)
        self.smoothed = np.zeros(N_BARS, dtype=np.float64)
        self.peaks = np.zeros(N_BARS, dtype=np.float64)
        self.wave_buf = np.zeros(BLOCK_SIZE, dtype=np.float32)
        self.cmap = stage_colormap()
        self.pulse = 0.0
        self.t = 0.0

        plt.rcParams["font.family"] = "DejaVu Sans"
        self.fig = plt.figure(figsize=(13.5, 7.6), facecolor="#03070d")
        try:
            self.fig.canvas.manager.set_window_title("Spettro Frequenza — Live")
        except Exception:  # noqa: BLE001
            pass

        # Layout: scena principale + slider sensibilità
        self.ax = self.fig.add_axes([0.06, 0.20, 0.88, 0.70])
        self.ax_wave = self.fig.add_axes([0.06, 0.905, 0.88, 0.055], sharex=None)
        self.ax_slider = self.fig.add_axes([0.18, 0.06, 0.58, 0.04])

        self._style_stage()
        self._build_artists()
        self._build_controls()
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)

    def _style_stage(self) -> None:
        self.ax.set_facecolor("#050b14")
        self.ax_wave.set_facecolor("#03070d")
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        for spine in self.ax_wave.spines.values():
            spine.set_visible(False)

        self.ax.set_xlim(-1.5, N_BARS + 0.5)
        self.ax.set_ylim(-1.15, 1.25)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.ax_wave.set_xlim(0, BLOCK_SIZE)
        self.ax_wave.set_ylim(-1.0, 1.0)
        self.ax_wave.set_xticks([])
        self.ax_wave.set_yticks([])

        # Vignetta / atmosfera
        self.ax.axhspan(-1.2, 0, color="#02060c", alpha=0.55, zorder=0)
        self.ax.axhline(0, color="#1a3348", linewidth=1.1, alpha=0.7, zorder=1)
        for y in (0.35, 0.7, 1.0, -0.35, -0.7, -1.0):
            self.ax.axhline(y, color="#102033", linewidth=0.6, alpha=0.35, zorder=1)

        self.title = self.ax.text(
            0.5,
            0.97,
            "SPETTRO FREQUENZA",
            transform=self.ax.transAxes,
            ha="center",
            va="center",
            color="#e8f4ff",
            fontsize=18,
            fontweight="bold",
            zorder=20,
        )

        self.subtitle = self.ax.text(
            0.5,
            0.915,
            "microfono live  ·  regolabile",
            transform=self.ax.transAxes,
            ha="center",
            va="center",
            color="#7f9bb0",
            fontsize=9,
            zorder=20,
        )
        self.status = self.ax.text(
            0.02,
            0.04,
            "In ascolto…",
            transform=self.ax.transAxes,
            ha="left",
            va="bottom",
            color="#6dffc2",
            fontsize=9,
            family="monospace",
            zorder=20,
        )
        self.hint = self.ax.text(
            0.98,
            0.04,
            "+ / −  sensibilità   ·   chiudi finestra per uscire",
            transform=self.ax.transAxes,
            ha="right",
            va="bottom",
            color="#5d7388",
            fontsize=8,
            zorder=20,
        )

        # Etichette frequenza decorative
        labels = ["40 Hz", "120", "400", "1k", "3k", "8k", "16k"]
        positions = np.linspace(0.04, 0.96, len(labels))
        for pos, lab in zip(positions, labels):
            self.ax.text(
                pos,
                0.5,
                lab,
                transform=self.ax.transAxes,
                ha="center",
                va="center",
                color="#2a4258",
                fontsize=7,
                zorder=2,
                alpha=0.85,
            )

    def _build_artists(self) -> None:
        base_colors = self.cmap(np.linspace(0.12, 0.98, N_BARS))
        widths = np.full(N_BARS, 0.78)

        # Bagliore ampio dietro
        self.glow_up = self.ax.bar(
            self.x_line,
            np.zeros(N_BARS),
            width=widths * 1.55,
            color=base_colors,
            align="center",
            edgecolor="none",
            alpha=0.18,
            zorder=3,
        )
        self.glow_dn = self.ax.bar(
            self.x_line,
            np.zeros(N_BARS),
            width=widths * 1.55,
            color=base_colors,
            align="center",
            edgecolor="none",
            alpha=0.12,
            zorder=3,
        )

        # Barre principali a specchio
        self.bars_up = self.ax.bar(
            self.x_line,
            np.zeros(N_BARS),
            width=widths,
            color=base_colors,
            align="center",
            edgecolor="none",
            alpha=0.95,
            zorder=5,
        )
        self.bars_dn = self.ax.bar(
            self.x_line,
            np.zeros(N_BARS),
            width=widths,
            color=base_colors,
            align="center",
            edgecolor="none",
            alpha=0.55,
            zorder=4,
        )

        # Curva inviluppo luminosa
        (self.env_line,) = self.ax.plot(
            self.x_line,
            np.zeros(N_BARS),
            color="#ffffff",
            linewidth=1.6,
            alpha=0.55,
            zorder=8,
        )
        self.env_fill = self.ax.fill_between(
            self.x_line,
            0,
            np.zeros(N_BARS),
            color="#1ad4b0",
            alpha=0.10,
            zorder=2,
        )

        # Picchi scintillanti
        (self.peak_dots,) = self.ax.plot(
            self.x_line,
            np.zeros(N_BARS),
            linestyle="None",
            marker="o",
            markersize=3.2,
            markerfacecolor="#fff6d8",
            markeredgecolor="#ff9f43",
            markeredgewidth=0.4,
            alpha=0.9,
            zorder=9,
        )
        (self.peak_dots_dn,) = self.ax.plot(
            self.x_line,
            np.zeros(N_BARS),
            linestyle="None",
            marker="o",
            markersize=2.4,
            markerfacecolor="#9fdfff",
            markeredgewidth=0,
            alpha=0.45,
            zorder=8,
        )

        # Forma d'onda in alto
        (self.wave_line,) = self.ax_wave.plot(
            np.arange(BLOCK_SIZE),
            np.zeros(BLOCK_SIZE),
            color="#1ad4b0",
            linewidth=1.1,
            alpha=0.85,
        )
        self.ax_wave.axhline(0, color="#1a3348", linewidth=0.6, alpha=0.6)

        # Cornice soft
        frame = FancyBboxPatch(
            (0.01, 0.01),
            0.98,
            0.98,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            transform=self.ax.transAxes,
            facecolor="none",
            edgecolor="#1c3348",
            linewidth=1.2,
            alpha=0.7,
            zorder=15,
        )
        self.ax.add_patch(frame)

    def _build_controls(self) -> None:
        self.ax_slider.set_facecolor("#0a121c")
        for spine in self.ax_slider.spines.values():
            spine.set_color("#24384c")

        self.sens_slider = Slider(
            ax=self.ax_slider,
            label="Sensibilità",
            valmin=0.25,
            valmax=3.5,
            valinit=self.sensitivity,
            valstep=0.05,
            color="#1ad4b0",
            track_color="#152433",
            handle_style={"facecolor": "#f2d06b", "edgecolor": "#f2d06b", "size": 10},
        )
        self.sens_slider.label.set_color("#c7d8e6")
        self.sens_slider.valtext.set_color("#f2d06b")
        self.sens_slider.on_changed(self._on_sensitivity)

        self.fig.text(
            0.5,
            0.025,
            "Trascina lo slider per regolare l’ampiezza dello spettro",
            ha="center",
            va="center",
            color="#5d7388",
            fontsize=8,
        )

    def _on_sensitivity(self, value: float) -> None:
        self.sensitivity = float(value)

    def _on_key(self, event) -> None:
        if event.key in ("+", "=", "up"):
            self.sensitivity = min(3.5, self.sensitivity + 0.1)
            self.sens_slider.set_val(self.sensitivity)
        elif event.key in ("-", "down"):
            self.sensitivity = max(0.25, self.sensitivity - 0.1)
            self.sens_slider.set_val(self.sensitivity)

    def _audio_callback(self, indata, frames, time_info, status) -> None:  # noqa: ARG002
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

        # Compressione dB + sensibilità utente
        bars = 20.0 * np.log10(bars + 1e-9)
        bars = (bars - FLOOR_DB) / (-FLOOR_DB)
        bars = np.clip(bars * self.sensitivity, 0.0, 1.0)
        # Leggera curva per rendere i bassi più “scenici”
        bars = np.power(bars, 0.85)
        return bars

    def _colorize(self, heights: np.ndarray) -> np.ndarray:
        # Colore dipende da frequenza + ampiezza momentanea
        base = np.linspace(0.10, 0.95, N_BARS)
        boost = 0.18 * heights
        return self.cmap(np.clip(base + boost, 0.0, 1.0))

    def _update(self, _frame):
        chunks: list[np.ndarray] = []
        while True:
            try:
                chunks.append(self.audio_q.get_nowait())
            except queue.Empty:
                break

        self.t += 0.033
        if chunks:
            samples = np.concatenate(chunks).astype(np.float32)
            self.wave_buf = samples[-BLOCK_SIZE:]
            if len(self.wave_buf) < BLOCK_SIZE:
                pad = np.zeros(BLOCK_SIZE, dtype=np.float32)
                pad[-len(self.wave_buf) :] = self.wave_buf
                self.wave_buf = pad
            bars = self._compute_spectrum(samples)
            self.smoothed = SMOOTHING * self.smoothed + (1.0 - SMOOTHING) * bars
            self.peaks = np.maximum(self.peaks * 0.955, self.smoothed)
            energy = float(np.mean(self.smoothed))
            self.pulse = 0.75 * self.pulse + 0.25 * energy
            self.status.set_text(
                f"LIVE  ·  sensibilità {self.sensitivity:.2f}  ·  energia {energy * 100:.0f}%"
            )
            self.status.set_color("#6dffc2")
        else:
            self.smoothed *= 0.93
            self.peaks *= 0.97
            self.wave_buf *= 0.9
            self.pulse *= 0.92
            self.status.set_text("In attesa del microfono…")
            self.status.set_color("#f2d06b")

        # Leggero “respiro” scenico
        breath = 1.0 + 0.04 * np.sin(self.t * 2.2)
        heights = np.clip(self.smoothed * breath, 0.0, 1.08)
        peaks = np.clip(self.peaks, 0.0, 1.12)
        colors = self._colorize(heights)

        for i, h in enumerate(heights):
            self.bars_up[i].set_height(float(h))
            self.bars_dn[i].set_height(float(-h * 0.72))
            self.glow_up[i].set_height(float(h * 1.18))
            self.glow_dn[i].set_height(float(-h * 0.85))
            self.bars_up[i].set_color(colors[i])
            self.bars_dn[i].set_color(colors[i])
            self.glow_up[i].set_color(colors[i])
            self.glow_dn[i].set_color(colors[i])
            self.bars_up[i].set_alpha(0.88 + 0.12 * h)
            self.glow_up[i].set_alpha(0.10 + 0.22 * h)

        self.env_line.set_ydata(heights * 1.02)
        self.peak_dots.set_ydata(peaks * 1.04)
        self.peak_dots_dn.set_ydata(-peaks * 0.72)
        self.peak_dots.set_alpha(0.55 + 0.45 * self.pulse)

        # Aggiorna fill inviluppo
        self.env_fill.remove()
        self.env_fill = self.ax.fill_between(
            self.x_line,
            0,
            heights * 1.02,
            color="#1ad4b0",
            alpha=0.08 + 0.10 * self.pulse,
            zorder=2,
        )

        # Forma d'onda (normalizzata con sensibilità)
        wave = self.wave_buf * min(2.8, 0.9 + self.sensitivity * 0.7)
        wave = np.clip(wave, -1.0, 1.0)
        self.wave_line.set_ydata(wave)
        self.wave_line.set_alpha(0.45 + 0.50 * self.pulse)

        # Titolo pulsa leggermente con l’energia
        self.title.set_alpha(0.75 + 0.25 * self.pulse)

        return ()

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
            print("\nSuggerimenti:")
            print("  1. Consenti l’accesso al microfono a Python / Terminale")
            print("  2. Elenca i dispositivi:")
            print("       python3 spectrum_visualizer.py --list-devices")
            print("  3. Scegline uno:")
            print("       python3 spectrum_visualizer.py --device 1")
            sys.exit(1)

        print("Spettro Frequenza avviato.")
        print("  · Slider / tasti + −  →  regola la sensibilità")
        print("  · Chiudi la finestra per uscire")
        anim = FuncAnimation(
            self.fig,
            self._update,
            interval=33,
            blit=False,
            cache_frame_data=False,
        )
        self._anim = anim
        try:
            plt.show()
        finally:
            self.stop()

    def stop(self) -> None:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spettro audio scenografico dal microfono (Python 3)."
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
    parser.add_argument(
        "--sensitivity",
        type=float,
        default=DEFAULT_SENSITIVITY,
        help=f"Sensibilità iniziale (default {DEFAULT_SENSITIVITY})",
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

    viz = SpectrumVisualizer(
        device=device,
        list_devices=args.list_devices,
        sensitivity=args.sensitivity,
    )
    viz.start()


if __name__ == "__main__":
    main()
