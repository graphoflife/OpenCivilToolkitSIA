# Voll

103 Berechnungen ausgeführt, 193 Werte bestimmt.

## Herleitung

### Plattenanalyse: Decke

**Plattendicke**

$$
h = 300\,\mathrm{mm}
$$

**Betrachtete Breite (x)**

$$
b = 1000\,\mathrm{mm}
$$

**Betrachtete Breite (y)**

$$
b_y = 1000\,\mathrm{mm}
$$

**Überdeckung unten**

$$
c_{nom,u} = 30\,\mathrm{mm}
$$

**Überdeckung oben**

$$
c_{nom,o} = 30\,\mathrm{mm}
$$

**Bewehrungsquerschnitt je Laufmeter** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{4712\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 300\,\mathrm{mm}} = 123\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 240\,\mathrm{mm} - 54\,\mathrm{mm} \\
  &= 186\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, statische Höhen und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $d\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | y | B500B | $12$ | $150$ | $36$ | $264$ | $754$ |
| 2. Lage Grundbewehrung | x | B500B | $18$ | $150$ | $51$ | $249$ | $1696$ |
| 2. Lage Zulage | x | B500B | $12$ | $150$ | $54$ | $246$ | $754$ |
| 3. Lage Grundbewehrung | x | B500B | $12$ | $150$ | $48$ | $48$ | $754$ |
| 4. Lage Grundbewehrung | y | B500B | $12$ | $150$ | $36$ | $36$ | $754$ |

### Resistenzlinie aus Handrechnung – x-Richtung

Druckzone als Spannungsblock der Höhe 0.85·x mit durchgehend f\_cd; gedrückter Stahl bleibt unberücksichtigt. Die Bewehrung ist je Seite zu einer Lage zusammengefasst, das Moment bezieht sich auf die halbe Querschnittshöhe.

**Statische Höhe der zusammengefassten Lage – 2. Lage Grundbewehrung + 2. Lage Zulage**

$$
\begin{aligned}
  d_{2,x} &= \frac{A_{s,2,x,g} \cdot f_{yd} \cdot d_{2,x,g} + A_{s,2,x,z} \cdot f_{yd} \cdot d_{2,x,z}}{A_{s,2,x,g} \cdot f_{yd} + A_{s,2,x,z} \cdot f_{yd}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{1696\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

**Bewehrungsquerschnitt der zusammengefassten Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $d\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung + 2. Lage Zulage | $2450$ | $248.1$ | $435$ |
| 3. Lage Grundbewehrung | $754$ | $48.0$ | $435$ |

#### Grösste Druckkraft

**Gleichmässiger Druck, ohne Bewehrung**

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd} = -1000\,\mathrm{mm} \cdot 300\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} = -6000\,\mathrm{kN}
$$

**Zugehöriges Moment**

$$
M_{Rd}(N_{Rd}^{-}) = 0\,\mathrm{kNm}
$$

#### Grösste Zugkraft

**Beide Lagen fliessen auf Zug**

$$
\begin{aligned}
  N_{Rd}^{+} &= A_{s,2,x} \cdot f_{yd} + A_{s,3,x} \cdot f_{yd} \\
  &= 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 1393.2\,\mathrm{kN}
\end{aligned}
$$

**Kräfte mal Hebelarm um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}(N_{Rd}^{+}) &= A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right) \\
  &= 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(48\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right) \\
  &= 71.1\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{+} = \frac{A_{s,2,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 62.7\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{+} &= A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \frac{0.85 \cdot x^{+}}{2}\right) \\
  &= 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \frac{0.85 \cdot 62.7\,\mathrm{mm}}{2}\right) \\
  &= 235.9\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe: x = h/2**

$$
x^{+} = \frac{h}{2} = \frac{300\,\mathrm{mm}}{2} = 150\,\mathrm{mm}
$$

**Fliesskriterium – Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(248.1\,\mathrm{mm} - 150\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{150\,\mathrm{mm}} = 2.29\,\text{‰}
$$

ε\_s = 2.29 ‰ ≥ ε\_yd = 2.17 ‰ – die Zugbewehrung fliesst, f\_sd = f\_yd gilt.

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot f_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} + 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1484.6\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot f_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} \cdot \left(\tfrac{300\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 150\,\mathrm{mm}}{2}\right) + 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right)\right] \\
  &= 324.4\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{-} = \frac{A_{s,3,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 19.3\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{-} &= -A_{s,3,x} \cdot f_{yd} \cdot \left(d_{3,x} - \frac{0.85 \cdot x^{-}}{2}\right) \\
  &= -754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(252\,\mathrm{mm} - \frac{0.85 \cdot 19.3\,\mathrm{mm}}{2}\right) \\
  &= -79.9\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe: x = h/2**

$$
x^{-} = \frac{h}{2} = \frac{300\,\mathrm{mm}}{2} = 150\,\mathrm{mm}
$$

**Fliesskriterium – Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{3,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(252\,\mathrm{mm} - 150\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{150\,\mathrm{mm}} = 2.38\,\text{‰}
$$

ε\_s = 2.38 ‰ ≥ ε\_yd = 2.17 ‰ – die Zugbewehrung fliesst, f\_sd = f\_yd gilt.

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,3,x} \cdot f_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -2222.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,3,x} \cdot f_{sd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right)\right] \\
  &= -\left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} \cdot \left(\tfrac{300\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 150\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(252\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right)\right] \\
  &= -253.4\,\mathrm{kNm}
\end{aligned}
$$

**Eckpunkte der Resistenzlinie aus Handrechnung**

| Eckpunkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{-}$ | $-6000.0$ | $0.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1484.6$ | $324.4$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $235.9$ |
| $N_{Rd}^{+}$ | $1393.2$ | $71.1$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $0.0$ | $-79.9$ |
| $M_{Rd}(x=\tfrac{h}{2})^{-}$ | $-2222.2$ | $-253.4$ |

#### Nachweis – Feld

**Einwirkung**

$$
M_{Ed} = 150\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 235.9\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{235.9\,\mathrm{kNm}}{150\,\mathrm{kNm}} = 1.57 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Feld mit Druck

**Einwirkung**

$$
M_{Ed} = 120\,\mathrm{kNm} \qquad N_{Ed} = -300\,\mathrm{kN}
$$

**Widerstand bei festgehaltenem N\_Ed = -300.0 kN**

$$
\begin{aligned}
  M_{Rd} &= M_1 + \frac{N_{Ed} - N_1}{N_2 - N_1} \cdot \left(M_2 - M_1\right) \\
  &= 324.4\,\mathrm{kNm} + \frac{-300\,\mathrm{kN} - \left(-1484.6\,\mathrm{kN}\right)}{0\,\mathrm{kN} - \left(-1484.6\,\mathrm{kN}\right)} \cdot \left(235.9\,\mathrm{kNm} - 324.4\,\mathrm{kNm}\right) \\
  &= 253.8\,\mathrm{kNm}
\end{aligned}
$$

**Stützpunkte der Interpolation**

| Punkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1484.6$ | $324.4$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $235.9$ |

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld mit Druck}} = \frac{M_{Rd}}{M_{Ed}} = \frac{253.8\,\mathrm{kNm}}{120\,\mathrm{kNm}} = 2.12 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Stütze

**Einwirkung**

$$
M_{Ed} = -60\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{-} = -79.9\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Stütze}} = \frac{M_{Rd}}{M_{Ed}} = \frac{79.9\,\mathrm{kNm}}{60\,\mathrm{kNm}} = 1.33 \quad \Rightarrow \quad \text{erfüllt}
$$

**Bügeldurchmesser**

$$
\varnothing_{V} = 8\,\mathrm{mm}
$$

**Bügelteilung in x-Richtung**

$$
s_{V,x} = 200\,\mathrm{mm}
$$

**Bügelzahl über die betrachtete Breite**

$$
n_{V,y} = 5
$$

**Kleinste Neigung der Druckdiagonalen**

$$
\alpha_{min} = 30{}^{\circ}
$$

**Grösste Neigung der Druckdiagonalen**

$$
\alpha_{max} = 45{}^{\circ}
$$

**Querschnitt eines Bügelschenkels** *(SIA 262:2025, 5.5.2)*

$$
A_{\varnothing,V} = \frac{\pi \cdot \left(\varnothing_{V}\right)^{2}}{4} = \frac{\pi \cdot \left(8\,\mathrm{mm}\right)^{2}}{4} = 50.3\,\mathrm{mm}^{2}
$$

### Querkraft – x-Richtung

Querkraftwiderstand mit Querkraftbewehrung, Fachwerkmodell mit veränderlicher Neigung der Druckdiagonalen. Massgebend ist das Kleinere aus dem Widerstand der Bügel und dem der Druckdiagonalen; der Betonanteil ohne Bügel geht nicht zusätzlich ein.

**Ansatz** *(SIA 262:2025, 4.3.3.4)*

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot\alpha \qquad V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin\alpha \cdot \cos\alpha
$$

Beide Anteile gelten je Laufmeter, wie die Querkraft selbst. Gesucht wird ganzgradig zwischen α\_min und α\_max die Neigung mit dem grössten Widerstand V\_Rd = min(V\_Rd,s; V\_Rd,c). Bei einer Normalzugkraft steilt sich die Druckdiagonale auf: α\_min wird dann auf 40° gesetzt und α\_max notfalls mitgehoben.

**Teilung in y aus der Stabzahl**

$$
s_{V,y} = \frac{b}{n_{V,y}} = \frac{1000}{5} = 200.0\,\mathrm{mm}
$$

#### Nachweis – Feld

**Einwirkung**

$$
V_{Ed} = 80\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 150\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der gezogenen Bewehrung (unten)**

$$
d = 249.0\,\mathrm{mm}
$$

Zwischen α = 30° und α = 45° ganzgradig durchgerechnet; den grössten Widerstand liefert α = 30°.

**Widerstand der Bügel**

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot\alpha
= \frac{50.3\,\mathrm{mm}^{2}}{200\,\mathrm{mm} \cdot 200\,\mathrm{mm}} \cdot 0.9 \cdot 249.0\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30^{\circ} = 212.1\,\mathrm{kN}/\mathrm{m}
$$

**Widerstand der Druckdiagonalen**

$$
V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin\alpha \cdot \cos\alpha
= 0.9 \cdot 249.0\,\mathrm{mm} \cdot 0.55 \cdot 20.0\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30^{\circ} \cdot \cos 30^{\circ} = 1067.4\,\mathrm{kN}/\mathrm{m}
$$

**Querkraftwiderstand**

$$
V_{Rd} = \min\left[V_{Rd,s};\ V_{Rd,c}\right] = \min\left[212.1\,\mathrm{kN}/\mathrm{m};\ 1067.4\,\mathrm{kN}/\mathrm{m}\right] = 212.1\,\mathrm{kN}/\mathrm{m}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x} = \frac{V_{Rd}}{\left|V_{Ed}\right|} = \frac{212.1\,\mathrm{kN}/\mathrm{m}}{80.0\,\mathrm{kN}/\mathrm{m}} = 2.65 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Stütze

**Einwirkung**

$$
V_{Ed} = 60\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = -60\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der gezogenen Bewehrung (oben)**

$$
d = 252.0\,\mathrm{mm}
$$

