import io
import re
import unicodedata
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import signal as sp_signal
from scipy.io import wavfile


SAMPLE_RATE = 44100
DEFAULT_DURATION = 0.5
AMPLITUDE = 0.25
SEQUENCE_GAP = 0.02

OCTAVE_MIN = -3
OCTAVE_MAX = 3

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


@st.cache_data
def read_markdown_file(filename: str) -> str:
    app_dir = Path(__file__).resolve().parent
    file_path = app_dir / filename
    return file_path.read_text(encoding="utf-8")


@st.cache_data
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


def load_documentation() -> tuple[dict[str, str], dict[str, str]]:
    try:
        documentation_fr = read_markdown_file("documentation_fr.md")
        doc_fr_sections = split_markdown_by_h2(documentation_fr)
    except FileNotFoundError:
        doc_fr_sections = {
            "Documentation not found": "The file `documentation_fr.md` was not found."
        }

    try:
        documentation_en = read_markdown_file("documentation_en.md")
        doc_en_sections = split_markdown_by_h2(documentation_en)
    except FileNotFoundError:
        doc_en_sections = {
            "Documentation not found": "The file `documentation_en.md` was not found."
        }

    return doc_fr_sections, doc_en_sections


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text.lower().strip()


def generate_tone(
    frequency: float,
    duration: float,
    sample_rate: int = SAMPLE_RATE,
    amplitude: float = AMPLITUDE,
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


def change_octave(current_octave: int | None, delta: int) -> tuple[int, str, str]:
    octave = max(OCTAVE_MIN, min(OCTAVE_MAX, int(current_octave or 0) + delta))
    return octave, f"{octave:+d}", f"Octave set to {octave:+d}"


def create_time_plot(audio: np.ndarray, sample_rate: int) -> go.Figure:
    time = np.arange(len(audio)) / sample_rate

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time,
            y=audio,
            mode="lines",
            name="Signal",
        )
    )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        template="plotly_white",
        margin=dict(l=60, r=20, t=20, b=50),
    )
    return fig


def create_frequency_plot(audio: np.ndarray, sample_rate: int) -> go.Figure:
    spectrum = np.abs(np.fft.rfft(audio))
    frequencies = np.fft.rfftfreq(len(audio), d=1 / sample_rate)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frequencies,
            y=spectrum,
            mode="lines",
            name="Spectrum",
        )
    )
    fig.update_layout(
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
        template="plotly_white",
        margin=dict(l=60, r=20, t=20, b=50),
    )
    fig.update_xaxes(range=[0, min(2000, sample_rate / 2)])
    return fig


def create_time_frequency_plot(audio: np.ndarray, sample_rate: int) -> go.Figure:
    nperseg = min(1024, len(audio))
    noverlap = nperseg // 2

    frequencies, times, spectrogram = sp_signal.spectrogram(
        audio,
        fs=sample_rate,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        scaling="density",
        mode="psd",
    )

    spectrogram_db = 10 * np.log10(np.maximum(spectrogram, 1e-12))

    fig = go.Figure(
        data=go.Heatmap(
            x=times,
            y=frequencies,
            z=spectrogram_db,
            colorscale="Magma",
            colorbar=dict(title="PSD (dB)"),
        )
    )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        template="plotly_white",
        margin=dict(l=60, r=20, t=20, b=50),
    )
    fig.update_yaxes(range=[0, min(2000, sample_rate / 2)])
    return fig


def build_outputs(audio: np.ndarray, status: str) -> tuple[np.ndarray, go.Figure, go.Figure, go.Figure, str]:
    time_plot = create_time_plot(audio, SAMPLE_RATE)
    frequency_plot = create_frequency_plot(audio, SAMPLE_RATE)
    time_frequency_plot = create_time_frequency_plot(audio, SAMPLE_RATE)
    return audio, time_plot, frequency_plot, time_frequency_plot, status


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


def generate_sequence_audio(
    sequence_text: str,
    base_octave: int,
    duration: float,
) -> tuple[np.ndarray, list[str]]:
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


def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> bytes:
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio * 32767.0).astype(np.int16)

    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, audio_int16)
    return buffer.getvalue()


