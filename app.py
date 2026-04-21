import re
import unicodedata

import gradio as gr
import numpy as np
import plotly.graph_objects as go
from scipy import signal as sp_signal

SAMPLE_RATE = 44100
DEFAULT_DURATION = 0.5
AMPLITUDE = 0.25
SEQUENCE_GAP = 0.02  # silence between notes in a sequence

NOTES = {
    "Do": 261.63,
    "Re": 293.66,
    "Mi": 329.63,
    "Fa": 349.23,
    "Sol": 392.00,
    "La": 440.00,
    "Si": 493.88,
}

NOTE_ALIASES = {
    "do": "Do",
    "re": "Re",
    "mi": "Mi",
    "fa": "Fa",
    "sol": "Sol",
    "la": "La",
    "si": "Si",
}

LATEX_DELIMITERS = [
    {"left": "$$", "right": "$$", "display": True},
    {"left": "$", "right": "$", "display": False},
]

with open("documentation_fr.md", "r", encoding="utf-8") as f:
    DOCUMENTATION_fr = f.read()

with open("documentation_en.md", "r", encoding="utf-8") as f:
    DOCUMENTATION_en = f.read()


def split_markdown_by_h2(markdown_text: str) -> dict[str, str]:
    sections = {}
    parts = re.split(r"(?m)^##\s+", markdown_text.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        lines = part.splitlines()
        title = lines[0].strip()

        if title.lower() in {"table des matières", "table of contents"}:
            continue

        sections[title] = "## " + part

    return sections


DOC_FR_SECTIONS = split_markdown_by_h2(DOCUMENTATION_fr)
DOC_EN_SECTIONS = split_markdown_by_h2(DOCUMENTATION_en)

DOC_FR_TITLES = list(DOC_FR_SECTIONS.keys())
DOC_EN_TITLES = list(DOC_EN_SECTIONS.keys())


def load_doc_fr_section(title: str) -> str:
    return DOC_FR_SECTIONS[title]


def load_doc_en_section(title: str) -> str:
    return DOC_EN_SECTIONS[title]
    

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text.lower().strip()


def generate_tone(
    frequency: float,
    duration: float,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = AMPLITUDE
) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = amplitude * np.sin(2 * np.pi * frequency * t)

    fade_duration = min(0.01, duration / 10)
    fade_samples = int(sample_rate * fade_duration)
    if fade_samples > 0 and 2 * fade_samples < len(audio):
        fade_in = np.linspace(0.0, 1.0, fade_samples)
        fade_out = np.linspace(1.0, 0.0, fade_samples)
        audio[:fade_samples] *= fade_in
        audio[-fade_samples:] *= fade_out

    return audio.astype(np.float32)


def sanitize_duration(duration: float | None) -> tuple[float, str | None]:
    if duration is None or duration <= 0:
        return DEFAULT_DURATION, f"Invalid duration, reset to {DEFAULT_DURATION:.2f} s"
    return float(duration), None


def change_octave(current_octave: int | None, delta: int):
    octave = int(current_octave or 0) + delta
    return octave, f"{octave:+d}", f"Octave set to {octave:+d}"


def create_time_plot(audio: np.ndarray, sample_rate: int):
    time = np.arange(len(audio)) / sample_rate

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time,
            y=audio,
            mode="lines",
            name="Signal"
        )
    )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        template="plotly_white"
    )
    return fig


def create_frequency_plot(audio: np.ndarray, sample_rate: int):
    spectrum = np.abs(np.fft.rfft(audio))
    frequencies = np.fft.rfftfreq(len(audio), d=1 / sample_rate)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frequencies,
            y=spectrum,
            mode="lines",
            name="Spectrum"
        )
    )
    fig.update_layout(
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        template="plotly_white"
    )
    fig.update_xaxes(range=[0, min(2000, sample_rate / 2)])
    return fig


def create_time_frequency_plot(audio: np.ndarray, sample_rate: int):
    nperseg = min(1024, len(audio))
    noverlap = nperseg // 2

    frequencies, times, spectrogram = sp_signal.spectrogram(
        audio,
        fs=sample_rate,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        scaling="density",
        mode="psd"
    )

    spectrogram_db = 10 * np.log10(np.maximum(spectrogram, 1e-12))

    fig = go.Figure(
        data=go.Heatmap(
            x=times,
            y=frequencies,
            z=spectrogram_db,
            colorscale="Magma",
            colorbar=dict(title="PSD (dB)")
        )
    )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        template="plotly_white"
    )
    fig.update_yaxes(range=[0, min(2000, sample_rate / 2)])
    return fig


def build_outputs(audio: np.ndarray, status: str):
    time_plot = create_time_plot(audio, SAMPLE_RATE)
    frequency_plot = create_frequency_plot(audio, SAMPLE_RATE)
    time_frequency_plot = create_time_frequency_plot(audio, SAMPLE_RATE)
    return (SAMPLE_RATE, audio), time_plot, frequency_plot, time_frequency_plot, status


def play_note(note_name: str, octave: int | None, duration: float | None):
    octave = int(octave or 0)
    duration, warning = sanitize_duration(duration)

    base_frequency = NOTES[note_name]
    frequency = base_frequency * (2 ** octave)
    audio = generate_tone(frequency=frequency, duration=duration)

    status = f"{note_name} - {frequency:.2f} Hz - {duration:.2f} s"
    if warning is not None:
        status = f"{warning} | {status}"

    return build_outputs(audio, status)