Zwischen α = 30° und α = 45° ganzgradig durchgerechnet; den grössten Widerstand liefert α = 30°.

**Widerstand der Bügel**

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot\alpha
= \frac{50.3\,\mathrm{mm}^{2}}{200\,\mathrm{mm} \cdot 200\,\mathrm{mm}} \cdot 0.9 \cdot 252.0\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30^{\circ} = 214.6\,\mathrm{kN}/\mathrm{m}
$$

**Widerstand der Druckdiagonalen**

$$
V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin\alpha \cdot \cos\alpha
= 0.9 \cdot 252.0\,\mathrm{mm} \cdot 0.55 \cdot 20.0\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30^{\circ} \cdot \cos 30^{\circ} = 1080.3\,\mathrm{kN}/\mathrm{m}
$$

**Querkraftwiderstand**

$$
V_{Rd} = \min\left[V_{Rd,s};\ V_{Rd,c}\right] = \min\left[214.6\,\mathrm{kN}/\mathrm{m};\ 1080.3\,\mathrm{kN}/\mathrm{m}\right] = 214.6\,\mathrm{kN}/\mathrm{m}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x} = \frac{V_{Rd}}{\left|V_{Ed}\right|} = \frac{214.6\,\mathrm{kN}/\mathrm{m}}{60.0\,\mathrm{kN}/\mathrm{m}} = 3.58 \quad \Rightarrow \quad \text{erfüllt}
$$

### Duktilität

Die Druckzone muss schlank bleiben, damit der Stahl lange fliesst, bevor der Beton versagt: der Querschnitt kündigt sein Versagen an. Gerechnet wird die Druckzonenhöhe bei reiner Biegung, je Lage einzeln.

**Kräftegleichgewicht bei M\_Ed = 0** *(SIA 262:2025, 4.1.4.2.5)*

$$
0.85 \cdot x \cdot b \cdot f_{cd} = A_s \cdot f_{sd} \qquad \Rightarrow \qquad x = \frac{A_s \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}}
$$

**Bedingung**

$$
\frac{x}{d} \le 0.35
$$

d wird von der gedrückten Randfaser aus gemessen: bei den unteren Lagen von der Oberkante, bei den oberen von der Unterkante. Grundbewehrung und Zulage einer Lage zählen mit ihrem gemeinsamen Schwerpunkt.

#### Duktilität – 2. Lage

**Bewehrung der Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

**Gemeinsamer Schwerpunkt der Lage**

$$
\begin{aligned}
  d_{2,x} &= \frac{A_{s,2,x,g} \cdot d_{2,x,g} + A_{s,2,x,z} \cdot d_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

**Druckzonenhöhe bei reiner Biegung**

$$
x = \frac{A_{s,2,x} \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}} = \frac{2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 62.7\,\mathrm{mm}
$$

**Bezogene Druckzonenhöhe** *(SIA 262:2025, 4.1.4.2.5)*

$$
\left(x/d\right)_{2} = \frac{x}{d_{2,x}} = \frac{62.7\,\mathrm{mm}}{248.1\,\mathrm{mm}} = 0.253 \quad \le \quad \left(x/d\right)_{max} = 0.35 \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,D,2} = \frac{\left(x/d\right)_{max}}{\left(x/d\right)_{2}} = \frac{0.35}{0.253} = 1.39
$$

#### Duktilität – 3. Lage

**Statische Höhe ab der gedrückten Randfaser (unten)**

$$
d_{3,x,g} = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

**Druckzonenhöhe bei reiner Biegung**

$$
x = \frac{A_{s,3,x,g} \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}} = \frac{754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 19.3\,\mathrm{mm}
$$

**Bezogene Druckzonenhöhe** *(SIA 262:2025, 4.1.4.2.5)*

$$
\left(x/d\right)_{3} = \frac{x}{d_{3,x,g}} = \frac{19.3\,\mathrm{mm}}{252\,\mathrm{mm}} = 0.077 \quad \le \quad \left(x/d\right)_{max} = 0.35 \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,D,3} = \frac{\left(x/d\right)_{max}}{\left(x/d\right)_{3}} = \frac{0.35}{0.077} = 4.57
$$

Massgebend ist die 2. Lage mit dem kleineren Erfüllungsgrad; sie steht in der Zusammenfassung.

### Sprödes Versagen unter Zwängung – x-Richtung

Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick. Die Bewehrung muss die Kraft übernehmen können, die der Beton beim Reissen abgibt – erst dann kündigt sich das Versagen an.

**Rissaktive Plattendicke**

$$
h_{eff} = \min\left[500\,\mathrm{mm};\ h\right] = \min\left[500;\ 300\right] = 300\,\mathrm{mm}
$$

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h_{eff}} = \frac{1}{1 + 0.5 \cdot 0.300\,\mathrm{m}} = 0.870
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.870 \cdot 2.90\,\mathrm{N}/\mathrm{mm}^{2} = 2.52\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Risskraft der gezogenen Querschnittshälfte**

$$
N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff} = \frac{300\,\mathrm{mm}}{2} \cdot 1000\,\mathrm{mm} \cdot 2.52\,\mathrm{N}/\mathrm{mm}^{2} = 378.3\,\mathrm{kN}
$$

#### Rissnormalkraft – 2. Lage x

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm,2,x} = \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{2,x}}};\ f_{yk}\right]
= \min\left[\sqrt{\frac{9 \cdot 200000 \cdot 2.90 \cdot 0.5}{18}};\ 500\right] = 381\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Aufnehmbare Risskraft**

$$
N_{s,adm,2,x} = A_{s,2,x} \cdot \sigma_{s,adm,2,x} = 2450\,\mathrm{mm}^{2} \cdot 381\,\mathrm{N}/\mathrm{mm}^{2} = 933.1\,\mathrm{kN} \quad \ge \quad N_{Riss} = 378.3\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,NR,2,x} = \frac{N_{s,adm,2,x}}{N_{Riss}} = \frac{933.1\,\mathrm{kN}}{378.3\,\mathrm{kN}} = 2.47
$$

#### Rissnormalkraft – 3. Lage x

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm,3,x,g} = \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{3,x,g}}};\ f_{yk}\right]
= \min\left[\sqrt{\frac{9 \cdot 200000 \cdot 2.90 \cdot 0.5}{12}};\ 500\right] = 466\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Aufnehmbare Risskraft**

$$
N_{s,adm,3,x,g} = A_{s,3,x,g} \cdot \sigma_{s,adm,3,x,g} = 754\,\mathrm{mm}^{2} \cdot 466\,\mathrm{N}/\mathrm{mm}^{2} = 351.6\,\mathrm{kN} \quad < \quad N_{Riss} = 378.3\,\mathrm{kN} \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,NR,3,x,g} = \frac{N_{s,adm,3,x,g}}{N_{Riss}} = \frac{351.6\,\mathrm{kN}}{378.3\,\mathrm{kN}} = 0.93
$$

Massgebend ist die 3. Lage mit dem kleineren Erfüllungsgrad; sie steht in der Zusammenfassung.

### Sprödes Versagen – x-Richtung

Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick. Nachgewiesen wird deshalb, dass der bewehrte Querschnitt mehr trägt als der unbewehrte im Augenblick des Risses: M\_Rd(N\_Ed = 0) ≥ M\_Riss.

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.1.3)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.3/3} = 0.952 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.952 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.76\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6} = 2.76\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\left(300\,\mathrm{mm}\right)^{2} \cdot 1000\,\mathrm{mm}}{6} = 41.4\,\mathrm{kNm}
$$

#### Sprödes Versagen – 2. Lage x

**Biegewiderstand gegen Rissmoment**

$$
M_{Rd,x}(N_{Ed} = 0)_{2} = 235.9\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 41.4\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,SV,2,x} = \frac{M_{Rd,x}(N_{Ed} = 0)_{2}}{M_{Riss}} = \frac{235.9\,\mathrm{kNm}}{41.4\,\mathrm{kNm}} = 5.69
$$

#### Sprödes Versagen – 3. Lage x

**Biegewiderstand gegen Rissmoment**

$$
M_{Rd,x}(N_{Ed} = 0)_{3} = 79.9\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 41.4\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,SV,3,x} = \frac{M_{Rd,x}(N_{Ed} = 0)_{3}}{M_{Riss}} = \frac{79.9\,\mathrm{kNm}}{41.4\,\mathrm{kNm}} = 1.93
$$

Massgebend ist die 3. Lage mit dem kleineren Erfüllungsgrad; sie steht in der Zusammenfassung.

### Zwängung auf Biegung – x-Richtung

Eine aufgezwungene Krümmung erzeugt beim Reissen ein Moment, das die Bewehrung übernehmen muss – ohne über die zulässige Stahlspannung zu kommen. Nicht zu verwechseln mit dem Nachweis gegen sprödes Versagen: dort steht der Biegewiderstand gegen das Rissmoment, hier die Stahlspannung gegen ihre Grenze.

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.300\,\mathrm{m}/3} = 0.952
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.952 \cdot 2.90\,\mathrm{N}/\mathrm{mm}^{2} = 2.76\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6} = 2.76\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\left(300\,\mathrm{mm}\right)^{2} \cdot 1000\,\mathrm{mm}}{6} = 41.4\,\mathrm{kNm}
$$

Das Rissmoment gilt für den ungerissenen Bruttoquerschnitt – den Zustand vor dem Riss. Der Widerstand dagegen wird am gerissenen Querschnitt bestimmt, also für den Augenblick danach. Dass zwei verschiedene Querschnitte auftreten, ist genau die Frage: reicht die Bewehrung für das, was der Beton abgibt?

**Wertigkeit im gerissenen Zustand**

$$
n = \frac{E_s}{E_{cm}} \cdot \left(1 + \varphi\right) = \frac{200000\,\mathrm{N}/\mathrm{mm}^{2}}{33620\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \left(1 + 2.00\right) = 17.85
$$

Das Kriechen weicht den Beton auf: E\_c,eff = E\_cm/(1+φ), und die Wertigkeit ist E\_s/E\_c,eff. Ein grösseres φ senkt damit den Hebelarm und liegt auf der sicheren Seite.

#### Zwängung auf Biegung – 2. Lage x

**Statische Höhe ab der gedrückten Randfaser (unten)**

$$
d_{2,x} = 248.1\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm,2,x} = \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{2,x}}};\ f_{yk}\right]
= \min\left[\sqrt{\frac{9 \cdot 200000 \cdot 2.90 \cdot 0.5}{18}};\ 500\right] = 381\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Nulllinie des gerissenen Querschnitts**

$$
\rho = \frac{n \cdot A_{s,2,x}}{b} \qquad x = \sqrt{\rho^{2} + 2 \cdot d_{2,x} \cdot \rho} - \rho
= \sqrt{\left(43.73\,\mathrm{mm}\right)^{2} + 2 \cdot 248.1\,\mathrm{mm} \cdot 43.73\,\mathrm{mm}} - 43.73\,\mathrm{mm} = 109.9\,\mathrm{mm}
$$

**Innerer Hebelarm**

$$
z = d_{2,x} - \frac{x}{3} = 248.1\,\mathrm{mm} - \frac{109.9\,\mathrm{mm}}{3} = 211.4\,\mathrm{mm}
$$