def initialise_session_state() -> None:
    defaults = {
        "octave": 0,
        "status": "Ready",
        "status_kind": "info",
        "audio": None,
        "time_plot": None,
        "frequency_plot": None,
        "time_frequency_plot": None,
        "selected_doc_fr": None,
        "selected_doc_en": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_status(message: str, kind: str = "info") -> None:
    st.session_state.status = message
    st.session_state.status_kind = kind


def store_generated_outputs(
    audio: np.ndarray | None,
    time_plot: go.Figure | None,
    frequency_plot: go.Figure | None,
    time_frequency_plot: go.Figure | None,
    status: str,
    status_kind: str = "success",
) -> None:
    st.session_state.audio = audio
    st.session_state.time_plot = time_plot
    st.session_state.frequency_plot = frequency_plot
    st.session_state.time_frequency_plot = time_frequency_plot
    set_status(status, status_kind)


def octave_down_callback() -> None:
    octave, _, status = change_octave(st.session_state.octave, -1)
    st.session_state.octave = octave
    set_status(status, "info")


def octave_up_callback() -> None:
    octave, _, status = change_octave(st.session_state.octave, +1)
    st.session_state.octave = octave
    set_status(status, "info")


def play_note_callback(note_name: str) -> None:
    audio, time_plot, frequency_plot, time_frequency_plot, status = play_note(
        note_name=note_name,
        octave=st.session_state.octave,
        duration=st.session_state.duration_input,
    )
    store_generated_outputs(
        audio,
        time_plot,
        frequency_plot,
        time_frequency_plot,
        status,
        "success",
    )


def play_sequence_callback() -> None:
    audio, time_plot, frequency_plot, time_frequency_plot, status = play_sequence(
        sequence_text=st.session_state.sequence_input,
        octave=st.session_state.octave,
        duration=st.session_state.duration_input,
    )

    if audio is None:
        store_generated_outputs(None, None, None, None, status, "error")
    else:
        store_generated_outputs(
            audio,
            time_plot,
            frequency_plot,
            time_frequency_plot,
            status,
            "success",
        )


def set_doc_section(state_key: str, title: str) -> None:
    st.session_state[state_key] = title


def show_status() -> None:
    message = st.session_state.status
    kind = st.session_state.status_kind

    if kind == "error":
        st.error(message)
    elif kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.info(message)


def render_app_tab() -> None:
    control_cols = st.columns([1, 1, 1, 2])

    with control_cols[0]:
        st.button(
            "Octave -",
            key="octave_down_button",
            on_click=octave_down_callback,
            width="stretch",
        )

    with control_cols[1]:
        st.text_input(
            "Current octave",
            value=f"{st.session_state.octave:+d}",
            disabled=True,
        )

    with control_cols[2]:
        st.button(
            "Octave +",
            key="octave_up_button",
            on_click=octave_up_callback,
            width="stretch",
        )

    with control_cols[3]:
        st.number_input(
            "Duration per note (s)",
            min_value=0.1,
            max_value=5.0,
            value=DEFAULT_DURATION,
            step=0.05,
            format="%.2f",
            key="duration_input",
        )

    note_cols = st.columns(len(NOTES))
    for column, note_name in zip(note_cols, NOTES.keys()):
        with column:
            st.button(
                note_name,
                key=f"note_button_{note_name}",
                type="primary",
                on_click=play_note_callback,
                args=(note_name,),
                width="stretch",
            )

    sequence_cols = st.columns([4, 1])
    with sequence_cols[0]:
        st.text_area(
            "Sequence of notes",
            placeholder="Example: Do Re Mi Fa Sol La Si or Do+1 Re Mi Sol-1",
            height=90,
            key="sequence_input",
        )

    with sequence_cols[1]:
        st.write("")
        st.write("")
        st.button(
            "Play sequence",
            key="sequence_button",
            type="primary",
            on_click=play_sequence_callback,
            width="stretch",
        )

    if st.session_state.audio is not None:
        st.audio(
            audio_to_wav_bytes(st.session_state.audio, SAMPLE_RATE),
            format="audio/wav",
            autoplay=True,
            width="stretch",
        )

        plot_cols = st.columns(3)
        with plot_cols[0]:
            st.plotly_chart(
                st.session_state.time_plot,
                width="stretch",
                config={"scrollZoom": True},
            )
        with plot_cols[1]:
            st.plotly_chart(
                st.session_state.frequency_plot,
                width="stretch",
                config={"scrollZoom": True},
            )
        with plot_cols[2]:
            st.plotly_chart(
                st.session_state.time_frequency_plot,
                width="stretch",
                config={"scrollZoom": True},
            )

    show_status()


def render_documentation_tab(
    sections: dict[str, str],
    state_key: str,
) -> None:
    titles = list(sections.keys())
    if not titles:
        st.warning("No documentation section found.")
        return

    if st.session_state[state_key] not in titles:
        st.session_state[state_key] = titles[0]

    button_col, markdown_col = st.columns([1, 2])

    with button_col:
        for index, title in enumerate(titles):
            st.button(
                title,
                key=f"{state_key}_{index}",
                on_click=set_doc_section,
                args=(state_key, title),
                width="stretch",
            )

    with markdown_col:
        selected_title = st.session_state[state_key]
        st.markdown(sections[selected_title])


def main() -> None:
    st.set_page_config(
        page_title="Pure Tone Generator",
        layout="wide",
    )

    initialise_session_state()
    doc_fr_sections, doc_en_sections = load_documentation()

    app_tab, doc_fr_tab, doc_en_tab = st.tabs(
        ["App", "Documentation FR", "Documentation EN"]
    )

    with app_tab:
        render_app_tab()

    with doc_fr_tab:
        render_documentation_tab(doc_fr_sections, "selected_doc_fr")

    with doc_en_tab:
        render_documentation_tab(doc_en_sections, "selected_doc_en")


if __name__ == "__main__":
    main()