def parse_note_token(token: str, base_octave: int) -> tuple[str, int]:
    normalized = normalize_text(token)
    match = re.fullmatch(r"([a-z]+)([+-]\d+)?", normalized)

    if match is None:
        raise ValueError(
            f"Invalid token '{token}'. Use notes like Do Re Mi or Do+1 Sol-1"
        )

    note_part = match.group(1)
    octave_shift = int(match.group(2) or 0)

    if note_part not in NOTE_ALIASES:
        raise ValueError(
            f"Unknown note '{token}'. Allowed notes: Do Re Mi Fa Sol La Si"
        )

    note_name = NOTE_ALIASES[note_part]
    note_octave = base_octave + octave_shift
    return note_name, note_octave


def generate_sequence_audio(sequence_text: str, base_octave: int, duration: float) -> tuple[np.ndarray, list[str]]:
    tokens = [token for token in re.split(r"[\s,;|/]+", sequence_text.strip()) if token]

    if not tokens:
        raise ValueError("Please enter at least one note.")

    audio_segments = []
    played_notes = []
    gap = np.zeros(int(SEQUENCE_GAP * SAMPLE_RATE), dtype=np.float32)

    for index, token in enumerate(tokens):
        note_name, note_octave = parse_note_token(token, base_octave)
        frequency = NOTES[note_name] * (2 ** note_octave)
        note_audio = generate_tone(frequency=frequency, duration=duration)

        audio_segments.append(note_audio)
        if index < len(tokens) - 1:
            audio_segments.append(gap)

        played_notes.append(f"{note_name}{note_octave:+d}")

    full_audio = np.concatenate(audio_segments).astype(np.float32)
    return full_audio, played_notes


def play_sequence(sequence_text: str, octave: int | None, duration: float | None):
    octave = int(octave or 0)
    duration, warning = sanitize_duration(duration)

    try:
        audio, played_notes = generate_sequence_audio(sequence_text, octave, duration)
    except ValueError as error:
        return None, None, None, None, str(error)

    status = f"Sequence played: {' '.join(played_notes)} - {duration:.2f} s per note"
    if warning is not None:
        status = f"{warning} | {status}"

    return build_outputs(audio, status)


def make_note_handler(note_name: str):
    def handler(octave, duration):
        return play_note(note_name, octave, duration)
    return handler


with gr.Blocks(title="Monofrequency note generator") as demo:
    with gr.Tab("App"):
        octave_state = gr.State(0)

        with gr.Row():
            octave_down_button = gr.Button("Octave -")
            octave_display = gr.Textbox(
                label="Current octave",
                value="+0",
                interactive=False
            )
            octave_up_button = gr.Button("Octave +")
            duration_input = gr.Number(
                label="Duration per note (s)",
                value=DEFAULT_DURATION,
                precision=2,
                minimum=0.05,
                maximum=10.0,
                step=0.05
            )

        with gr.Row():
            note_buttons = []
            for note_name in NOTES.keys():
                note_buttons.append(gr.Button(note_name))

        with gr.Row():
            sequence_input = gr.Textbox(
                label="Sequence of notes",
                placeholder="Example: Do Re Mi Fa Sol La Si or Do+1 Re Mi Sol-1",
                lines=2
            )
            sequence_button = gr.Button("Play sequence")

        audio_output = gr.Audio(
            label="Generated note / sequence",
            autoplay=True,
            interactive=False,
            format="wav"
        )

        with gr.Row():
            time_plot_output = gr.Plot(label="Time view")
            frequency_plot_output = gr.Plot(label="Frequency view")
            time_frequency_plot_output = gr.Plot(label="Time-frequency view")

        status_box = gr.Textbox(label="Status", value="Ready", interactive=False)

        octave_down_button.click(
            fn=lambda octave: change_octave(octave, -1),
            inputs=[octave_state],
            outputs=[octave_state, octave_display, status_box]
        )

        octave_up_button.click(
            fn=lambda octave: change_octave(octave, +1),
            inputs=[octave_state],
            outputs=[octave_state, octave_display, status_box]
        )

        for note_name, button in zip(NOTES.keys(), note_buttons):
            button.click(
                fn=make_note_handler(note_name),
                inputs=[octave_state, duration_input],
                outputs=[
                    audio_output,
                    time_plot_output,
                    frequency_plot_output,
                    time_frequency_plot_output,
                    status_box
                ]
            )

        sequence_button.click(
            fn=play_sequence,
            inputs=[sequence_input, octave_state, duration_input],
            outputs=[
                audio_output,
                time_plot_output,
                frequency_plot_output,
                time_frequency_plot_output,
                status_box
            ]
        )

    with gr.Tab("Documentation FR"):
        with gr.Row():
            with gr.Column(scale=1):
                doc_fr_buttons = []
                for title in DOC_FR_TITLES:
                    btn = gr.Button(title)
                    doc_fr_buttons.append((btn, title))

            with gr.Column(scale=3):
                doc_fr_view = gr.Markdown(
                    value=load_doc_fr_section(DOC_FR_TITLES[0]),
                    latex_delimiters=LATEX_DELIMITERS
                )

        for btn, title in doc_fr_buttons:
            btn.click(
                lambda t=title: load_doc_fr_section(t),
                inputs=None,
                outputs=doc_fr_view,
            )

    with gr.Tab("Documentation EN"):
        with gr.Row():
            with gr.Column(scale=1):
                doc_en_buttons = []
                for title in DOC_EN_TITLES:
                    btn = gr.Button(title)
                    doc_en_buttons.append((btn, title))

            with gr.Column(scale=3):
                doc_en_view = gr.Markdown(
                    value=load_doc_en_section(DOC_EN_TITLES[0]),
                    latex_delimiters=LATEX_DELIMITERS
                )

        for btn, title in doc_en_buttons:
            btn.click(
                lambda t=title: load_doc_en_section(t),
                inputs=None,
                outputs=doc_en_view,
            )

demo.launch()