Die Betondruckspannung verläuft dreieckig – null in der Nulllinie, am grössten an der gedrückten Kante. Ihre Resultierende liegt deshalb bei x/3 von dieser Kante.

**Aufnehmbares Moment der Bewehrung**

$$
M_{s,adm,2,x} = \sigma_{s,adm,2,x} \cdot A_{s,2,x} \cdot z = 381\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2450\,\mathrm{mm}^{2} \cdot 211.4\,\mathrm{mm} = 197.3\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 41.4\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,2,x} = \frac{M_{s,adm,2,x}}{M_{Riss}} = \frac{197.3\,\mathrm{kNm}}{41.4\,\mathrm{kNm}} = 4.76
$$

#### Zwängung auf Biegung – 3. Lage x

**Statische Höhe ab der gedrückten Randfaser (oben)**

$$
d_{3,x,g} = 252.0\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm,3,x,g} = \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{3,x,g}}};\ f_{yk}\right]
= \min\left[\sqrt{\frac{9 \cdot 200000 \cdot 2.90 \cdot 0.5}{12}};\ 500\right] = 466\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Nulllinie des gerissenen Querschnitts**

$$
\rho = \frac{n \cdot A_{s,3,x,g}}{b} \qquad x = \sqrt{\rho^{2} + 2 \cdot d_{3,x,g} \cdot \rho} - \rho
= \sqrt{\left(13.46\,\mathrm{mm}\right)^{2} + 2 \cdot 252.0\,\mathrm{mm} \cdot 13.46\,\mathrm{mm}} - 13.46\,\mathrm{mm} = 70.0\,\mathrm{mm}
$$

**Innerer Hebelarm**

$$
z = d_{3,x,g} - \frac{x}{3} = 252.0\,\mathrm{mm} - \frac{70.0\,\mathrm{mm}}{3} = 228.7\,\mathrm{mm}
$$

Die Betondruckspannung verläuft dreieckig – null in der Nulllinie, am grössten an der gedrückten Kante. Ihre Resultierende liegt deshalb bei x/3 von dieser Kante.

**Aufnehmbares Moment der Bewehrung**

$$
M_{s,adm,3,x,g} = \sigma_{s,adm,3,x,g} \cdot A_{s,3,x,g} \cdot z = 466\,\mathrm{N}/\mathrm{mm}^{2} \cdot 754\,\mathrm{mm}^{2} \cdot 228.7\,\mathrm{mm} = 80.4\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 41.4\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,3,x,g} = \frac{M_{s,adm,3,x,g}}{M_{Riss}} = \frac{80.4\,\mathrm{kNm}}{41.4\,\mathrm{kNm}} = 1.94
$$

Massgebend ist die 3. Lage mit dem kleineren Erfüllungsgrad; sie steht in der Zusammenfassung.

### Stahlspannung unter quasi-ständiger Einwirkung – x-Richtung

Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Rissbreite – dieselbe Grenze wie bei der Zwängung, nur dass die Spannung hier aus den Lasten kommt und nicht aus einer aufgezwungenen Verformung. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf, im Druck rechnet er linear mit dem wirksamen Modul. Gezählt wird nur gezogene Bewehrung.

**Wirksamer Elastizitätsmodul**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad n = 17.85
$$

**Dickster Stab der Tragrichtung**

$$
\varnothing_{max} = 18\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{max}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{18\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 381\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

#### Welche Werte angesetzt werden

Drei Festlegungen stecken in jeder Zahl unten, und alle drei sind Auslegung der Norm und nicht Rechnung. Erstens das Kriechen: angesetzt wird dasselbe φ wie sonst, hier aus der Eingabe. Das liegt auf der sicheren Seite – ein grösseres φ weicht den Beton auf, die Druckzone wächst, der Hebelarm wird kleiner und die Stahlspannung damit grösser. Wer φ = 0 setzte, bekäme kleinere Spannungen und einen Nachweis, der leichter aufgeht.

Zweitens die Werkstoffgesetze: sie rechnen mit den charakteristischen Festigkeiten. Der Stahl ist linear bis f\_yk und fliesst dann, der Beton linear bis f\_ck. Ein Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was er darf – der Teilsicherheitsbeiwert gehört in die Tragsicherheit. Läge das Plateau bei f\_yd, bliebe jede Stahlspannung darunter, und eine Grenze darüber könnte nie überschritten werden.

**Werkstoffgesetze im Gebrauchszustand**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2} \qquad \sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

Drittens die Grenze: dieselbe wie bei der Zwängung, mit f\_yk und bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die Rissbreite. Massgebend ist der dickste Stab der Tragrichtung. Welche Lage die grösste Zugspannung trägt, wechselt mit dem Lastfall – bei einem Feldmoment die untere, bei einem Stützmoment die obere –, und der dickste Stab gibt die kleinste zulässige Spannung. Das liegt für beide auf der sicheren Seite.

Fliesst die Bewehrung, bleibt ihre Spannung bei f\_yk stehen, während die Dehnung weiterwächst. Verglichen wird dann die Dehnung: ε\_s gegen ε\_s,adm = σ\_s,adm / E\_s. Solange der Stahl elastisch bleibt, ist das genau der Spannungsvergleich; fliesst er, fällt der Nachweis durch, und zwar um so deutlicher, je weiter er gedehnt ist.

#### Wie die Dehnungsebene gefunden wird

Die Dehnungsebene wird gesucht, nicht hergeleitet. Eine ebene Dehnungsverteilung hat zwei Unbekannte – die Dehnung in der Mittelebene ε\_m und die Krümmung χ – und ihnen stehen zwei Gleichgewichtsbedingungen gegenüber: N und M. Geschlossen auflösen lässt sich das nicht, weil die Werkstoffgesetze nichtlinear sind.

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet, jede mit der Spannung in ihrer Mitte; der Stahl kommt Lage für Lage dazu, und die von ihm verdrängte Betonfläche wird abgezogen, damit dieselbe Fläche nicht zweimal zählt.

Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer festgehaltenen Krümmung χ wird ε\_m so lange halbiert, bis N\_int die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr Zug bedeutet. Aussen: mit diesem ε\_m bleibt ein Moment übrig, und χ wird so lange halbiert, bis auch M\_int stimmt – hier trägt die Monotonie, dass mehr Krümmung mehr Moment heisst.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.0 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Halbierung liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Nachgewiesen wird deshalb nicht der Weg, sondern das Ergebnis: dass die gefundene Ebene genau die angegebenen Schnittgrössen erzeugt. Diese Probe steht bei jedem Fall.

#### Quasi-ständiger Lastfall – Feld (60 %)

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = 90\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.2725\,\text{‰} \qquad \chi = 0.00607\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 90\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 175\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{381\,\mathrm{N}/\mathrm{mm}^{2}}{175\,\mathrm{N}/\mathrm{mm}^{2}} = 2.18
$$

#### Quasi-ständiger Lastfall – Feld mit Druck (60 %)

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = 72\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = -180\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.1006\,\text{‰} \qquad \chi = 0.00432\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = -180\,\mathrm{kN} \;\checkmark \qquad M_{int} = 72\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 106\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,x,\text{Feld mit Druck (60 \%)}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{381\,\mathrm{N}/\mathrm{mm}^{2}}{106\,\mathrm{N}/\mathrm{mm}^{2}} = 3.60
$$

#### Quasi-ständiger Lastfall – Stütze (60 %)

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = -36\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.4864\,\text{‰} \qquad \chi = -0.00565\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = -36\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 212\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,x,\text{Stütze (60 \%)}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{381\,\mathrm{N}/\mathrm{mm}^{2}}{212\,\mathrm{N}/\mathrm{mm}^{2}} = 1.79
$$

#### Quasi-ständiger Lastfall – Dauerlast

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = 70\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.212\,\text{‰} \qquad \chi = 0.00472\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 70\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 136\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,x,\text{Dauerlast}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{381\,\mathrm{N}/\mathrm{mm}^{2}}{136\,\mathrm{N}/\mathrm{mm}^{2}} = 2.80
$$

### Stahlspannung unter häufiger Einwirkung – x-Richtung

Unter häufiger Einwirkung darf die Bewehrung nicht fliessen – sonst bleiben Risse und Durchbiegung dauerhaft. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf, im Druck rechnet er linear mit dem wirksamen Modul. Gezählt wird nur gezogene Bewehrung.

**Wirksamer Elastizitätsmodul**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad n = 17.85
$$

**Zulässige Stahlspannung** *(SIA 262:2025, Tabelle 17)*

$$
\sigma_{s,adm} = f_{yd} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 435\,\mathrm{N}/\mathrm{mm}^{2} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 355\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

Drei Festlegungen stecken in jeder Zahl unten, und alle drei sind Auslegung der Norm und nicht Rechnung. Erstens das Kriechen: angesetzt wird dasselbe φ wie sonst, hier aus der Eingabe. Das liegt auf der sicheren Seite – ein grösseres φ weicht den Beton auf, die Druckzone wächst, der Hebelarm wird kleiner und die Stahlspannung damit grösser. Wer φ = 0 setzte, bekäme kleinere Spannungen und einen Nachweis, der leichter aufgeht.

Zweitens die Werkstoffgesetze: sie rechnen mit den charakteristischen Festigkeiten. Der Stahl ist linear bis f\_yk und fliesst dann, der Beton linear bis f\_ck. Ein Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was er darf – der Teilsicherheitsbeiwert gehört in die Tragsicherheit. Läge das Plateau bei f\_yd, bliebe jede Stahlspannung darunter, und eine Grenze darüber könnte nie überschritten werden.

**Werkstoffgesetze im Gebrauchszustand**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2} \qquad \sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

Drittens die Grenze: sie rechnet mit dem Bemessungswert, σ\_s,adm = f\_yd − 80 N/mm², und nicht mit f\_yk − 80. Die Norm sagt an dieser Stelle nicht eindeutig, welcher Wert gemeint ist; f\_yd ist die strengere Wahl – die Grenze liegt rund 15 % tiefer –, gewählt ist deshalb die Seite, auf der man nicht danebenliegen kann. Das ist etwas anderes als das Fliessplateau oben: dort geht es darum, was der Stahl tut, hier darum, wie viel Abstand man davon verlangt.

Fliesst die Bewehrung, bleibt ihre Spannung bei f\_yk stehen, während die Dehnung weiterwächst. Verglichen wird dann die Dehnung: ε\_s gegen ε\_s,adm = σ\_s,adm / E\_s. Solange der Stahl elastisch bleibt, ist das genau der Spannungsvergleich; fliesst er, fällt der Nachweis durch, und zwar um so deutlicher, je weiter er gedehnt ist.

#### Wie die Dehnungsebene gefunden wird

Die Dehnungsebene wird gesucht, nicht hergeleitet. Eine ebene Dehnungsverteilung hat zwei Unbekannte – die Dehnung in der Mittelebene ε\_m und die Krümmung χ – und ihnen stehen zwei Gleichgewichtsbedingungen gegenüber: N und M. Geschlossen auflösen lässt sich das nicht, weil die Werkstoffgesetze nichtlinear sind.

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet, jede mit der Spannung in ihrer Mitte; der Stahl kommt Lage für Lage dazu, und die von ihm verdrängte Betonfläche wird abgezogen, damit dieselbe Fläche nicht zweimal zählt.

Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer festgehaltenen Krümmung χ wird ε\_m so lange halbiert, bis N\_int die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr Zug bedeutet. Aussen: mit diesem ε\_m bleibt ein Moment übrig, und χ wird so lange halbiert, bis auch M\_int stimmt – hier trägt die Monotonie, dass mehr Krümmung mehr Moment heisst.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.0 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Halbierung liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Nachgewiesen wird deshalb nicht der Weg, sondern das Ergebnis: dass die gefundene Ebene genau die angegebenen Schnittgrössen erzeugt. Diese Probe steht bei jedem Fall.

