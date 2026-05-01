---
title: Music Note Generator Monofrequency
emoji: 😻
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 6.13.0
app_file: app.py
pinned: false
short_description: Generate notes, sequences, and live spectral displays easily
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Music Note Generator Monofrequency

This repository contains an interactive pure-tone music note generator.

The app synthesises monofrequency sinusoidal notes from the C major solfège scale, plays individual notes or note sequences, and displays the generated signal in the time, frequency, and time-frequency domains.

It is designed as an educational and portfolio demo for audio synthesis, musical acoustics, Fourier analysis, and spectrogram interpretation.

A Streamlit deployment is available here:

https://music-note-monofrequency.streamlit.app/

## Main features

- Generate pure sinusoidal tones for the seven notes:
  - Do,
  - Re,
  - Mi,
  - Fa,
  - Sol,
  - La,
  - Si.
- Control the global octave from `-3` to `+3`.
- Set the duration of each generated note.
- Generate note sequences from a text input.
- Use per-note octave shifts in sequences, such as `Do+1` or `Sol-1`.
- Listen to the generated note or sequence directly in the interface.
- Display the generated waveform in the time domain.
- Display the DFT magnitude spectrum in the frequency domain.
- Display a spectrogram in the time-frequency domain.
- Read the English and French documentation tabs.

## Method overview

The app generates a pure tone using the discrete-time sinusoidal model:

```text
s[n] = A sin(2 pi f n / fs)
```

where:

- `A` is the amplitude,
- `f` is the note frequency,
- `fs = 44100 Hz` is the sampling frequency,
- `n` is the sample index.

A short fade-in and fade-out envelope is applied to each generated tone to avoid audible clicks at the beginning and end of the sound.

The generated audio is stored as a floating-point waveform and played through the interface.

## Musical notes

The app implements the seven notes of the C major diatonic scale:

| Solfège | Scientific note | Frequency |
|---|---:|---:|
| Do | C4 | 261.63 Hz |
| Re | D4 | 293.66 Hz |
| Mi | E4 | 329.63 Hz |
| Fa | F4 | 349.23 Hz |
| Sol | G4 | 392.00 Hz |
| La | A4 | 440.00 Hz |
| Si | B4 | 493.88 Hz |

The reference is the standard concert pitch:

```text
A4 = 440 Hz
```

## Octave transposition

The octave control multiplies the base frequency by a power of 2:

```text
f_transposed = f_base * 2^k
```

where `k` is the selected octave shift.

For example:

- octave `+1` doubles the frequency,
- octave `-1` divides the frequency by 2.

The range is limited to `[-3, +3]` to keep the generated notes in a musically useful and comfortable listening range.

## Note sequences

The sequence input accepts notes separated by spaces, commas, semicolons, vertical bars, or slashes.

Examples:

```text
Do Re Mi Fa Sol La Si
```

```text
Do+1 Re Mi Sol-1
```

Each token can contain:

- a note name,
- an optional octave modifier such as `+1` or `-2`.

The app normalises accented inputs, so variants such as `Ré` are handled robustly.

A short silence gap is inserted between consecutive notes to make the sequence easier to hear.

## Visual analysis

The app provides three complementary visualisations.

### Time-domain view

The time-domain plot shows the raw waveform amplitude as a function of time.

For a pure tone, this view directly shows the sinusoidal oscillation and the short fade-in and fade-out envelope.

### Frequency-domain view

The frequency-domain plot displays the magnitude of the DFT spectrum.

For a pure tone, the spectrum contains one dominant peak located at the generated note frequency.

### Time-frequency view

The spectrogram shows how the frequency content evolves over time.

This is especially useful for note sequences, because different notes appear as successive horizontal frequency components.

## Repository structure

```text
.
├── app.py                 # Gradio / Hugging Face Space entry point
├── app_sl.py              # Streamlit version of the app
├── documentation_en.md    # English documentation
├── documentation_fr.md    # French documentation
├── requirements.txt       # Python dependencies
├── LICENSE.txt            # License file
└── README.md              # Repository and Hugging Face Space description
```

## Installation

Clone the repository:

```bash
git clone https://github.com/trungtin-dinh/music_note_generator_monofrequency.git
cd music_note_generator_monofrequency
```

Install the Python dependencies.

If `requirements.txt` is populated in your local version, use:

```bash
pip install -r requirements.txt
```

Otherwise, install the main dependencies manually:

```bash
pip install gradio streamlit numpy scipy plotly
```

## Run the Gradio app

```bash
python app.py
```

The local interface will usually be available at:

```text
http://127.0.0.1:7860
```

## Run the Streamlit app

```bash
streamlit run app_sl.py
```

The local interface will usually be available at:

```text
http://localhost:8501
```

## Hugging Face Space notes

The YAML block at the top of this README is used by Hugging Face Spaces.

The current metadata launches the Gradio version:

```yaml
sdk: gradio
app_file: app.py
```

If you want Hugging Face to launch the Streamlit version instead, update the metadata to:

```yaml
sdk: streamlit
app_file: app_sl.py
```

In that case, make sure `streamlit` is included in `requirements.txt`.

## Documentation

The repository includes two Markdown documentation files:

- `documentation_en.md` for the English documentation.
- `documentation_fr.md` for the French documentation.

These files explain acoustic waves, musical note frequencies, equal temperament, pure-tone synthesis, octave transposition, click suppression with amplitude envelopes, note sequence parsing, time-domain analysis, DFT spectrum analysis, spectrogram analysis, sampling, quantisation, and the audio generation pipeline.

## Notes and limitations

This app intentionally generates monofrequency pure tones.

Real musical instruments are richer because they contain harmonics, transients, resonances, and time-varying timbre. The goal here is not to simulate a full instrument, but to provide a clean and interpretable signal for learning audio synthesis and spectral analysis.

The generated tones can be loud depending on the listening setup. Start with a moderate volume.

## License

This project is released under the MIT License.

## Author

Developed by Trung-Tin Dinh as part of a portfolio of interactive signal, audio, image, and computer vision mini apps.
