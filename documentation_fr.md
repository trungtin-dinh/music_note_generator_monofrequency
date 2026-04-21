## Table des matières

1. [Acoustique et notes de musique : fondements physiques](#1-acoustique-et-notes-de-musique--fondements-physiques)
2. [La gamme tempérée](#2-la-gamme-tempérée)
3. [Synthèse de ton pur : le modèle sinusoïdal](#3-synthèse-de-ton-pur--le-modèle-sinusoïdal)
4. [Transposition d'octave](#4-transposition-doctave)
5. [Enveloppes d'amplitude et suppression des clics](#5-enveloppes-damplitude-et-suppression-des-clics)
6. [Séquences de notes et concaténation temporelle](#6-séquences-de-notes-et-concaténation-temporelle)
7. [Analyse dans le domaine temporel](#7-analyse-dans-le-domaine-temporel)
8. [Analyse dans le domaine fréquentiel : le spectre DFT](#8-analyse-dans-le-domaine-fréquentiel--le-spectre-dft)
9. [Analyse temps-fréquence : le spectrogramme](#9-analyse-temps-fréquence--le-spectrogramme)
10. [Échantillonnage, quantification et chaîne audio](#10-échantillonnage-quantification-et-chaîne-audio)
11. [Guide des paramètres](#11-guide-des-paramètres)

---

## 1. Acoustique et notes de musique : fondements physiques

### 1.1 Le son comme onde de pression

Le son est une onde mécanique longitudinale : une perturbation propagative de la pression de l'air autour de la valeur atmosphérique d'équilibre $P_0$. En un point fixe de l'espace, la pression varie en fonction du temps $p(t)$. Lorsque cette variation est périodique de période $T$, la hauteur perçue correspond à la **fréquence fondamentale** $f_0 = 1/T$, mesurée en Hertz (cycles par seconde).

Le système auditif humain perçoit des fréquences approximativement dans l'intervalle $[20\text{ Hz},\; 20\text{ kHz}]$. Dans cet intervalle, la perception de la hauteur est **logarithmique** : des intervalles perçus comme égaux correspondent à des *rapports* de fréquences égaux, et non à des *différences* de fréquences égales. Deux notes séparées par un facteur 2 en fréquence sont dites espacées d'une **octave**, et sont perçues comme la "même note" dans des registres différents.

### 1.2 Les notes musicales de la gamme diatonique

L'application implémente les sept notes de la gamme diatonique de Do majeur dans leur quatrième octave standard (diapason, A4 = 440 Hz) :

| Note | Solfège | Fréquence (Hz) |
|---|---|---|
| C4 | Do | 261.63 |
| D4 | Re | 293.66 |
| E4 | Mi | 329.63 |
| F4 | Fa | 349.23 |
| G4 | Sol | 392.00 |
| A4 | La | 440.00 |
| B4 | Si | 493.88 |

Ces fréquences ne sont pas arbitraires : elles sont dérivées du système d'accord **tempéré égal** décrit dans la section suivante.

---

## 2. La gamme tempérée

### 2.1 Le tempérament égal à 12 sons (12-TET)

La musique occidentale moderne utilise le **tempérament égal à 12 sons** : l'octave est divisée en 12 intervalles logarithmiquement égaux appelés **demi-tons**. Puisqu'une octave correspond à un rapport de fréquence égal à 2, et que les 12 demi-tons doivent la partitionner également sur une échelle logarithmique, chaque demi-ton correspond à un rapport de fréquence égal à :

$$r = 2^{1/12} \approx 1.05946$$

La fréquence de toute note située à $n$ demi-tons au-dessus d'une note de référence $f_{\text{ref}}$ est donc :

$$f_n = f_{\text{ref}} \cdot 2^{n/12}$$

La référence standard internationale est **A4 = 440 Hz** (ISO 16:1975). À partir de cet ancrage, toutes les autres fréquences de notes peuvent être dérivées en comptant les demi-tons.

### 2.2 Déduction de la gamme de Do majeur

La gamme de Do majeur utilise 7 des 12 hauteurs chromatiques. La structure intervallique en demi-tons de Do à Do est : **2 – 2 – 1 – 2 – 2 – 2 – 1** (ton-ton-demi-ton-ton-ton-ton-demi-ton). En partant de A4 = 440 Hz, C4 se trouve 9 demi-tons en dessous :

$$f_{C4} = 440 \cdot 2^{-9/12} = 440 \cdot 2^{-3/4} \approx 261.63\text{ Hz}$$

Chaque note suivante de la gamme de Do majeur s'obtient en appliquant ce motif intervallique :

$$f_{D4} = f_{C4} \cdot 2^{2/12} \approx 293.66\text{ Hz}, \quad f_{E4} = f_{C4} \cdot 2^{4/12} \approx 329.63\text{ Hz}, \quad \ldots$$

### 2.3 Les cents : une unité logarithmique d'intervalle

Pour les comparaisons d'accord fin, le **cent** est défini comme le centième d'un demi-ton :

$$\Delta\text{(cents)} = 1200 \cdot \log_2\!\left(\frac{f_2}{f_1}\right)$$

Une octave = 1200 cents, un demi-ton = 100 cents. Cette unité rend explicite la nature logarithmique de la hauteur et fournit une mesure perceptivement linéaire de la taille d'un intervalle.

---

## 3. Synthèse de ton pur : le modèle sinusoïdal

### 3.1 Le ton pur en temps discret

Le **ton pur** (ou sinusoïde) est le signal acoustique le plus simple : il contient de l'énergie à une seule fréquence. En temps continu, un ton pur de fréquence $f$ Hz s'écrit :

$$s(t) = A \sin(2\pi f t + \phi)$$

où $A$ est l'amplitude et $\phi$ la phase initiale. Dans l'application, $\phi = 0$ et $A$ est la constante globale d'amplitude.

Après **échantillonnage** à la fréquence $f_s$ (ici $f_s = 44100$ Hz), le signal en temps discret devient :

$$s[n] = A \sin(2\pi f n / f_s), \qquad n = 0, 1, 2, \ldots, N-1$$

où $N = \lfloor f_s \cdot T \rfloor$ est le nombre total d'échantillons pour un ton de durée $T$ secondes.

L'axe temporel est construit comme $t[n] = n / f_s$, une grille uniformément espacée de pas $T_s = 1/f_s$.

### 3.2 Pourquoi une sinusoïde pure ? Le signal monochromatique

Une onde sinusoïdale pure est la **fonction propre** de tout système linéaire invariant dans le temps (LTI) : elle le traverse sans changement de fréquence, seules son amplitude et sa phase étant modifiées. Sa transformée de Fourier est une **distribution de Dirac** (ou, dans le cas discret de longueur finie, un pic spectral concentré) :

$$S(f') = \frac{A}{2j}\left[\delta(f' - f) - \delta(f' + f)\right]$$

Cela fait du ton pur le signal pédagogique idéal pour visualiser les représentations fréquentielles : le spectre s'interprète trivialement comme un unique pic à la fréquence de la note.

Les instruments de musique réels produisent des **sons harmoniques** : leurs spectres contiennent la fondamentale $f_0$ ainsi qu'une série d'**harmoniques** (partiels) à des multiples entiers $2f_0, 3f_0, 4f_0, \ldots$, avec des amplitudes qui caractérisent le **timbre** de l'instrument. Le ton pur généré ici n'a pas d'harmoniques : il correspond à un oscillateur parfaitement sinusoïdal, cas limite d'un diapason ou d'un générateur de signal.

### 3.3 Amplitude et normalisation

L'amplitude est fixée à $A = 0.25$ (sur une échelle de $[-1, 1]$), ce qui maintient le signal largement dans la marge dynamique numérique et évite l'écrêtage. Les échantillons de sortie sont stockés sous forme de nombres flottants 32 bits (`float32`), ce qui fournit une dynamique plus que suffisante ($\approx 1500$ dB théoriques, bien au-delà de toute exigence en audio).

---

## 4. Transposition d'octave

### 4.1 L'octave comme multiplication fréquentielle

Transposer une note de $k$ octaves multiplie sa fréquence par $2^k$ :

$$f_{\text{transposed}} = f_{\text{base}} \cdot 2^k, \qquad k \in \mathbb{Z}$$

Pour $k > 0$, la note est transposée vers le haut (hauteur plus élevée) ; pour $k < 0$, elle est transposée vers le bas. Les fréquences de base dans l'application correspondent à l'octave 4 (C4–B4 en notation scientifique). Sélectionner l'octave $+1$ produit C5–B5, et l'octave $-1$ produit C3–B3.

### 4.2 Décalage d'octave par note dans les séquences

Dans une séquence de notes, chaque note peut porter son propre modificateur d'octave relatif, écrit `Note+k` ou `Note-k` (par exemple `Do+1`, `Sol-2`). Ce décalage s'**ajoute** à l'octave globale de base :

$$f = f_{\text{base\_note}} \cdot 2^{k_{\text{global}} + k_{\text{local}}}$$

Cela permet une notation compacte pour des mélodies s'étendant sur plus d'une octave sans modifier le registre global de toutes les notes.

### 4.3 Fondement perceptif : l'équivalence d'octave

Le choix du facteur 2 pour l'équivalence d'octave est enraciné dans la **série harmonique** : le premier partiel d'ordre supérieur de tout système vibrant apparaît exactement à $2f_0$. Lorsqu'une note et son octave sont jouées ensemble, la seconde harmonique de la note grave coïncide avec la fondamentale de la note aiguë, créant une fusion perceptive que le système auditif interprète comme "la même note, plus haute". C'est la raison la plus profonde pour laquelle l'octave constitue l'intervalle fondamental dans toutes les traditions musicales connues.

---

## 5. Enveloppes d'amplitude et suppression des clics

### 5.1 L'artefact de clic

Une onde sinusoïdale pure démarrée ou arrêtée brutalement produit un **clic** - un artefact impulsionnel large bande audible comme un son percussif bref et sec. La cause physique en est la discontinuité de la forme d'onde (ou de ses dérivées) au début et à la fin : toute discontinuité dans un signal nécessite une bande passante infinie pour être représentée, et lorsque cette bande passante est limitée par la fréquence de Nyquist du système audio, l'énergie se redistribue sur l'ensemble du spectre sous la forme d'un transitoire audible.

Mathématiquement, une sinusoïde fenêtrée par une porte rectangulaire $s[n] = A\sin(2\pi f n/f_s) \cdot \mathbf{1}_{[0, N-1]}[n]$ a pour spectre la convolution du spectre en delta de la sinusoïde avec le spectre en sinc de la fenêtre rectangulaire, ce qui produit de larges lobes spectraux se manifestant comme le clic.

### 5.2 Enveloppe linéaire de fade-in et fade-out

Pour supprimer les clics, l'application applique une **enveloppe d'amplitude linéaire** au début et à la fin de chaque ton. La durée de fondu est :

$$T_{\text{fade}} = \min\!\left(0.01\text{ s},\; \frac{T}{10}\right)$$

Cela garantit que le fondu dure au plus 10 ms (durée imperceptiblement courte à l'oreille comme rampe de hauteur), mais jamais plus de 10% de la durée totale de la note, afin de préserver l'intégrité des notes très courtes.

La rampe de fade-in sur $M = \lfloor f_s \cdot T_{\text{fade}} \rfloor$ échantillons est :

$$w_{\text{in}}[n] = \frac{n}{M-1}, \qquad n = 0, 1, \ldots, M-1$$

et la rampe de fade-out est son renversement temporel :

$$w_{\text{out}}[n] = 1 - \frac{n}{M-1} = \frac{M-1-n}{M-1}, \qquad n = 0, 1, \ldots, M-1$$

Elles sont appliquées par multiplication élément par élément aux $M$ premiers et derniers échantillons du ton respectivement :

$$s_{\text{enveloped}}[n] = \begin{cases} w_{\text{in}}[n] \cdot s[n] & 0 \leq n < M \\ w_{\text{out}}[n-(N-M)] \cdot s[n] & N-M \leq n < N \\ s[n] & \text{otherwise} \end{cases}$$

### 5.3 Contexte ADSR

Le fondu linéaire est une enveloppe minimale à deux étapes (Attack–Release). La synthèse sonore complète utilise une **enveloppe ADSR** à quatre étapes (Attack, Decay, Sustain, Release) pour modéliser l'évolution temporelle des sons d'instruments réels. L'attaque contrôle la rapidité avec laquelle la note atteint son amplitude maximale ; le decay la ramène à un niveau de sustain ; le sustain la maintient tant que la touche est enfoncée ; le release la fait décroître après le relâchement de la touche. Ici, puisque l'objectif est d'obtenir un ton pur propre plutôt qu'une simulation d'instrument, seules les phases d'attaque et de relâchement sont présentes, et toutes deux sont linéaires.

---

## 6. Séquences de notes et concaténation temporelle

### 6.1 Analyse syntaxique des séquences

Une séquence est une chaîne de caractères composée de tokens séparés par des espaces, des virgules, des points-virgules, des barres verticales ou des slashs. Chaque token est analysé par une expression régulière qui extrait un **nom de note** (la syllabe de solfège, normalisée en Unicode puis convertie en minuscules) et un éventuel **modificateur d'octave** de la forme `+k` ou `-k` :

$$\text{token} = \underbrace{\text{note\_name}}_{\in \{\text{do, re, mi, fa, sol, la, si}\}} \underbrace{[\pm k]}_{\text{entier, optionnel}}$$

La normalisation Unicode (décomposition NFD suivie de la suppression des diacritiques combinés) garantit que les caractères accentués (par exemple `Ré`, `Dó`) sont traités de manière identique à leurs équivalents ASCII, ce qui rend la saisie robuste vis-à-vis des claviers internationaux.

### 6.2 Silences entre les notes

Entre deux notes consécutives, un **silence** de durée $T_{\text{gap}} = 0.02$ s est inséré : un tableau de zéros de longueur $\lfloor f_s \cdot T_{\text{gap}} \rfloor$ échantillons. Ce silence remplit deux fonctions :

- **Articulation perceptive** : sans silence, deux notes consécutives de même hauteur fusionneraient en un seul ton continu, rendant le rythme mélodique imperceptible. Le silence donne à chaque note une attaque distincte.
- **Modélisation acoustique** : dans les instruments réels, ce silence correspond au bref intervalle entre deux attaques de notes - l'équivalent de l'articulation ou d'un phrasé staccato.

### 6.3 Concaténation comme signal par morceaux

Le signal audio complet de la séquence est la concaténation de segments alternés de notes et de silences :

$$x[n] = \left[s_1[n],\; \mathbf{0}_{\text{gap}},\; s_2[n],\; \mathbf{0}_{\text{gap}},\; \ldots,\; s_K[n]\right]$$

où chaque $s_k$ est un ton entièrement enveloppé de même durée. La longueur totale est :

$$N_{\text{total}} = K \cdot N_{\text{note}} + (K-1) \cdot N_{\text{gap}}$$

avec $N_{\text{note}} = \lfloor f_s \cdot T \rfloor$ et $N_{\text{gap}} = \lfloor f_s \cdot T_{\text{gap}} \rfloor$.

---

## 7. Analyse dans le domaine temporel

### 7.1 La vue forme d'onde

Le **graphique temporel** affiche les valeurs brutes des échantillons $s[n]$ en fonction de l'axe temporel $t[n] = n / f_s$. Pour une sinusoïde pure de fréquence $f$ et de durée $T$, le graphe montre exactement $f \cdot T$ cycles complets d'oscillation.

Lecture de la vue temporelle :

- **Période** : la distance entre deux pics successifs est de $1/f$ seconde. Pour La (440 Hz), $T_0 = 1/440 \approx 2.27$ ms.
- **Amplitude** : l'excursion maximale par rapport à zéro vaut $A = 0.25$.
- **Enveloppe** : les courts fade-in et fade-out linéaires sont visibles au tout début et à la toute fin du signal sous la forme d'une légère rampe.
- **Phase** : pour une sinusoïde pure commençant à $\phi = 0$, le signal démarre à zéro et croît immédiatement - contrairement à un cosinus, qui commencerait à son maximum.

### 7.2 Limites du domaine temporel

Pour des tons purs isolés, le domaine temporel fournit une description complète et non ambiguë. Pour des signaux complexes (séquences de notes différentes, enregistrements d'instruments réels), le domaine temporel devient difficile à interpréter : la forme d'onde encode simultanément toutes les composantes fréquentielles, ce qui rend difficile l'identification des hauteurs individuelles. Cela motive l'usage des représentations fréquentielle et temps-fréquence décrites ci-dessous.

---

## 8. Analyse dans le domaine fréquentiel : le spectre DFT

### 8.1 La FFT réelle

Le spectre fréquentiel est calculé via `np.fft.rfft`, la **Fast Fourier Transform à entrée réelle**, qui calcule les $\lfloor N/2 \rfloor + 1$ premiers coefficients de la DFT :

$$X[k] = \sum_{n=0}^{N-1} s[n]\, e^{-j2\pi kn/N}, \qquad k = 0, 1, \ldots, \lfloor N/2 \rfloor$$

Les fréquences physiques correspondantes sont $f_k = k \cdot f_s / N$, avec une résolution fréquentielle $\Delta f = f_s / N$. Pour un ton de 0.5 s à $f_s = 44100$ Hz, $N = 22050$ et $\Delta f = 2$ Hz - suffisamment fin pour résoudre des notes musicales adjacentes (le plus petit intervalle de la gamme est d'environ 30 Hz entre Do et Re).

Le spectre d'amplitude $|X[k]|$ est affiché (échelle linéaire). L'affichage est limité à $[0, 2000\text{ Hz}]$ afin de se concentrer sur la zone musicalement pertinente et d'éviter la portion haute fréquence vide.

### 8.2 Pic spectral d'un ton pur

Pour une sinusoïde pure $s[n] = A\sin(2\pi f_0 n / f_s)$ de longueur finie $N$, la DFT présente un pic dominant au bin $k^* = \text{round}(f_0 N / f_s)$ le plus proche de la fréquence réelle. Comme $f_0 N / f_s$ n'est généralement pas entier, le pic n'est pas infiniment fin mais s'étale sur les bins voisins - un phénomène appelé **fuite spectrale**.

L'amplitude du bin principal vaut approximativement :

$$|X[k^*]| \approx \frac{A \cdot N}{2}$$

Cette fuite est un artefact de la fenêtre d'observation finie, équivalente à la multiplication de la sinusoïde infinie par une fenêtre rectangulaire de longueur $N$. Puisqu'aucun fenêtrage n'est appliqué avant la FFT dans le graphique du spectre, la fenêtre rectangulaire est implicite. Pour la visualisation d'un ton pur, cela reste acceptable ; pour l'analyse spectrale de signaux complexes, un fenêtrage préalable réduirait la fuite.

### 8.3 Ce que le spectre révèle sur les séquences

Pour une séquence de notes différentes, le spectre présente **plusieurs pics**, un par note distincte. Si une même note apparaît à deux octaves différentes, deux pics à $f$ et $2f$ sont visibles. Les hauteurs relatives des pics dépendent à la fois de l'amplitude et de la durée totale passée sur chaque note.

---

## 9. Analyse temps-fréquence : le spectrogramme

### 9.1 Motivation : non-stationnarité

Une seule DFT calculée sur l'ensemble du signal indique *quelles* fréquences sont présentes, mais pas *quand*. Pour une séquence de notes - signal fondamentalement **non stationnaire** dont le contenu fréquentiel évolue dans le temps - cela est insuffisant. Le **spectrogramme** fournit une vue simultanée du temps et de la fréquence.

### 9.2 La transformée de Fourier à court terme (STFT)

La **transformée de Fourier à court terme** (STFT) est définie en faisant glisser une fenêtre d'analyse $w[m]$ de longueur $L$ sur le signal, puis en calculant une DFT pour chaque position de fenêtre :

$$\text{STFT}[n, k] = \sum_{m=0}^{L-1} s[n + m]\, w[m]\, e^{-j2\pi km/L}$$

où $n$ est le **pas temporel** (hop entre fenêtres consécutives) et $k$ l'indice de bin fréquentiel. Le résultat est un **tableau complexe 2D** indexé en temps et en fréquence.

Le **spectrogramme** est le module au carré de la STFT, c'est-à-dire la **densité spectrale de puissance (PSD)** :

$$\text{PSD}[n, k] = |\text{STFT}[n, k]|^2$$

L'application le calcule avec `scipy.signal.spectrogram` en utilisant une fenêtre de Hann, une longueur de segment $L = \min(1024, N)$, et un recouvrement de 50% ($\text{noverlap} = L/2$).

### 9.3 La fenêtre de Hann

La **fenêtre de Hann** $w[m] = \frac{1}{2}\left[1 - \cos\!\left(\frac{2\pi m}{L-1}\right)\right]$ est utilisée pour toutes les fenêtres d'analyse. Elle offre un bon compromis entre **résolution temporelle** (à quel point les transitions entre notes sont localisées avec précision) et **résolution fréquentielle** (à quel point les pics spectraux apparaissent étroits), avec une faible fuite spectrale. Le recouvrement de 50% garantit une couverture temporelle lisse et constitue la pratique standard pour le calcul de spectrogrammes : avec un recouvrement de 50% et une fenêtre de Hann, la reconstruction est stable et l'énergie est répartie de façon approximativement uniforme entre les trames temporelles.

### 9.4 Le compromis résolution temps-fréquence

La STFT est régie par un principe d'incertitude fondamental analogue au principe d'incertitude de Heisenberg en mécanique quantique. Pour une fenêtre de longueur $L$ et une fréquence d'échantillonnage $f_s$, les résolutions temporelle et fréquentielle sont :

$$\Delta t \approx \frac{L}{f_s} \quad \text{(secondes par trame)}, \qquad \Delta f \approx \frac{f_s}{L} \quad \text{(Hz par bin)}$$

Leur produit est minoré :

$$\Delta t \cdot \Delta f \geq 1$$

Cela signifie qu'on ne peut pas obtenir simultanément une résolution temporelle arbitrairement fine et une résolution fréquentielle arbitrairement fine. Une fenêtre longue donne une résolution fréquentielle précise (pics étroits) mais une mauvaise résolution temporelle (les attaques de notes apparaissent floues). Une fenêtre courte donne une bonne résolution temporelle (transitions nettes) mais une mauvaise résolution fréquentielle (pics larges et notes potentiellement confondues). La taille de fenêtre $L = 1024$ à $f_s = 44100$ Hz donne $\Delta t \approx 23$ ms et $\Delta f \approx 43$ Hz - un compromis raisonnable pour l'analyse de notes musicales.

### 9.5 La PSD en décibels

Les valeurs de PSD couvrent plusieurs ordres de grandeur, ce qui rend un affichage linéaire peu informatif (les pics dominants compriment tout le reste vers zéro). Le spectrogramme est donc affiché en **décibels** :

$$\text{PSD}_{\text{dB}}[n, k] = 10 \log_{10}\!\left(\max\!\left(\text{PSD}[n, k],\; 10^{-12}\right)\right)$$

Le seuil plancher $10^{-12}$ empêche l'apparition de $-\infty$ dans les zones silencieuses. La palette **Magma** associe les faibles valeurs en dB à des teintes violet foncé/noir et les fortes valeurs à du jaune/blanc lumineux, ce qui permet d'identifier facilement les trajectoires des notes (bandes horizontales lumineuses) sur le fond sombre du bruit de fond.

### 9.6 Lecture du spectrogramme pour les séquences de notes

Pour une séquence de tons purs, le spectrogramme montre des **bandes horizontales lumineuses** à la fréquence de chaque note, chaque bande occupant l'intervalle temporel où la note est jouée. Entre les notes, l'intervalle de 20 ms apparaît comme une bande verticale sombre. L'échelle logarithmique en dB rend les frontières entre notes nettes même lorsque les différences d'amplitude sont faibles. L'axe fréquentiel est limité à $[0, 2000\text{ Hz}]$, couvrant toute la plage des sept notes et de leurs transpositions jusqu'à +2 octaves.

---

## 10. Échantillonnage, quantification et chaîne audio

### 10.1 Le théorème de Nyquist-Shannon

Un signal en temps continu $s(t)$ dont la fréquence maximale est $f_{\max}$ peut être parfaitement reconstruit à partir de ses échantillons $s[n] = s(nT_s)$ si et seulement si la fréquence d'échantillonnage vérifie :

$$f_s > 2 f_{\max} \qquad \text{(critère de Nyquist)}$$

Le seuil $f_N = f_s / 2$ est la **fréquence de Nyquist**. Toute fréquence supérieure à $f_N$ présente dans le signal original sera **repliée** (aliasing) - elle apparaîtra dans le signal échantillonné à une autre fréquence plus basse $f_N - (f - f_N) = f_s - f$, corrompant le spectre.

L'application utilise $f_s = 44100$ Hz (fréquence standard des CD audio), donnant une fréquence de Nyquist de 22050 Hz - bien au-dessus de la note la plus haute générée (Si = 493.88 Hz, soit $\approx 3951$ Hz à l'octave $+3$).

### 10.2 Le format de sortie WAV

L'audio est exporté au **format WAV** avec des échantillons `float32`. Le widget audio de Gradio gère la conversion vers le format de lecture approprié. Le stockage en `float32` préserve toute la précision d'amplitude du signal synthétisé (pas d'erreur de quantification due à une conversion entière), ce qui est particulièrement important pour une forme d'onde sinusoïdale propre, car tout écrêtage ou bruit de quantification introduirait une distorsion harmonique visible dans le spectre.

### 10.3 Audio mono

Le signal généré est **mono** (un seul canal) : un tableau 1D de $N$ échantillons. L'audio stéréo nécessiterait un tableau 2D $(N \times 2)$, avec des canaux gauche et droit indépendants. Puisque l'application illustre les propriétés d'un ton pur plutôt que l'audio spatial, une sortie mono est appropriée et divise par deux les besoins en mémoire et en stockage.

---

## 11. Guide des paramètres

| Paramètre | Rôle mathématique | Effet pratique |
|---|---|---|
| **Durée par note** $T$ | Définit $N = \lfloor f_s T \rfloor$ échantillons par ton | Les notes longues sont plus faciles à analyser dans le spectrogramme ; les notes courtes mettent à l'épreuve le compromis temps-fréquence |
| **Octave** $k$ | Multiplicateur fréquentiel $2^k$ appliqué à toutes les fréquences de base des notes | $k = 0$ : plage C4–B4 ; $k = +1$ : C5–B5 ; $k = -1$ : C3–B3 |
| **Modificateur d'octave par note** $\pm k$ | Décalage additif par rapport à l'octave globale, pour chaque token d'une séquence | Permet des mélodies couvrant plusieurs octaves sans changer le registre global |
| **Boutons de notes** (Do–Si) | Sélectionne $f_0 \in \{261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88\}$ Hz | Lecture directe d'une note unique avec l'octave et la durée courantes |
| **Entrée de séquence** | Liste ordonnée de tokens interprétés comme des paires $(f_k, \text{octave}_k)$ | Génère une forme d'onde concaténée avec des silences de 20 ms entre les notes |