#### Häufiger Lastfall – Feld (70 %)

**Einwirkung**

$$
M_{Ed,häufig} = 105\,\mathrm{kNm} \qquad N_{Ed,häufig} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.318\,\text{‰} \qquad \chi = 0.00709\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 105\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 204\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,x,\text{Feld (70 \%)}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{204\,\mathrm{N}/\mathrm{mm}^{2}} = 1.74
$$

#### Häufiger Lastfall – Feld mit Druck (70 %)

**Einwirkung**

$$
M_{Ed,häufig} = 84\,\mathrm{kNm} \qquad N_{Ed,häufig} = -210\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.1174\,\text{‰} \qquad \chi = 0.00504\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = -210\,\mathrm{kN} \;\checkmark \qquad M_{int} = 84\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 123\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,x,\text{Feld mit Druck (70 \%)}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{123\,\mathrm{N}/\mathrm{mm}^{2}} = 2.88
$$

#### Häufiger Lastfall – Stütze (70 %)

**Einwirkung**

$$
M_{Ed,häufig} = -42\,\mathrm{kNm} \qquad N_{Ed,häufig} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.5674\,\text{‰} \qquad \chi = -0.00659\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = -42\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 248\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,x,\text{Stütze (70 \%)}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{248\,\mathrm{N}/\mathrm{mm}^{2}} = 1.43
$$

#### Häufiger Lastfall – Gebrauch

**Einwirkung**

$$
M_{Ed,häufig} = 90\,\mathrm{kNm} \qquad N_{Ed,häufig} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.2725\,\text{‰} \qquad \chi = 0.00607\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 90\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 175\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,x,\text{Gebrauch}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{175\,\mathrm{N}/\mathrm{mm}^{2}} = 2.03
$$

### Knicken

Nachgewiesen wird am verformten System. Die Ausmitte zweiter Ordnung hängt von der Krümmung ab, die Krümmung vom Moment und das Moment wieder von der Ausmitte – also wird die Folge so lange durchlaufen, bis sie einläuft. Läuft sie nicht ein, gibt es keine Gleichgewichtslage: das System knickt.

Der Erfüllungsgrad ist ein Verhältnis von Normalkräften: N\_Rd ist die grösste Druckkraft, unter der der Stab noch steht. Über Momente zu vergleichen ginge nur, solange es ein Gleichgewicht gibt – beim Knicken ist gerade das der Fall, der fehlt.

**Ungewollte Ausmitte – allgemein** *(SIA 262:2025, 4.3.7)*

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \qquad e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

**Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}\right)
$$

**Steifigkeit des Betons**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad f_{cd} = 20\,\mathrm{N}/\mathrm{mm}^{2}
$$

Angesetzt wird das Kriechen mit demselben φ wie sonst, hier aus der Eingabe. Beim Knicken ist das nicht bloss zulässig, sondern wesentlich: ein aufgeweichter Beton verformt sich mehr, die Ausmitte zweiter Ordnung wächst, und der Stab knickt früher. φ = 0 läge hier deutlich auf der unsicheren Seite.

Die Festigkeiten sind Bemessungswerte – f\_cd und f\_yd, nicht die charakteristischen. Gerechnet wird mit dem nichtlinearen Betongesetz; im Bereich der Gebrauchslasten unterscheidet es sich kaum vom linearen, in der Nähe der Grenzlast erheblich, und genau dort entscheidet sich, ob es noch eine Gleichgewichtslage gibt.

#### Wie die Dehnungsebene gefunden wird

Die Dehnungsebene wird gesucht, nicht hergeleitet. Eine ebene Dehnungsverteilung hat zwei Unbekannte – die Dehnung in der Mittelebene ε\_m und die Krümmung χ – und ihnen stehen zwei Gleichgewichtsbedingungen gegenüber: N und M. Geschlossen auflösen lässt sich das nicht, weil die Werkstoffgesetze nichtlinear sind.

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet, jede mit der Spannung in ihrer Mitte; der Stahl kommt Lage für Lage dazu, und die von ihm verdrängte Betonfläche wird abgezogen, damit dieselbe Fläche nicht zweimal zählt.

Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer festgehaltenen Krümmung χ wird ε\_m so lange halbiert, bis N\_int die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr Zug bedeutet. Aussen: mit diesem ε\_m bleibt ein Moment übrig, und χ wird so lange halbiert, bis auch M\_int stimmt – hier trägt die Monotonie, dass mehr Krümmung mehr Moment heisst.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.0 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Halbierung liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Nachgewiesen wird deshalb nicht der Weg, sondern das Ergebnis: dass die gefundene Ebene genau die angegebenen Schnittgrössen erzeugt. Diese Probe steht bei jedem Fall.

Die Ausmitten-Iteration darüber steht dagegen vollständig da, Durchlauf für Durchlauf: sie ist das Verfahren selbst, und dass sie einläuft, ist die Aussage des Nachweises.

#### Knicken – Wand

**Einwirkung und System**

$$
N_{Ed} = -800\,\mathrm{kN} \qquad M_{Ed,1} = 20\,\mathrm{kNm} \qquad l = 3\,\mathrm{m} \qquad l_{cr} = 3\,\mathrm{m}
$$

**Schiefstellung** *(SIA 262:2025, 4.3.7)*

$$
\begin{aligned}
  \alpha_i &= \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= \min\left[\max\left(\frac{0.01}{\sqrt{3}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= 0.005 \quad \left(l\ \text{in}\ \mathrm{m}\right)
\end{aligned}
$$

**Ungewollte Ausmitte** *(SIA 262:2025, 4.3.7)*

$$
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right) = \max\left(\frac{249\,\mathrm{mm}}{30};\ \frac{0.005 \cdot 3\,\mathrm{m}}{2}\right) = 8.3\,\mathrm{mm}
$$

**Gewollte Ausmitte**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| = \left|\frac{20\,\mathrm{kNm}}{-800\,\mathrm{kN}}\right| = 25\,\mathrm{mm}
$$

**Das Verfahren** *(SIA 262:2025, 4.3.7)*

$$
e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}^{(k-1)}\right)
$$

Zu jedem Moment wird die Dehnungsebene gesucht, die es im Gleichgewicht hält; aus deren Krümmung folgt die nächste Ausmitte. Begonnen wird mit e\_2d = 0, also ohne Verformung.

**Ausmitten-Iteration bei N\_Ed = 800.0 kN**

| $k$ | $e_{2d}^{(k-1)}\ [\mathrm{mm}]$ | $M_{Ed,II}^{(k)}\ [\mathrm{kNm}]$ | $\chi^{(k)}\ [\mathrm{m}^{-1}]$ | $e_{2d}^{(k)}\ [\mathrm{mm}]$ |
| ---: | ---: | ---: | ---: | ---: |
| $1$ | $0.00$ | $26.64$ | $0.00087$ | $0.79$ |
| $2$ | $0.79$ | $27.28$ | $0.00089$ | $0.81$ |
| $3$ | $0.81$ | $27.29$ | $0.00089$ | $0.81$ |
| $4$ | $0.81$ | $27.29$ | $0.00089$ | $0.81$ |

**Probe: die gefundene Ebene erzeugt die Schnittgrössen**

$$
\varepsilon_m = -0.1743\,\text{‰} \qquad \chi = 0.00089\,\mathrm{m}^{-1} \qquad N_{int} = -800\,\mathrm{kN} \;\checkmark \qquad M_{int} = 27.3\,\mathrm{kNm} \;\checkmark
$$

**Querschnitt am verformten System**

$$
M_{Rd,x}(N_{Ed}) = 283.6\,\mathrm{kNm} \quad \ge \quad M_{Ed,II} = 27.3\,\mathrm{kNm}
$$

Gesucht wird die grösste Druckkraft mit Gleichgewichtslage. Die gewollte Ausmitte e\_1d bleibt dabei fest – sie gehört zum System und nicht zur Last, M\_Ed,1 wächst also mit. Bei N = 0 trägt der Stab immer; von dort aus wird das Fenster halbiert, bis getragene und nicht getragene Kraft zusammenfallen.

**Grenzkraft des Stabes**

$$
N_{Rd,K} = 3900.6\,\mathrm{kN} \quad \ge \quad \left|N_{Ed}\right| = 800\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,K,\text{Wand}} = \frac{N_{Rd,K}}{\left|N_{Ed}\right|} = \frac{3900.6\,\mathrm{kN}}{800\,\mathrm{kN}} = 4.88 \quad \Rightarrow \quad \text{erfüllt}
$$

### Beton: C30/37

**Charakteristische Zylinderdruckfestigkeit** *(SIA 262:2025, 3.1.2.2.7)*

$$
f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert zur Berücksichtigung der Festigkeitsminderung** *(SIA 262:2025, 2.4.2.3)*

$$
\eta_{fc} = \min\left[\left(\frac{40\,\mathrm{N}/\mathrm{mm}^{2}}{f_{ck}}\right)^{1/3};\ 1.0\right] = \min\left[\left(\frac{40\,\mathrm{N}/\mathrm{mm}^{2}}{30\,\mathrm{N}/\mathrm{mm}^{2}}\right)^{1/3};\ 1.0\right] = 1
$$

**Teilsicherheitsbeiwert für Beton** *(SIA 262:2025, 2.4.2.6)*

$$
\gamma_c = 1.5
$$

**Bemessungswert der Betondruckfestigkeit** *(SIA 262:2025, 2.4.2.3)*

$$
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c} = \frac{1 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}{1.5} = 20\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Dehnung am Ende des ansteigenden Astes** *(SIA 262:2025, 4.2.1.4)*

$$
\varepsilon_{c1d} = 2\,\text{‰}
$$

**Bruchdehnung des Betons** *(SIA 262:2025, 4.2.1.4)*

$$
\varepsilon_{c2d} = 3.5\,\text{‰}
$$

**Beiwert für die Gesteinskörnung** *(SIA 262:2025, 3.1.2.3.3)*

$$
k_e = 10000
$$

**Mittelwert der Zylinderdruckfestigkeit** *(SIA 262:2025, 3.1.2.2.2)*

$$
f_{cm} = f_{ck} + 8\,\mathrm{N}/\mathrm{mm}^{2} = 30\,\mathrm{N}/\mathrm{mm}^{2} + 8\,\mathrm{N}/\mathrm{mm}^{2} = 38\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Mittelwert des Elastizitätsmoduls** *(SIA 262:2025, 3.1.2.3.3)*

$$
E_{cm} = k_e \cdot \sqrt[3]{f_{cm}} = 10000 \cdot \sqrt[3]{38} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

**Teilsicherheitsbeiwert für den Elastizitätsmodul** *(SIA 262:2025, 4.2.1.15)*

$$
\gamma_{cE} = 1
$$

**Bemessungswert des Elastizitätsmoduls** *(SIA 262:2025, 4.2.1.15)*

