## Table of Contents

1. [Acoustics and Musical Notes: Physical Background](#1-acoustics-and-musical-notes-physical-background)
2. [The Equal Temperament Scale](#2-the-equal-temperament-scale)
3. [Pure Tone Synthesis: The Sinusoidal Model](#3-pure-tone-synthesis-the-sinusoidal-model)
4. [Octave Transposition](#4-octave-transposition)
5. [Amplitude Envelopes and Click Suppression](#5-amplitude-envelopes-and-click-suppression)
6. [Note Sequences and Temporal Concatenation](#6-note-sequences-and-temporal-concatenation)
7. [Time-Domain Analysis](#7-time-domain-analysis)
8. [Frequency-Domain Analysis: The DFT Spectrum](#8-frequency-domain-analysis-the-dft-spectrum)
9. [Time-Frequency Analysis: The Spectrogram](#9-time-frequency-analysis-the-spectrogram)
10. [Sampling, Quantisation, and the Audio Pipeline](#10-sampling-quantisation-and-the-audio-pipeline)
11. [Parameter Guide](#11-parameter-guide)

---

## 1. Acoustics and Musical Notes: Physical Background

### 1.1 Sound as a Pressure Wave

Sound is a mechanical longitudinal wave: a propagating perturbation of air pressure around the equilibrium atmospheric value $P_0$. At a fixed point in space, the pressure varies as a function of time $p(t)$. When this variation is periodic with period $T$, the perceived pitch corresponds to the **fundamental frequency** $f_0 = 1/T$, measured in Hertz (cycles per second).

The human auditory system perceives frequencies roughly in the range $[20\text{ Hz},\; 20\text{ kHz}]$. Within this range, pitch perception is **logarithmic**: equal perceived intervals correspond to equal frequency *ratios*, not equal frequency *differences*. Two notes separated by a factor of 2 in frequency are said to be one **octave** apart, and are perceived as the "same note" at different registers.

### 1.2 The Musical Notes of the Diatonic Scale

The app implements the seven notes of the C major diatonic scale in their standard fourth octave (concert pitch, A4 = 440 Hz):

| Note | Solfège | Frequency (Hz) |
|---|---|---|
| C4 | Do | 261.63 |
| D4 | Re | 293.66 |
| E4 | Mi | 329.63 |
| F4 | Fa | 349.23 |
| G4 | Sol | 392.00 |
| A4 | La | 440.00 |
| B4 | Si | 493.88 |

These frequencies are not arbitrary: they are derived from the **equal temperament** tuning system described in the next section.

---

## 2. The Equal Temperament Scale

### 2.1 The 12-Tone Equal Temperament (12-TET)

Modern Western music uses **12-tone equal temperament**: the octave is divided into 12 logarithmically equal intervals called **semitones**. Since one octave corresponds to a frequency ratio of 2, and the 12 semitones must partition it equally on a logarithmic scale, each semitone corresponds to a frequency ratio of:

$$r = 2^{1/12} \approx 1.05946$$

The frequency of any note $n$ semitones above a reference note $f_{\text{ref}}$ is therefore:

$$f_n = f_{\text{ref}} \cdot 2^{n/12}$$

The international standard reference is **A4 = 440 Hz** (ISO 16:1975). From this anchor, all other note frequencies can be derived by counting semitones.

### 2.2 Deriving the C Major Scale

The C major scale uses 7 of the 12 chromatic pitches. The interval structure in semitones from C to C is: **2 – 2 – 1 – 2 – 2 – 2 – 1** (whole-whole-half-whole-whole-whole-half). Starting from A4 = 440 Hz, C4 is 9 semitones below:

$$f_{C4} = 440 \cdot 2^{-9/12} = 440 \cdot 2^{-3/4} \approx 261.63\text{ Hz}$$

Each subsequent note of the C major scale is obtained by applying the interval pattern:

$$f_{D4} = f_{C4} \cdot 2^{2/12} \approx 293.66\text{ Hz}, \quad f_{E4} = f_{C4} \cdot 2^{4/12} \approx 329.63\text{ Hz}, \quad \ldots$$

### 2.3 Cents: A Logarithmic Unit of Interval

For fine tuning comparisons, the **cent** is defined as one hundredth of a semitone:

$$\Delta\text{(cents)} = 1200 \cdot \log_2\!\left(\frac{f_2}{f_1}\right)$$

One octave = 1200 cents, one semitone = 100 cents. This unit makes the logarithmic nature of pitch explicit and provides a perceptually linear measure of interval size.

---

## 3. Pure Tone Synthesis: The Sinusoidal Model

### 3.1 The Discrete-Time Pure Tone

The **pure tone** (or sinusoid) is the simplest acoustic signal: it contains energy at exactly one frequency. In continuous time, a pure tone at frequency $f$ Hz is:

$$s(t) = A \sin(2\pi f t + \phi)$$

where $A$ is the amplitude and $\phi$ is the initial phase. In the app, $\phi = 0$ and $A$ is the global amplitude constant.

After **sampling** at rate $f_s$ (here $f_s = 44100$ Hz), the discrete-time signal is:

$$s[n] = A \sin(2\pi f n / f_s), \qquad n = 0, 1, 2, \ldots, N-1$$

where $N = \lfloor f_s \cdot T \rfloor$ is the total number of samples for a tone of duration $T$ seconds.

The time axis is constructed as $t[n] = n / f_s$, a uniformly spaced grid with spacing $T_s = 1/f_s$.

### 3.2 Why a Pure Sine? The Monochromatic Signal

A pure sine wave is the **eigenfunction** of any linear time-invariant (LTI) system: it passes through unchanged in frequency, with only amplitude and phase modified. Its Fourier transform is a **Dirac delta** (or, for the discrete finite-length case, a concentrated spectral peak):

$$S(f') = \frac{A}{2j}\left[\delta(f' - f) - \delta(f' + f)\right]$$

This makes the pure tone the ideal pedagogical signal for visualising frequency-domain representations: the spectrum is trivially interpretable as a single spike at the note frequency.

Real musical instruments produce **harmonic sounds**: their spectra contain the fundamental $f_0$ plus a series of **harmonics** (overtones) at integer multiples $2f_0, 3f_0, 4f_0, \ldots$, with amplitudes that characterise the **timbre** of the instrument. The pure tone generated here has no harmonics — it corresponds to a perfectly sinusoidal oscillator, which is the limiting case of a tuning fork or a signal generator.

### 3.3 Amplitude and Normalisation

The amplitude is set to $A = 0.25$ (on a scale of $[-1, 1]$), keeping the signal well within the digital headroom and avoiding clipping. The output samples are stored as 32-bit floating-point values (`float32`), which provide more than sufficient dynamic range ($\approx 1500$ dB theoretical, far beyond any audio application requirement).

---

## 4. Octave Transposition

### 4.1 Octave as a Frequency Multiplication

Shifting a note by $k$ octaves multiplies its frequency by $2^k$:

$$f_{\text{transposed}} = f_{\text{base}} \cdot 2^k, \qquad k \in \mathbb{Z}$$

For $k > 0$, the note is shifted up (higher pitch); for $k < 0$, it is shifted down. The base frequencies in the app correspond to octave 4 (C4–B4 in scientific pitch notation). Selecting octave $+1$ produces C5–B5, and octave $-1$ produces C3–B3. The global octave is bounded to the range $[-3, +3]$, keeping all generated frequencies within the musically and perceptually useful range (approximately 33 Hz to 3952 Hz).

### 4.2 Per-Note Octave Shift in Sequences

Within a note sequence, individual notes can carry their own relative octave modifier, written as `Note+k` or `Note-k` (e.g., `Do+1`, `Sol-2`). This shift is **added** to the global base octave:

$$f = f_{\text{base\_note}} \cdot 2^{k_{\text{global}} + k_{\text{local}}}$$

This allows compact notation for melodies that span more than one octave without changing the global register for all notes.

### 4.3 Perceptual Basis: Octave Equivalence

The choice of the factor 2 for octave equivalence is rooted in the **harmonic series**: the first overtone of any vibrating system occurs at exactly $2f_0$. When a note and its octave are played together, the second harmonic of the lower note coincides with the fundamental of the upper note, creating a perceptual fusion that the auditory system interprets as "the same note, higher." This is the deepest reason why the octave is the fundamental interval in all known musical traditions.

---

## 5. Amplitude Envelopes and Click Suppression

### 5.1 The Click Artefact

A pure sine wave that is abruptly started or stopped causes a **click** — a broadband impulse artefact audible as a sharp percussive sound. The physical cause is the discontinuity in the waveform (or its derivatives) at the onset and offset: any discontinuity in a signal requires infinite bandwidth to represent, and when this bandwidth is limited by the audio system's Nyquist frequency, the energy is redistributed across the entire spectrum as an audible transient.

Mathematically, a rectangular windowed sine $s[n] = A\sin(2\pi f n/f_s) \cdot \mathbf{1}_{[0, N-1]}[n]$ has a spectrum that is the convolution of the sinusoid's delta-function spectrum with the sinc-shaped spectrum of the rectangular window, producing wide spectral shoulders that manifest as the click.

### 5.2 Linear Fade-In and Fade-Out Envelope

To suppress clicks, the app applies a **linear amplitude envelope** at the start and end of each tone. The fade duration is:

$$T_{\text{fade}} = \min\!\left(0.01\text{ s},\; \frac{T}{10}\right)$$

This ensures the fade is at most 10 ms (imperceptibly short to the ear as a pitch ramp) but never longer than 10% of the total note duration, preserving the integrity of very short notes.

The fade-in ramp over $M = \lfloor f_s \cdot T_{\text{fade}} \rfloor$ samples is:

$$w_{\text{in}}[n] = \frac{n}{M-1}, \qquad n = 0, 1, \ldots, M-1$$

and the fade-out ramp is its time-reversal:

$$w_{\text{out}}[n] = 1 - \frac{n}{M-1} = \frac{M-1-n}{M-1}, \qquad n = 0, 1, \ldots, M-1$$

These are applied by elementwise multiplication to the first and last $M$ samples of the tone respectively:

$$s_{\text{enveloped}}[n] = \begin{cases} w_{\text{in}}[n] \cdot s[n] & 0 \leq n < M \\ w_{\text{out}}[n-(N-M)] \cdot s[n] & N-M \leq n < N \\ s[n] & \text{otherwise} \end{cases}$$

### 5.3 ADSR Context

The linear fade is a minimal two-stage envelope (Attack–Release). Full synthesiser design uses a four-stage **ADSR envelope** (Attack, Decay, Sustain, Release) to model the temporal evolution of real instrument sounds. The attack controls how quickly the note rises to peak amplitude; the decay brings it to a sustain level; the sustain maintains it while the key is held; the release fades it after the key is released. Here, since the goal is a clean pure tone rather than an instrument simulation, only the attack and release stages are present, both linear.

---

## 6. Note Sequences and Temporal Concatenation

### 6.1 Sequence Parsing

A sequence is a string of whitespace-, comma-, semicolon-, pipe- or slash-separated tokens. Each token is parsed by a regular expression that extracts a **note name** (the solfège syllable, Unicode-normalised and lowercased) and an optional **octave modifier** of the form `+k` or `-k`:

$$\text{token} = \underbrace{\text{note\_name}}_{\in \{\text{do, re, mi, fa, sol, la, si}\}} \underbrace{[\pm k]}_{\text{integer, optional}}$$

Unicode normalisation (NFD decomposition followed by removal of combining diacritics) ensures that accented characters (e.g., `Ré`, `Dó`) are treated identically to their ASCII equivalents, making the input robust to international keyboard layouts.

### 6.2 Silence Gaps Between Notes

Between consecutive notes, a **silence gap** of $T_{\text{gap}} = 0.02$ s is inserted: a zero-valued array of length $\lfloor f_s \cdot T_{\text{gap}} \rfloor$ samples. This gap serves two roles:

- **Perceptual articulation**: without a gap, consecutive notes at the same pitch would fuse into a single continuous tone, making the melodic rhythm imperceptible. The gap gives each note a distinct onset.
- **Acoustic modelling**: in real instruments, the gap corresponds to the brief silence between note attacks — the equivalent of note articulation or staccato phrasing.

### 6.3 Concatenation as a Piecewise Signal

The complete sequence audio is the concatenation of alternating note and silence segments:

$$x[n] = \left[s_1[n],\; \mathbf{0}_{\text{gap}},\; s_2[n],\; \mathbf{0}_{\text{gap}},\; \ldots,\; s_K[n]\right]$$

where each $s_k$ is a fully enveloped tone of the same duration. The total length is:

$$N_{\text{total}} = K \cdot N_{\text{note}} + (K-1) \cdot N_{\text{gap}}$$

with $N_{\text{note}} = \lfloor f_s \cdot T \rfloor$ and $N_{\text{gap}} = \lfloor f_s \cdot T_{\text{gap}} \rfloor$.

---

## 7. Time-Domain Analysis

### 7.1 The Waveform View

The **time-domain plot** displays the raw sample values $s[n]$ against the time axis $t[n] = n / f_s$. For a pure sine wave of frequency $f$ and duration $T$, the plot shows exactly $f \cdot T$ complete oscillation cycles.

Reading the time-domain view:

- **Period**: the distance between two successive peaks is $1/f$ seconds. For La (440 Hz), $T_0 = 1/440 \approx 2.27$ ms.
- **Amplitude**: the peak excursion from zero equals $A = 0.25$.
- **Envelope**: the short linear fade-in and fade-out are visible at the very beginning and end of the signal as a slight ramp.
- **Phase**: for a pure sine starting at $\phi = 0$, the signal starts at zero and immediately rises — unlike a cosine, which would start at its peak.

### 7.2 Limitations of the Time Domain

For single pure tones, the time domain provides a complete and unambiguous description. For complex signals (sequences of different notes, real instrument recordings), the time domain becomes difficult to interpret: the waveform encodes all frequency components simultaneously, making it hard to distinguish individual pitches. This motivates the frequency-domain and time-frequency representations described below.

---

## 8. Frequency-Domain Analysis: The DFT Spectrum

### 8.1 The Real FFT

The frequency spectrum is computed via `np.fft.rfft`, the **real-input Fast Fourier Transform**, which computes the first $\lfloor N/2 \rfloor + 1$ DFT coefficients:

$$X[k] = \sum_{n=0}^{N-1} s[n]\, e^{-j2\pi kn/N}, \qquad k = 0, 1, \ldots, \lfloor N/2 \rfloor$$

The corresponding physical frequencies are $f_k = k \cdot f_s / N$, with frequency resolution $\Delta f = f_s / N$. For a 0.5 s tone at $f_s = 44100$ Hz, $N = 22050$ and $\Delta f = 2$ Hz — fine enough to resolve adjacent musical notes (the smallest interval in the scale is about 32 Hz between Do and Re).

The magnitude spectrum $|X[k]|$ is plotted (linear scale). The display is limited to $[0, 2000\text{ Hz}]$ to focus on the musically relevant range and avoid the empty high-frequency portion.

### 8.2 Spectral Peak of a Pure Tone

For a pure sine $s[n] = A\sin(2\pi f_0 n / f_s)$ of finite length $N$, the DFT has a dominant peak at the bin $k^* = \text{round}(f_0 N / f_s)$ closest to the true frequency. Since $f_0 N / f_s$ is generally not an integer, the peak is not infinitely sharp but spreads across neighbouring bins — a phenomenon called **spectral leakage**.

The magnitude of the peak bin is approximately:

$$|X[k^*]| \approx \frac{A \cdot N}{2}$$

The leakage is an artefact of the finite observation window, equivalent to multiplying the infinite sinusoid by a rectangular window of length $N$. Since no windowing is applied before the FFT in the spectrum plot, the rectangular window is implicit. For a pure tone visualisation this is acceptable; for spectral analysis of complex signals, pre-windowing would reduce leakage.

### 8.3 What the Spectrum Reveals About Sequences

For a sequence of different notes, the spectrum shows **multiple peaks**, one per distinct note. If the same note appears at two different octaves, two peaks at $f$ and $2f$ are visible. The relative heights of the peaks depend on both the amplitude and the total duration spent on each note.

---

## 9. Time-Frequency Analysis: The Spectrogram

### 9.1 Motivation: Non-Stationarity

A single DFT computed over the entire signal tells you *which* frequencies are present, but not *when*. For a note sequence — a fundamentally **non-stationary** signal whose frequency content changes over time — this is insufficient. The **spectrogram** provides a simultaneous view of both time and frequency.

### 9.2 The Short-Time Fourier Transform (STFT)

The **Short-Time Fourier Transform** (STFT) is defined by sliding an analysis window $w[m]$ of length $L$ over the signal and computing a DFT for each window position:

$$\text{STFT}[n, k] = \sum_{m=0}^{L-1} s[n + m]\, w[m]\, e^{-j2\pi km/L}$$

where $n$ is the **frame index** (starting sample position of the analysis window) and $k$ is the frequency bin index. The result is a **2D complex array** indexed by time and frequency.

The **spectrogram** is the squared magnitude of the STFT, i.e. the **Power Spectral Density (PSD)**:

$$\text{PSD}[n, k] = |\text{STFT}[n, k]|^2$$

The app computes this using `scipy.signal.spectrogram` with the Hann window, segment length $L = \min(1024, N)$, and 50% overlap ($\text{noverlap} = L/2$).

### 9.3 The Hann Window

The **Hann window** $w[m] = \frac{1}{2}\left[1 - \cos\!\left(\frac{2\pi m}{L-1}\right)\right]$ is used for all analysis windows. It offers a good trade-off between **time resolution** (how sharply transitions between notes are localised) and **frequency resolution** (how narrowly spectral peaks appear), with low spectral leakage. The 50% overlap ensures smooth temporal coverage and is the standard practice for spectrogram computation: with 50% overlap and a Hann window, the reconstruction is stable and the energy is approximately uniformly distributed across time frames.

### 9.4 The Time-Frequency Resolution Trade-off

The STFT is governed by a fundamental uncertainty principle analogous to the Heisenberg uncertainty principle in quantum mechanics. For a window of length $L$ and sampling rate $f_s$, the time and frequency resolutions are:

$$\Delta t \approx \frac{L}{f_s} \quad \text{(seconds per frame)}, \qquad \Delta f \approx \frac{f_s}{L} \quad \text{(Hz per bin)}$$

Their product is bounded below:

$$\Delta t \cdot \Delta f \geq 1$$

This means you cannot simultaneously achieve arbitrarily fine time resolution and arbitrarily fine frequency resolution. A long window gives precise frequency resolution (narrow peaks) but poor time resolution (note onsets appear blurred). A short window gives sharp time resolution (note transitions are crisp) but poor frequency resolution (peaks are broad and notes may overlap). The window size $L = 1024$ at $f_s = 44100$ Hz gives $\Delta t \approx 23$ ms and $\Delta f \approx 43$ Hz — a reasonable balance for musical note analysis.

### 9.5 The PSD in Decibels

The PSD values span many orders of magnitude, making a linear display uninformative (dominant peaks would compress everything else to near-zero). The spectrogram is therefore displayed in **decibels**:

$$\text{PSD}_{\text{dB}}[n, k] = 10 \log_{10}\!\left(\max\!\left(\text{PSD}[n, k],\; 10^{-12}\right)\right)$$

The floor $10^{-12}$ prevents $-\infty$ from appearing in silent regions. The **Magma** colormap maps low dB values to dark purple/black and high values to bright yellow/white, making it easy to identify the note tracks (bright horizontal bands) against the dark noise floor.

### 9.6 Reading the Spectrogram for Note Sequences

For a sequence of pure tones, the spectrogram shows **horizontal bright bands** at the frequency of each note, each band occupying the time interval when that note is playing. Between notes, the 20 ms gap appears as a dark vertical stripe. The logarithmic dB colour scale makes note boundaries crisp even when the amplitude differences are small. The frequency axis is limited to $[0, 2000\text{ Hz}]$, encompassing the full range of all seven notes and their transpositions up to +2 octaves.

---

## 10. Sampling, Quantisation, and the Audio Pipeline

### 10.1 The Nyquist-Shannon Theorem

A continuous-time signal $s(t)$ with highest frequency component $f_{\max}$ can be perfectly reconstructed from its samples $s[n] = s(nT_s)$ if and only if the sampling frequency satisfies:

$$f_s > 2 f_{\max} \qquad \text{(Nyquist criterion)}$$

The threshold $f_N = f_s / 2$ is the **Nyquist frequency**. Any frequency above $f_N$ present in the original signal will be **aliased** — it will appear in the sampled signal at a different, lower frequency $f_N - (f - f_N) = f_s - f$, corrupting the spectrum.

The app uses $f_s = 44100$ Hz (the standard audio CD sampling rate), giving a Nyquist frequency of 22050 Hz — well above the highest note generated (Si = 493.88 Hz, or $\approx 3951$ Hz at octave $+3$).

### 10.2 The WAV Output Format

The audio is exported in **WAV format** with `float32` samples. The Gradio audio widget handles the conversion to the appropriate playback format. Storing as `float32` preserves the full amplitude precision of the synthesised signal (no quantisation error from integer conversion), which is particularly important for the clean sinusoidal waveform where clipping or quantisation noise would introduce harmonic distortion visible in the spectrum.

### 10.3 Mono Audio

The generated signal is **mono** (single channel): a 1D array of $N$ samples. Stereo audio would require a 2D array $(N \times 2)$, with independent left and right channels. Since the app demonstrates pure tone properties rather than spatial audio, mono output is appropriate and halves the memory and storage requirements.

---

## 11. Parameter Guide

| Parameter | Mathematical role | Practical effect |
|---|---|---|
| **Duration per note** $T$ | Sets $N = \lfloor f_s T \rfloor$ samples per tone | Longer notes are easier to analyse in the spectrogram; shorter notes test the time-frequency resolution trade-off |
| **Octave** $k$ | Frequency multiplier $2^k$ applied to all base note frequencies; bounded to $k \in [-3, +3]$ | $k = 0$: C4–B4 range; $k = +1$: C5–B5; $k = -1$: C3–B3; $k = +3$: C7–B7 (up to ~3952 Hz) |
| **Per-note octave modifier** $\pm k$ | Additive offset to the global octave, per token in a sequence | Allows melodies spanning multiple octaves without changing the global register |
| **Note buttons** (Do–Si) | Select $f_0 \in \{261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88\}$ Hz | Direct single-note playback with current octave and duration |
| **Sequence input** | Ordered list of tokens parsed as $(f_k, \text{octave}_k)$ pairs | Generates a concatenated waveform with 20 ms gaps between notes |