$$
E_{cd} = \frac{E_{cm}}{\gamma_{cE}} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1} = 33620\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung** *(SIA 262:2025, 4.2.1.6)*

$$
k_{\sigma} = \frac{E_{cd}}{400 \cdot f_{cd}} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 4.202
$$

**Bemessungswert der Schubspannungsgrenze** *(SIA 262:2025, 2.4.2.4)*

$$
\tau_{cd} = \frac{0.3 \cdot \sqrt{f_{ck}}}{\gamma_c} = \frac{0.3 \cdot \sqrt{30}}{1.5} = 1.1\,\mathrm{N}/\mathrm{mm}^{2} \quad \left(f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

**Mittelwert der Zugfestigkeit** *(SIA 262:2025, 3.1.2.2.7)*

$$
f_{ctm} = 2.9\,\mathrm{N}/\mathrm{mm}^{2}
$$

### Betonstahl: B500B

**Elastizitätsmodul des Betonstahls** *(SIA 262:2025, 3.2.2.4)*

$$
E_s = 200000\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Charakteristische Fliessgrenze** *(SIA 262:2025, 3.2.2.3)*

$$
f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Teilsicherheitsbeiwert für Betonstahl** *(SIA 262:2025, 2.4.2.6)*

$$
\gamma_s = 1.15
$$

**Bemessungswert der Fliessgrenze** *(SIA 262:2025, 2.4.2.5)*

$$
f_{yd} = \frac{f_{yk}}{\gamma_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{1.15} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Charakteristische Fliessgrenze auf Druck** *(SIA 262:2025, 3.2.2.3)*

$$
f_{yk}^{-} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Bemessungswert der Fliessgrenze auf Druck** *(SIA 262:2025, 2.4.2.5)*

$$
f_{yd}^{-} = \frac{f_{yk}^{-}}{\gamma_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{1.15} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Bemessungswert der Dehnung bei Höchstlast** *(SIA 262:2025, 4.2.2.1)*

$$
\varepsilon_{ud} = 4.5\,\%
$$

### Plattenanalyse: Dach

**Plattendicke**

$$
h = 200\,\mathrm{mm}
$$

**Betrachtete Breite (x)**

$$
b = 1000\,\mathrm{mm}
$$

**Betrachtete Breite (y)**

$$
b_y = 1000\,\mathrm{mm}
$$

**Überdeckung unten**

$$
c_{nom,u} = 30\,\mathrm{mm}
$$

**Überdeckung oben**

$$
c_{nom,o} = 30\,\mathrm{mm}
$$

**Bewehrungsquerschnitt je Laufmeter** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{1717\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 200\,\mathrm{mm}} = 67\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 152\,\mathrm{mm} - 48\,\mathrm{mm} \\
  &= 104\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, statische Höhen und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $d\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | x | B500B | $10$ | $150$ | $35$ | $165$ | $524$ |
| 2. Lage Grundbewehrung | y | B500B | $8$ | $150$ | $44$ | $156$ | $335$ |
| 3. Lage Grundbewehrung | y | B500B | $8$ | $150$ | $44$ | $44$ | $335$ |
| 4. Lage Grundbewehrung | x | B500B | $10$ | $150$ | $35$ | $35$ | $524$ |

### Resistenzlinie aus Handrechnung – x-Richtung

Druckzone als Spannungsblock der Höhe 0.85·x mit durchgehend f\_cd; gedrückter Stahl bleibt unberücksichtigt. Die Bewehrung ist je Seite zu einer Lage zusammengefasst, das Moment bezieht sich auf die halbe Querschnittshöhe.

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $d\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | $524$ | $165.0$ | $435$ |
| 4. Lage Grundbewehrung | $524$ | $35.0$ | $435$ |

#### Grösste Druckkraft

**Gleichmässiger Druck, ohne Bewehrung**

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd} = -1000\,\mathrm{mm} \cdot 200\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} = -4000\,\mathrm{kN}
$$

**Zugehöriges Moment**

$$
M_{Rd}(N_{Rd}^{-}) = 0\,\mathrm{kNm}
$$

#### Grösste Zugkraft

**Beide Lagen fliessen auf Zug**

$$
\begin{aligned}
  N_{Rd}^{+} &= A_{s,1,x} \cdot f_{yd} + A_{s,4,x} \cdot f_{yd} \\
  &= 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 455.3\,\mathrm{kN}
\end{aligned}
$$

**Kräfte mal Hebelarm um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}(N_{Rd}^{+}) &= A_{s,1,x} \cdot f_{yd} \cdot \left(d_{1,x} - \tfrac{h}{2}\right) + A_{s,4,x} \cdot f_{yd} \cdot \left(d_{4,x} - \tfrac{h}{2}\right) \\
  &= 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(35\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right) \\
  &= 0\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{+} = \frac{A_{s,1,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 13.4\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{+} &= A_{s,1,x} \cdot f_{yd} \cdot \left(d_{1,x} - \frac{0.85 \cdot x^{+}}{2}\right) \\
  &= 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \frac{0.85 \cdot 13.4\,\mathrm{mm}}{2}\right) \\
  &= 36.3\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe: x = h/2**

$$
x^{+} = \frac{h}{2} = \frac{200\,\mathrm{mm}}{2} = 100\,\mathrm{mm}
$$

**Fliesskriterium – Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{1,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(165\,\mathrm{mm} - 100\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{100\,\mathrm{mm}} = 2.27\,\text{‰}
$$

ε\_s = 2.27 ‰ ≥ ε\_yd = 2.17 ‰ – die Zugbewehrung fliesst, f\_sd = f\_yd gilt.

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,1,x} \cdot f_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1472.3\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,1,x} \cdot f_{sd} \cdot \left(d_{1,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} \cdot \left(\tfrac{200\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 100\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right)\right] \\
  &= 112.5\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{-} = \frac{A_{s,4,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 13.4\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{-} &= -A_{s,4,x} \cdot f_{yd} \cdot \left(d_{4,x} - \frac{0.85 \cdot x^{-}}{2}\right) \\
  &= -524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \frac{0.85 \cdot 13.4\,\mathrm{mm}}{2}\right) \\
  &= -36.3\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe: x = h/2**

$$
x^{-} = \frac{h}{2} = \frac{200\,\mathrm{mm}}{2} = 100\,\mathrm{mm}
$$

**Fliesskriterium – Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{4,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(165\,\mathrm{mm} - 100\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{100\,\mathrm{mm}} = 2.27\,\text{‰}
$$

ε\_s = 2.27 ‰ ≥ ε\_yd = 2.17 ‰ – die Zugbewehrung fliesst, f\_sd = f\_yd gilt.

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,4,x} \cdot f_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1472.3\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,4,x} \cdot f_{sd} \cdot \left(d_{4,x} - \tfrac{h}{2}\right)\right] \\
  &= -\left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} \cdot \left(\tfrac{200\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 100\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right)\right] \\
  &= -112.5\,\mathrm{kNm}
\end{aligned}
$$

**Eckpunkte der Resistenzlinie aus Handrechnung**

| Eckpunkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{-}$ | $-4000.0$ | $0.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1472.3$ | $112.5$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $36.3$ |
| $N_{Rd}^{+}$ | $455.3$ | $0.0$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $0.0$ | $-36.3$ |
| $M_{Rd}(x=\tfrac{h}{2})^{-}$ | $-1472.3$ | $-112.5$ |

#### Nachweis – Feld

**Einwirkung**

$$
M_{Ed} = 80\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 36.3\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{36.3\,\mathrm{kNm}}{80\,\mathrm{kNm}} = 0.45 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

#### Nachweis – Rand

**Einwirkung**

$$
M_{Ed} = 20\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 36.3\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Rand}} = \frac{M_{Rd}}{M_{Ed}} = \frac{36.3\,\mathrm{kNm}}{20\,\mathrm{kNm}} = 1.81 \quad \Rightarrow \quad \text{erfüllt}
$$

### Querkraft – x-Richtung

Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und die Dehnung auf halber Höhe.

**Ansatz** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

**Dekompressionsmoment und Dehnung**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

Nur eine Normaldruckkraft entlastet; eine Zugkraft bleibt beim Dekompressionsmoment unberücksichtigt. Da der Widerstand über m\_Ed und N\_Ed von der Einwirkung abhängt, wird er für jede Kombination einzeln bestimmt.

**Grösstkorndurchmesser**

$$
D_{max} = 32\,\mathrm{mm}
$$

**Höhe der Einlage**

$$
e_{Einlage} = 40\,\mathrm{mm}
$$

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
k_g = \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right]
= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] = \max\left[1.20;\ 1.000\right] = 1.200
$$

#### Querkraftnachweis – Feld

**Einwirkung**

$$
V_{Ed} = 40\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 80\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der gezogenen Bewehrung**

$$
d = 165.0\,\mathrm{mm}\qquad \text{(Zug unten)}
$$

**Wirksame Höhe, um die Einlage vermindert**

$$
d_v = d - e_{Einlage} = 165.0\,\mathrm{mm} - 40.0\,\mathrm{mm} = 125.0\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|0.0\right| \cdot 200\,\mathrm{mm}}{6} = 0.0\,\mathrm{kNm/m}
$$

**Momentenwiderstand bei N\_Ed = 0.0 kN**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 36.3\,\mathrm{kNm}
$$

**Dehnung auf halber Höhe**

$$
\varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
= \frac{435 \cdot \left(80.0 - 0.0\right)}{200000 \cdot \left(36.3 - 0.0\right)} = 3.261\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 3.2609 \cdot 10^{-3} \cdot 165.0 \cdot 1.200} = 0.6077
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd,x}(M_{Ed} = 80\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = k_d \cdot \tau_{cd} \cdot d_v
= 0.6077 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125.0\,\mathrm{mm} = 83.2\,\mathrm{kN}/\mathrm{m}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x} = \frac{V_{Rd}}{\left|V_{Ed}\right|} = \frac{83.2\,\mathrm{kN}/\mathrm{m}}{40.0\,\mathrm{kN}/\mathrm{m}} = 2.08 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Querkraftnachweis – Rand

**Einwirkung**

$$
V_{Ed} = 30\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 20\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der gezogenen Bewehrung**

$$
d = 165.0\,\mathrm{mm}\qquad \text{(Zug unten)}
$$

**Wirksame Höhe, um die Einlage vermindert**

$$
d_v = d - e_{Einlage} = 165.0\,\mathrm{mm} - 40.0\,\mathrm{mm} = 125.0\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|0.0\right| \cdot 200\,\mathrm{mm}}{6} = 0.0\,\mathrm{kNm/m}
$$

**Momentenwiderstand bei N\_Ed = 0.0 kN**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 36.3\,\mathrm{kNm}
$$

**Dehnung auf halber Höhe**

$$
\varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
= \frac{435 \cdot \left(20.0 - 0.0\right)}{200000 \cdot \left(36.3 - 0.0\right)} = 1.199\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 1.1988 \cdot 10^{-3} \cdot 165.0 \cdot 1.200} = 0.8082
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd,x}(M_{Ed} = 20\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = k_d \cdot \tau_{cd} \cdot d_v
= 0.8082 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125.0\,\mathrm{mm} = 110.7\,\mathrm{kN}/\mathrm{m}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x} = \frac{V_{Rd}}{\left|V_{Ed}\right|} = \frac{110.7\,\mathrm{kN}/\mathrm{m}}{30.0\,\mathrm{kN}/\mathrm{m}} = 3.69 \quad \Rightarrow \quad \text{erfüllt}
$$

### Stahlspannung unter quasi-ständiger Einwirkung – x-Richtung

Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Rissbreite – dieselbe Grenze wie bei der Zwängung, nur dass die Spannung hier aus den Lasten kommt und nicht aus einer aufgezwungenen Verformung. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf, im Druck rechnet er linear mit dem wirksamen Modul. Gezählt wird nur gezogene Bewehrung.

**Wirksamer Elastizitätsmodul**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad n = 17.85
$$

**Zulässige Stahlspannung (normale Anforderung)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm} = f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

Drei Festlegungen stecken in jeder Zahl unten, und alle drei sind Auslegung der Norm und nicht Rechnung. Erstens das Kriechen: angesetzt wird dasselbe φ wie sonst, hier aus der Eingabe. Das liegt auf der sicheren Seite – ein grösseres φ weicht den Beton auf, die Druckzone wächst, der Hebelarm wird kleiner und die Stahlspannung damit grösser. Wer φ = 0 setzte, bekäme kleinere Spannungen und einen Nachweis, der leichter aufgeht.

Zweitens die Werkstoffgesetze: sie rechnen mit den charakteristischen Festigkeiten. Der Stahl ist linear bis f\_yk und fliesst dann, der Beton linear bis f\_ck. Ein Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was er darf – der Teilsicherheitsbeiwert gehört in die Tragsicherheit. Läge das Plateau bei f\_yd, bliebe jede Stahlspannung darunter, und eine Grenze darüber könnte nie überschritten werden.

**Werkstoffgesetze im Gebrauchszustand**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2} \qquad \sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

Drittens die Grenze: dieselbe wie bei der Zwängung, mit f\_yk und bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die Rissbreite. Massgebend ist der dickste Stab der Tragrichtung. Welche Lage die grösste Zugspannung trägt, wechselt mit dem Lastfall – bei einem Feldmoment die untere, bei einem Stützmoment die obere –, und der dickste Stab gibt die kleinste zulässige Spannung. Das liegt für beide auf der sicheren Seite.

Fliesst die Bewehrung, bleibt ihre Spannung bei f\_yk stehen, während die Dehnung weiterwächst. Verglichen wird dann die Dehnung: ε\_s gegen ε\_s,adm = σ\_s,adm / E\_s. Solange der Stahl elastisch bleibt, ist das genau der Spannungsvergleich; fliesst er, fällt der Nachweis durch, und zwar um so deutlicher, je weiter er gedehnt ist.

#### Wie die Dehnungsebene gefunden wird

Die Dehnungsebene wird gesucht, nicht hergeleitet. Eine ebene Dehnungsverteilung hat zwei Unbekannte – die Dehnung in der Mittelebene ε\_m und die Krümmung χ – und ihnen stehen zwei Gleichgewichtsbedingungen gegenüber: N und M. Geschlossen auflösen lässt sich das nicht, weil die Werkstoffgesetze nichtlinear sind.

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet, jede mit der Spannung in ihrer Mitte; der Stahl kommt Lage für Lage dazu, und die von ihm verdrängte Betonfläche wird abgezogen, damit dieselbe Fläche nicht zweimal zählt.

Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer festgehaltenen Krümmung χ wird ε\_m so lange halbiert, bis N\_int die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr Zug bedeutet. Aussen: mit diesem ε\_m bleibt ein Moment übrig, und χ wird so lange halbiert, bis auch M\_int stimmt – hier trägt die Monotonie, dass mehr Krümmung mehr Moment heisst.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.0 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Halbierung liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Nachgewiesen wird deshalb nicht der Weg, sondern das Ergebnis: dass die gefundene Ebene genau die angegebenen Schnittgrössen erzeugt. Diese Probe steht bei jedem Fall.

#### Quasi-ständiger Lastfall – Dauerlast

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = 40\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 2.3198\,\text{‰} \qquad \chi = 0.03612\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 40\,\mathrm{kNm} \;\checkmark
$$

Die Bewehrung fliesst: die grösste Zugdehnung liegt über der Fliessdehnung, die Spannung steht bei 500 N/mm² und sagt nichts mehr darüber, wie weit die Grenze überschritten ist. Verglichen wird die Dehnung.

**Grösste Zugdehnung in der Bewehrung**

$$
\varepsilon_y = \frac{f_{yk}}{E_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.5\,\text{‰} \quad < \quad \varepsilon_{s,x} = 4.67\,\text{‰}
$$

**Zulässige Dehnung**

$$
\begin{aligned}
  \varepsilon_{s,adm} &= \frac{\sigma_{s,adm}}{E_s} \\
  &= \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} \\
  &= 2.5\,\text{‰} \quad < \quad \varepsilon_{s,x} = 4.67\,\text{‰} \quad \Rightarrow \quad \text{NICHT erfüllt}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,x,\text{Dauerlast}} = \frac{\varepsilon_{s,adm}}{\varepsilon_{s,x}} = \frac{2.5\,\text{‰}}{4.67\,\text{‰}} = 0.54
$$

### Plattenanalyse: Konsole

**Plattendicke**

$$
h = 250\,\mathrm{mm}
$$

**Betrachtete Breite (x)**

$$
b = 1000\,\mathrm{mm}
$$

**Betrachtete Breite (y)**

$$
b_y = 1000\,\mathrm{mm}
$$

**Überdeckung unten**

$$
c_{nom,u} = 30\,\mathrm{mm}
$$

**Überdeckung oben**

$$
c_{nom,o} = 30\,\mathrm{mm}
$$

**Bewehrungsquerschnitt je Laufmeter** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{2555\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 250\,\mathrm{mm}} = 80\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 198\,\mathrm{mm} - 52\,\mathrm{mm} \\
  &= 146\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, statische Höhen und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $d\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | y | B500B | $10$ | $150$ | $35$ | $215$ | $524$ |
| 2. Lage Grundbewehrung | x | B500B | $12$ | $150$ | $46$ | $204$ | $754$ |
| 3. Lage Grundbewehrung | x | B500B | $12$ | $150$ | $46$ | $46$ | $754$ |
| 4. Lage Grundbewehrung | y | B500B | $10$ | $150$ | $35$ | $35$ | $524$ |

### Resistenzlinie aus Handrechnung – x-Richtung

Druckzone als Spannungsblock der Höhe 0.85·x mit durchgehend f\_cd; gedrückter Stahl bleibt unberücksichtigt. Die Bewehrung ist je Seite zu einer Lage zusammengefasst, das Moment bezieht sich auf die halbe Querschnittshöhe.

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $d\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $754$ | $204.0$ | $435$ |
| 3. Lage Grundbewehrung | $754$ | $46.0$ | $435$ |

#### Grösste Druckkraft

**Gleichmässiger Druck, ohne Bewehrung**

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd} = -1000\,\mathrm{mm} \cdot 250\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} = -5000\,\mathrm{kN}
$$

**Zugehöriges Moment**

$$
M_{Rd}(N_{Rd}^{-}) = 0\,\mathrm{kNm}
$$

#### Grösste Zugkraft

**Beide Lagen fliessen auf Zug**

$$
\begin{aligned}
  N_{Rd}^{+} &= A_{s,2,x} \cdot f_{yd} + A_{s,3,x} \cdot f_{yd} \\
  &= 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 655.6\,\mathrm{kN}
\end{aligned}
$$

**Kräfte mal Hebelarm um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}(N_{Rd}^{+}) &= A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right) \\
  &= 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(46\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right) \\
  &= 0\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{+} = \frac{A_{s,2,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 19.3\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{+} &= A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \frac{0.85 \cdot x^{+}}{2}\right) \\
  &= 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \frac{0.85 \cdot 19.3\,\mathrm{mm}}{2}\right) \\
  &= 64.2\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe: x = h/2**

$$
x^{+} = \frac{h}{2} = \frac{250\,\mathrm{mm}}{2} = 125\,\mathrm{mm}
$$

**Fliesskriterium – Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(204\,\mathrm{mm} - 125\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{125\,\mathrm{mm}} = 2.21\,\text{‰}
$$

ε\_s = 2.21 ‰ ≥ ε\_yd = 2.17 ‰ – die Zugbewehrung fliesst, f\_sd = f\_yd gilt.

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot f_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1797.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot f_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} \cdot \left(\tfrac{250\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 125\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right)\right] \\
  &= 178.6\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{-} = \frac{A_{s,3,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 19.3\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{-} &= -A_{s,3,x} \cdot f_{yd} \cdot \left(d_{3,x} - \frac{0.85 \cdot x^{-}}{2}\right) \\
  &= -754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \frac{0.85 \cdot 19.3\,\mathrm{mm}}{2}\right) \\
  &= -64.2\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe: x = h/2**

$$
x^{-} = \frac{h}{2} = \frac{250\,\mathrm{mm}}{2} = 125\,\mathrm{mm}
$$

**Fliesskriterium – Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{3,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(204\,\mathrm{mm} - 125\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{125\,\mathrm{mm}} = 2.21\,\text{‰}
$$

ε\_s = 2.21 ‰ ≥ ε\_yd = 2.17 ‰ – die Zugbewehrung fliesst, f\_sd = f\_yd gilt.

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,3,x} \cdot f_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1797.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,3,x} \cdot f_{sd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right)\right] \\
  &= -\left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} \cdot \left(\tfrac{250\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 125\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right)\right] \\
  &= -178.6\,\mathrm{kNm}
\end{aligned}
$$

**Eckpunkte der Resistenzlinie aus Handrechnung**

| Eckpunkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{-}$ | $-5000.0$ | $0.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1797.2$ | $178.6$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $64.2$ |
| $N_{Rd}^{+}$ | $655.6$ | $0.0$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $0.0$ | $-64.2$ |
| $M_{Rd}(x=\tfrac{h}{2})^{-}$ | $-1797.2$ | $-178.6$ |

#### Nachweis – Feld

**Einwirkung**

$$
M_{Ed} = 40\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 64.2\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{64.2\,\mathrm{kNm}}{40\,\mathrm{kNm}} = 1.60 \quad \Rightarrow \quad \text{erfüllt}
$$

### Querkraft – x-Richtung

Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und die Dehnung auf halber Höhe.

**Ansatz** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

**Dekompressionsmoment und Dehnung**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

Nur eine Normaldruckkraft entlastet; eine Zugkraft bleibt beim Dekompressionsmoment unberücksichtigt. Da der Widerstand über m\_Ed und N\_Ed von der Einwirkung abhängt, wird er für jede Kombination einzeln bestimmt.

**Grösstkorndurchmesser**

$$
D_{max} = 32\,\mathrm{mm}
$$

**Höhe der Einlage**

$$
e_{Einlage} = 0\,\mathrm{mm}
$$

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
k_g = \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right]
= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] = \max\left[1.20;\ 1.000\right] = 1.200
$$

#### Querkraftnachweis – Feld

**Einwirkung**

$$
V_{Ed} = 50\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 40\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der gezogenen Bewehrung**

$$
d = 204.0\,\mathrm{mm}\qquad \text{(Zug unten)}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v = d = 204.0\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|0.0\right| \cdot 250\,\mathrm{mm}}{6} = 0.0\,\mathrm{kNm/m}
$$

**Momentenwiderstand bei N\_Ed = 0.0 kN**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 64.2\,\mathrm{kNm}
$$

**Dehnung auf halber Höhe**

$$
\varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
= \frac{435 \cdot \left(40.0 - 0.0\right)}{200000 \cdot \left(64.2 - 0.0\right)} = 1.355\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 1.3547 \cdot 10^{-3} \cdot 204.0 \cdot 1.200} = 0.7510
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd,x}(M_{Ed} = 40\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = k_d \cdot \tau_{cd} \cdot d_v
= 0.7510 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 204.0\,\mathrm{mm} = 167.8\,\mathrm{kN}/\mathrm{m}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x} = \frac{V_{Rd}}{\left|V_{Ed}\right|} = \frac{167.8\,\mathrm{kN}/\mathrm{m}}{50.0\,\mathrm{kN}/\mathrm{m}} = 3.36 \quad \Rightarrow \quad \text{erfüllt}
$$

### Plattenanalyse: Ohne x

### Ohne Bewehrung – x-Richtung

In x-Richtung ist keine Bewehrung definiert. Der Widerstand der Handrechnung ist damit null, der Nachweis nicht erfüllt.

## Nachweise

### Decke

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 300\,\mathrm{mm} \qquad b_x = 1000\,\mathrm{mm}
$$

**Bewehrung von oben nach unten**

| Lage | Richtung | Bewehrung | Stahl |
| :--- | :--- | :--- | :--- |
| Überdeckung oben | – | $30\,\mathrm{mm}$ | – |
| 4. Lage | y | $\varnothing 12@150$ | B500B |
| 3. Lage | x | $\varnothing 12@150$ | B500B |
| 2. Lage | x | $\varnothing 18@150 + \varnothing 12@150$ | B500B |
| 1. Lage | y | $\varnothing 12@150$ | B500B |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – |
| Querkraftbewehrung | x/y | $\varnothing 8@200@5\,\text{Stk}$ | B500B |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 235.9\,\mathrm{kNm}$ | $M_{Ed,x} = 150.0\,\mathrm{kNm}$ | $1.57$ |
| Biegung und Normalkraft | Feld mit Druck | $M_{Rd,x}(N_{Ed} = -300\,\mathrm{kN}) = 253.8\,\mathrm{kNm}$ | $M_{Ed,x} = 120.0\,\mathrm{kNm}$ | $2.12$ |
| Biegung und Normalkraft | Stütze | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = -79.9\,\mathrm{kNm}$ | $M_{Ed,x} = -60.0\,\mathrm{kNm}$ | $1.33$ |
| Querkraft | Feld | $V_{Rd,x}(M_{Ed} = 150\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 212.1\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 80.0\,\mathrm{kN}/\mathrm{m}$ | $2.65$ |
| Querkraft | Stütze | $V_{Rd,x}(M_{Ed} = -60\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 214.6\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 60.0\,\mathrm{kN}/\mathrm{m}$ | $3.58$ |
| Duktilität | 2. Lage | $\left(x/d\right)_{max} = 0.35$ | $\left(x/d\right)_{2} = 0.253$ | $1.39$ |
| Zwängung auf Normalkraft | 3. Lage | $N_{s,adm,3,x} = 351.6\,\mathrm{kN}$ | $N_{Riss} = 378.3\,\mathrm{kN}$ | $0.93$ |
| Sprödes Versagen | 3. Lage | $M_{Rd,x}(N_{Ed} = 0)_{3} = 79.9\,\mathrm{kNm}$ | $M_{Riss} = 41.4\,\mathrm{kNm}$ | $1.93$ |
| Zwängung auf Biegung | 3. Lage | $M_{s,adm,3,x} = 80.4\,\mathrm{kNm}$ | $M_{Riss} = 41.4\,\mathrm{kNm}$ | $1.94$ |
| Stahlspannung aus Rissbreite | Feld (60 %) | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 175\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.18$ |
| Stahlspannung aus Rissbreite | Feld mit Druck (60 %) | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 106\,\mathrm{N}/\mathrm{mm}^{2}$ | $3.60$ |
| Stahlspannung aus Rissbreite | Stütze (60 %) | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 212\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.79$ |
| Stahlspannung aus Rissbreite | Dauerlast | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 136\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.80$ |
| Stahlspannung gegen Fliessen | Feld (70 %) | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 204\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.74$ |
| Stahlspannung gegen Fliessen | Feld mit Druck (70 %) | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 123\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.88$ |
| Stahlspannung gegen Fliessen | Stütze (70 %) | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 248\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.43$ |
| Stahlspannung gegen Fliessen | Gebrauch | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 175\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.03$ |
| Knicken | Wand | $N_{Rd,K} = 3900.6\,\mathrm{kN}$ | $N_{Ed} = 800.0\,\mathrm{kN}$ | $4.88$ |

> **Warnung:** Zwängung auf Normalkraft – 3. Lage: nicht erfüllt. A\_s = 754 mm² bei σ\_s,adm = 466 N/mm² ergibt N\_s,adm = 351.6 kN gegen N\_Riss = 378.3 kN.

### Dach

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 200\,\mathrm{mm} \qquad b_x = 1000\,\mathrm{mm}
$$

**Bewehrung von oben nach unten**

| Lage | Richtung | Bewehrung | Stahl |
| :--- | :--- | :--- | :--- |
| Überdeckung oben | – | $30\,\mathrm{mm}$ | – |
| 4. Lage | x | $\varnothing 10@150$ | B500B |
| 3. Lage | y | $\varnothing 8@150$ | B500B |
| 2. Lage | y | $\varnothing 8@150$ | B500B |
| 1. Lage | x | $\varnothing 10@150$ | B500B |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 36.3\,\mathrm{kNm}$ | $M_{Ed,x} = 80.0\,\mathrm{kNm}$ | $0.45$ |
| Biegung und Normalkraft | Rand | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 36.3\,\mathrm{kNm}$ | $M_{Ed,x} = 20.0\,\mathrm{kNm}$ | $1.81$ |
| Querkraft | Feld | $V_{Rd,x}(M_{Ed} = 80\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 83.2\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 40.0\,\mathrm{kN}/\mathrm{m}$ | $2.08$ |
| Querkraft | Rand | $V_{Rd,x}(M_{Ed} = 20\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 110.7\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 30.0\,\mathrm{kN}/\mathrm{m}$ | $3.69$ |
| Stahlspannung aus Rissbreite | Dauerlast | $\varepsilon_{s,adm} = 2.50\,\text{‰}$ | $\varepsilon_{s,x} = 4.67\,\text{‰}$ | $0.54$ |

> **Warnung:** Biegung und Normalkraft – Feld: nicht erfüllt. Bei festgehaltenem N\_Ed = 0 kN beträgt der Momentenwiderstand M\_Rd = 36.3 kNm.

> **Warnung:** Stahlspannung aus Rissbreite – Dauerlast: nicht erfüllt. Gerissener Querschnitt: ε\_m = 2.3198 ‰, χ = 0.03612 1/m. Die Bewehrung fliesst: ε\_s = 4.67 ‰ über der Fliessdehnung 2.50 ‰, gegen ε\_s,adm = 2.50 ‰ aus σ\_s,adm = 500 N/mm².

> **Hinweis:** Zwängung auf Normalkraft – 1. Lage: nicht erfüllt (α\_eff = 0.99). Dieser Nachweis ist ausgeschaltet und steht nicht in der Herleitung. A\_s = 524 mm² bei σ\_s,adm = 500 N/mm² ergibt N\_s,adm = 261.8 kN gegen N\_Riss = 263.6 kN.

### Ohne x

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 250\,\mathrm{mm} \qquad b_x = 1000\,\mathrm{mm}
$$

**Bewehrung von oben nach unten**

| Lage | Richtung | Bewehrung | Stahl |
| :--- | :--- | :--- | :--- |
| Überdeckung oben | – | $30\,\mathrm{mm}$ | – |
| 4. Lage | y | $\varnothing 12@150$ | B500B |
| 3. Lage | x | – | – |
| 2. Lage | x | – | – |
| 1. Lage | y | $\varnothing 12@150$ | B500B |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x} = 0.0\,\mathrm{kNm}$ | $M_{Ed,x} = 30.0\,\mathrm{kNm}$ | $0.00$ |
| Querkraft | Feld | $V_{Rd,x} = 0.0\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 20.0\,\mathrm{kN}/\mathrm{m}$ | $0.00$ |

> **Hinweis:** Biegung und Normalkraft – Feld, Querkraft – Feld: In x-Richtung ist keine Bewehrung definiert. Der Widerstand der Handrechnung ist damit null, der Nachweis nicht erfüllt.

### Konsole

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 250\,\mathrm{mm} \qquad b_x = 1000\,\mathrm{mm}
$$

**Bewehrung von oben nach unten**

| Lage | Richtung | Bewehrung | Stahl |
| :--- | :--- | :--- | :--- |
| Überdeckung oben | – | $30\,\mathrm{mm}$ | – |
| 4. Lage | y | $\varnothing 10@150$ | B500B |
| 3. Lage | x | $\varnothing 12@150$ | B500B |
| 2. Lage | x | $\varnothing 12@150$ | B500B |
| 1. Lage | y | $\varnothing 10@150$ | B500B |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 64.2\,\mathrm{kNm}$ | $M_{Ed,x} = 40.0\,\mathrm{kNm}$ | $1.60$ |
| Querkraft | Feld | $V_{Rd,x}(M_{Ed} = 40\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 167.8\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 50.0\,\mathrm{kN}/\mathrm{m}$ | $3.36$ |

Mindestens ein Nachweis ist nicht erfüllt.

## Werte

| Bezeichnung | Symbol | Wert | Einheit | Herkunft |
| :--- | :--- | ---: | :--- | :--- |
| Bemessungswert des Elastizitätsmoduls | $E_{cd}$ | $33620$ | N/mm² | berechnet |
| Mittelwert des Elastizitätsmoduls | $E_{cm}$ | $33620$ | N/mm² | berechnet |
| Dehnung am Ende des ansteigenden Astes | $\varepsilon_{c1d}$ | $2$ | ‰ | Vorgabe |
| Bruchdehnung des Betons | $\varepsilon_{c2d}$ | $3.5$ | ‰ | Vorgabe |
| Beiwert zur Berücksichtigung der Festigkeitsminderung | $\eta_{fc}$ | $1$ |  | berechnet |
| Bemessungswert der Betondruckfestigkeit | $f_{cd}$ | $20$ | N/mm² | berechnet |
| Charakteristische Zylinderdruckfestigkeit | $f_{ck}$ | $30$ | N/mm² | Vorgabe |
| Mittelwert der Zylinderdruckfestigkeit | $f_{cm}$ | $38$ | N/mm² | berechnet |
| Mittelwert der Zugfestigkeit | $f_{ctm}$ | $2.9$ | N/mm² | Vorgabe |
| Teilsicherheitsbeiwert für Beton | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Teilsicherheitsbeiwert für den Elastizitätsmodul | $\gamma_{cE}$ | $1$ |  | Vorgabe |
| Beiwert für die Gesteinskörnung | $k_e$ | $10000$ |  | Vorgabe |
| Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung | $k_{\sigma}$ | $4.202$ |  | berechnet |
| Bemessungswert der Schubspannungsgrenze | $\tau_{cd}$ | $1.1$ | N/mm² | berechnet |
| Elastizitätsmodul des Betonstahls | $E_s$ | $200000$ | N/mm² | Vorgabe |
| Bemessungswert der Dehnung bei Höchstlast | $\varepsilon_{ud}$ | $4.5$ | % | Vorgabe |
| Bemessungswert der Fliessgrenze | $f_{yd}$ | $435$ | N/mm² | berechnet |
| Bemessungswert der Fliessgrenze auf Druck | $f_{yd}^{-}$ | $435$ | N/mm² | berechnet |
| Charakteristische Fliessgrenze | $f_{yk}$ | $500$ | N/mm² | Vorgabe |
| Charakteristische Fliessgrenze auf Druck | $f_{yk}^{-}$ | $500$ | N/mm² | Vorgabe |
| Teilsicherheitsbeiwert für Betonstahl | $\gamma_s$ | $1.15$ |  | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $123$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $186$ | mm | berechnet |
| Plattendicke | $h$ | $300$ | mm | Vorgabe |
| Abminderung der Betondruckfestigkeit in der Druckdiagonalen | $k_c$ | $0.55$ |  | Vorgabe |
| Kriechzahl | $\varphi$ | $2$ |  | Vorgabe |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,y,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,y,g}$ | $12$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,y,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 1. Lage Grundbewehrung (ab Oberkante) | $d_{1,y,g}$ | $264$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,x,g}$ | $1696$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,x,g}$ | $18$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,x,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 2. Lage Grundbewehrung (ab Oberkante) | $d_{2,x,g}$ | $249$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Zulage | $A_{s,2,x,z}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Zulage | $\varnothing_{2,x,z}$ | $12$ | mm | Vorgabe |
| Teilung 2. Lage Zulage | $s_{2,x,z}$ | $150$ | mm | Vorgabe |
| Statische Höhe 2. Lage Zulage (ab Oberkante) | $d_{2,x,z}$ | $246$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,x,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,x,g}$ | $12$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,x,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 3. Lage Grundbewehrung (ab Oberkante) | $d_{3,x,g}$ | $48$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,y,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,y,g}$ | $12$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,y,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 4. Lage Grundbewehrung (ab Oberkante) | $d_{4,y,g}$ | $36$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 2. Lage | $\alpha_{eff,D,2}$ | $1.39$ |  | berechnet |
| Bezogene Druckzonenhöhe – 2. Lage | $\left(x/d\right)_{2}$ | $0.253$ |  | berechnet |
| Erfüllungsgrad Duktilität – 3. Lage | $\alpha_{eff,D,3}$ | $4.57$ |  | berechnet |
| Bezogene Druckzonenhöhe – 3. Lage | $\left(x/d\right)_{3}$ | $0.077$ |  | berechnet |
| Erfüllungsgrad Knicken – Wand | $\alpha_{eff,K,\text{Wand}}$ | $4.88$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $235.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $1.573$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld mit Druck | $M_{Rd,x}(N_{Ed})_{\text{Feld mit Druck}}$ | $253.8$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld mit Druck | $\alpha_{eff,x,\text{Feld mit Druck}}$ | $2.115$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-79.9$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $235.9$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $324.4$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-253.4$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-6000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $1393.2$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Stütze | $M_{Rd,x}(N_{Ed})_{\text{Stütze}}$ | $79.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Stütze | $\alpha_{eff,x,\text{Stütze}}$ | $1.332$ |  | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Feld | $\alpha_{eff,V,x,\text{Feld}}$ | $2.65$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Feld | $V_{Rd,x}$ | $212.1$ | kN/m | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Stütze | $\alpha_{eff,V,x,\text{Stütze}}$ | $3.58$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Stütze | $V_{Rd,x}$ | $214.6$ | kN/m | berechnet |
| Erfüllungsgrad Rissnormalkraft – 2. Lage x | $\alpha_{eff,NR,2,x}$ | $2.47$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 3. Lage x | $\alpha_{eff,NR,3,x}$ | $0.93$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen x-Richtung – Feld (70 %) | $\alpha_{eff,\sigma,x,\text{Feld (70 \%)}}$ | $1.74$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen x-Richtung – Feld mit Druck (70 %) | $\alpha_{eff,\sigma,x,\text{Feld mit Druck (70 \%)}}$ | $2.88$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen x-Richtung – Gebrauch | $\alpha_{eff,\sigma,x,\text{Gebrauch}}$ | $2.03$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen x-Richtung – Stütze (70 %) | $\alpha_{eff,\sigma,x,\text{Stütze (70 \%)}}$ | $1.43$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Dauerlast | $\alpha_{eff,\sigma,w,x,\text{Dauerlast}}$ | $2.8$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $2.18$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld mit Druck (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld mit Druck (60 \%)}}$ | $3.6$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Stütze (60 %) | $\alpha_{eff,\sigma,w,x,\text{Stütze (60 \%)}}$ | $1.79$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $5.69$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $1.93$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $4.76$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $1.94$ |  | berechnet |
| Querschnitt eines Bügelschenkels | $A_{\varnothing,V}$ | $50.3$ | mm² | berechnet |
| Grösste Neigung der Druckdiagonalen | $\alpha_{max}$ | $45$ | ° | Vorgabe |
| Kleinste Neigung der Druckdiagonalen | $\alpha_{min}$ | $30$ | ° | Vorgabe |
| Bügelzahl über die betrachtete Breite | $n_{V,y}$ | $5$ |  | Vorgabe |
| Bügeldurchmesser | $\varnothing_{V}$ | $8$ | mm | Vorgabe |
| Bügelteilung in x-Richtung | $s_{V,x}$ | $200$ | mm | Vorgabe |
| Grösstkorndurchmesser | $D_{max}$ | $32$ | mm | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $67$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $104$ | mm | berechnet |
| Höhe der Einlage | $e_{Einlage}$ | $40$ | mm | Vorgabe |
| Plattendicke | $h$ | $200$ | mm | Vorgabe |
| Kriechzahl | $\varphi$ | $2$ |  | Vorgabe |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,x,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,x,g}$ | $10$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,x,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 1. Lage Grundbewehrung (ab Oberkante) | $d_{1,x,g}$ | $165$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,y,g}$ | $335$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,y,g}$ | $8$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,y,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 2. Lage Grundbewehrung (ab Oberkante) | $d_{2,y,g}$ | $156$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,y,g}$ | $335$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,y,g}$ | $8$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,y,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 3. Lage Grundbewehrung (ab Oberkante) | $d_{3,y,g}$ | $44$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,x,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,x,g}$ | $10$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,x,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 4. Lage Grundbewehrung (ab Oberkante) | $d_{4,x,g}$ | $35$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 1. Lage | $\alpha_{eff,D,1}$ | $4.31$ |  | berechnet |
| Bezogene Druckzonenhöhe – 1. Lage | $\left(x/d\right)_{1}$ | $0.081$ |  | berechnet |
| Erfüllungsgrad Duktilität – 4. Lage | $\alpha_{eff,D,4}$ | $4.31$ |  | berechnet |
| Bezogene Druckzonenhöhe – 4. Lage | $\left(x/d\right)_{4}$ | $0.081$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $36.3$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $0.453$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-36.3$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $36.3$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $112.5$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-112.5$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-4000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $455.3$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Rand | $M_{Rd,x}(N_{Ed})_{\text{Rand}}$ | $36.3$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Rand | $\alpha_{eff,x,\text{Rand}}$ | $1.813$ |  | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Feld | $\alpha_{eff,V,x,\text{Feld}}$ | $2.08$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Feld | $V_{Rd,x}$ | $83.2$ | kN/m | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Rand | $\alpha_{eff,V,x,\text{Rand}}$ | $3.69$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Rand | $V_{Rd,x}$ | $110.7$ | kN/m | berechnet |
| Erfüllungsgrad Rissnormalkraft – 1. Lage x | $\alpha_{eff,NR,1,x}$ | $0.99$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 4. Lage x | $\alpha_{eff,NR,4,x}$ | $0.99$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Dauerlast | $\alpha_{eff,\sigma,w,x,\text{Dauerlast}}$ | $0.54$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $0$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Rand (60 %) | $\alpha_{eff,\sigma,w,x,\text{Rand (60 \%)}}$ | $3.23$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 1. Lage x | $\alpha_{eff,SV,1,x}$ | $1.94$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 4. Lage x | $\alpha_{eff,SV,4,x}$ | $1.94$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 1. Lage x | $\alpha_{eff,ZB,1,x}$ | $2.09$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 4. Lage x | $\alpha_{eff,ZB,4,x}$ | $2.09$ |  | berechnet |
| Erfüllungsgrad M-N x-Richtung – Feld (keine Bewehrung) | $\alpha_{eff,M-N,x,\text{Feld}}$ | $0$ |  | berechnet |
| Erfüllungsgrad V x-Richtung – Feld (keine Bewehrung) | $\alpha_{eff,V,x,\text{Feld}}$ | $0$ |  | berechnet |
| Grösstkorndurchmesser | $D_{max}$ | $32$ | mm | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $80$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $146$ | mm | berechnet |
| Höhe der Einlage | $e_{Einlage}$ | $0$ | mm | Vorgabe |
| Plattendicke | $h$ | $250$ | mm | Vorgabe |
| Kriechzahl | $\varphi$ | $2$ |  | Vorgabe |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,y,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,y,g}$ | $10$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,y,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 1. Lage Grundbewehrung (ab Oberkante) | $d_{1,y,g}$ | $215$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,x,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,x,g}$ | $12$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,x,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 2. Lage Grundbewehrung (ab Oberkante) | $d_{2,x,g}$ | $204$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,x,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,x,g}$ | $12$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,x,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 3. Lage Grundbewehrung (ab Oberkante) | $d_{3,x,g}$ | $46$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,y,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,y,g}$ | $10$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,y,g}$ | $150$ | mm | Vorgabe |
| Statische Höhe 4. Lage Grundbewehrung (ab Oberkante) | $d_{4,y,g}$ | $35$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 2. Lage | $\alpha_{eff,D,2}$ | $3.7$ |  | berechnet |
| Bezogene Druckzonenhöhe – 2. Lage | $\left(x/d\right)_{2}$ | $0.095$ |  | berechnet |
| Erfüllungsgrad Duktilität – 3. Lage | $\alpha_{eff,D,3}$ | $3.7$ |  | berechnet |
| Bezogene Druckzonenhöhe – 3. Lage | $\left(x/d\right)_{3}$ | $0.095$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $64.2$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $1.605$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-64.2$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $64.2$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $178.6$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-178.6$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-5000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $655.6$ | kN | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Feld | $\alpha_{eff,V,x,\text{Feld}}$ | $3.36$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Feld | $V_{Rd,x}$ | $167.8$ | kN/m | berechnet |
| Erfüllungsgrad Rissnormalkraft – 2. Lage x | $\alpha_{eff,NR,2,x}$ | $1.17$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 3. Lage x | $\alpha_{eff,NR,3,x}$ | $1.17$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $2.86$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $2.21$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $2.21$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $2.38$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $2.38$ |  | berechnet |
