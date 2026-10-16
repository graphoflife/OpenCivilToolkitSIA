# Voll

348 Berechnungen ausgeführt, 584 Werte bestimmt.

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

**Bewehrungsquerschnitt über die Breite b** *(SIA 262:2025, 5.5.2)*

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

**Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $z\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | y | B500B | $12$ | $150$ | $36$ | $264$ | $754$ |
| 2. Lage Grundbewehrung | x | B500B | $18$ | $150$ | $51$ | $249$ | $1696$ |
| 2. Lage Zulage | x | B500B | $12$ | $150$ | $54$ | $246$ | $754$ |
| 3. Lage Grundbewehrung | x | B500B | $12$ | $150$ | $48$ | $48$ | $754$ |
| 4. Lage Grundbewehrung | y | B500B | $12$ | $150$ | $36$ | $36$ | $754$ |

### Resistenzlinie aus Handrechnung – x-Richtung

**Rechenwahl**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Handrechnung}
$$

**Schwerpunkt der zusammengefassten Lage – 2. Lage Grundbewehrung + 2. Lage Zulage**

$$
\begin{aligned}
  z_{2,x} &= \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

**Bewehrungsquerschnitt der zusammengefassten Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
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
  M_{Rd}(N_{Rd}^{+}) &= A_{s,2,x} \cdot f_{yd} \cdot \left(z_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(z_{3,x} - \tfrac{h}{2}\right) \\
  &= 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(48\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right) \\
  &= 71.1\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{2,x} = z_{2,x} = 248.1\,\mathrm{mm}
$$

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

**Nulllinie auf halber Höhe**

$$
x^{+} = \frac{h}{2} = \frac{300\,\mathrm{mm}}{2} = 150\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(248.1\,\mathrm{mm} - 150\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{150\,\mathrm{mm}} = 2.29\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.29\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} + 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1484.6\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot \sigma_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} \cdot \left(\tfrac{300\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 150\,\mathrm{mm}}{2}\right) + 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(248.1\,\mathrm{mm} - \tfrac{300\,\mathrm{mm}}{2}\right)\right] \\
  &= 324.4\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{3,x} = h - z_{3,x} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

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

**Nulllinie auf halber Höhe**

$$
x^{-} = \frac{h}{2} = \frac{300\,\mathrm{mm}}{2} = 150\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{3,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(252\,\mathrm{mm} - 150\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{150\,\mathrm{mm}} = 2.38\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{-};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.38\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,3,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -2222.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,3,x} \cdot \sigma_{sd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right)\right] \\
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

**Ansatz** *(SIA 262:2025, 4.3.3.4)*

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot\alpha \qquad V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin\alpha \cdot \cos\alpha
$$

**Teilung in y aus der Stabzahl**

$$
s_{V,y} = \frac{b}{n_{V,y}} = \frac{1000\,\mathrm{mm}}{5} = 200\,\mathrm{mm}
$$

#### Nachweis – Feld

**Einwirkung**

$$
V_{Ed} = 80\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 150\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d = z_{2,x,g} = 249\,\mathrm{mm}
$$

α = 30° … 45° ganzgradig → grösster Widerstand bei α = 30°.

**Widerstand der Bügel**

$$
\begin{aligned}
  V_{Rd,s} &= \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot \alpha \\
  &= \frac{50.3\,\mathrm{mm}^{2}}{200\,\mathrm{mm} \cdot 200\,\mathrm{mm}} \cdot 0.9 \cdot 249\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30{}^{\circ} \\
  &= 212.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Widerstand der Druckdiagonalen**

$$
\begin{aligned}
  V_{Rd,c} &= 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha \\
  &= 0.9 \cdot 249\,\mathrm{mm} \cdot 0.55 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30{}^{\circ} \cdot \cos 30{}^{\circ} \\
  &= 1067.4\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand**

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 150\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= \min\left[V_{Rd,s};\ V_{Rd,c}\right] \\
  &= \min\left[212.1\,\mathrm{kN}/\mathrm{m};\ 1067.4\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 212.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x,\text{Feld}} = \frac{V_{Rd,x}}{V_{Ed,x}} = \frac{212.1\,\mathrm{kN}/\mathrm{m}}{80\,\mathrm{kN}/\mathrm{m}} = 2.65 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Stütze

**Einwirkung**

$$
V_{Ed} = 60\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = -60\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

α = 30° … 45° ganzgradig → grösster Widerstand bei α = 30°.

**Widerstand der Bügel**

$$
\begin{aligned}
  V_{Rd,s} &= \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot \alpha \\
  &= \frac{50.3\,\mathrm{mm}^{2}}{200\,\mathrm{mm} \cdot 200\,\mathrm{mm}} \cdot 0.9 \cdot 252\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30{}^{\circ} \\
  &= 214.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Widerstand der Druckdiagonalen**

$$
\begin{aligned}
  V_{Rd,c} &= 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha \\
  &= 0.9 \cdot 252\,\mathrm{mm} \cdot 0.55 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30{}^{\circ} \cdot \cos 30{}^{\circ} \\
  &= 1080.3\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand**

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = -60\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= \min\left[V_{Rd,s};\ V_{Rd,c}\right] \\
  &= \min\left[214.6\,\mathrm{kN}/\mathrm{m};\ 1080.3\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 214.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x,\text{Stütze}} = \frac{V_{Rd,x}}{V_{Ed,x}} = \frac{214.6\,\mathrm{kN}/\mathrm{m}}{60\,\mathrm{kN}/\mathrm{m}} = 3.58 \quad \Rightarrow \quad \text{erfüllt}
$$

### Duktilität

**Kräftegleichgewicht bei M\_Ed = 0** *(SIA 262:2025, 4.1.4.2.5)*

$$
0.85 \cdot x \cdot b \cdot f_{cd} = A_s \cdot f_{sd} \qquad \Rightarrow \qquad x = \frac{A_s \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}}
$$

**Bedingung**

$$
\frac{x}{d} \le 0.35
$$

#### Duktilität – 2. Lage

**Bewehrung der Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

**Gemeinsamer Schwerpunkt der Lage**

$$
\begin{aligned}
  z_{2,x} &= \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{2,x} = z_{2,x} = 248.1\,\mathrm{mm}
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

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

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

Massgebend: 2. Lage (kleinster Erfüllungsgrad).

### Sprödes Versagen unter Zwängung – x-Richtung

**Rissaktive Plattendicke**

$$
h_{eff} = \min\left[500\,\mathrm{mm};\ h\right] = \min\left[500\,\mathrm{mm};\ 300\,\mathrm{mm}\right] = 300\,\mathrm{mm}
$$

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h_{eff}} = \frac{1}{1 + 0.5 \cdot 0.3} = 0.87 \quad \left(h_{eff}\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.87 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.52\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Risskraft der gezogenen Querschnittshälfte**

$$
N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff} = \frac{300\,\mathrm{mm}}{2} \cdot 1000\,\mathrm{mm} \cdot 2.52\,\mathrm{N}/\mathrm{mm}^{2} = 378.3\,\mathrm{kN}
$$

#### Rissnormalkraft – 2. Lage x

**Bewehrung der Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

**Dickster Stab der Lage**

$$
\varnothing_{2,x} = \max\left[\varnothing_{2,x,g};\ \varnothing_{2,x,z}\right] = \max\left[18\,\mathrm{mm};\ 12\,\mathrm{mm}\right] = 18\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,2,x} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{2,x}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{18\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 381\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Aufnehmbare Risskraft**

$$
\begin{aligned}
  N_{s,adm,2,x} &= A_{s,2,x} \cdot \sigma_{s,adm,2,x} \\
  &= 2450\,\mathrm{mm}^{2} \cdot 381\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 933.1\,\mathrm{kN} \quad \ge \quad N_{Riss} = 378.3\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,NR,2,x} = \frac{N_{s,adm,2,x}}{N_{Riss}} = \frac{933.1\,\mathrm{kN}}{378.3\,\mathrm{kN}} = 2.47
$$

#### Rissnormalkraft – 3. Lage x

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,3,x} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{3,x,g}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{12\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 466\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Aufnehmbare Risskraft**

$$
\begin{aligned}
  N_{s,adm,3,x} &= A_{s,3,x,g} \cdot \sigma_{s,adm,3,x} \\
  &= 754\,\mathrm{mm}^{2} \cdot 466\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 351.6\,\mathrm{kN} \quad < \quad N_{Riss} = 378.3\,\mathrm{kN} \quad \Rightarrow \quad \text{NICHT erfüllt}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,NR,3,x} = \frac{N_{s,adm,3,x}}{N_{Riss}} = \frac{351.6\,\mathrm{kN}}{378.3\,\mathrm{kN}} = 0.93
$$

Massgebend: 3. Lage (kleinster Erfüllungsgrad).

### Sprödes Versagen – x-Richtung

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

Massgebend: 3. Lage (kleinster Erfüllungsgrad).

### Zwängung auf Biegung – x-Richtung

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.2)*

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

**Wertigkeit im gerissenen Zustand**

$$
n = \frac{E_s}{E_{cm}} \cdot \left(1 + \varphi\right) = \frac{200000\,\mathrm{N}/\mathrm{mm}^{2}}{33620\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \left(1 + 2\right) = 17.85
$$

#### Zwängung auf Biegung – 2. Lage x

**Bewehrung der Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

**Gemeinsamer Schwerpunkt der Lage**

$$
\begin{aligned}
  z_{2,x} &= \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{2,x} = z_{2,x} = 248.1\,\mathrm{mm}
$$

**Dickster Stab der Lage**

$$
\varnothing_{2,x} = \max\left[\varnothing_{2,x,g};\ \varnothing_{2,x,z}\right] = \max\left[18\,\mathrm{mm};\ 12\,\mathrm{mm}\right] = 18\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,2,x} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{2,x}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{18\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 381\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Hilfsgrösse der Nulllinie**

$$
\rho = \frac{n \cdot A_{s,2,x}}{b} = \frac{17.85 \cdot 2450\,\mathrm{mm}^{2}}{1000\,\mathrm{mm}} = 43.73\,\mathrm{mm}
$$

**Nulllinie des gerissenen Querschnitts**

$$
\begin{aligned}
  x &= \sqrt{\rho^{2} + 2 \cdot d_{2,x} \cdot \rho} - \rho \\
  &= \sqrt{\left(43.73\,\mathrm{mm}\right)^{2} + 2 \cdot 248.1\,\mathrm{mm} \cdot 43.73\,\mathrm{mm}} - 43.73\,\mathrm{mm} \\
  &= 109.9\,\mathrm{mm}
\end{aligned}
$$

**Innerer Hebelarm**

$$
z = d_{2,x} - \frac{x}{3} = 248.1\,\mathrm{mm} - \frac{109.9\,\mathrm{mm}}{3} = 211.4\,\mathrm{mm}
$$

**Aufnehmbares Moment der Bewehrung**

$$
\begin{aligned}
  M_{s,adm,2,x} &= \sigma_{s,adm,2,x} \cdot A_{s,2,x} \cdot z \\
  &= 381\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2450\,\mathrm{mm}^{2} \cdot 211.4\,\mathrm{mm} \\
  &= 197.3\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 41.4\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,2,x} = \frac{M_{s,adm,2,x}}{M_{Riss}} = \frac{197.3\,\mathrm{kNm}}{41.4\,\mathrm{kNm}} = 4.76
$$

#### Zwängung auf Biegung – 3. Lage x

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{3,x,g} = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,3,x} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{3,x,g}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{12\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 466\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Hilfsgrösse der Nulllinie**

$$
\rho = \frac{n \cdot A_{s,3,x,g}}{b} = \frac{17.85 \cdot 754\,\mathrm{mm}^{2}}{1000\,\mathrm{mm}} = 13.46\,\mathrm{mm}
$$

**Nulllinie des gerissenen Querschnitts**

$$
\begin{aligned}
  x &= \sqrt{\rho^{2} + 2 \cdot d_{3,x,g} \cdot \rho} - \rho \\
  &= \sqrt{\left(13.46\,\mathrm{mm}\right)^{2} + 2 \cdot 252\,\mathrm{mm} \cdot 13.46\,\mathrm{mm}} - 13.46\,\mathrm{mm} \\
  &= 70\,\mathrm{mm}
\end{aligned}
$$

**Innerer Hebelarm**

$$
z = d_{3,x,g} - \frac{x}{3} = 252\,\mathrm{mm} - \frac{70\,\mathrm{mm}}{3} = 228.7\,\mathrm{mm}
$$

**Aufnehmbares Moment der Bewehrung**

$$
\begin{aligned}
  M_{s,adm,3,x} &= \sigma_{s,adm,3,x} \cdot A_{s,3,x,g} \cdot z \\
  &= 466\,\mathrm{N}/\mathrm{mm}^{2} \cdot 754\,\mathrm{mm}^{2} \cdot 228.7\,\mathrm{mm} \\
  &= 80.4\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 41.4\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,3,x} = \frac{M_{s,adm,3,x}}{M_{Riss}} = \frac{80.4\,\mathrm{kNm}}{41.4\,\mathrm{kNm}} = 1.94
$$

Massgebend: 3. Lage (kleinster Erfüllungsgrad).

### Stahlspannung unter quasi-ständiger Einwirkung – x-Richtung

**Rechenwahl**

$$
\varphi = 2 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{elastisch}
$$

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

**Werkstoffgesetze im Gebrauchszustand**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2} \qquad \sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

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

**Rechenwahl**

$$
\varphi = 2 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{elastisch}
$$

**Wirksamer Elastizitätsmodul**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad n = 17.85
$$

**Zulässige Stahlspannung** *(SIA 262:2025, Tabelle 17)*

$$
\sigma_{s,adm} = f_{yd} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 435\,\mathrm{N}/\mathrm{mm}^{2} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 355\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

**Werkstoffgesetze im Gebrauchszustand**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2} \qquad \sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

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

### Vergrösserungsfaktor der Durchbiegung

**Vergrösserungsfaktor der Durchbiegung – allgemein** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

**Kriechzahl**

$$
\varphi = 2
$$

**x-Bewehrung unten, zusammen**

$$
A_{s,u} = A_{s,2,x,g} + A_{s,2,x,z} = 1696\,\mathrm{mm}^{2} + 754\,\mathrm{mm}^{2} = 2450\,\mathrm{mm}^{2}
$$

**Schwerpunkt der x-Bewehrung unten**

$$
\begin{aligned}
  z_{u} &= \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,u}} \\
  &= \frac{1696\,\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 246\,\mathrm{mm}}{2450\,\mathrm{mm}^{2}} \\
  &= 248.1\,\mathrm{mm}
\end{aligned}
$$

**Statische Höhe der x-Bewehrung unten**

$$
d_{u} = z_{u} = 248.1\,\mathrm{mm}
$$

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,u}}{b \cdot d_{u}} = \frac{2450\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 248.1\,\mathrm{mm}} = 0.00988
$$

**Statische Höhe der x-Bewehrung oben**

$$
d_{o} = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

**Bewehrungsgehalt oben**

$$
\rho_{o} = \frac{A_{s,3,x,g}}{b \cdot d_{o}} = \frac{754\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 252\,\mathrm{mm}} = 0.00299
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00299}{10 \cdot 0.00988^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{300\,\mathrm{mm}}{248.1\,\mathrm{mm}}\right)^{3} \\
  &= 4
\end{aligned}
$$

**Vergrösserungsfaktor, Zug oben** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w' &= \frac{1 - 20 \cdot \rho_{u}}{10 \cdot \rho_{o}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{o}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00988}{10 \cdot 0.00299^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{300\,\mathrm{mm}}{252\,\mathrm{mm}}\right)^{3} \\
  &= 7.52
\end{aligned}
$$

### Verformung

> **Annahme:** w ist mit der Steifigkeit E\_cm ermittelt. Grenzwert w\_max = L/350 nach Vorgabe, nicht nachgeschlagen.

#### Verformung – Feld

**Wirksame Durchbiegung, Zug unten**

$$
w_{eff} = \omega_w \cdot w = 4 \cdot 3\,\mathrm{mm} = 12\,\mathrm{mm}
$$

**Grenzwert der Durchbiegung, nach Vorgabe**

$$
w_{max} = \frac{L}{350} = \frac{6\,\mathrm{m}}{350} = 17.1\,\mathrm{mm}
$$

**Durchbiegung gegen Grenzwert**

$$
w_{eff} = 12\,\mathrm{mm} \quad \le \quad w_{max} = 17.1\,\mathrm{mm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,w,\text{Feld}} = \frac{w_{max}}{w_{eff}} = \frac{17.1\,\mathrm{mm}}{12\,\mathrm{mm}} = 1.43 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Verformung – Kragarm

**Wirksame Durchbiegung, Zug oben**

$$
w_{eff} = \omega_w' \cdot w = 7.52 \cdot 0.8\,\mathrm{mm} = 6\,\mathrm{mm}
$$

**Grenzwert der Durchbiegung, nach Vorgabe**

$$
w_{max} = \frac{L}{350} = \frac{2.5\,\mathrm{m}}{350} = 7.1\,\mathrm{mm}
$$

**Durchbiegung gegen Grenzwert**

$$
w_{eff} = 6\,\mathrm{mm} \quad \le \quad w_{max} = 7.1\,\mathrm{mm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,w,\text{Kragarm}} = \frac{w_{max}}{w_{eff}} = \frac{7.1\,\mathrm{mm}}{6\,\mathrm{mm}} = 1.19 \quad \Rightarrow \quad \text{erfüllt}
$$

### Knicken

**Ungewollte Ausmitte – allgemein** *(SIA 262:2025, 4.3.7)*

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \qquad e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

**Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}\right)
$$

#### Verformung

**Rechenwahl – Verformung (e\_2d)**

$$
\varphi = 2 \qquad \text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Präzise ohne Vereinfachung}
$$

**Steifigkeit des Betons**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad f_{cd} = 20\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{11207\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 1.4
$$

**Werkstoffgesetze der Verformung: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze der Verformung: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yd}\right] \quad f_{yd} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

#### Widerstand: Resistenzlinie aus Dehnungsebenen – x-Richtung

**Rechenwahl – Widerstand (N\_Rd)**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad 0.85 \cdot x\text{-Vereinfachung}
$$

**Werkstoffgesetze: Beton, Spannungsblock 0.85·x**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{cd} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werkstoffgesetze: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Schnittgrössen aus der Spannungsverteilung**

$$
N = \int_A \sigma\,\mathrm{d}A \qquad M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A
$$

**Berücksichtigte Bewehrungslagen**

| Lage | $a_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $1696$ | $249.0$ | $435$ |
| 2. Lage Zulage | $754$ | $246.0$ | $435$ |
| 3. Lage Grundbewehrung | $754$ | $48.0$ | $435$ |

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
M_{Rd,x}(N_{Ed}) = 307\,\mathrm{kNm} \quad \ge \quad M_{Ed,II} = 27.3\,\mathrm{kNm}
$$

**Grenzkraft des Stabes**

$$
N_{Rd,K} = 4496.7\,\mathrm{kN} \quad \ge \quad \left|N_{Ed}\right| = 800\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,K,\text{Wand}} = \frac{N_{Rd,K}}{\left|N_{Ed}\right|} = \frac{4496.7\,\mathrm{kN}}{800\,\mathrm{kN}} = 5.62 \quad \Rightarrow \quad \text{erfüllt}
$$

### Kennzahlen

Die Eckpunkte stammen aus der Handrechnung der Tragsicherheit – sie rechnet ebenso, von Hand mit Bemessungswerten.

#### Biegung und Normalkraft

**Momentenwiderstand bei N\_Ed = 0, Zug unten**

$$
M_{Rd}^{+}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{+} = 235.9\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten**

$$
\left(x/d\right)^{+} = \frac{x^{+}}{d_{2,x}} = \frac{62.7\,\mathrm{mm}}{248.1\,\mathrm{mm}} = 0.253
$$

**Momentenwiderstand bei N\_Ed = 0, Zug oben**

$$
M_{Rd}^{-}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{-} = -79.9\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben**

$$
\left(x/d\right)^{-} = \frac{x^{-}}{d_{3,x}} = \frac{19.3\,\mathrm{mm}}{252\,\mathrm{mm}} = 0.077
$$

**Zugwiderstand bei M\_Ed = 0**

$$
\begin{aligned}
  N_{Rd}^{+}(M_{Ed} = 0) &= N_1 + \frac{M_{Ed} - M_1}{M_2 - M_1} \cdot \left(N_2 - N_1\right) \\
  &= 1393.2\,\mathrm{kN} + \frac{0\,\mathrm{kNm} - 71.1\,\mathrm{kNm}}{-79.9\,\mathrm{kNm} - 71.1\,\mathrm{kNm}} \cdot \left(0\,\mathrm{kN} - 1393.2\,\mathrm{kN}\right) \\
  &= 737.5\,\mathrm{kN}
\end{aligned}
$$

**Stützpunkte der Interpolation**

| Punkt | $M\ [\mathrm{kNm}]$ | $N\ [\mathrm{kN}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{+}$ | $71.1$ | $1393.2$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $-79.9$ | $0.0$ |

**Druckwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-} = -6000\,\mathrm{kN}
$$

#### Querkraftwiderstand mit Bügeln bei N\_Ed = 0

**Teilung in y aus der Stabzahl**

$$
s_{V,y} = \frac{b}{n_{V,y}} = \frac{1000\,\mathrm{mm}}{5} = 200\,\mathrm{mm}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d^{+} = z_{2,x,g} = 249\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{+} = d^{+} = 249\,\mathrm{mm}
$$

Zug unten: α = 30° … 45° ganzgradig → grösster Widerstand bei α = 30°.

**Widerstand der Bügel, Zug unten**

$$
\begin{aligned}
  V_{Rd,s}^{+} &= \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d^{+} \cdot f_{yd} \cdot \cot \alpha_{opt}^{+} \\
  &= \frac{50.3\,\mathrm{mm}^{2}}{200\,\mathrm{mm} \cdot 200\,\mathrm{mm}} \cdot 0.9 \cdot 249\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30{}^{\circ} \\
  &= 212.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Widerstand der Druckdiagonalen, Zug unten**

$$
\begin{aligned}
  V_{Rd,c}^{+} &= 0.9 \cdot d^{+} \cdot k_c \cdot f_{cd} \cdot \sin \alpha_{opt}^{+} \cdot \cos \alpha_{opt}^{+} \\
  &= 0.9 \cdot 249\,\mathrm{mm} \cdot 0.55 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30{}^{\circ} \cdot \cos 30{}^{\circ} \\
  &= 1067.4\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand, Zug unten**

$$
\begin{aligned}
  V_{Rd}^{+}(\alpha_{opt}) &= \min\left[V_{Rd,s}^{+};\ V_{Rd,c}^{+}\right] \\
  &= \min\left[212.1\,\mathrm{kN}/\mathrm{m};\ 1067.4\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 212.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d^{-} = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{-} = d^{-} = 252\,\mathrm{mm}
$$

Zug oben: α = 30° … 45° ganzgradig → grösster Widerstand bei α = 30°.

**Widerstand der Bügel, Zug oben**

$$
\begin{aligned}
  V_{Rd,s}^{-} &= \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d^{-} \cdot f_{yd} \cdot \cot \alpha_{opt}^{-} \\
  &= \frac{50.3\,\mathrm{mm}^{2}}{200\,\mathrm{mm} \cdot 200\,\mathrm{mm}} \cdot 0.9 \cdot 252\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30{}^{\circ} \\
  &= 214.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Widerstand der Druckdiagonalen, Zug oben**

$$
\begin{aligned}
  V_{Rd,c}^{-} &= 0.9 \cdot d^{-} \cdot k_c \cdot f_{cd} \cdot \sin \alpha_{opt}^{-} \cdot \cos \alpha_{opt}^{-} \\
  &= 0.9 \cdot 252\,\mathrm{mm} \cdot 0.55 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30{}^{\circ} \cdot \cos 30{}^{\circ} \\
  &= 1080.3\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand, Zug oben**

$$
\begin{aligned}
  V_{Rd}^{-}(\alpha_{opt}) &= \min\left[V_{Rd,s}^{-};\ V_{Rd,c}^{-}\right] \\
  &= \min\left[214.6\,\mathrm{kN}/\mathrm{m};\ 1080.3\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 214.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand mit Bügeln, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.4)*

$$
\begin{aligned}
  V_{Rd}(\alpha_{opt}) &= \min\left[V_{Rd}^{+}(\alpha_{opt});\ V_{Rd}^{-}(\alpha_{opt})\right] \\
  &= \min\left[212.1\,\mathrm{kN}/\mathrm{m};\ 214.6\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 212.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
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

**Bemessungswert der Schubspannungsgrenze** *(SIA 262:2025, 2.4.2.4)*

$$
\tau_{cd} = \frac{0.3 \cdot \sqrt{f_{ck}}}{\gamma_c} = \frac{0.3 \cdot \sqrt{30}}{1.5} = 1.1\,\mathrm{N}/\mathrm{mm}^{2} \quad \left(f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

**Mittelwert der Zugfestigkeit** *(SIA 262:2025, 3.1.2.2.7)*

$$
f_{ctm} = 2.9\,\mathrm{N}/\mathrm{mm}^{2}
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
b = 500\,\mathrm{mm}
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

**Bewehrungsquerschnitt über die Breite b** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{859\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{500\,\mathrm{mm} \cdot 200\,\mathrm{mm}} = 67\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 152\,\mathrm{mm} - 48\,\mathrm{mm} \\
  &= 104\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | $b\ [\mathrm{mm}]$ | Randabstand [mm] | $z\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | x | B500B | $10$ | $150$ | $500$ | $35$ | $165$ | $262$ |
| 2. Lage Grundbewehrung | y | B500B | $8$ | $150$ | $1000$ | $44$ | $156$ | $335$ |
| 3. Lage Grundbewehrung | y | B500B | $8$ | $150$ | $1000$ | $44$ | $44$ | $335$ |
| 4. Lage Grundbewehrung | x | B500B | $10$ | $150$ | $500$ | $35$ | $35$ | $262$ |

### Resistenzlinie aus Handrechnung – x-Richtung

**Rechenwahl**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Handrechnung}
$$

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | $262$ | $165.0$ | $435$ |
| 4. Lage Grundbewehrung | $262$ | $35.0$ | $435$ |

#### Grösste Druckkraft

**Gleichmässiger Druck, ohne Bewehrung**

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd} = -500\,\mathrm{mm} \cdot 200\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} = -2000\,\mathrm{kN}
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
  &= 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 227.7\,\mathrm{kN}
\end{aligned}
$$

**Kräfte mal Hebelarm um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}(N_{Rd}^{+}) &= A_{s,1,x} \cdot f_{yd} \cdot \left(z_{1,x} - \tfrac{h}{2}\right) + A_{s,4,x} \cdot f_{yd} \cdot \left(z_{4,x} - \tfrac{h}{2}\right) \\
  &= 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right) + 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(35\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right) \\
  &= 0\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{1,x} = z_{1,x} = 165\,\mathrm{mm}
$$

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{+} = \frac{A_{s,1,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 500\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 13.4\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{+} &= A_{s,1,x} \cdot f_{yd} \cdot \left(d_{1,x} - \frac{0.85 \cdot x^{+}}{2}\right) \\
  &= 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \frac{0.85 \cdot 13.4\,\mathrm{mm}}{2}\right) \\
  &= 18.1\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe**

$$
x^{+} = \frac{h}{2} = \frac{200\,\mathrm{mm}}{2} = 100\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{1,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(165\,\mathrm{mm} - 100\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{100\,\mathrm{mm}} = 2.27\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.27\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,1,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 500\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} + 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -736.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,1,x} \cdot \sigma_{sd} \cdot \left(d_{1,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 500\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} \cdot \left(\tfrac{200\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 100\,\mathrm{mm}}{2}\right) + 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right)\right] \\
  &= 56.3\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{4,x} = h - z_{4,x} = 200\,\mathrm{mm} - 35\,\mathrm{mm} = 165\,\mathrm{mm}
$$

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{-} = \frac{A_{s,4,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 500\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 13.4\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{-} &= -A_{s,4,x} \cdot f_{yd} \cdot \left(d_{4,x} - \frac{0.85 \cdot x^{-}}{2}\right) \\
  &= -262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \frac{0.85 \cdot 13.4\,\mathrm{mm}}{2}\right) \\
  &= -18.1\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe**

$$
x^{-} = \frac{h}{2} = \frac{200\,\mathrm{mm}}{2} = 100\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{4,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(165\,\mathrm{mm} - 100\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{100\,\mathrm{mm}} = 2.27\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{-};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.27\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,4,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 500\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} + 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -736.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,4,x} \cdot \sigma_{sd} \cdot \left(d_{4,x} - \tfrac{h}{2}\right)\right] \\
  &= -\left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 500\,\mathrm{mm} \cdot 0.85 \cdot 100\,\mathrm{mm} \cdot \left(\tfrac{200\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 100\,\mathrm{mm}}{2}\right) + 262\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(165\,\mathrm{mm} - \tfrac{200\,\mathrm{mm}}{2}\right)\right] \\
  &= -56.3\,\mathrm{kNm}
\end{aligned}
$$

**Eckpunkte der Resistenzlinie aus Handrechnung**

| Eckpunkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{-}$ | $-2000.0$ | $0.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-736.2$ | $56.3$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $18.1$ |
| $N_{Rd}^{+}$ | $227.7$ | $0.0$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $0.0$ | $-18.1$ |
| $M_{Rd}(x=\tfrac{h}{2})^{-}$ | $-736.2$ | $-56.3$ |

#### Nachweis – Feld

**Einwirkung**

$$
M_{Ed} = 40\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 18.1\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{18.1\,\mathrm{kNm}}{40\,\mathrm{kNm}} = 0.45 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

#### Nachweis – Rand

**Einwirkung**

$$
M_{Ed} = 10\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 18.1\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Rand}} = \frac{M_{Rd}}{M_{Ed}} = \frac{18.1\,\mathrm{kNm}}{10\,\mathrm{kNm}} = 1.81 \quad \Rightarrow \quad \text{erfüllt}
$$

### Querkraft – x-Richtung

**Ansatz** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

**Dekompressionsmoment und Dehnung**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

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
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

#### Querkraftnachweis – Feld

**Einwirkung**

$$
V_{Ed} = 40\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 40\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d = z_{1,x,g} = 165\,\mathrm{mm}
$$

**Wirksame Höhe, um die Einlage vermindert**

$$
d_v = d - e_{Einlage} = 165\,\mathrm{mm} - 40\,\mathrm{mm} = 125\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|\min(0\,\mathrm{kN};\ 0)\right| \cdot 200\,\mathrm{mm}}{6} = 0\,\mathrm{kNm}
$$

**Momentenwiderstand bei N\_Ed = 0.0 kN**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 18.1\,\mathrm{kNm}
$$

\|m\_Ed\| = 40 kNm \> m\_Rd(N\_Ed) = 18.1 kNm → Bewehrung fliesst, ε\_v fest.

**Dehnung auf halber Höhe**

$$
\varepsilon_v = 1.5 \cdot \frac{f_{yd}}{E_s} = 1.5 \cdot \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 3.261\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 3.261\,\text{‰} \cdot 165 \cdot 1.2} = 0.6077 \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 40\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= k_d \cdot \tau_{cd} \cdot d_v \\
  &= 0.6077 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125\,\mathrm{mm} \\
  &= 83.2\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x,\text{Feld}} = \frac{V_{Rd,x}}{V_{Ed,x}} = \frac{83.2\,\mathrm{kN}/\mathrm{m}}{40\,\mathrm{kN}/\mathrm{m}} = 2.08 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Querkraftnachweis – Rand

**Einwirkung**

$$
V_{Ed} = 30\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 10\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d = z_{1,x,g} = 165\,\mathrm{mm}
$$

**Wirksame Höhe, um die Einlage vermindert**

$$
d_v = d - e_{Einlage} = 165\,\mathrm{mm} - 40\,\mathrm{mm} = 125\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|\min(0\,\mathrm{kN};\ 0)\right| \cdot 200\,\mathrm{mm}}{6} = 0\,\mathrm{kNm}
$$

**Momentenwiderstand bei N\_Ed = 0.0 kN**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 18.1\,\mathrm{kNm}
$$

**Dehnung auf halber Höhe**

$$
\begin{aligned}
  \varepsilon_v &= \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)} \\
  &= \frac{435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|10\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)}{200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|18.1\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)} \\
  &= 1.199\,\text{‰}
\end{aligned}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 1.199\,\text{‰} \cdot 165 \cdot 1.2} = 0.8082 \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 10\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= k_d \cdot \tau_{cd} \cdot d_v \\
  &= 0.8082 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125\,\mathrm{mm} \\
  &= 110.7\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x,\text{Rand}} = \frac{V_{Rd,x}}{V_{Ed,x}} = \frac{110.7\,\mathrm{kN}/\mathrm{m}}{30\,\mathrm{kN}/\mathrm{m}} = 3.69 \quad \Rightarrow \quad \text{erfüllt}
$$

### Stahlspannung unter quasi-ständiger Einwirkung – x-Richtung

**Rechenwahl**

$$
\varphi = 2 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{elastisch}
$$

**Wirksamer Elastizitätsmodul**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad n = 17.85
$$

**Zulässige Stahlspannung (normale Anforderung)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm} = f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

**Werkstoffgesetze im Gebrauchszustand**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2} \qquad \sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

#### Quasi-ständiger Lastfall – Dauerlast

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = 20\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 2.3198\,\text{‰} \qquad \chi = 0.03612\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 20\,\mathrm{kNm} \;\checkmark
$$

Stahl fliesst (σ\_s = 500 N/mm²) → Vergleich über die Dehnung.

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

### Vergrösserungsfaktor der Durchbiegung

**Vergrösserungsfaktor der Durchbiegung – allgemein** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

**Kriechzahl**

$$
\varphi = 1.5
$$

**Statische Höhe der x-Bewehrung unten**

$$
d_{u} = z_{1,x,g} = 165\,\mathrm{mm}
$$

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,1,x,g}}{b \cdot d_{u}} = \frac{262\,\mathrm{mm}^{2}}{500\,\mathrm{mm} \cdot 165\,\mathrm{mm}} = 0.00317
$$

**Statische Höhe der x-Bewehrung oben**

$$
d_{o} = h - z_{4,x,g} = 200\,\mathrm{mm} - 35\,\mathrm{mm} = 165\,\mathrm{mm}
$$

**Bewehrungsgehalt oben**

$$
\rho_{o} = \frac{A_{s,4,x,g}}{b \cdot d_{o}} = \frac{262\,\mathrm{mm}^{2}}{500\,\mathrm{mm} \cdot 165\,\mathrm{mm}} = 0.00317
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00317}{10 \cdot 0.00317^{0.7}} \cdot \left(0.75 + 0.1 \cdot 1.5\right) \cdot \left(\frac{200\,\mathrm{mm}}{165\,\mathrm{mm}}\right)^{3} \\
  &= 8.42
\end{aligned}
$$

**Vergrösserungsfaktor, Zug oben** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w' &= \frac{1 - 20 \cdot \rho_{u}}{10 \cdot \rho_{o}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{o}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00317}{10 \cdot 0.00317^{0.7}} \cdot \left(0.75 + 0.1 \cdot 1.5\right) \cdot \left(\frac{200\,\mathrm{mm}}{165\,\mathrm{mm}}\right)^{3} \\
  &= 8.42
\end{aligned}
$$

### Verformung

> **Annahme:** w ist mit der Steifigkeit E\_cm ermittelt. Grenzwert w\_max = L/350 nach Vorgabe, nicht nachgeschlagen.

#### Verformung – Feld

**Wirksame Durchbiegung, Zug unten**

$$
w_{eff} = \omega_w \cdot w = 8.42 \cdot 2\,\mathrm{mm} = 16.8\,\mathrm{mm}
$$

**Grenzwert der Durchbiegung, nach Vorgabe**

$$
w_{max} = \frac{L}{350} = \frac{5\,\mathrm{m}}{350} = 14.3\,\mathrm{mm}
$$

**Durchbiegung gegen Grenzwert**

$$
w_{eff} = 16.8\,\mathrm{mm} \quad > \quad w_{max} = 14.3\,\mathrm{mm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,w,\text{Feld}} = \frac{w_{max}}{w_{eff}} = \frac{14.3\,\mathrm{mm}}{16.8\,\mathrm{mm}} = 0.85 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

### Kennzahlen

Die Eckpunkte stammen aus der Handrechnung der Tragsicherheit – sie rechnet ebenso, von Hand mit Bemessungswerten.

#### Biegung und Normalkraft

**Momentenwiderstand bei N\_Ed = 0, Zug unten**

$$
M_{Rd}^{+}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{+} = 18.1\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten**

$$
\left(x/d\right)^{+} = \frac{x^{+}}{d_{1,x}} = \frac{13.4\,\mathrm{mm}}{165\,\mathrm{mm}} = 0.081
$$

**Momentenwiderstand bei N\_Ed = 0, Zug oben**

$$
M_{Rd}^{-}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{-} = -18.1\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben**

$$
\left(x/d\right)^{-} = \frac{x^{-}}{d_{4,x}} = \frac{13.4\,\mathrm{mm}}{165\,\mathrm{mm}} = 0.081
$$

**Zugwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{+}(M_{Ed} = 0) = N_{Rd}^{+} = 227.7\,\mathrm{kN}
$$

**Druckwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-} = -2000\,\mathrm{kN}
$$

#### Querkraftwiderstand ohne Bügel bei N\_Ed = 0

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d^{+} = z_{1,x,g} = 165\,\mathrm{mm}
$$

**Wirksame Höhe, um die Einlage vermindert**

$$
d_v^{+} = d^{+} - e_{Einlage} = 165\,\mathrm{mm} - 40\,\mathrm{mm} = 125\,\mathrm{mm}
$$

**Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125\,\mathrm{mm} = 136.9\,\mathrm{kN}/\mathrm{m}
$$

**Zug unten, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{+} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 165 \cdot 1.2} = 0.6991 \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug unten, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) &= k_d^{+} \cdot \tau_{cd} \cdot d_v^{+} \\
  &= 0.6991 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125\,\mathrm{mm} \\
  &= 95.7\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d^{-} = h - z_{4,x,g} = 200\,\mathrm{mm} - 35\,\mathrm{mm} = 165\,\mathrm{mm}
$$

**Wirksame Höhe, um die Einlage vermindert**

$$
d_v^{-} = d^{-} - e_{Einlage} = 165\,\mathrm{mm} - 40\,\mathrm{mm} = 125\,\mathrm{mm}
$$

**Zug oben, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{-}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{-} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125\,\mathrm{mm} = 136.9\,\mathrm{kN}/\mathrm{m}
$$

**Zug oben, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{-} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{-} = \frac{1}{1 + \varepsilon_v^{-} \cdot d^{-} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 165 \cdot 1.2} = 0.6991 \quad \left(d^{-}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug oben, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-}) &= k_d^{-} \cdot \tau_{cd} \cdot d_v^{-} \\
  &= 0.6991 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125\,\mathrm{mm} \\
  &= 95.7\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = 0, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,max} &= \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right] \\
  &= \min\left[136.9\,\mathrm{kN}/\mathrm{m};\ 136.9\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 136.9\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,min} &= \min\left[V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+});\ V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-})\right] \\
  &= \min\left[95.7\,\mathrm{kN}/\mathrm{m};\ 95.7\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 95.7\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

### Plattenanalyse: Parabel

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

**Bewehrungsquerschnitt über die Breite b** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{2325\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 250\,\mathrm{mm}} = 73\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 198\,\mathrm{mm} - 50\,\mathrm{mm} \\
  &= 148\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $z\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | y | B500B | $10$ | $150$ | $35$ | $215$ | $524$ |
| 2. Lage Grundbewehrung | x | B500B | $12$ | $150$ | $46$ | $204$ | $754$ |
| 3. Lage Grundbewehrung | x | B500B | $10$ | $150$ | $45$ | $45$ | $524$ |
| 4. Lage Grundbewehrung | y | B500B | $10$ | $150$ | $35$ | $35$ | $524$ |

### Resistenzlinie aus Dehnungsebenen – x-Richtung

**Rechenwahl**

$$
\varphi = 1 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{Präzise ohne Vereinfachung}
$$

**Wirksamer Modul der Parabel**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 1} = 16810\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{ck}}\right) = \max\left(1;\ \frac{16810\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 1.4
$$

**Werkstoffgesetze: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yk}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yk}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Schnittgrössen aus der Spannungsverteilung**

$$
N = \int_A \sigma\,\mathrm{d}A \qquad M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A
$$

**Berücksichtigte Bewehrungslagen**

| Lage | $a_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yk}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $754$ | $204.0$ | $500$ |
| 3. Lage Grundbewehrung | $524$ | $45.0$ | $500$ |

#### Nachweis – Feld

**Einwirkung**

$$
M_{Ed} = 60\,\mathrm{kNm} \qquad N_{Ed} = -200\,\mathrm{kN}
$$

**Bruchzustand bei N\_Ed = -200.0 kN – die Dehnungsebene**

$$
\varepsilon_{oben} = -3.5\,\text{‰} \qquad \varepsilon_{unten} = 24.155\,\text{‰}
$$

**Kräfte in diesem Bruchzustand – Zug positiv, z ab Oberkante**

| Teil | $\varepsilon\ [‰]$ | $\sigma\ [\mathrm{N/mm^2}]$ | $A\ [\mathrm{mm}^2]$ | $F\ [\mathrm{kN}]$ | $z\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Beton, Resultierende | $–$ | $–$ | $–$ | $-731.8$ | $12.6$ |
| 2. Lage Grundbewehrung | $19.066$ | $500.0$ | $754$ | $377.0$ | $204.0$ |
| 3. Lage Grundbewehrung | $1.478$ | $295.6$ | $524$ | $154.8$ | $45.0$ |

**Probe: die Ebene trägt genau die Einwirkung**

$$
\sum F_i = -200\,\mathrm{kN} = N_{Ed}
$$

**Momentenwiderstand aus den Teilkräften**

$$
M_{Rk} = \sum F_i \cdot \left(z_i - \tfrac{h}{2}\right) = 99.6\,\mathrm{kNm}
$$

Massgebend: Beton am oberen Rand auf der Grenzdehnung.

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rk}}{M_{Ed}} = \frac{99.6\,\mathrm{kNm}}{60\,\mathrm{kNm}} = 1.66 \quad \Rightarrow \quad \text{erfüllt}
$$

### Querkraft – x-Richtung

**Ansatz** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

**Dekompressionsmoment und Dehnung**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

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
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

#### Querkraftnachweis – Feld

**Einwirkung**

$$
V_{Ed} = 50\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 60\,\mathrm{kNm} \qquad N_{Ed} = -200\,\mathrm{kN}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d = z_{2,x,g} = 204\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v = d = 204\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|\min(-200\,\mathrm{kN};\ 0)\right| \cdot 250\,\mathrm{mm}}{6} = 8.3\,\mathrm{kNm}
$$

**Momentenwiderstand bei N\_Ed = -200.0 kN**

$$
\varepsilon_{oben} = -3.5\,\text{‰} \qquad \varepsilon_{unten} = 24.155\,\text{‰}
$$

**Kräfte in diesem Bruchzustand – Zug positiv, z ab Oberkante**

| Teil | $\varepsilon\ [‰]$ | $\sigma\ [\mathrm{N/mm^2}]$ | $A\ [\mathrm{mm}^2]$ | $F\ [\mathrm{kN}]$ | $z\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Beton, Resultierende | $–$ | $–$ | $–$ | $-731.8$ | $12.6$ |
| 2. Lage Grundbewehrung | $19.066$ | $500.0$ | $754$ | $377.0$ | $204.0$ |
| 3. Lage Grundbewehrung | $1.478$ | $295.6$ | $524$ | $154.8$ | $45.0$ |

**Probe: die Ebene trägt genau die Einwirkung**

$$
\sum F_i = -200\,\mathrm{kN} = N_{Ed}
$$

**Momentenwiderstand aus den Teilkräften**

$$
M_{Rk} = \sum F_i \cdot \left(z_i - \tfrac{h}{2}\right) = 99.6\,\mathrm{kNm}
$$

Massgebend: Beton am oberen Rand auf der Grenzdehnung.

**Dehnung auf halber Höhe**

$$
\begin{aligned}
  \varepsilon_v &= \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rk}(N_{Ed})\right| - m_{Dd}\right)} \\
  &= \frac{435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|60\,\mathrm{kNm}\right| - 8.3\,\mathrm{kNm}\right)}{200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|99.6\,\mathrm{kNm}\right| - 8.3\,\mathrm{kNm}\right)} \\
  &= 1.23\,\text{‰}
\end{aligned}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 1.23\,\text{‰} \cdot 204 \cdot 1.2} = 0.7685 \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 60\,\mathrm{kNm},\ N_{Ed} = -200\,\mathrm{kN}) &= k_d \cdot \tau_{cd} \cdot d_v \\
  &= 0.7685 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 204\,\mathrm{mm} \\
  &= 171.7\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x,\text{Feld}} = \frac{V_{Rd,x}}{V_{Ed,x}} = \frac{171.7\,\mathrm{kN}/\mathrm{m}}{50\,\mathrm{kN}/\mathrm{m}} = 3.43 \quad \Rightarrow \quad \text{erfüllt}
$$

### Sprödes Versagen – x-Richtung

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.1.3)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.25/3} = 0.96 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.96 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.78\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6} = 2.78\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\left(250\,\mathrm{mm}\right)^{2} \cdot 1000\,\mathrm{mm}}{6} = 29\,\mathrm{kNm}
$$

#### Sprödes Versagen – 2. Lage x

**Biegewiderstand gegen Rissmoment**

$$
M_{Rk,x}(N_{Ed} = 0)_{2} = 81.3\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 29\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,SV,2,x} = \frac{M_{Rk,x}(N_{Ed} = 0)_{2}}{M_{Riss}} = \frac{81.3\,\mathrm{kNm}}{29\,\mathrm{kNm}} = 2.80
$$

#### Sprödes Versagen – 3. Lage x

**Biegewiderstand gegen Rissmoment**

$$
M_{Rk,x}(N_{Ed} = 0)_{3} = 63.7\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 29\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,SV,3,x} = \frac{M_{Rk,x}(N_{Ed} = 0)_{3}}{M_{Riss}} = \frac{63.7\,\mathrm{kNm}}{29\,\mathrm{kNm}} = 2.20
$$

Massgebend: 3. Lage (kleinster Erfüllungsgrad).

### Stahlspannung unter quasi-ständiger Einwirkung – x-Richtung

**Rechenwahl**

$$
\text{charakteristisch}\ f_{ck},\ f_{yk} \qquad 0.85 \cdot x\text{-Vereinfachung}
$$

**Dickster Stab der Tragrichtung**

$$
\varnothing_{max} = 12\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{max}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{12\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 466\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

#### Welche Werte angesetzt werden

**Werkstoffgesetze im Gebrauchszustand: Beton, Spannungsblock 0.85·x**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{ck} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werkstoffgesetze im Gebrauchszustand: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

#### Quasi-ständiger Lastfall – Dauerlast

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = 30\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.4069\,\text{‰} \qquad \chi = 0.00773\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 30\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 203\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 466\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,x,\text{Dauerlast}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{466\,\mathrm{N}/\mathrm{mm}^{2}}{203\,\mathrm{N}/\mathrm{mm}^{2}} = 2.29
$$

### Stahlspannung unter häufiger Einwirkung – x-Richtung

**Rechenwahl**

$$
\varphi = 2 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{Präzise ohne Vereinfachung}
$$

**Wirksamer Elastizitätsmodul**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Zulässige Stahlspannung** *(SIA 262:2025, Tabelle 17)*

$$
\sigma_{s,adm} = f_{yd} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 435\,\mathrm{N}/\mathrm{mm}^{2} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 355\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{ck}}\right) = \max\left(1;\ \frac{11207\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 1
$$

**Werkstoffgesetze im Gebrauchszustand: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze im Gebrauchszustand: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

#### Häufiger Lastfall – Gebrauch

**Einwirkung**

$$
M_{Ed,häufig} = 45\,\mathrm{kNm} \qquad N_{Ed,häufig} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.7643\,\text{‰} \qquad \chi = 0.01075\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 45\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 323\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,x,\text{Gebrauch}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{323\,\mathrm{N}/\mathrm{mm}^{2}} = 1.10
$$

### Knicken

**Ungewollte Ausmitte – allgemein** *(SIA 262:2025, 4.3.7)*

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \qquad e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

**Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}\right)
$$

#### Verformung

**Rechenwahl – Verformung (e\_2d)**

$$
\varphi = 0 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{Präzise ohne Vereinfachung}
$$

**Steifigkeit des Betons**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 0} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \qquad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{ck}}\right) = \max\left(1;\ \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 2.8
$$

**Werkstoffgesetze der Verformung: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze der Verformung: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

#### Widerstand: Resistenzlinie aus Dehnungsebenen – x-Richtung

**Rechenwahl – Widerstand (N\_Rd)**

$$
\varphi = 0 \qquad \text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Präzise ohne Vereinfachung}
$$

**Wirksamer Modul der Parabel**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 0} = 33620\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 4.2
$$

**Werkstoffgesetze: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Schnittgrössen aus der Spannungsverteilung**

$$
N = \int_A \sigma\,\mathrm{d}A \qquad M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A
$$

**Berücksichtigte Bewehrungslagen**

| Lage | $a_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $754$ | $204.0$ | $435$ |
| 3. Lage Grundbewehrung | $524$ | $45.0$ | $435$ |

#### Knicken – Stütze

**Einwirkung und System**

$$
N_{Ed} = -600\,\mathrm{kN} \qquad M_{Ed,1} = 10\,\mathrm{kNm} \qquad l = 3\,\mathrm{m} \qquad l_{cr} = 3\,\mathrm{m}
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
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right) = \max\left(\frac{204\,\mathrm{mm}}{30};\ \frac{0.005 \cdot 3\,\mathrm{m}}{2}\right) = 7.5\,\mathrm{mm}
$$

**Gewollte Ausmitte**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| = \left|\frac{10\,\mathrm{kNm}}{-600\,\mathrm{kN}}\right| = 16.7\,\mathrm{mm}
$$

**Das Verfahren** *(SIA 262:2025, 4.3.7)*

$$
e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}^{(k-1)}\right)
$$

**Ausmitten-Iteration bei N\_Ed = 600.0 kN**

| $k$ | $e_{2d}^{(k-1)}\ [\mathrm{mm}]$ | $M_{Ed,II}^{(k)}\ [\mathrm{kNm}]$ | $\chi^{(k)}\ [\mathrm{m}^{-1}]$ | $e_{2d}^{(k)}\ [\mathrm{mm}]$ |
| ---: | ---: | ---: | ---: | ---: |
| $1$ | $0.00$ | $14.50$ | $0.00028$ | $0.25$ |
| $2$ | $0.25$ | $14.65$ | $0.00028$ | $0.26$ |
| $3$ | $0.26$ | $14.65$ | $0.00028$ | $0.26$ |
| $4$ | $0.26$ | $14.65$ | $0.00028$ | $0.26$ |

**Probe: die gefundene Ebene erzeugt die Schnittgrössen**

$$
\varepsilon_m = -0.0582\,\text{‰} \qquad \chi = 0.00028\,\mathrm{m}^{-1} \qquad N_{int} = -600\,\mathrm{kN} \;\checkmark \qquad M_{int} = 14.7\,\mathrm{kNm} \;\checkmark
$$

**Querschnitt am verformten System**

$$
M_{Rd,x}(N_{Ed}) = 120\,\mathrm{kNm} \quad \ge \quad M_{Ed,II} = 14.7\,\mathrm{kNm}
$$

**Grenzkraft des Stabes**

$$
N_{Rd,K} = 4156.2\,\mathrm{kN} \quad \ge \quad \left|N_{Ed}\right| = 600\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,K,\text{Stütze}} = \frac{N_{Rd,K}}{\left|N_{Ed}\right|} = \frac{4156.2\,\mathrm{kN}}{600\,\mathrm{kN}} = 6.93 \quad \Rightarrow \quad \text{erfüllt}
$$

### Vergrösserungsfaktor der Durchbiegung

**Vergrösserungsfaktor der Durchbiegung – allgemein** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

**Kriechzahl**

$$
\varphi = 2
$$

**Statische Höhe der x-Bewehrung unten**

$$
d_{u} = z_{2,x,g} = 204\,\mathrm{mm}
$$

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,2,x,g}}{b \cdot d_{u}} = \frac{754\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 204\,\mathrm{mm}} = 0.0037
$$

**Statische Höhe der x-Bewehrung oben**

$$
d_{o} = h - z_{3,x,g} = 250\,\mathrm{mm} - 45\,\mathrm{mm} = 205\,\mathrm{mm}
$$

**Bewehrungsgehalt oben**

$$
\rho_{o} = \frac{A_{s,3,x,g}}{b \cdot d_{o}} = \frac{524\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 205\,\mathrm{mm}} = 0.00255
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00255}{10 \cdot 0.0037^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{250\,\mathrm{mm}}{204\,\mathrm{mm}}\right)^{3} \\
  &= 8.37
\end{aligned}
$$

**Vergrösserungsfaktor, Zug oben** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w' &= \frac{1 - 20 \cdot \rho_{u}}{10 \cdot \rho_{o}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{o}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.0037}{10 \cdot 0.00255^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{250\,\mathrm{mm}}{205\,\mathrm{mm}}\right)^{3} \\
  &= 10.42
\end{aligned}
$$

### Kennzahlen

#### Kennzahlen: Resistenzlinie aus Handrechnung – x-Richtung

**Rechenwahl – Kennzahlen**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Handrechnung}
$$

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $754$ | $204.0$ | $435$ |
| 3. Lage Grundbewehrung | $524$ | $45.0$ | $435$ |

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
  &= 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 555.5\,\mathrm{kN}
\end{aligned}
$$

**Kräfte mal Hebelarm um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}(N_{Rd}^{+}) &= A_{s,2,x} \cdot f_{yd} \cdot \left(z_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(z_{3,x} - \tfrac{h}{2}\right) \\
  &= 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(45\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right) \\
  &= 7.7\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{2,x} = z_{2,x} = 204\,\mathrm{mm}
$$

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

**Nulllinie auf halber Höhe**

$$
x^{+} = \frac{h}{2} = \frac{250\,\mathrm{mm}}{2} = 125\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(204\,\mathrm{mm} - 125\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{125\,\mathrm{mm}} = 2.21\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.21\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1797.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot \sigma_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} \cdot \left(\tfrac{250\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 125\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right)\right] \\
  &= 178.6\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{3,x} = h - z_{3,x} = 250\,\mathrm{mm} - 45\,\mathrm{mm} = 205\,\mathrm{mm}
$$

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{-} = \frac{A_{s,3,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 13.4\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{-} &= -A_{s,3,x} \cdot f_{yd} \cdot \left(d_{3,x} - \frac{0.85 \cdot x^{-}}{2}\right) \\
  &= -524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(205\,\mathrm{mm} - \frac{0.85 \cdot 13.4\,\mathrm{mm}}{2}\right) \\
  &= -45.4\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe**

$$
x^{-} = \frac{h}{2} = \frac{250\,\mathrm{mm}}{2} = 125\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{3,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(205\,\mathrm{mm} - 125\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{125\,\mathrm{mm}} = 2.24\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{-};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.24\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,3,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1897.3\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,3,x} \cdot \sigma_{sd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right)\right] \\
  &= -\left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} \cdot \left(\tfrac{250\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 125\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(205\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right)\right] \\
  &= -170.9\,\mathrm{kNm}
\end{aligned}
$$

**Eckpunkte der Resistenzlinie aus Handrechnung**

| Eckpunkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{-}$ | $-5000.0$ | $0.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1797.2$ | $178.6$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $64.2$ |
| $N_{Rd}^{+}$ | $555.5$ | $7.7$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $0.0$ | $-45.4$ |
| $M_{Rd}(x=\tfrac{h}{2})^{-}$ | $-1897.3$ | $-170.9$ |

#### Biegung und Normalkraft

**Momentenwiderstand bei N\_Ed = 0, Zug unten**

$$
M_{Rd}^{+}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{+} = 64.2\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten**

$$
\left(x/d\right)^{+} = \frac{x^{+}}{d_{2,x}} = \frac{19.3\,\mathrm{mm}}{204\,\mathrm{mm}} = 0.095
$$

**Momentenwiderstand bei N\_Ed = 0, Zug oben**

$$
M_{Rd}^{-}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{-} = -45.4\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben**

$$
\left(x/d\right)^{-} = \frac{x^{-}}{d_{3,x}} = \frac{13.4\,\mathrm{mm}}{205\,\mathrm{mm}} = 0.065
$$

**Zugwiderstand bei M\_Ed = 0**

$$
\begin{aligned}
  N_{Rd}^{+}(M_{Ed} = 0) &= N_1 + \frac{M_{Ed} - M_1}{M_2 - M_1} \cdot \left(N_2 - N_1\right) \\
  &= 555.5\,\mathrm{kN} + \frac{0\,\mathrm{kNm} - 7.7\,\mathrm{kNm}}{-45.4\,\mathrm{kNm} - 7.7\,\mathrm{kNm}} \cdot \left(0\,\mathrm{kN} - 555.5\,\mathrm{kN}\right) \\
  &= 475\,\mathrm{kN}
\end{aligned}
$$

**Stützpunkte der Interpolation**

| Punkt | $M\ [\mathrm{kNm}]$ | $N\ [\mathrm{kN}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{+}$ | $7.7$ | $555.5$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $-45.4$ | $0.0$ |

**Druckwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-} = -5000\,\mathrm{kN}
$$

#### Querkraftwiderstand ohne Bügel bei N\_Ed = 0

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d^{+} = z_{2,x,g} = 204\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{+} = d^{+} = 204\,\mathrm{mm}
$$

**Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 204\,\mathrm{mm} = 223.5\,\mathrm{kN}/\mathrm{m}
$$

**Zug unten, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{+} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 204 \cdot 1.2} = 0.6527 \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug unten, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) &= k_d^{+} \cdot \tau_{cd} \cdot d_v^{+} \\
  &= 0.6527 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 204\,\mathrm{mm} \\
  &= 145.9\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d^{-} = h - z_{3,x,g} = 250\,\mathrm{mm} - 45\,\mathrm{mm} = 205\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{-} = d^{-} = 205\,\mathrm{mm}
$$

**Zug oben, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{-}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{-} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 205\,\mathrm{mm} = 224.6\,\mathrm{kN}/\mathrm{m}
$$

**Zug oben, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{-} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{-} = \frac{1}{1 + \varepsilon_v^{-} \cdot d^{-} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 205 \cdot 1.2} = 0.6516 \quad \left(d^{-}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug oben, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-}) &= k_d^{-} \cdot \tau_{cd} \cdot d_v^{-} \\
  &= 0.6516 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 205\,\mathrm{mm} \\
  &= 146.3\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = 0, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,max} &= \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right] \\
  &= \min\left[223.5\,\mathrm{kN}/\mathrm{m};\ 224.6\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 223.5\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,min} &= \min\left[V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+});\ V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-})\right] \\
  &= \min\left[145.9\,\mathrm{kN}/\mathrm{m};\ 146.3\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 145.9\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

### Plattenanalyse: Block

**Plattendicke**

$$
h = 220\,\mathrm{mm}
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

**Bewehrungsquerschnitt über die Breite b** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{1717\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 220\,\mathrm{mm}} = 61\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 172\,\mathrm{mm} - 48\,\mathrm{mm} \\
  &= 124\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $z\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | y | B500B | $8$ | $150$ | $34$ | $186$ | $335$ |
| 2. Lage Grundbewehrung | x | B500B | $10$ | $150$ | $43$ | $177$ | $524$ |
| 3. Lage Grundbewehrung | x | B500B | $10$ | $150$ | $43$ | $43$ | $524$ |
| 4. Lage Grundbewehrung | y | B500B | $8$ | $150$ | $34$ | $34$ | $335$ |

### Resistenzlinie aus Dehnungsebenen – x-Richtung

**Rechenwahl**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad 0.85 \cdot x\text{-Vereinfachung}
$$

**Werkstoffgesetze: Beton, Spannungsblock 0.85·x**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{cd} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werkstoffgesetze: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Schnittgrössen aus der Spannungsverteilung**

$$
N = \int_A \sigma\,\mathrm{d}A \qquad M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A
$$

**Berücksichtigte Bewehrungslagen**

| Lage | $a_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $524$ | $177.0$ | $435$ |
| 3. Lage Grundbewehrung | $524$ | $43.0$ | $435$ |

#### Nachweis – Feld

**Einwirkung**

$$
M_{Ed} = 25\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Bruchzustand bei N\_Ed = 0.0 kN – die Dehnungsebene**

$$
\varepsilon_{oben} = -3.5\,\text{‰} \qquad \varepsilon_{unten} = 25.408\,\text{‰}
$$

**Kräfte in diesem Bruchzustand – Zug positiv, z ab Oberkante**

| Teil | $\varepsilon\ [‰]$ | $\sigma\ [\mathrm{N/mm^2}]$ | $A\ [\mathrm{mm}^2]$ | $F\ [\mathrm{kN}]$ | $z\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Beton, Resultierende | $–$ | $–$ | $–$ | $-452.8$ | $11.3$ |
| 2. Lage Grundbewehrung | $19.758$ | $434.8$ | $524$ | $227.7$ | $177.0$ |
| 3. Lage Grundbewehrung | $2.150$ | $430.0$ | $524$ | $225.2$ | $43.0$ |

**Probe: die Ebene trägt genau die Einwirkung**

$$
\sum F_i = 0\,\mathrm{kN} = N_{Ed}
$$

**Momentenwiderstand aus den Teilkräften**

$$
M_{Rd} = \sum F_i \cdot \left(z_i - \tfrac{h}{2}\right) = 44.8\,\mathrm{kNm}
$$

Massgebend: Beton am oberen Rand auf der Grenzdehnung.

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{44.8\,\mathrm{kNm}}{25\,\mathrm{kNm}} = 1.79 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Rand

**Einwirkung**

$$
M_{Ed} = -15\,\mathrm{kNm} \qquad N_{Ed} = -100\,\mathrm{kN}
$$

**Bruchzustand bei M\_Ed = -15.0 kNm – die Dehnungsebene**

$$
\varepsilon_{oben} = -0.487\,\text{‰} \qquad \varepsilon_{unten} = -3.135\,\text{‰}
$$

**Kräfte in diesem Bruchzustand – Zug positiv, z ab Oberkante**

| Teil | $\varepsilon\ [‰]$ | $\sigma\ [\mathrm{N/mm^2}]$ | $A\ [\mathrm{mm}^2]$ | $F\ [\mathrm{kN}]$ | $z\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Beton, Resultierende | $–$ | $–$ | $–$ | $-4316.4$ | $111.6$ |
| 2. Lage Grundbewehrung | $-2.617$ | $-434.8$ | $524$ | $-227.7$ | $177.0$ |
| 3. Lage Grundbewehrung | $-1.005$ | $-200.9$ | $524$ | $-105.2$ | $43.0$ |

**Probe: die Ebene trägt genau die Einwirkung**

$$
\sum F_i \cdot \left(z_i - \tfrac{h}{2}\right) = -15\,\mathrm{kNm} = M_{Ed}
$$

**Normalkraftwiderstand aus den Teilkräften**

$$
N_{Rd} = \sum F_i = -4649.2\,\mathrm{kN}
$$

Massgebend: Beton im Punkt C auf der Grenzdehnung.

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Rand}} = \frac{N_{Rd}}{N_{Ed}} = \frac{4649.2\,\mathrm{kN}}{100\,\mathrm{kN}} = 46.49 \quad \Rightarrow \quad \text{erfüllt}
$$

### Querkraft – x-Richtung

**Ansatz** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

**Dekompressionsmoment und Dehnung**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

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
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

#### Querkraftnachweis – Feld

**Einwirkung**

$$
V_{Ed} = 30\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 25\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d = z_{2,x,g} = 177\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v = d = 177\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|\min(0\,\mathrm{kN};\ 0)\right| \cdot 220\,\mathrm{mm}}{6} = 0\,\mathrm{kNm}
$$

**Momentenwiderstand bei N\_Ed = 0.0 kN**

$$
\varepsilon_{oben} = -3.5\,\text{‰} \qquad \varepsilon_{unten} = 25.408\,\text{‰}
$$

**Kräfte in diesem Bruchzustand – Zug positiv, z ab Oberkante**

| Teil | $\varepsilon\ [‰]$ | $\sigma\ [\mathrm{N/mm^2}]$ | $A\ [\mathrm{mm}^2]$ | $F\ [\mathrm{kN}]$ | $z\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Beton, Resultierende | $–$ | $–$ | $–$ | $-452.8$ | $11.3$ |
| 2. Lage Grundbewehrung | $19.758$ | $434.8$ | $524$ | $227.7$ | $177.0$ |
| 3. Lage Grundbewehrung | $2.150$ | $430.0$ | $524$ | $225.2$ | $43.0$ |

**Probe: die Ebene trägt genau die Einwirkung**

$$
\sum F_i = 0\,\mathrm{kN} = N_{Ed}
$$

**Momentenwiderstand aus den Teilkräften**

$$
M_{Rd} = \sum F_i \cdot \left(z_i - \tfrac{h}{2}\right) = 44.8\,\mathrm{kNm}
$$

Massgebend: Beton am oberen Rand auf der Grenzdehnung.

**Dehnung auf halber Höhe**

$$
\begin{aligned}
  \varepsilon_v &= \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)} \\
  &= \frac{435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|25\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)}{200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|44.8\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)} \\
  &= 1.212\,\text{‰}
\end{aligned}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 1.212\,\text{‰} \cdot 177 \cdot 1.2} = 0.7953 \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 25\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= k_d \cdot \tau_{cd} \cdot d_v \\
  &= 0.7953 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 177\,\mathrm{mm} \\
  &= 154.2\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x,\text{Feld}} = \frac{V_{Rd,x}}{V_{Ed,x}} = \frac{154.2\,\mathrm{kN}/\mathrm{m}}{30\,\mathrm{kN}/\mathrm{m}} = 5.14 \quad \Rightarrow \quad \text{erfüllt}
$$

### Stahlspannung unter quasi-ständiger Einwirkung – x-Richtung

**Rechenwahl**

$$
\text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{Handrechnung}
$$

**Zulässige Stahlspannung (normale Anforderung)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm} = f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

**Werkstoffgesetze im Gebrauchszustand: Beton, Spannungsblock 0.85·x**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{ck} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werkstoffgesetze im Gebrauchszustand: Stahl, nur auf Zug**

$$
\sigma_s = \begin{cases} \min\left(E_s \cdot \varepsilon_s;\ f_{yk}\right) & \varepsilon_s > 0 \\[1ex] 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen}) \end{cases}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

#### Quasi-ständiger Lastfall – Dauerlast

**Einwirkung**

$$
M_{Ed,\text{quasi-ständig}} = 12\,\mathrm{kNm} \qquad N_{Ed,\text{quasi-ständig}} = 0\,\mathrm{kN}
$$

**Gefundene Dehnungsebene**

$$
\varepsilon_m = 0.202\,\text{‰} \qquad \chi = 0.00675\,\mathrm{m}^{-1} \qquad \varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \tfrac{h}{2}\right)
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{int} = 12\,\mathrm{kNm} \;\checkmark
$$

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_{s,x} = 131\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 500\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,x,\text{Dauerlast}} = \frac{\sigma_{s,adm}}{\sigma_{s,x}} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{131\,\mathrm{N}/\mathrm{mm}^{2}} = 3.82
$$

### Knicken

**Ungewollte Ausmitte – allgemein** *(SIA 262:2025, 4.3.7)*

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \qquad e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

**Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}\right)
$$

#### Verformung

**Rechenwahl – Verformung (e\_2d)**

$$
\varphi = 0 \qquad \text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Präzise ohne Vereinfachung}
$$

**Steifigkeit des Betons**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 0} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \qquad f_{cd} = 20\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 4.2
$$

**Werkstoffgesetze der Verformung: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze der Verformung: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yd}\right] \quad f_{yd} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

#### Widerstand

**Rechenwahl – Widerstand (N\_Rd)**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad 0.85 \cdot x\text{-Vereinfachung}
$$

Dieselbe Wahl wie die Tragsicherheit: der Momentenwiderstand bei der Druckkraft kommt aus deren Resistenzlinie.

#### Knicken – Wand

**Einwirkung und System**

$$
N_{Ed} = -400\,\mathrm{kN} \qquad M_{Ed,1} = 5\,\mathrm{kNm} \qquad l = 2.5\,\mathrm{m} \qquad l_{cr} = 2.5\,\mathrm{m}
$$

**Schiefstellung** *(SIA 262:2025, 4.3.7)*

$$
\begin{aligned}
  \alpha_i &= \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= \min\left[\max\left(\frac{0.01}{\sqrt{2.5}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= 0.005 \quad \left(l\ \text{in}\ \mathrm{m}\right)
\end{aligned}
$$

**Ungewollte Ausmitte** *(SIA 262:2025, 4.3.7)*

$$
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right) = \max\left(\frac{177\,\mathrm{mm}}{30};\ \frac{0.005 \cdot 2.5\,\mathrm{m}}{2}\right) = 6.2\,\mathrm{mm}
$$

**Gewollte Ausmitte**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| = \left|\frac{5\,\mathrm{kNm}}{-400\,\mathrm{kN}}\right| = 12.5\,\mathrm{mm}
$$

**Das Verfahren** *(SIA 262:2025, 4.3.7)*

$$
e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}^{(k-1)}\right)
$$

**Ausmitten-Iteration bei N\_Ed = 400.0 kN**

| $k$ | $e_{2d}^{(k-1)}\ [\mathrm{mm}]$ | $M_{Ed,II}^{(k)}\ [\mathrm{kNm}]$ | $\chi^{(k)}\ [\mathrm{m}^{-1}]$ | $e_{2d}^{(k)}\ [\mathrm{mm}]$ |
| ---: | ---: | ---: | ---: | ---: |
| $1$ | $0.00$ | $7.50$ | $0.00022$ | $0.14$ |
| $2$ | $0.14$ | $7.56$ | $0.00022$ | $0.14$ |
| $3$ | $0.14$ | $7.56$ | $0.00022$ | $0.14$ |

**Probe: die gefundene Ebene erzeugt die Schnittgrössen**

$$
\varepsilon_m = -0.045\,\text{‰} \qquad \chi = 0.00022\,\mathrm{m}^{-1} \qquad N_{int} = -400\,\mathrm{kN} \;\checkmark \qquad M_{int} = 7.6\,\mathrm{kNm} \;\checkmark
$$

**Querschnitt am verformten System**

$$
M_{Rd,x}(N_{Ed}) = 74.8\,\mathrm{kNm} \quad \ge \quad M_{Ed,II} = 7.6\,\mathrm{kNm}
$$

**Grenzkraft des Stabes**

$$
N_{Rd,K} = 3508.6\,\mathrm{kN} \quad \ge \quad \left|N_{Ed}\right| = 400\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,K,\text{Wand}} = \frac{N_{Rd,K}}{\left|N_{Ed}\right|} = \frac{3508.6\,\mathrm{kN}}{400\,\mathrm{kN}} = 8.77 \quad \Rightarrow \quad \text{erfüllt}
$$

### Vergrösserungsfaktor der Durchbiegung

**Vergrösserungsfaktor der Durchbiegung – allgemein** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

**Kriechzahl**

$$
\varphi = 2
$$

**Statische Höhe der x-Bewehrung unten**

$$
d_{u} = z_{2,x,g} = 177\,\mathrm{mm}
$$

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,2,x,g}}{b \cdot d_{u}} = \frac{524\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 177\,\mathrm{mm}} = 0.00296
$$

**Statische Höhe der x-Bewehrung oben**

$$
d_{o} = h - z_{3,x,g} = 220\,\mathrm{mm} - 43\,\mathrm{mm} = 177\,\mathrm{mm}
$$

**Bewehrungsgehalt oben**

$$
\rho_{o} = \frac{A_{s,3,x,g}}{b \cdot d_{o}} = \frac{524\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 177\,\mathrm{mm}} = 0.00296
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00296}{10 \cdot 0.00296^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{220\,\mathrm{mm}}{177\,\mathrm{mm}}\right)^{3} \\
  &= 10.11
\end{aligned}
$$

**Vergrösserungsfaktor, Zug oben** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w' &= \frac{1 - 20 \cdot \rho_{u}}{10 \cdot \rho_{o}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{o}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00296}{10 \cdot 0.00296^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{220\,\mathrm{mm}}{177\,\mathrm{mm}}\right)^{3} \\
  &= 10.11
\end{aligned}
$$

### Kennzahlen

#### Kennzahlen: Resistenzlinie aus Handrechnung – x-Richtung

**Rechenwahl – Kennzahlen**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Handrechnung}
$$

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $524$ | $177.0$ | $435$ |
| 3. Lage Grundbewehrung | $524$ | $43.0$ | $435$ |

#### Grösste Druckkraft

**Gleichmässiger Druck, ohne Bewehrung**

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd} = -1000\,\mathrm{mm} \cdot 220\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} = -4400\,\mathrm{kN}
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
  &= 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 455.3\,\mathrm{kN}
\end{aligned}
$$

**Kräfte mal Hebelarm um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}(N_{Rd}^{+}) &= A_{s,2,x} \cdot f_{yd} \cdot \left(z_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(z_{3,x} - \tfrac{h}{2}\right) \\
  &= 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(177\,\mathrm{mm} - \tfrac{220\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(43\,\mathrm{mm} - \tfrac{220\,\mathrm{mm}}{2}\right) \\
  &= 0\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{2,x} = z_{2,x} = 177\,\mathrm{mm}
$$

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{+} = \frac{A_{s,2,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 13.4\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{+} &= A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \frac{0.85 \cdot x^{+}}{2}\right) \\
  &= 524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(177\,\mathrm{mm} - \frac{0.85 \cdot 13.4\,\mathrm{mm}}{2}\right) \\
  &= 39\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe**

$$
x^{+} = \frac{h}{2} = \frac{220\,\mathrm{mm}}{2} = 110\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(177\,\mathrm{mm} - 110\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{110\,\mathrm{mm}} = 2.13\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.13\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 426\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 110\,\mathrm{mm} + 524\,\mathrm{mm}^{2} \cdot 426\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1646.8\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot \sigma_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 110\,\mathrm{mm} \cdot \left(\tfrac{220\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 110\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 426\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(177\,\mathrm{mm} - \tfrac{220\,\mathrm{mm}}{2}\right)\right] \\
  &= 133.2\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{3,x} = h - z_{3,x} = 220\,\mathrm{mm} - 43\,\mathrm{mm} = 177\,\mathrm{mm}
$$

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{-} = \frac{A_{s,3,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 13.4\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{-} &= -A_{s,3,x} \cdot f_{yd} \cdot \left(d_{3,x} - \frac{0.85 \cdot x^{-}}{2}\right) \\
  &= -524\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(177\,\mathrm{mm} - \frac{0.85 \cdot 13.4\,\mathrm{mm}}{2}\right) \\
  &= -39\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe**

$$
x^{-} = \frac{h}{2} = \frac{220\,\mathrm{mm}}{2} = 110\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{3,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(177\,\mathrm{mm} - 110\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{110\,\mathrm{mm}} = 2.13\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{-};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.13\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 426\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,3,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 110\,\mathrm{mm} + 524\,\mathrm{mm}^{2} \cdot 426\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1646.8\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,3,x} \cdot \sigma_{sd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right)\right] \\
  &= -\left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 110\,\mathrm{mm} \cdot \left(\tfrac{220\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 110\,\mathrm{mm}}{2}\right) + 524\,\mathrm{mm}^{2} \cdot 426\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(177\,\mathrm{mm} - \tfrac{220\,\mathrm{mm}}{2}\right)\right] \\
  &= -133.2\,\mathrm{kNm}
\end{aligned}
$$

**Eckpunkte der Resistenzlinie aus Handrechnung**

| Eckpunkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{-}$ | $-4400.0$ | $0.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1646.8$ | $133.2$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $39.0$ |
| $N_{Rd}^{+}$ | $455.3$ | $-0.0$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $0.0$ | $-39.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{-}$ | $-1646.8$ | $-133.2$ |

#### Biegung und Normalkraft

**Momentenwiderstand bei N\_Ed = 0, Zug unten**

$$
M_{Rd}^{+}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{+} = 39\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten**

$$
\left(x/d\right)^{+} = \frac{x^{+}}{d_{2,x}} = \frac{13.4\,\mathrm{mm}}{177\,\mathrm{mm}} = 0.076
$$

**Momentenwiderstand bei N\_Ed = 0, Zug oben**

$$
M_{Rd}^{-}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{-} = -39\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben**

$$
\left(x/d\right)^{-} = \frac{x^{-}}{d_{3,x}} = \frac{13.4\,\mathrm{mm}}{177\,\mathrm{mm}} = 0.076
$$

**Zugwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{+}(M_{Ed} = 0) = N_{Rd}^{+} = 455.3\,\mathrm{kN}
$$

**Druckwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-} = -4400\,\mathrm{kN}
$$

#### Querkraftwiderstand ohne Bügel bei N\_Ed = 0

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d^{+} = z_{2,x,g} = 177\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{+} = d^{+} = 177\,\mathrm{mm}
$$

**Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 177\,\mathrm{mm} = 193.9\,\mathrm{kN}/\mathrm{m}
$$

**Zug unten, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{+} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 177 \cdot 1.2} = 0.6841 \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug unten, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) &= k_d^{+} \cdot \tau_{cd} \cdot d_v^{+} \\
  &= 0.6841 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 177\,\mathrm{mm} \\
  &= 132.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d^{-} = h - z_{3,x,g} = 220\,\mathrm{mm} - 43\,\mathrm{mm} = 177\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{-} = d^{-} = 177\,\mathrm{mm}
$$

**Zug oben, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{-}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{-} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 177\,\mathrm{mm} = 193.9\,\mathrm{kN}/\mathrm{m}
$$

**Zug oben, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{-} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{-} = \frac{1}{1 + \varepsilon_v^{-} \cdot d^{-} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 177 \cdot 1.2} = 0.6841 \quad \left(d^{-}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug oben, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-}) &= k_d^{-} \cdot \tau_{cd} \cdot d_v^{-} \\
  &= 0.6841 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 177\,\mathrm{mm} \\
  &= 132.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = 0, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,max} &= \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right] \\
  &= \min\left[193.9\,\mathrm{kN}/\mathrm{m};\ 193.9\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 193.9\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,min} &= \min\left[V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+});\ V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-})\right] \\
  &= \min\left[132.6\,\mathrm{kN}/\mathrm{m};\ 132.6\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 132.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
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

**Bewehrungsquerschnitt über die Breite b** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{10409\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 250\,\mathrm{mm}} = 327\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 168\,\mathrm{mm} - 52\,\mathrm{mm} \\
  &= 116\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $z\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | y | B500B | $40$ | $150$ | $50$ | $200$ | $8378$ |
| 2. Lage Grundbewehrung | x | B500B | $12$ | $150$ | $76$ | $174$ | $754$ |
| 3. Lage Grundbewehrung | x | B500B | $12$ | $150$ | $46$ | $46$ | $754$ |
| 4. Lage Grundbewehrung | y | B500B | $10$ | $150$ | $35$ | $35$ | $524$ |

### Resistenzlinie aus Handrechnung – x-Richtung

**Rechenwahl**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Handrechnung}
$$

**Zusammengefasste Bewehrung**

| Seite | $A_s\ [\mathrm{mm}^2]$ | $z\ [\mathrm{mm}]$ | $f_{yd}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| 2. Lage Grundbewehrung | $754$ | $174.0$ | $435$ |
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
  M_{Rd}(N_{Rd}^{+}) &= A_{s,2,x} \cdot f_{yd} \cdot \left(z_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(z_{3,x} - \tfrac{h}{2}\right) \\
  &= 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(174\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(46\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right) \\
  &= -9.8\,\mathrm{kNm}
\end{aligned}
$$

#### Positives Moment (Zug unten)

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{2,x} = z_{2,x} = 174\,\mathrm{mm}
$$

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{+} = \frac{A_{s,2,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}} = \frac{754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{0.85 \cdot 1000\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 19.3\,\mathrm{mm}
$$

**Momentenwiderstand bei reiner Biegung**

$$
\begin{aligned}
  M_{Rd}(N_{Ed}=0)^{+} &= A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \frac{0.85 \cdot x^{+}}{2}\right) \\
  &= 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(174\,\mathrm{mm} - \frac{0.85 \cdot 19.3\,\mathrm{mm}}{2}\right) \\
  &= 54.4\,\mathrm{kNm}
\end{aligned}
$$

**Nulllinie auf halber Höhe**

$$
x^{+} = \frac{h}{2} = \frac{250\,\mathrm{mm}}{2} = 125\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(174\,\mathrm{mm} - 125\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{125\,\mathrm{mm}} = 1.37\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1.37\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 274\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 274\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1918.1\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{+} &= \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot \sigma_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right] \\
  &= \left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} \cdot \left(\tfrac{250\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 125\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 274\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(174\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right)\right] \\
  &= 162.9\,\mathrm{kNm}
\end{aligned}
$$

#### Negatives Moment (Zug oben)

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{3,x} = h - z_{3,x} = 250\,\mathrm{mm} - 46\,\mathrm{mm} = 204\,\mathrm{mm}
$$

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

**Nulllinie auf halber Höhe**

$$
x^{-} = \frac{h}{2} = \frac{250\,\mathrm{mm}}{2} = 125\,\mathrm{mm}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{-} = \left(d_{3,x} - x^{-}\right) \cdot \frac{\varepsilon_{c2d}}{x^{-}} = \left(204\,\mathrm{mm} - 125\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{125\,\mathrm{mm}} = 2.21\,\text{‰}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{-};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.21\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Kräftegleichgewicht**

$$
\begin{aligned}
  N_{Rd}^{-} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{-} + A_{s,3,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1797.2\,\mathrm{kN}
\end{aligned}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
\begin{aligned}
  M_{Rd}^{-} &= -\left[f_{cd} \cdot b \cdot 0.85 \cdot x^{-} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{-}}{2}\right) + A_{s,3,x} \cdot \sigma_{sd} \cdot \left(d_{3,x} - \tfrac{h}{2}\right)\right] \\
  &= -\left[20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 125\,\mathrm{mm} \cdot \left(\tfrac{250\,\mathrm{mm}}{2} - \tfrac{0.85 \cdot 125\,\mathrm{mm}}{2}\right) + 754\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(204\,\mathrm{mm} - \tfrac{250\,\mathrm{mm}}{2}\right)\right] \\
  &= -178.6\,\mathrm{kNm}
\end{aligned}
$$

**Eckpunkte der Resistenzlinie aus Handrechnung**

| Eckpunkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $N_{Rd}^{-}$ | $-5000.0$ | $0.0$ |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1918.1$ | $162.9$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $54.4$ |
| $N_{Rd}^{+}$ | $655.6$ | $-9.8$ |
| $M_{Rd}(N_{Ed}=0)^{-}$ | $0.0$ | $-64.2$ |
| $M_{Rd}(x=\tfrac{h}{2})^{-}$ | $-1797.2$ | $-178.6$ |

#### Nachweis – Feld

**Einwirkung**

$$
M_{Ed} = 40\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 54.4\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{54.4\,\mathrm{kNm}}{40\,\mathrm{kNm}} = 1.36 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Schräg

**Einwirkung**

$$
M_{Ed} = 30\,\mathrm{kNm} \qquad N_{Ed} = -500\,\mathrm{kN}
$$

**Bezugsgrösse der Normalkraft**

$$
\begin{aligned}
  N_{ref} &= \max\left(\left|N_{Rd,x}^{+}\right|;\ \left|N_{Rd,x}^{-}\right|\right) \\
  &= \max\left(\left|655.6\,\mathrm{kN}\right|;\ \left|-5000\,\mathrm{kN}\right|\right) \\
  &= 5000\,\mathrm{kN}
\end{aligned}
$$

**Bezugsgrösse des Moments**

$$
\begin{aligned}
  M_{ref} &= \max\left(\left|M_{Rd,x}^{+}\right|;\ \left|M_{Rd,x}^{-}\right|\right) \\
  &= \max\left(\left|162.9\,\mathrm{kNm}\right|;\ \left|-178.6\,\mathrm{kNm}\right|\right) \\
  &= 178.6\,\mathrm{kNm}
\end{aligned}
$$

**Einwirkung im normierten Diagramm**

$$
\bar{E}_{d,x} = \sqrt{\left(\frac{N_{Ed}}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed}}{M_{ref}}\right)^{2}} = \sqrt{\left(\frac{-500\,\mathrm{kN}}{5000\,\mathrm{kN}}\right)^{2} + \left(\frac{30\,\mathrm{kNm}}{178.6\,\mathrm{kNm}}\right)^{2}} = 0.195
$$

**Nächster Punkt P der Resistenzlinie**

$$
N_P = 160.8\,\mathrm{kN} \qquad M_P = 38.6\,\mathrm{kNm}
$$

**Kürzester Abstand zur Resistenzlinie**

$$
\begin{aligned}
  a &= \sqrt{\left(\frac{N_{Ed} - N_P}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed} - M_P}{M_{ref}}\right)^{2}} \\
  &= \sqrt{\left(\frac{-500\,\mathrm{kN} - 160.8\,\mathrm{kN}}{5000\,\mathrm{kN}}\right)^{2} + \left(\frac{30\,\mathrm{kNm} - 38.6\,\mathrm{kNm}}{178.6\,\mathrm{kNm}}\right)^{2}} \\
  &= 0.141
\end{aligned}
$$

**Widerstand im normierten Diagramm**

$$
\bar{R}_{d,x} = \bar{E}_{d,x} + a = 0.195 + 0.141 = 0.336
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Schräg}} = \frac{\bar{R}_{d,x}}{\bar{E}_{d,x}} = \frac{0.336}{0.195} = 1.72 \quad \Rightarrow \quad \text{erfüllt}
$$

### Querkraft – x-Richtung

**Ansatz** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

**Dekompressionsmoment und Dehnung**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

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
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

#### Querkraftnachweis – Feld

**Einwirkung**

$$
V_{Ed} = 50\,\mathrm{kN}/\mathrm{m} \qquad M_{Ed} = 40\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d = z_{2,x,g} = 174\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v = d = 174\,\mathrm{mm}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|\min(0\,\mathrm{kN};\ 0)\right| \cdot 250\,\mathrm{mm}}{6} = 0\,\mathrm{kNm}
$$

**Momentenwiderstand bei N\_Ed = 0.0 kN**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 54.4\,\mathrm{kNm}
$$

**Dehnung auf halber Höhe**

$$
\begin{aligned}
  \varepsilon_v &= \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)} \\
  &= \frac{435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|40\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)}{200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|54.4\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)} \\
  &= 1.6\,\text{‰}
\end{aligned}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 1.6\,\text{‰} \cdot 174 \cdot 1.2} = 0.7496 \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 40\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= k_d \cdot \tau_{cd} \cdot d_v \\
  &= 0.7496 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 174\,\mathrm{mm} \\
  &= 142.9\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,V,x,\text{Feld}} = \frac{V_{Rd,x}}{V_{Ed,x}} = \frac{142.9\,\mathrm{kN}/\mathrm{m}}{50\,\mathrm{kN}/\mathrm{m}} = 2.86 \quad \Rightarrow \quad \text{erfüllt}
$$

### Vergrösserungsfaktor der Durchbiegung

**Vergrösserungsfaktor der Durchbiegung – allgemein** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

**Kriechzahl**

$$
\varphi = 2
$$

**Statische Höhe der x-Bewehrung unten**

$$
d_{u} = z_{2,x,g} = 174\,\mathrm{mm}
$$

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,2,x,g}}{b \cdot d_{u}} = \frac{754\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 174\,\mathrm{mm}} = 0.00433
$$

**Statische Höhe der x-Bewehrung oben**

$$
d_{o} = h - z_{3,x,g} = 250\,\mathrm{mm} - 46\,\mathrm{mm} = 204\,\mathrm{mm}
$$

**Bewehrungsgehalt oben**

$$
\rho_{o} = \frac{A_{s,3,x,g}}{b \cdot d_{o}} = \frac{754\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 204\,\mathrm{mm}} = 0.0037
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.0037}{10 \cdot 0.00433^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{250\,\mathrm{mm}}{174\,\mathrm{mm}}\right)^{3} \\
  &= 11.77
\end{aligned}
$$

**Vergrösserungsfaktor, Zug oben** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w' &= \frac{1 - 20 \cdot \rho_{u}}{10 \cdot \rho_{o}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{o}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00433}{10 \cdot 0.0037^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{250\,\mathrm{mm}}{204\,\mathrm{mm}}\right)^{3} \\
  &= 8.05
\end{aligned}
$$

### Kennzahlen

Die Eckpunkte stammen aus der Handrechnung der Tragsicherheit – sie rechnet ebenso, von Hand mit Bemessungswerten.

#### Biegung und Normalkraft

**Momentenwiderstand bei N\_Ed = 0, Zug unten**

$$
M_{Rd}^{+}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{+} = 54.4\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten**

$$
\left(x/d\right)^{+} = \frac{x^{+}}{d_{2,x}} = \frac{19.3\,\mathrm{mm}}{174\,\mathrm{mm}} = 0.111
$$

**Momentenwiderstand bei N\_Ed = 0, Zug oben**

$$
M_{Rd}^{-}(N_{Ed} = 0) = M_{Rd}(N_{Ed}=0)^{-} = -64.2\,\mathrm{kNm}
$$

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben**

$$
\left(x/d\right)^{-} = \frac{x^{-}}{d_{3,x}} = \frac{19.3\,\mathrm{mm}}{204\,\mathrm{mm}} = 0.095
$$

**Zugwiderstand bei M\_Ed = 0**

$$
\begin{aligned}
  N_{Rd}^{+}(M_{Ed} = 0) &= N_1 + \frac{M_{Ed} - M_1}{M_2 - M_1} \cdot \left(N_2 - N_1\right) \\
  &= 0\,\mathrm{kN} + \frac{0\,\mathrm{kNm} - 54.4\,\mathrm{kNm}}{-9.8\,\mathrm{kNm} - 54.4\,\mathrm{kNm}} \cdot \left(655.6\,\mathrm{kN} - 0\,\mathrm{kN}\right) \\
  &= 555.2\,\mathrm{kN}
\end{aligned}
$$

**Stützpunkte der Interpolation**

| Punkt | $M\ [\mathrm{kNm}]$ | $N\ [\mathrm{kN}]$ |
| :--- | ---: | ---: |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $54.4$ | $0.0$ |
| $N_{Rd}^{+}$ | $-9.8$ | $655.6$ |

**Druckwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-} = -5000\,\mathrm{kN}
$$

#### Querkraftwiderstand ohne Bügel bei N\_Ed = 0

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  k_g &= \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \\
  &= \max\left[1.20;\ \frac{48}{16 + 32 \cdot \min\left[1.0;\ \left(\frac{60}{30}\right)^{2}\right]}\right] \\
  &= 1.2 \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
\end{aligned}
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d^{+} = z_{2,x,g} = 174\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{+} = d^{+} = 174\,\mathrm{mm}
$$

**Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 174\,\mathrm{mm} = 190.6\,\mathrm{kN}/\mathrm{m}
$$

**Zug unten, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{+} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 174 \cdot 1.2} = 0.6878 \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug unten, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) &= k_d^{+} \cdot \tau_{cd} \cdot d_v^{+} \\
  &= 0.6878 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 174\,\mathrm{mm} \\
  &= 131.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d^{-} = h - z_{3,x,g} = 250\,\mathrm{mm} - 46\,\mathrm{mm} = 204\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{-} = d^{-} = 204\,\mathrm{mm}
$$

**Zug oben, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{-}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{-} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 204\,\mathrm{mm} = 223.5\,\mathrm{kN}/\mathrm{m}
$$

**Zug oben, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{-} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{-} = \frac{1}{1 + \varepsilon_v^{-} \cdot d^{-} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 204 \cdot 1.2} = 0.6527 \quad \left(d^{-}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug oben, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-}) &= k_d^{-} \cdot \tau_{cd} \cdot d_v^{-} \\
  &= 0.6527 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 204\,\mathrm{mm} \\
  &= 145.9\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = 0, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,max} &= \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right] \\
  &= \min\left[190.6\,\mathrm{kN}/\mathrm{m};\ 223.5\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 190.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,min} &= \min\left[V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+});\ V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-})\right] \\
  &= \min\left[131.1\,\mathrm{kN}/\mathrm{m};\ 145.9\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 131.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

### Plattenanalyse: Ohne x

### Ohne Bewehrung – x-Richtung

Keine Bewehrung in x-Richtung → Widerstand 0, nicht erfüllt.

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

**Bewehrungsquerschnitt über die Breite b** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{1508\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 250\,\mathrm{mm}} = 47\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
\begin{aligned}
  h_{Dist} &= \text{OK innere untere Lage} - \text{UK innere obere Lage} \\
  &= 208\,\mathrm{mm} - 42\,\mathrm{mm} \\
  &= 166\,\mathrm{mm}
\end{aligned}
$$

**Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte**

| Bewehrung | Richtung | Stahl | $\varnothing\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ | Randabstand [mm] | $z\ [\mathrm{mm}]$ | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1. Lage Grundbewehrung | y | B500B | $12$ | $150$ | $36$ | $214$ | $754$ |
| 4. Lage Grundbewehrung | y | B500B | $12$ | $150$ | $36$ | $36$ | $754$ |

### Querschnittsanalyse: Kastenträger

**Fläche und Schwerpunkt eines Polygons (Satz von Gauss)**

$$
A = \frac{1}{2} \sum_i c_i \qquad y_S = \frac{1}{6A} \sum_i (y_i + y_{i+1})\, c_i \qquad z_S = \frac{1}{6A} \sum_i (z_i + z_{i+1})\, c_i \qquad c_i = y_i\, z_{i+1} - y_{i+1}\, z_i
$$

**Trägheitsmomente eines Polygons, bezogen auf den Schwerpunkt**

$$
I_y = \frac{1}{12} \sum_i (z_i^2 + z_i z_{i+1} + z_{i+1}^2)\, c_i - A\, z_S^2\qquad I_z = \frac{1}{12} \sum_i (y_i^2 + y_i y_{i+1} + y_{i+1}^2)\, c_i - A\, y_S^2
$$

**Polygone des Querschnitts**

| Polygon | Material | liegt in | Ecken | $\pm A\ [\mathrm{mm}^2]$ | $y_S\ [\mathrm{mm}]$ | $z_S\ [\mathrm{mm}]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| Polygon 1 | C30/37 | – | $4$ | $480000$ | $400.0$ | $300.0$ |
| Aussparung 2 | – | Polygon 1 | $4$ | $-150000$ | $400.0$ | $300.0$ |

**Fläche des Bruttoquerschnitts**

$$
A = 330000\,\mathrm{mm}^{2}
$$

**Schwerpunkt, y**

$$
y_S = 400\,\mathrm{mm}
$$

**Schwerpunkt, z**

$$
z_S = 300\,\mathrm{mm}
$$

**Trägheitsmoment um y**

$$
I_y = 13275\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Trägheitsmoment um z**

$$
I_z = 22475\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Deviationsmoment**

$$
I_{yz} = 0\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Teilung einer Stablinie: gleiche Felder, auf die Länge gerundet**

$$
s = \frac{L}{m} \qquad m = \mathrm{runde}\left(\frac{L}{s_{gewählt}}\right)
$$

**Bewehrung**

| Element | $\text{Lage}\ [\mathrm{mm}]$ | Bewehrung | Stahl | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: |
| Stab 1 | $(760;\ 300)$ | $\varnothing 20$ | B500B | $314$ |
| Linie 1 | $(50;\ 50) \rightarrow (750;\ 50)$ | $6 \varnothing 16\ @\ 140.0\ (\text{gewählt } 150)$ | B500B | $1206$ |
| Linie 2 | $(60;\ 550) \rightarrow (740;\ 550)$ | $4 \varnothing 12\ @\ 136.0$ | B500B | $452$ |
| Linie 3 | $(40;\ 150) \rightarrow (40;\ 450)$ | verschmiert | B500B | $400$ |

**Stahlfläche der Bewehrung**

$$
A_{s,tot} = 2373\,\mathrm{mm}^{2}
$$

**Bügelquerschnitt je Länge einer Schubwand (n Schnitte)**

$$
\frac{A_{sw}}{s} = \frac{n \cdot \pi\, \varnothing^2 / 4}{s}
$$

**Schubwände**

| Wand | $\text{Achse}\ [\mathrm{mm}]$ | $l\ [\mathrm{mm}]$ | $b_w\ [\mathrm{mm}]$ | Bügel | $A_{sw}/s\ [\mathrm{mm}^2/\mathrm{m}]$ |
| :--- | :--- | ---: | ---: | :--- | ---: |
| Wand 1 | $(75;\ 75) \rightarrow (725;\ 75)$ | $650$ | $150$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |
| Wand 2 | $(725;\ 75) \rightarrow (725;\ 525)$ | $450$ | $150$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |
| Wand 3 | $(725;\ 525) \rightarrow (75;\ 525)$ | $650$ | $150$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |
| Wand 4 | $(75;\ 525) \rightarrow (75;\ 75)$ | $450$ | $150$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |

**Querkraft über die Federn der Wände**

$$
k_i = b_{w,i} \cdot l_i \qquad \sum_i k_i\, e_i e_i^T\, u = V \qquad V_i = k_i\, e_i \cdot u \qquad \Delta T = \sum_i V_i\, r_i
$$

**Torsion in den Zellen (Bredt, mehrzellig)**

$$
T - \Delta T = \sum_k 2 A_k\, q_k \qquad \oint_k \frac{q}{b_w}\, \mathrm{d}s = 2 A_k\, \theta
$$

**Widerstand je Länge einer Wand (Fachwerk)** *(SIA 262:2025, 4.3.3.4)*

$$
v_{Rd,s} = \frac{A_{sw}}{s}\, f_{sd} \cot\alpha \qquad v_{Rd,c} = b_w\, k_c\, f_{cd} \sin\alpha \cos\alpha \qquad v_{Rd} = \max_\alpha \min(v_{Rd,s};\ v_{Rd,c})
$$

**Druckfeld**

| Grenze | Wert |
| :--- | ---: |
| $\alpha_{min}$ | $30{}^{\circ}$ |
| $\alpha_{max}$ | $45{}^{\circ}$ |
| $k_c$ | $0.55$ |

**Schubwände und ihre Steifigkeit**

| Wand | $l\ [\mathrm{mm}]$ | $b_w\ [\mathrm{mm}]$ | $k = b_w l\ [\mathrm{mm}^2]$ | $A_{sw}/s\ [\mathrm{mm^2/m}]$ | Zelle |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Wand 1 | $650$ | $150$ | $97500$ | $524$ | 1 |
| Wand 2 | $450$ | $150$ | $67500$ | $524$ | 1 |
| Wand 3 | $650$ | $150$ | $97500$ | $524$ | 1 |
| Wand 4 | $450$ | $150$ | $67500$ | $524$ | 1 |

#### Feld

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| V\_y,Ed | $0.0$ | kN |
| V\_z,Ed | $250.0$ | kN |
| T\_Ed | $60.0$ | kNm |

**Versatz: Moment der Querkraftanteile um den Schwerpunkt**

$$
\Delta T = \sum_i V_i \cdot r_i = 0\,\mathrm{kNm}
$$

**Was die Zellen tragen**

$$
T_{Zellen} = T_{Ed} - \Delta T = 60\,\mathrm{kNm} - \left(0\,\mathrm{kNm}\right) = 60\,\mathrm{kNm}
$$

**Umlauf-Schubfluss der Zellen (Bredt)**

| Zelle | $A_k\ [\mathrm{mm}^2]$ | $q_k\ [\mathrm{kN/m}]$ |
| :--- | ---: | ---: |
| Zelle 1 | $292500$ | $102.6$ |

**Je Wand: Kraft aus der Querkraft, stärkster Schubfluss, Widerstand**

| Wand | $V_i\ [\mathrm{kN}]$ | $\vert q_{Ed}\vert \ [\mathrm{kN/m}]$ | $\alpha\ [{}^{\circ}]$ | $v_{Rd,s}\ [\mathrm{kN/m}]$ | $v_{Rd,c}\ [\mathrm{kN/m}]$ | $v_{Rd}\ [\mathrm{kN/m}]$ | $\alpha_{eff}$ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wand 1 | $0.0$ | $102.6$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $3.84$ |
| Wand 2 | $125.0$ | $380.3$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $1.04$ |
| Wand 3 | $0.0$ | $102.6$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $3.84$ |
| Wand 4 | $-125.0$ | $175.2$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $2.25$ |

Massgebend: Wand 2.

**Erfüllungsgrad**

$$
\alpha_{eff,V,\text{Feld}} = \frac{v_{Rd}}{q_{Ed}} = \frac{394.3\,\mathrm{kN}/\mathrm{m}}{380.3\,\mathrm{kN}/\mathrm{m}} = 1.04 \quad \Rightarrow \quad \text{erfüllt}
$$

**Längszugkraft aus dem Druckfeld der Wände, je Stück in seiner Mitte**

| Längszugkraft | Wert |  |
| :--- | ---: | :--- |
| $\Delta N = \sum \vert q\vert \, l \cot\alpha$ | $664.0$ | kN |
| $\Delta M_y = -\sum \Delta N_i (z_i - z_S)$ | $0.0$ | kNm |
| $\Delta M_z = -\sum \Delta N_i (y_i - y_S)$ | $-52.0$ | kNm |

#### Schief

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| V\_y,Ed | $100.0$ | kN |
| V\_z,Ed | $0.0$ | kN |
| T\_Ed | $0.0$ | kNm |

**Versatz: Moment der Querkraftanteile um den Schwerpunkt**

$$
\Delta T = \sum_i V_i \cdot r_i = 0\,\mathrm{kNm}
$$

**Was die Zellen tragen**

$$
T_{Zellen} = T_{Ed} - \Delta T = 0\,\mathrm{kNm} - \left(0\,\mathrm{kNm}\right) = 0\,\mathrm{kNm}
$$

**Umlauf-Schubfluss der Zellen (Bredt)**

| Zelle | $A_k\ [\mathrm{mm}^2]$ | $q_k\ [\mathrm{kN/m}]$ |
| :--- | ---: | ---: |
| Zelle 1 | $292500$ | $0.0$ |

**Je Wand: Kraft aus der Querkraft, stärkster Schubfluss, Widerstand**

| Wand | $V_i\ [\mathrm{kN}]$ | $\vert q_{Ed}\vert \ [\mathrm{kN/m}]$ | $\alpha\ [{}^{\circ}]$ | $v_{Rd,s}\ [\mathrm{kN/m}]$ | $v_{Rd,c}\ [\mathrm{kN/m}]$ | $v_{Rd}\ [\mathrm{kN/m}]$ | $\alpha_{eff}$ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wand 1 | $50.0$ | $76.9$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $5.13$ |
| Wand 2 | $0.0$ | $0.0$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $\infty$ |
| Wand 3 | $-50.0$ | $76.9$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $5.13$ |
| Wand 4 | $0.0$ | $0.0$ | $30$ | $394.3$ | $714.5$ | $394.3$ | $\infty$ |

Massgebend: Wand 1.

**Erfüllungsgrad**

$$
\alpha_{eff,V,\text{Schief}} = \frac{v_{Rd}}{q_{Ed}} = \frac{394.3\,\mathrm{kN}/\mathrm{m}}{76.9\,\mathrm{kN}/\mathrm{m}} = 5.13 \quad \Rightarrow \quad \text{erfüllt}
$$

**Längszugkraft aus dem Druckfeld der Wände, je Stück in seiner Mitte**

| Längszugkraft | Wert |  |
| :--- | ---: | :--- |
| $\Delta N = \sum \vert q\vert \, l \cot\alpha$ | $173.2$ | kN |
| $\Delta M_y = -\sum \Delta N_i (z_i - z_S)$ | $0.0$ | kNm |
| $\Delta M_z = -\sum \Delta N_i (y_i - y_S)$ | $0.0$ | kNm |

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

**Erfüllungsgrad bei fester Normalkraft und fester Richtung**

$$
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}
$$

**C30/37: Spannungsblock 0.85·x, Bemessungswerte**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{cd} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werte C30/37**

| Kennwert | Wert |
| :--- | ---: |
| $f_{cd}$ | $20\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $\varepsilon_{c1d}$ | $2\,\text{‰}$ |
| $\varepsilon_{c2d}$ | $3.5\,\text{‰}$ |

**B500B: bilineare Beziehung, Bemessungswerte** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Werte B500B**

| Kennwert | Wert |
| :--- | ---: |
| $f_{yd}$ | $435\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $f_{yd}^{-}$ | $435\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $E_s$ | $200000\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $\varepsilon_{ud}$ | $4.5\,\%$ |

**Reine Normalkraft**

| Grenze | Wert |
| :--- | ---: |
| reiner Zug, gleichmässig | $N_{Rd}^{+} = 1031.7\,\mathrm{kN}$ |
| reiner Druck, gleichmässig | $N_{Rd}^{-} = -7501.7\,\mathrm{kN}$ |

#### Feld

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| N\_Ed | $0.0$ | kN |
| M\_y,Ed | $300.0$ | kNm |
| M\_z,Ed | $0.0$ | kNm |
| ΔN aus Querkraft und Torsion | $664.0$ | kN |
| ΔM\_y | $0.0$ | kNm |
| ΔM\_z | $-52.0$ | kNm |
| N (nachgewiesen) | $664.0$ | kN |
| M\_y (nachgewiesen) | $300.0$ | kNm |
| M\_z (nachgewiesen) | $-52.0$ | kNm |

Bruchzustand: Zugrichtung n = (0.046; -0.999), -87.3° gegen die y-Achse. Die Nulllinie steht senkrecht zur Zugrichtung, 272.7 mm auf der Druckseite des Schwerpunkts.

**Dehnungsebene**

| $\varepsilon_0\ [\text{‰}]$ | $\kappa\ [\mathrm{1/m}]$ |
| ---: | ---: |
| $20.965$ | $0.07689$ |

**Kräfte im Bruchzustand -- Beton als Resultierende, Bewehrung je Element**

| Teil | $F\ [\mathrm{kN}]$ | $y\ [\mathrm{mm}]$ | $z\ [\mathrm{mm}]$ | $\varepsilon\ [\text{‰}]$ | $\sigma\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| C30/37 | $-323.4$ | $277.4$ | $587.0$ | – | – |
| Stab 1 | $136.6$ | $760.0$ | $300.0$ | $22.25$ | $435$ |
| Linie 1 | $524.5$ | $400.0$ | $50.0$ | $38.92 \ldots 41.41$ | $435$ |
| Linie 2 | $152.4$ | $439.3$ | $550.0$ | $1.04 \ldots 2.49$ | $207 \ldots 435$ |
| Linie 3 | $173.9$ | $40.0$ | $300.0$ | $8.88 \ldots 30.49$ | $435$ |

**Probe: Normalkraft**

$$
N_{Rd} = \sum F_i = 664\,\mathrm{kN}
$$

**Probe: Moment um y**

$$
M_{y,Rd} = -\sum F_i \cdot (z_i - z_S) = 185.9\,\mathrm{kNm}
$$

**Probe: Moment um z**

$$
M_{z,Rd} = -\sum F_i \cdot (y_i - y_S) = -32.2\,\mathrm{kNm}
$$

**Widerstand in der Richtung der Einwirkung**

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}} = \sqrt{\left(185.9\,\mathrm{kNm}\right)^{2} + \left(-32.2\,\mathrm{kNm}\right)^{2}} = 188.6\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{188.6\,\mathrm{kNm}}{304.5\,\mathrm{kNm}} = 0.62 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

#### Schief

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| N\_Ed | $-1500.0$ | kN |
| M\_y,Ed | $250.0$ | kNm |
| M\_z,Ed | $150.0$ | kNm |
| ΔN aus Querkraft und Torsion | $173.2$ | kN |
| ΔM\_y | $0.0$ | kNm |
| ΔM\_z | $0.0$ | kNm |
| N (nachgewiesen) | $-1326.8$ | kN |
| M\_y (nachgewiesen) | $250.0$ | kNm |
| M\_z (nachgewiesen) | $150.0$ | kNm |

Bruchzustand: Zugrichtung n = (-0.333; -0.943), -109.4° gegen die y-Achse. Die Nulllinie steht senkrecht zur Zugrichtung, 120.3 mm auf der Druckseite des Schwerpunkts.

**Dehnungsebene**

| $\varepsilon_0\ [\text{‰}]$ | $\kappa\ [\mathrm{1/m}]$ |
| ---: | ---: |
| $1.424$ | $0.01184$ |

**Kräfte im Bruchzustand -- Beton als Resultierende, Bewehrung je Element**

| Teil | $F\ [\mathrm{kN}]$ | $y\ [\mathrm{mm}]$ | $z\ [\mathrm{mm}]$ | $\varepsilon\ [\text{‰}]$ | $\sigma\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| C30/37 | $-1898.5$ | $545.7$ | $516.1$ | – | – |
| Stab 1 | $0.4$ | $760.0$ | $300.0$ | $0.01$ | $1$ |
| Linie 1 | $524.5$ | $400.0$ | $50.0$ | $2.84 \ldots 5.59$ | $435$ |
| Linie 2 | $-115.0$ | $470.8$ | $550.0$ | $-2.17 \ldots -0.56$ | $-434 \ldots -113$ |
| Linie 3 | $161.8$ | $40.0$ | $291.1$ | $1.27 \ldots 4.41$ | $255 \ldots 435$ |

**Probe: Normalkraft**

$$
N_{Rd} = \sum F_i = -1326.8\,\mathrm{kN}
$$

**Probe: Moment um y**

$$
M_{y,Rd} = -\sum F_i \cdot (z_i - z_S) = 571.6\,\mathrm{kNm}
$$

**Probe: Moment um z**

$$
M_{z,Rd} = -\sum F_i \cdot (y_i - y_S) = 343\,\mathrm{kNm}
$$

**Widerstand in der Richtung der Einwirkung**

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}} = \sqrt{\left(571.6\,\mathrm{kNm}\right)^{2} + \left(343\,\mathrm{kNm}\right)^{2}} = 666.6\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\text{Schief}} = \frac{M_{Rd}}{M_{Ed}} = \frac{666.6\,\mathrm{kNm}}{291.5\,\mathrm{kNm}} = 2.29 \quad \Rightarrow \quad \text{erfüllt}
$$

**Duktilität** *(SIA 262:2025, 4.1.4.2.5)*

$$
\frac{x}{d} \le \left(\frac{x}{d}\right)_{max}
$$

#### Zug unten

**Bezogene Druckzonenhöhe bei reiner Biegung**

$$
x/d = \frac{x}{d} = \frac{64.8\,\mathrm{mm}}{560.3\,\mathrm{mm}} = 0.116 \quad \le \quad 0.35 \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x/d,\text{Zug unten}} = \frac{\left(x/d\right)_{max}}{x/d} = \frac{0.35}{0.116} = 3.02
$$

#### Zug oben

**Bezogene Druckzonenhöhe bei reiner Biegung**

$$
x/d = \frac{x}{d} = \frac{47.4\,\mathrm{mm}}{554.1\,\mathrm{mm}} = 0.086 \quad \le \quad 0.35 \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x/d,\text{Zug oben}} = \frac{\left(x/d\right)_{max}}{x/d} = \frac{0.35}{0.086} = 4.09
$$

#### Zug links

**Bezogene Druckzonenhöhe bei reiner Biegung**

$$
x/d = \frac{x}{d} = \frac{109\,\mathrm{mm}}{807.7\,\mathrm{mm}} = 0.135 \quad \le \quad 0.35 \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x/d,\text{Zug links}} = \frac{\left(x/d\right)_{max}}{x/d} = \frac{0.35}{0.135} = 2.59
$$

#### Zug rechts

**Bezogene Druckzonenhöhe bei reiner Biegung**

$$
x/d = \frac{x}{d} = \frac{103.5\,\mathrm{mm}}{789.9\,\mathrm{mm}} = 0.131 \quad \le \quad 0.35 \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x/d,\text{Zug rechts}} = \frac{\left(x/d\right)_{max}}{x/d} = \frac{0.35}{0.131} = 2.67
$$

Massgebend: Zug links (kleinster Erfüllungsgrad).

**Spannung im ungerissenen Querschnitt**

$$
\sigma(y, z) = -\frac{M_y\,(I_z z' - I_{yz} y') + M_z\,(I_y y' - I_{yz} z')}{I_y I_z - I_{yz}^2}\qquad y' = y - y_S,\ z' = z - z_S
$$

**Sprödes Versagen** *(SIA 262:2025, 4.4.1.3)*

$$
M_{Rd}(N = 0) \ge M_{Riss} = f_{ct,eff} \cdot W
$$

#### Zug unten

Gezogenster Betonpunkt: y = 0 mm, z = 0 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.1.3)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.6/3} = 0.909 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.909 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.64\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot y' - I_z \cdot z'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right) - 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right)} \\
  &= 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.64\,\mathrm{N}/\mathrm{mm}^{2} \cdot 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3} = 116.7\,\mathrm{kNm}
$$

**Biegewiderstand bei N = 0 in dieser Richtung**

$$
M_{Rd} = 359.8\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,Riss,\text{Zug unten}} = \frac{M_{Rd}}{M_{Riss}} = \frac{359.8\,\mathrm{kNm}}{116.7\,\mathrm{kNm}} = 3.08
$$

#### Zug oben

Gezogenster Betonpunkt: y = 800 mm, z = 600 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.1.3)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.6/3} = 0.909 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.909 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.64\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_z \cdot z' - I_{yz} \cdot y'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{22475\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 300\,\mathrm{mm} - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 400\,\mathrm{mm}} \\
  &= 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.64\,\mathrm{N}/\mathrm{mm}^{2} \cdot 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3} = 116.7\,\mathrm{kNm}
$$

**Biegewiderstand bei N = 0 in dieser Richtung**

$$
M_{Rd} = 194.7\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,Riss,\text{Zug oben}} = \frac{M_{Rd}}{M_{Riss}} = \frac{194.7\,\mathrm{kNm}}{116.7\,\mathrm{kNm}} = 1.67
$$

#### Zug links

Gezogenster Betonpunkt: y = 0 mm, z = 0 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.1.3)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.8/3} = 0.882 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.882 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.56\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot z' - I_y \cdot y'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right) - 13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right)} \\
  &= 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.56\,\mathrm{N}/\mathrm{mm}^{2} \cdot 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3} = 143.8\,\mathrm{kNm}
$$

**Biegewiderstand bei N = 0 in dieser Richtung**

$$
M_{Rd} = 388.5\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,Riss,\text{Zug links}} = \frac{M_{Rd}}{M_{Riss}} = \frac{388.5\,\mathrm{kNm}}{143.8\,\mathrm{kNm}} = 2.70
$$

#### Zug rechts

Gezogenster Betonpunkt: y = 800 mm, z = 0 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.1.3)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.8/3} = 0.882 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.882 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.56\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_y \cdot y' - I_{yz} \cdot z'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 400\,\mathrm{mm} - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right)} \\
  &= 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.56\,\mathrm{N}/\mathrm{mm}^{2} \cdot 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3} = 143.8\,\mathrm{kNm}
$$

**Biegewiderstand bei N = 0 in dieser Richtung**

$$
M_{Rd} = 362.5\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,Riss,\text{Zug rechts}} = \frac{M_{Rd}}{M_{Riss}} = \frac{362.5\,\mathrm{kNm}}{143.8\,\mathrm{kNm}} = 2.52
$$

Massgebend: Zug oben (kleinster Erfüllungsgrad).

### Sprödes Versagen unter Zwängung

**Rissaktive Dicke: die kleinere Abmessung, höchstens 500 mm**

$$
t = \min\left[500\,\mathrm{mm};\ b;\ h\right] = \min\left[500\,\mathrm{mm};\ 800\,\mathrm{mm};\ 600\,\mathrm{mm}\right] = 500\,\mathrm{mm}
$$

**Beiwert für die rissaktive Dicke, C30/37** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot t} = \frac{1}{1 + 0.5 \cdot 0.5} = 0.8 \quad \left(t\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.8 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.32\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Risskraft des ganzen Querschnitts**

$$
N_{Riss} = A_c \cdot f_{ct,eff} = 330000\,\mathrm{mm}^{2} \cdot 2.32\,\mathrm{N}/\mathrm{mm}^{2} = 765.6\,\mathrm{kN}
$$

**Linie 3: verschmiert, als Stäbe mit 150 mm Teilung**

$$
\varnothing_{fikt} = \sqrt{\frac{4}{\pi} \cdot \frac{A_s}{l} \cdot s} = \sqrt{\frac{4}{\pi} \cdot \frac{400\,\mathrm{mm}^{2}}{300\,\mathrm{mm}} \cdot 150\,\mathrm{mm}} = 16\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,1} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{20\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 361\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,2} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{16\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 404\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,3} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{12\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 466\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,4} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{fikt}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{16\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 404\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Welche Stäbe welche Grenze haben**

| Grenze | Elemente | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | :--- | ---: |
| $\sigma_{s,adm,1}$ | Stab 1 | $361$ |
| $\sigma_{s,adm,2}$ | Linie 1 | $404$ |
| $\sigma_{s,adm,3}$ | Linie 2 | $466$ |
| $\sigma_{s,adm,4}$ | Linie 3 | $404$ |

**Aufnehmbare Risskraft**

$$
\begin{aligned}
  N_{s,adm} &= A_{s,1} \cdot \sigma_{s,adm,1} + A_{s,2} \cdot \sigma_{s,adm,2} + A_{s,3} \cdot \sigma_{s,adm,3} + A_{s,4} \cdot \sigma_{s,adm,4} \\
  &= 314\,\mathrm{mm}^{2} \cdot 361\,\mathrm{N}/\mathrm{mm}^{2} + 1206\,\mathrm{mm}^{2} \cdot 404\,\mathrm{N}/\mathrm{mm}^{2} + 452\,\mathrm{mm}^{2} \cdot 466\,\mathrm{N}/\mathrm{mm}^{2} + 400\,\mathrm{mm}^{2} \cdot 404\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 973.5\,\mathrm{kN} \quad \ge \quad N_{Riss} = 765.6\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,NR} = \frac{N_{s,adm}}{N_{Riss}} = \frac{973.5\,\mathrm{kN}}{765.6\,\mathrm{kN}} = 1.27
$$

### Zwängung auf Biegung

**Zwängung auf Biegung, je Stab** *(SIA 262:2025, 4.4.2)*

$$
\max_i \frac{\sigma_{s,i}(M_{s,adm})}{\sigma_{s,adm,i}} = 1\qquad M_{s,adm} \ge M_{Riss}
$$

**Spannung im ungerissenen Querschnitt**

$$
\sigma(y, z) = -\frac{M_y\,(I_z z' - I_{yz} y') + M_z\,(I_y y' - I_{yz} z')}{I_y I_z - I_{yz}^2}\qquad y' = y - y_S,\ z' = z - z_S
$$

**Rechenwahl**

$$
\varphi = 1 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{elastisch}
$$

**Wirksamer Elastizitätsmodul C30/37**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 1} = 16810\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Werkstoffgesetze im gerissenen Zustand, C30/37: Beton, elastisch ohne Zug**

$$
\sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Werkstoffgesetze im gerissenen Zustand: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Linie 3: verschmiert, als Stäbe mit 150 mm Teilung**

$$
\varnothing_{fikt} = \sqrt{\frac{4}{\pi} \cdot \frac{A_s}{l} \cdot s} = \sqrt{\frac{4}{\pi} \cdot \frac{400\,\mathrm{mm}^{2}}{300\,\mathrm{mm}} \cdot 150\,\mathrm{mm}} = 16\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,1} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{20\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 361\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,2} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{16\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 404\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,3} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{12\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 466\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,4} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{fikt}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{16\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 404\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Welche Stäbe welche Grenze haben**

| Grenze | Elemente | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | :--- | ---: |
| $\sigma_{s,adm,1}$ | Stab 1 | $361$ |
| $\sigma_{s,adm,2}$ | Linie 1 | $404$ |
| $\sigma_{s,adm,3}$ | Linie 2 | $466$ |
| $\sigma_{s,adm,4}$ | Linie 3 | $404$ |

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

#### Zug unten

Gezogenster Betonpunkt: y = 0 mm, z = 0 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.6/3} = 0.909 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.909 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.64\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot y' - I_z \cdot z'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right) - 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right)} \\
  &= 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.64\,\mathrm{N}/\mathrm{mm}^{2} \cdot 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3} = 116.7\,\mathrm{kNm}
$$

**Moment, bei dem der erste gezogene Stab σ\_s,adm erreicht**

$$
M_{s,adm} = 277.4\,\mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = -89.7^\circ \qquad \varepsilon_0 = 0.8065\,\text{‰} \qquad \kappa = 0.00481\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 277.4\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = 0\,\mathrm{kNm} \;\checkmark
$$

**An der Grenze: Linie 1 (y = 750 mm, z = 50 mm)**

$$
\sigma_s = 404\,\mathrm{N}/\mathrm{mm}^{2} = \sigma_{s,adm,2} = 404\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Zwängung auf Biegung**

$$
M_{s,adm} = 277.4\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 116.7\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,\text{Zug unten}} = \frac{M_{s,adm}}{M_{Riss}} = \frac{277.4\,\mathrm{kNm}}{116.7\,\mathrm{kNm}} = 2.38
$$

#### Zug oben

Gezogenster Betonpunkt: y = 800 mm, z = 600 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.6/3} = 0.909 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.909 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.64\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_z \cdot z' - I_{yz} \cdot y'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{22475\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 300\,\mathrm{mm} - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 400\,\mathrm{mm}} \\
  &= 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.64\,\mathrm{N}/\mathrm{mm}^{2} \cdot 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3} = 116.7\,\mathrm{kNm}
$$

**Moment, bei dem der erste gezogene Stab σ\_s,adm erreicht**

$$
M_{s,adm} = 151.1\,\mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = 89.5^\circ \qquad \varepsilon_0 = 1.0465\,\text{‰} \qquad \kappa = 0.0051\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = -151.1\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = 0\,\mathrm{kNm} \;\checkmark
$$

**An der Grenze: Linie 2 (y = 604 mm, z = 550 mm)**

$$
\sigma_s = 466\,\mathrm{N}/\mathrm{mm}^{2} = \sigma_{s,adm,3} = 466\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Zwängung auf Biegung**

$$
M_{s,adm} = 151.1\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 116.7\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,\text{Zug oben}} = \frac{M_{s,adm}}{M_{Riss}} = \frac{151.1\,\mathrm{kNm}}{116.7\,\mathrm{kNm}} = 1.30
$$

#### Zug links

Gezogenster Betonpunkt: y = 0 mm, z = 0 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.8/3} = 0.882 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.882 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.56\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot z' - I_y \cdot y'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right) - 13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right)} \\
  &= 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.56\,\mathrm{N}/\mathrm{mm}^{2} \cdot 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3} = 143.8\,\mathrm{kNm}
$$

**Moment, bei dem der erste gezogene Stab σ\_s,adm erreicht**

$$
M_{s,adm} = 248.3\,\mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = 172.1^\circ \qquad \varepsilon_0 = 0.7986\,\text{‰} \qquad \kappa = 0.00325\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 0\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = 248.3\,\mathrm{kNm} \;\checkmark
$$

**An der Grenze: Linie 3 (y = 40 mm, z = 441 mm)**

$$
\sigma_s = 404\,\mathrm{N}/\mathrm{mm}^{2} = \sigma_{s,adm,4} = 404\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Zwängung auf Biegung**

$$
M_{s,adm} = 248.3\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 143.8\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,\text{Zug links}} = \frac{M_{s,adm}}{M_{Riss}} = \frac{248.3\,\mathrm{kNm}}{143.8\,\mathrm{kNm}} = 1.73
$$

#### Zug rechts

Gezogenster Betonpunkt: y = 800 mm, z = 0 mm (C30/37).

**Beiwert für die Höhe in Biegerichtung** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.8/3} = 0.882 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.882 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.56\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_y \cdot y' - I_{yz} \cdot z'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 400\,\mathrm{mm} - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right)} \\
  &= 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.56\,\mathrm{N}/\mathrm{mm}^{2} \cdot 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3} = 143.8\,\mathrm{kNm}
$$

**Moment, bei dem der erste gezogene Stab σ\_s,adm erreicht**

$$
M_{s,adm} = 208.2\,\mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = 8.4^\circ \qquad \varepsilon_0 = 0.7479\,\text{‰} \qquad \kappa = 0.00297\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 0\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = -208.2\,\mathrm{kNm} \;\checkmark
$$

**An der Grenze: Stab 1 (y = 760 mm, z = 300 mm)**

$$
\sigma_s = 361\,\mathrm{N}/\mathrm{mm}^{2} = \sigma_{s,adm,1} = 361\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Zwängung auf Biegung**

$$
M_{s,adm} = 208.2\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 143.8\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,ZB,\text{Zug rechts}} = \frac{M_{s,adm}}{M_{Riss}} = \frac{208.2\,\mathrm{kNm}}{143.8\,\mathrm{kNm}} = 1.45
$$

Massgebend: Zug oben (kleinster Erfüllungsgrad).

### Stahlspannung unter quasi-ständiger Einwirkung

**Rechenwahl**

$$
\varphi = 0 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{elastisch}
$$

**Linie 3: verschmiert, als Stäbe mit 150 mm Teilung**

$$
\varnothing_{fikt} = \sqrt{\frac{4}{\pi} \cdot \frac{A_s}{l} \cdot s} = \sqrt{\frac{4}{\pi} \cdot \frac{400\,\mathrm{mm}^{2}}{300\,\mathrm{mm}} \cdot 150\,\mathrm{mm}} = 16\,\mathrm{mm}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,1} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{20\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 361\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,2} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{16\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 404\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,3} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{12\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 466\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Zulässige Stahlspannung (Rissbreite w\_nom = 0.5 mm)** *(SIA 262:2025, 4.4.2)*

$$
\begin{aligned}
  \sigma_{s,adm,4} &= \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{fikt}}};\ f_{yk}\right] \\
  &= \min\left[\sqrt{\frac{9 \cdot 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} \cdot 0.5\,\mathrm{mm}}{16\,\mathrm{mm}}};\ 500\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 404\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

**Welche Stäbe welche Grenze haben**

| Grenze | Elemente | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | :--- | ---: |
| $\sigma_{s,adm,1}$ | Stab 1 | $361$ |
| $\sigma_{s,adm,2}$ | Linie 1 | $404$ |
| $\sigma_{s,adm,3}$ | Linie 2 | $466$ |
| $\sigma_{s,adm,4}$ | Linie 3 | $404$ |

#### Welche Werte angesetzt werden

**Wirksamer Elastizitätsmodul C30/37**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 0} = 33620\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Werkstoffgesetze im Gebrauchszustand, C30/37: Beton, elastisch ohne Zug**

$$
\sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Werkstoffgesetze im Gebrauchszustand: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

#### Quasi-ständiger Lastfall – Feld (60 %)

**Einwirkung**

$$
N_{Ed,\text{quasi-ständig}} = 0.0\ \mathrm{kN} \qquad M_{y,Ed,\text{quasi-ständig}} = 180.0\ \mathrm{kNm} \qquad M_{z,Ed,\text{quasi-ständig}} = 0.0\ \mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = -89.7^\circ \qquad \varepsilon_0 = 0.5609\,\text{‰} \qquad \kappa = 0.0028\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = 0\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 180\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = 0\,\mathrm{kNm} \;\checkmark
$$

**Gezogene Bewehrung, je Element der ungünstigste Stab**

| Element | $\varepsilon_s\ [‰]$ | $\sigma_s\ [\mathrm{N/mm^2}]$ | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| Stab 1 | $0.566$ | $113$ | $361$ |
| Linie 1 | $1.266$ | $253$ | $404$ |
| Linie 3 | $0.950$ | $190$ | $404$ |

Massgebend: Linie 1 (y = 750 mm, z = 50 mm).

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_s = 253\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm,2} = 404\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,\text{Feld (60 \%)}} = \frac{\sigma_{s,adm,2}}{\sigma_s} = \frac{404\,\mathrm{N}/\mathrm{mm}^{2}}{253\,\mathrm{N}/\mathrm{mm}^{2}} = 1.60
$$

#### Quasi-ständiger Lastfall – Schief (60 %)

**Einwirkung**

$$
N_{Ed,\text{quasi-ständig}} = -900.0\ \mathrm{kN} \qquad M_{y,Ed,\text{quasi-ständig}} = 150.0\ \mathrm{kNm} \qquad M_{z,Ed,\text{quasi-ständig}} = 90.0\ \mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = -110.9^\circ \qquad \varepsilon_0 = -0.0703\,\text{‰} \qquad \kappa = 0.00041\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = -900\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 150\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = 90\,\mathrm{kNm} \;\checkmark
$$

**Gezogene Bewehrung, je Element der ungünstigste Stab**

| Element | $\varepsilon_s\ [‰]$ | $\sigma_s\ [\mathrm{N/mm^2}]$ | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| Linie 1 | $0.076$ | $15$ | $404$ |
| Linie 3 | $0.036$ | $7$ | $404$ |

Massgebend: Linie 1 (y = 50 mm, z = 50 mm).

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_s = 15\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm,2} = 404\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,\text{Schief (60 \%)}} = \frac{\sigma_{s,adm,2}}{\sigma_s} = \frac{404\,\mathrm{N}/\mathrm{mm}^{2}}{15\,\mathrm{N}/\mathrm{mm}^{2}} = 26.63
$$

#### Quasi-ständiger Lastfall – Dauer

**Einwirkung**

$$
N_{Ed,\text{quasi-ständig}} = -300.0\ \mathrm{kN} \qquad M_{y,Ed,\text{quasi-ständig}} = 120.0\ \mathrm{kNm} \qquad M_{z,Ed,\text{quasi-ständig}} = 60.0\ \mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = -102.7^\circ \qquad \varepsilon_0 = 0.1279\,\text{‰} \qquad \kappa = 0.001\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = -300\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 120\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = 60\,\mathrm{kNm} \;\checkmark
$$

**Gezogene Bewehrung, je Element der ungünstigste Stab**

| Element | $\varepsilon_s\ [‰]$ | $\sigma_s\ [\mathrm{N/mm^2}]$ | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| Stab 1 | $0.049$ | $10$ | $361$ |
| Linie 1 | $0.449$ | $90$ | $404$ |
| Linie 3 | $0.344$ | $69$ | $404$ |

Massgebend: Linie 1 (y = 50 mm, z = 50 mm).

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_s = 90\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm,2} = 404\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,\text{Dauer}} = \frac{\sigma_{s,adm,2}}{\sigma_s} = \frac{404\,\mathrm{N}/\mathrm{mm}^{2}}{90\,\mathrm{N}/\mathrm{mm}^{2}} = 4.50
$$

### Stahlspannung unter häufiger Einwirkung

**Rechenwahl**

$$
\varphi = 0 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{elastisch}
$$

**Zulässige Stahlspannung** *(SIA 262:2025, Tabelle 17)*

$$
\sigma_{s,adm} = f_{yd} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 435\,\mathrm{N}/\mathrm{mm}^{2} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 355\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

**Wirksamer Elastizitätsmodul C30/37**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 0} = 33620\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Werkstoffgesetze im Gebrauchszustand, C30/37: Beton, elastisch ohne Zug**

$$
\sigma_c = \max\left[E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right] \quad f_{ck} = 30\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Werkstoffgesetze im Gebrauchszustand: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

#### Häufiger Lastfall – Häufig schief

**Einwirkung**

$$
N_{Ed,häufig} = -500.0\ \mathrm{kN} \qquad M_{y,Ed,häufig} = 200.0\ \mathrm{kNm} \qquad M_{z,Ed,häufig} = 100.0\ \mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = -102.7^\circ \qquad \varepsilon_0 = 0.2131\,\text{‰} \qquad \kappa = 0.00167\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = -500\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 200\,\mathrm{kNm} \;\checkmark \qquad M_{z,int} = 100\,\mathrm{kNm} \;\checkmark
$$

**Gezogene Bewehrung, je Element der ungünstigste Stab**

| Element | $\varepsilon_s\ [‰]$ | $\sigma_s\ [\mathrm{N/mm^2}]$ | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| Stab 1 | $0.081$ | $16$ | $355$ |
| Linie 1 | $0.748$ | $150$ | $355$ |
| Linie 3 | $0.574$ | $115$ | $355$ |

Massgebend: Linie 1 (y = 50 mm, z = 50 mm).

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_s = 150\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,\text{Häufig schief}} = \frac{\sigma_{s,adm}}{\sigma_s} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2}}{150\,\mathrm{N}/\mathrm{mm}^{2}} = 2.37
$$

### Querschnittsanalyse: Stütze

**Fläche und Schwerpunkt eines Polygons (Satz von Gauss)**

$$
A = \frac{1}{2} \sum_i c_i \qquad y_S = \frac{1}{6A} \sum_i (y_i + y_{i+1})\, c_i \qquad z_S = \frac{1}{6A} \sum_i (z_i + z_{i+1})\, c_i \qquad c_i = y_i\, z_{i+1} - y_{i+1}\, z_i
$$

**Trägheitsmomente eines Polygons, bezogen auf den Schwerpunkt**

$$
I_y = \frac{1}{12} \sum_i (z_i^2 + z_i z_{i+1} + z_{i+1}^2)\, c_i - A\, z_S^2\qquad I_z = \frac{1}{12} \sum_i (y_i^2 + y_i y_{i+1} + y_{i+1}^2)\, c_i - A\, y_S^2
$$

**Polygone des Querschnitts**

| Polygon | Material | liegt in | Ecken | $\pm A\ [\mathrm{mm}^2]$ | $y_S\ [\mathrm{mm}]$ | $z_S\ [\mathrm{mm}]$ |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| Polygon 1 | C30/37 | – | $4$ | $160000$ | $200.0$ | $200.0$ |

**Fläche des Bruttoquerschnitts**

$$
A = 160000\,\mathrm{mm}^{2}
$$

**Schwerpunkt, y**

$$
y_S = 200\,\mathrm{mm}
$$

**Schwerpunkt, z**

$$
z_S = 200\,\mathrm{mm}
$$

**Trägheitsmoment um y**

$$
I_y = 2133.3\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Trägheitsmoment um z**

$$
I_z = 2133.3\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Deviationsmoment**

$$
I_{yz} = 0\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Teilung einer Stablinie: gleiche Felder, auf die Länge gerundet**

$$
s = \frac{L}{m} \qquad m = \mathrm{runde}\left(\frac{L}{s_{gewählt}}\right)
$$

**Bewehrung**

| Element | $\text{Lage}\ [\mathrm{mm}]$ | Bewehrung | Stahl | $A_s\ [\mathrm{mm}^2]$ |
| :--- | :--- | :--- | ---: | ---: |
| Linie 1 | $(50;\ 50) \rightarrow (350;\ 50)$ | $3 \varnothing 20\ @\ 150.0$ | B500B | $942$ |
| Linie 2 | $(50;\ 350) \rightarrow (350;\ 350)$ | $3 \varnothing 20\ @\ 150.0$ | B500B | $942$ |

**Stahlfläche der Bewehrung**

$$
A_{s,tot} = 1885\,\mathrm{mm}^{2}
$$

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

**Erfüllungsgrad bei fester Normalkraft und fester Richtung**

$$
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}
$$

**C30/37: Parabel-Rechteck-Beziehung, charakteristische Werte** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Krümmungsbeiwert mit charakteristischer Festigkeit** *(SIA 262:2025, 4.2.1.6)*

$$
k_{\sigma,k} = \frac{E_{cd}}{400 \cdot f_{ck}} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}} = 2.802
$$

**Werte C30/37**

| Kennwert | Wert |
| :--- | ---: |
| $f_{ck}$ | $30\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $\varepsilon_{c1d}$ | $2\,\text{‰}$ |
| $\varepsilon_{c2d}$ | $3.5\,\text{‰}$ |

**B500B: bilineare Beziehung, charakteristische Werte** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yk}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yk}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Werte B500B**

| Kennwert | Wert |
| :--- | ---: |
| $f_{yk}$ | $500\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $f_{yk}^{-}$ | $500\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $E_s$ | $200000\,\mathrm{N}/\mathrm{mm}^{2}$ |
| $\varepsilon_{ud}$ | $4.5\,\%$ |

**Reine Normalkraft**

| Grenze | Wert |
| :--- | ---: |
| reiner Zug, gleichmässig | $N_{Rd}^{+} = 942.5\,\mathrm{kN}$ |
| reiner Druck, gleichmässig | $N_{Rd}^{-} = -5497.4\,\mathrm{kN}$ |

#### Druck

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| N\_Ed | $-2500.0$ | kN |
| M\_y,Ed | $120.0$ | kNm |

Bruchzustand: Zugrichtung n = (0.000; -1.000), -90.0° gegen die y-Achse. Die Nulllinie steht senkrecht zur Zugrichtung, 36.0 mm auf der Zugseite des Schwerpunkts.

**Dehnungsebene**

| $\varepsilon_0\ [\text{‰}]$ | $\kappa\ [\mathrm{1/m}]$ |
| ---: | ---: |
| $-0.534$ | $0.01483$ |

**Kräfte im Bruchzustand -- Beton als Resultierende, Bewehrung je Element**

| Teil | $F\ [\mathrm{kN}]$ | $y\ [\mathrm{mm}]$ | $z\ [\mathrm{mm}]$ | $\varepsilon\ [\text{‰}]$ | $\sigma\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| C30/37 | $-2375.7$ | $200.0$ | $298.8$ | – | – |
| Linie 1 | $318.7$ | $200.0$ | $50.0$ | $1.69$ | $338$ |
| Linie 2 | $-443.0$ | $200.0$ | $350.0$ | $-2.76$ | $-500$ |

**Probe: Normalkraft**

$$
N_{Rd} = \sum F_i = -2500\,\mathrm{kN}
$$

**Probe: Moment um y**

$$
M_{y,Rd} = -\sum F_i \cdot (z_i - z_S) = 348.9\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\text{Druck}} = \frac{M_{Rd}}{M_{Ed}} = \frac{348.9\,\mathrm{kNm}}{120\,\mathrm{kNm}} = 2.91 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Zug

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| N\_Ed | $400.0$ | kN |
| M\_y,Ed | $0.0$ | kNm |

**Erfüllungsgrad**

$$
\alpha_{eff,\text{Zug}} = \frac{N_{Rd}^{+}}{N_{Ed}} = \frac{942.5\,\mathrm{kN}}{400\,\mathrm{kN}} = 2.36 \quad \Rightarrow \quad \text{erfüllt}
$$

### Sprödes Versagen unter Zwängung

**Rissaktive Dicke: die kleinere Abmessung**

$$
t = \min\left[b;\ h\right] = \min\left[400\,\mathrm{mm};\ 400\,\mathrm{mm}\right] = 400\,\mathrm{mm}
$$

**Beiwert für die rissaktive Dicke, C30/37** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot t} = \frac{1}{1 + 0.5 \cdot 0.4} = 0.833 \quad \left(t\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm} = 0.833 \cdot 2.9\,\mathrm{N}/\mathrm{mm}^{2} = 2.42\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Risskraft des ganzen Querschnitts**

$$
N_{Riss} = A_c \cdot f_{ct,eff} = 160000\,\mathrm{mm}^{2} \cdot 2.42\,\mathrm{N}/\mathrm{mm}^{2} = 386.7\,\mathrm{kN}
$$

**Zulässige Stahlspannung (normale Anforderung)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm} = f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Aufnehmbare Risskraft**

$$
\begin{aligned}
  N_{s,adm} &= A_s \cdot \sigma_{s,adm} \\
  &= 1885\,\mathrm{mm}^{2} \cdot 500\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 942.5\,\mathrm{kN} \quad \ge \quad N_{Riss} = 386.7\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,NR} = \frac{N_{s,adm}}{N_{Riss}} = \frac{942.5\,\mathrm{kN}}{386.7\,\mathrm{kN}} = 2.44
$$

### Stahlspannung unter quasi-ständiger Einwirkung

**Rechenwahl**

$$
\varphi = 0 \qquad \text{charakteristisch}\ f_{ck},\ f_{yk} \qquad \text{Präzise ohne Vereinfachung}
$$

**Zulässige Stahlspannung (normale Anforderung)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm} = f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Welche Werte angesetzt werden

**Wirksamer Elastizitätsmodul C30/37**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 0} = 33620\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{ck}}\right) = \max\left(1;\ \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 2.8
$$

**Werkstoffgesetze im Gebrauchszustand, C30/37: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze im Gebrauchszustand: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yk}\right] \quad f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Wie die Dehnungsebene gefunden wird

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

#### Quasi-ständiger Lastfall – Dauer

**Einwirkung**

$$
N_{Ed,\text{quasi-ständig}} = -600.0\ \mathrm{kN} \qquad M_{y,Ed,\text{quasi-ständig}} = 80.0\ \mathrm{kNm}
$$

**Gefundene Dehnungsebene: Zugrichtung, Dehnung im Schwerpunkt, Krümmung**

$$
\psi = -90.0^\circ \qquad \varepsilon_0 = -0.0536\,\text{‰} \qquad \kappa = 0.0014\,\mathrm{m}^{-1}
$$

**Probe: die Ebene erzeugt die Einwirkung**

$$
N_{int} = -600\,\mathrm{kN} \;\checkmark \qquad M_{y,int} = 80\,\mathrm{kNm} \;\checkmark
$$

**Gezogene Bewehrung, je Element der ungünstigste Stab**

| Element | $\varepsilon_s\ [‰]$ | $\sigma_s\ [\mathrm{N/mm^2}]$ | $\sigma_{s,adm}\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: |
| Linie 1 | $0.156$ | $31$ | $500$ |

Massgebend: Linie 1 (y = 50 mm, z = 50 mm).

**Grösste Zugspannung in der Bewehrung**

$$
\sigma_s = 31\,\mathrm{N}/\mathrm{mm}^{2} \quad \le \quad \sigma_{s,adm} = 500\,\mathrm{N}/\mathrm{mm}^{2} \quad \Rightarrow \quad \text{erfüllt}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\sigma,w,\text{Dauer}} = \frac{\sigma_{s,adm}}{\sigma_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{31\,\mathrm{N}/\mathrm{mm}^{2}} = 16.04
$$

### Knicken

**Ungewollte Ausmitte – allgemein** *(SIA 262:2025, 4.3.7)*

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \qquad e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

**Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}\right)
$$

#### Verformung

**Rechenwahl – Verformung (e\_2d)**

$$
\varphi = 1.5 \qquad \text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad \text{Präzise ohne Vereinfachung}
$$

**Wirksamer Elastizitätsmodul C30/37**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 1.5} = 13448\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{13448\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 1.68
$$

**Werkstoffgesetze – Verformung, C30/37: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze – Verformung: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yd}\right] \quad f_{yd} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Widerstand

**Rechenwahl – Widerstand (N\_Rd)**

$$
\text{Bemessungswerte}\ f_{cd},\ f_{yd} \qquad 0.85 \cdot x\text{-Vereinfachung}
$$

**Werkstoffgesetze – Widerstand, C30/37: Beton, Spannungsblock 0.85·x**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{cd} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werkstoffgesetze – Widerstand: Stahl**

$$
\sigma_s = \min\left[E_s \cdot \varepsilon_s;\ f_{yd}\right] \quad f_{yd} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

#### Knicken – Stütze, Zug unten

**Einwirkung und System**

$$
N_{Ed} = -1500\,\mathrm{kN} \qquad M_{Ed,1} = 30\,\mathrm{kNm} \qquad l = 4\,\mathrm{m} \qquad l_{cr} = 4\,\mathrm{m}
$$

**Schiefstellung** *(SIA 262:2025, 4.3.7)*

$$
\begin{aligned}
  \alpha_i &= \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= \min\left[\max\left(\frac{0.01}{\sqrt{4}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= 0.005 \quad \left(l\ \text{in}\ \mathrm{m}\right)
\end{aligned}
$$

**Ungewollte Ausmitte** *(SIA 262:2025, 4.3.7)*

$$
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right) = \max\left(\frac{350\,\mathrm{mm}}{30};\ \frac{0.005 \cdot 4\,\mathrm{m}}{2}\right) = 11.7\,\mathrm{mm}
$$

**Gewollte Ausmitte**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| = \left|\frac{30\,\mathrm{kNm}}{-1500\,\mathrm{kN}}\right| = 20\,\mathrm{mm}
$$

**Das Verfahren** *(SIA 262:2025, 4.3.7)*

$$
e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}^{(k-1)}\right)
$$

**Ausmitten-Iteration bei N\_Ed = 1500.0 kN**

| $k$ | $e_{2d}^{(k-1)}\ [\mathrm{mm}]$ | $M_{Ed,II}^{(k)}\ [\mathrm{kNm}]$ | $\chi^{(k)}\ [\mathrm{m}^{-1}]$ | $e_{2d}^{(k)}\ [\mathrm{mm}]$ |
| ---: | ---: | ---: | ---: | ---: |
| $1$ | $0.00$ | $47.50$ | $0.00126$ | $2.05$ |
| $2$ | $2.05$ | $50.57$ | $0.00134$ | $2.18$ |
| $3$ | $2.18$ | $50.77$ | $0.00135$ | $2.19$ |
| $4$ | $2.19$ | $50.78$ | $0.00135$ | $2.19$ |
| $5$ | $2.19$ | $50.78$ | $0.00135$ | $2.19$ |

**Probe: die gefundene Ebene erzeugt die Schnittgrössen**

$$
\varepsilon_m = -0.536\,\text{‰} \qquad \chi = 0.00135\,\mathrm{m}^{-1} \qquad N_{int} = -1500\,\mathrm{kN} \;\checkmark \qquad M_{int} = 50.8\,\mathrm{kNm} \;\checkmark
$$

**Querschnitt am verformten System**

$$
M_{Rd}(N_{Ed}) = 276.3\,\mathrm{kNm} \quad \ge \quad M_{Ed,II} = 50.8\,\mathrm{kNm}
$$

**Grenzkraft des Stabes**

$$
N_{Rd,K} = 3032.2\,\mathrm{kN} \quad \ge \quad \left|N_{Ed}\right| = 1500\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,K,\text{Stütze}} = \frac{N_{Rd,K}}{\left|N_{Ed}\right|} = \frac{3032.2\,\mathrm{kN}}{1500\,\mathrm{kN}} = 2.02 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Knicken – Seitlich, Zug links

**Einwirkung und System**

$$
N_{Ed} = -1200\,\mathrm{kN} \qquad M_{Ed,1} = 10\,\mathrm{kNm} \qquad l = 5\,\mathrm{m} \qquad l_{cr} = 3.5\,\mathrm{m}
$$

**Schiefstellung** *(SIA 262:2025, 4.3.7)*

$$
\begin{aligned}
  \alpha_i &= \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= \min\left[\max\left(\frac{0.01}{\sqrt{5}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \\
  &= 0.00447 \quad \left(l\ \text{in}\ \mathrm{m}\right)
\end{aligned}
$$

**Ungewollte Ausmitte** *(SIA 262:2025, 4.3.7)*

$$
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right) = \max\left(\frac{350\,\mathrm{mm}}{30};\ \frac{0.00447 \cdot 3.5\,\mathrm{m}}{2}\right) = 11.7\,\mathrm{mm}
$$

**Gewollte Ausmitte**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| = \left|\frac{10\,\mathrm{kNm}}{-1200\,\mathrm{kN}}\right| = 8.3\,\mathrm{mm}
$$

**Das Verfahren** *(SIA 262:2025, 4.3.7)*

$$
e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}^{(k-1)}\right)
$$

**Ausmitten-Iteration bei N\_Ed = 1200.0 kN**

| $k$ | $e_{2d}^{(k-1)}\ [\mathrm{mm}]$ | $M_{Ed,II}^{(k)}\ [\mathrm{kNm}]$ | $\chi^{(k)}\ [\mathrm{m}^{-1}]$ | $e_{2d}^{(k)}\ [\mathrm{mm}]$ |
| ---: | ---: | ---: | ---: | ---: |
| $1$ | $0.00$ | $24.00$ | $0.00066$ | $0.82$ |
| $2$ | $0.82$ | $24.98$ | $0.00068$ | $0.85$ |
| $3$ | $0.85$ | $25.02$ | $0.00069$ | $0.85$ |
| $4$ | $0.85$ | $25.02$ | $0.00069$ | $0.85$ |

**Probe: die gefundene Ebene erzeugt die Schnittgrössen**

$$
\varepsilon_m = -0.4191\,\text{‰} \qquad \chi = 0.00069\,\mathrm{m}^{-1} \qquad N_{int} = -1200\,\mathrm{kN} \;\checkmark \qquad M_{int} = 25\,\mathrm{kNm} \;\checkmark
$$

**Querschnitt am verformten System**

$$
M_{Rd}(N_{Ed}) = 232.4\,\mathrm{kNm} \quad \ge \quad M_{Ed,II} = 25\,\mathrm{kNm}
$$

**Grenzkraft des Stabes**

$$
N_{Rd,K} = 3266.6\,\mathrm{kN} \quad \ge \quad \left|N_{Ed}\right| = 1200\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,K,\text{Seitlich}} = \frac{N_{Rd,K}}{\left|N_{Ed}\right|} = \frac{3266.6\,\mathrm{kN}}{1200\,\mathrm{kN}} = 2.72 \quad \Rightarrow \quad \text{erfüllt}
$$

### Grundbruch: Hang

**Reibungswinkel, charakteristisch**

$$
\varphi_k = 33{}^{\circ}
$$

**Partialfaktor des Reibungswinkels** *(SIA 267:2013, 5.3.2.2)*

$$
\gamma_{\varphi} = 1.2
$$

**Reibungswinkel, Bemessungswert** *(SIA 267:2013, 5.3.2.1)*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 33{}^{\circ}}{1.2}\right) = 28.42{}^{\circ}
$$

**Kohäsion, charakteristisch**

$$
c_k = 6\,\mathrm{kPa}
$$

**Partialfaktor der Kohäsion**

$$
\gamma_c = 1.5
$$

**Kohäsion, Bemessungswert**

$$
c_{eff} = \frac{c_k}{\gamma_c} = \frac{6\,\mathrm{kPa}}{1.5} = 4\,\mathrm{kPa}
$$

**Raumlast des Bodens**

$$
\gamma = 21\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Wassers**

$$
\gamma_w = 10\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Bodens unter Auftrieb**

$$
\gamma' = \gamma - \gamma_w = 21\,\mathrm{kN}/\mathrm{m}^{3} - 10\,\mathrm{kN}/\mathrm{m}^{3} = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Bemessungslast neben dem Fundament**

$$
q_{Ed} = 10\,\mathrm{kPa}
$$

**Breite des Fundaments**

$$
b = 1.6\,\mathrm{m}
$$

**Länge des Fundaments**

$$
L = 4\,\mathrm{m}
$$

**Tiefe des höchsten Grundwasserspiegels unter Terrain**

$$
t_1 = 2\,\mathrm{m}
$$

**Tiefe der Sohle unter Terrain**

$$
t = 0.8\,\mathrm{m}
$$

**Neigung der Sohle**

$$
\alpha = 5{}^{\circ}
$$

**Neigung des Geländes**

$$
\beta = 15{}^{\circ}
$$

### Grundbruch

**Erweiterte Tragfähigkeitsformel** *(Kap. 9.2.10)*

$$
\sigma_f = c \, N_c s_c d_c i_c g_c b_c + \sigma_{v,0} \, N_q s_q d_q i_q g_q b_q + \tfrac{1}{2} \gamma_G \, b \, N_{\gamma} s_{\gamma} d_{\gamma} i_{\gamma} g_{\gamma} b_{\gamma} \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

#### Tragfähigkeitsfaktoren

**Tragfähigkeitsfaktor der seitlichen Auflast** *(Kap. 9.2.6)*

$$
N_q = e^{\pi \tan \varphi_{eff}} \cdot \tan^{2}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) = e^{\pi \tan 28.42{}^{\circ}} \cdot \tan^{2}\left(45^\circ + \frac{28.42{}^{\circ}}{2}\right) = 15.42
$$

**Tragfähigkeitsfaktor der Kohäsion** *(Kap. 9.2.6)*

$$
N_c = \frac{N_q - 1}{\tan \varphi_{eff}} = \frac{15.42 - 1}{\tan 28.42{}^{\circ}} = 26.64
$$

**Tragfähigkeitsfaktor des Gleitkörpergewichts** *(Kap. 9.2.6)*

$$
N_{\gamma} = 1.8 \cdot \left(N_q - 1\right) \cdot \tan \varphi_{eff} = 1.8 \cdot \left(15.42 - 1\right) \cdot \tan 28.42{}^{\circ} = 14.05
$$

#### Gleitkörper und Grundwasser

**Reichweite des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  L_{Gl} &= b \cdot \tan\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \cdot e^{\frac{\pi}{2} \tan \varphi_{eff}} \\
  &= 1.6\,\mathrm{m} \cdot \tan\left(45^\circ + \frac{28.42{}^{\circ}}{2}\right) \cdot e^{\frac{\pi}{2} \tan 28.42{}^{\circ}} \\
  &= 6.28\,\mathrm{m}
\end{aligned}
$$

**Tiefe des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  H_{Gl} &= b \cdot \frac{\cos \varphi_{eff}}{2 \cos\left(45^\circ + \frac{\varphi_{eff}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \tan \varphi_{eff}} \\
  &= 1.6\,\mathrm{m} \cdot \frac{\cos 28.42{}^{\circ}}{2 \cos\left(45^\circ + \frac{28.42{}^{\circ}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{28.42{}^{\circ}}{2}\right) \tan 28.42{}^{\circ}} \\
  &= 2.4\,\mathrm{m}
\end{aligned}
$$

**Überlagerung auf Höhe der Sohle, Grundwasser tiefer** *(Kap. 9.2.8)*

$$
\sigma_{v,0} = \gamma \cdot t + q_{Ed} = 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 0.8\,\mathrm{m} + 10\,\mathrm{kPa} = 26.8\,\mathrm{kPa}
$$

**Abstand des Grundwassers unter der Sohle** *(Kap. 9.2.8)*

$$
T = t_1 - t = 2\,\mathrm{m} - 0.8\,\mathrm{m} = 1.2\,\mathrm{m}
$$

**Grundwasser im Gleitkörper, unter der Sohle**

$$
T = 1.2\,\mathrm{m} \quad < \quad H_{Gl} = 2.4\,\mathrm{m}
$$

> **Annahme:** Der Grundwasserspiegel liegt im Gleitkörper (T \< H). Das Kapitel verlangt dafür eine Stabilitätsberechnung; gerechnet wird mit γ' wie in Lage 2, auf der sicheren Seite.

**Raumlast im Gleitkörper, unter Wasser** *(Kap. 9.2.8)*

$$
\gamma_G = \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

#### Form, Tiefe, Gelände und Sohle

**Formfaktor der Kohäsion** *(Kap. 9.2.12)*

$$
s_c = 1 + \frac{b}{L} \cdot \frac{N_q}{N_c} = 1 + \frac{1.6\,\mathrm{m}}{4\,\mathrm{m}} \cdot \frac{15.42}{26.64} = 1.23
$$

**Formfaktor der seitlichen Auflast** *(Kap. 9.2.12)*

$$
s_q = 1 + \frac{b}{L} \cdot \tan \varphi_{eff} = 1 + \frac{1.6\,\mathrm{m}}{4\,\mathrm{m}} \cdot \tan 28.42{}^{\circ} = 1.22
$$

**Formfaktor des Gleitkörpergewichts** *(Kap. 9.2.12)*

$$
s_{\gamma} = 1 - 0.4 \cdot \frac{b}{L} = 1 - 0.4 \cdot \frac{1.6\,\mathrm{m}}{4\,\mathrm{m}} = 0.84
$$

**Winkel der Einbindetiefe, in Grad** *(Kap. 9.2.13)*

$$
\vartheta_t = \arctan\frac{t}{b} = \arctan\frac{0.8\,\mathrm{m}}{1.6\,\mathrm{m}} = 26.6{}^{\circ}
$$

**Tiefenfaktor der Kohäsion** *(Kap. 9.2.13)*

$$
d_c = 1 + 0.007 \cdot \vartheta_t = 1 + 0.007 \cdot 26.6{}^{\circ} = 1.19
$$

**Tiefenfaktor der seitlichen Auflast** *(Kap. 9.2.13)*

$$
\begin{aligned}
  d_q &= 1 + 0.035 \cdot \tan \varphi_{eff} \cdot \left(1 - \sin \varphi_{eff}\right)^{2} \cdot \vartheta_t \\
  &= 1 + 0.035 \cdot \tan 28.42{}^{\circ} \cdot \left(1 - \sin 28.42{}^{\circ}\right)^{2} \cdot 26.6{}^{\circ} \\
  &= 1.14
\end{aligned}
$$

Der Tiefenfaktor des Gleitkörpergewichts ist d\_γ = 1.

**Geländeneigungsfaktor der Kohäsion** *(Kap. 9.2.15)*

$$
g_c = 1 - \frac{\beta}{147^\circ} = 1 - \frac{15{}^{\circ}}{147^\circ} = 0.9
$$

**Geländeneigungsfaktor der Auflast und des Gleitkörpers** *(Kap. 9.2.15)*

$$
g_q = \left(1 - 0.5 \cdot \tan \beta\right)^{5} = \left(1 - 0.5 \cdot \tan 15{}^{\circ}\right)^{5} = 0.49
$$

Für das Gleitkörpergewicht gilt derselbe Faktor: g\_γ = g\_q.

**Sohlneigungsfaktor der Kohäsion** *(Kap. 9.2.16)*

$$
b_c = 1 - \frac{\alpha}{147^\circ} = 1 - \frac{5{}^{\circ}}{147^\circ} = 0.97
$$

**Sohlneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.16)*

$$
b_q = e^{-0.035 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.035 \cdot 5{}^{\circ} \cdot \tan 28.42{}^{\circ}} = 0.91
$$

**Sohlneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.16)*

$$
b_{\gamma} = e^{-0.047 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.047 \cdot 5{}^{\circ} \cdot \tan 28.42{}^{\circ}} = 0.88
$$

> **Annahme:** b\_γ mit tan φ wie in Tabelle 9.2.18 -- im Text des Kapitels steht tan α; die Tabelle und die Formel für b\_q rechnen mit tan φ.

#### Grundbruch – Normal

**Neigung der Last** *(Kap. 9.2.14)*

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}} = \arctan\frac{120\,\mathrm{kN}}{900\,\mathrm{kN}} = 7.6{}^{\circ}
$$

**Lastneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_q &= \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{0.5 \cdot 120\,\mathrm{kN}}{900\,\mathrm{kN} + 1.6\,\mathrm{m} \cdot 4\,\mathrm{m} \cdot 4\,\mathrm{kPa} \cdot \cot 28.42{}^{\circ}}\right]^{5} \\
  &= 0.72
\end{aligned}
$$

**Lastneigungsfaktor der Kohäsion** *(Kap. 9.2.14)*

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1} = 0.72 - \frac{1 - 0.72}{15.42 - 1} = 0.7
$$

**Lastneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_{\gamma} &= \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{\left(0.7 - \frac{5{}^{\circ}}{450^\circ}\right) \cdot 120\,\mathrm{kN}}{900\,\mathrm{kN} + 1.6\,\mathrm{m} \cdot 4\,\mathrm{m} \cdot 4\,\mathrm{kPa} \cdot \cot 28.42{}^{\circ}}\right]^{5} \\
  &= 0.63
\end{aligned}
$$

**Bruchspannung in der Sohle** *(Kap. 9.2.10)*

$$
\begin{aligned}
  \sigma_f &= c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma} \\
  &= 4\,\mathrm{kPa} \cdot 26.64 \cdot 1.23 \cdot 1.19 \cdot 0.7 \cdot 0.9 \cdot 0.97 + 26.8\,\mathrm{kPa} \cdot 15.42 \cdot 1.22 \cdot 1.14 \cdot 0.72 \cdot 0.49 \cdot 0.91 + \tfrac{1}{2} \cdot 11\,\mathrm{kN}/\mathrm{m}^{3} \cdot 1.6\,\mathrm{m} \cdot 14.05 \cdot 0.84 \cdot 1 \cdot 0.63 \cdot 0.49 \cdot 0.88 \\
  &= 305.7\,\mathrm{kPa}
\end{aligned}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L = 305.7\,\mathrm{kPa} \cdot 1.6\,\mathrm{m} \cdot 4\,\mathrm{m} = 1956.7\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
N_{Ed} = 900\,\mathrm{kN} \quad \le \quad N_{Rd} = 1956.7\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GB,\text{Normal}} = \frac{N_{Rd}}{N_{Ed}} = \frac{1956.7\,\mathrm{kN}}{900\,\mathrm{kN}} = 2.17 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Grundbruch – Steil

**Neigung der Last** *(Kap. 9.2.14)*

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}} = \arctan\frac{300\,\mathrm{kN}}{150\,\mathrm{kN}} = 63.4{}^{\circ}
$$

**Lastneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_q &= \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{0.5 \cdot 300\,\mathrm{kN}}{150\,\mathrm{kN} + 1.6\,\mathrm{m} \cdot 4\,\mathrm{m} \cdot 4\,\mathrm{kPa} \cdot \cot 28.42{}^{\circ}}\right]^{5} \\
  &= 0
\end{aligned}
$$

**Lastneigungsfaktor der Kohäsion** *(Kap. 9.2.14)*

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1} = 0 - \frac{1 - 0}{15.42 - 1} = -0.07
$$

**Lastneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_{\gamma} &= \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{\left(0.7 - \frac{5{}^{\circ}}{450^\circ}\right) \cdot 300\,\mathrm{kN}}{150\,\mathrm{kN} + 1.6\,\mathrm{m} \cdot 4\,\mathrm{m} \cdot 4\,\mathrm{kPa} \cdot \cot 28.42{}^{\circ}}\right]^{5} \\
  &= 0
\end{aligned}
$$

> **Annahme:** Ist die Klammer eines Lastneigungsfaktors kleiner als null, gilt null: die Last ist so stark geneigt, dass die Auflast oder das Gewicht des Gleitkörpers nichts mehr trägt.

**Bruchspannung in der Sohle** *(Kap. 9.2.10)*

$$
\begin{aligned}
  \sigma_f &= c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma} \\
  &= 4\,\mathrm{kPa} \cdot 26.64 \cdot 1.23 \cdot 1.19 \cdot \left(-0.07\right) \cdot 0.9 \cdot 0.97 + 26.8\,\mathrm{kPa} \cdot 15.42 \cdot 1.22 \cdot 1.14 \cdot 0 \cdot 0.49 \cdot 0.91 + \tfrac{1}{2} \cdot 11\,\mathrm{kN}/\mathrm{m}^{3} \cdot 1.6\,\mathrm{m} \cdot 14.05 \cdot 0.84 \cdot 1 \cdot 0 \cdot 0.49 \cdot 0.88 \\
  &= -9\,\mathrm{kPa}
\end{aligned}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L = -9\,\mathrm{kPa} \cdot 1.6\,\mathrm{m} \cdot 4\,\mathrm{m} = 0\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
N_{Ed} = 150\,\mathrm{kN} \quad > \quad N_{Rd} = 0\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GB,\text{Steil}} = \frac{N_{Rd}}{N_{Ed}} = \frac{0\,\mathrm{kN}}{150\,\mathrm{kN}} = 0.00 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

**Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ**

$$
k_{\delta} = 0.67
$$

### Gleiten

**Reibungswinkel der Sohlfuge** *(Kap. 9.2.18)*

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff} = 0.67 \cdot 28.42{}^{\circ} = 19.04{}^{\circ}
$$

#### Gleiten – Normal

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 900\,\mathrm{kN} \cdot \tan 19.04{}^{\circ} = 310.6\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 120\,\mathrm{kN} \quad \le \quad T_{Rd} = 310.6\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Normal}} = \frac{T_{Rd}}{T_{Ed}} = \frac{310.6\,\mathrm{kN}}{120\,\mathrm{kN}} = 2.59 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Gleiten – Steil

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 150\,\mathrm{kN} \cdot \tan 19.04{}^{\circ} = 51.8\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 300\,\mathrm{kN} \quad > \quad T_{Rd} = 51.8\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Steil}} = \frac{T_{Rd}}{T_{Ed}} = \frac{51.8\,\mathrm{kN}}{300\,\mathrm{kN}} = 0.17 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

### Grundbruch: Ufer

**Reibungswinkel, charakteristisch**

$$
\varphi_k = 30{}^{\circ}
$$

**Partialfaktor des Reibungswinkels** *(SIA 267:2013, 5.3.2.2)*

$$
\gamma_{\varphi} = 1.2
$$

**Reibungswinkel, Bemessungswert** *(SIA 267:2013, 5.3.2.1)*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 30{}^{\circ}}{1.2}\right) = 25.69{}^{\circ}
$$

**Kohäsion, charakteristisch**

$$
c_k = 0\,\mathrm{kPa}
$$

**Partialfaktor der Kohäsion**

$$
\gamma_c = 1.5
$$

**Kohäsion, Bemessungswert**

$$
c_{eff} = \frac{c_k}{\gamma_c} = \frac{0\,\mathrm{kPa}}{1.5} = 0\,\mathrm{kPa}
$$

**Raumlast des Bodens**

$$
\gamma = 21\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Wassers**

$$
\gamma_w = 10\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Bodens unter Auftrieb**

$$
\gamma' = \gamma - \gamma_w = 21\,\mathrm{kN}/\mathrm{m}^{3} - 10\,\mathrm{kN}/\mathrm{m}^{3} = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Bemessungslast neben dem Fundament**

$$
q_{Ed} = 0\,\mathrm{kPa}
$$

**Breite des Fundaments**

$$
b = 1.5\,\mathrm{m}
$$

**Länge des Fundaments**

$$
L = 1.5\,\mathrm{m}
$$

**Tiefe des höchsten Grundwasserspiegels unter Terrain**

$$
t_1 = 0.4\,\mathrm{m}
$$

**Tiefe der Sohle unter Terrain**

$$
t = 1\,\mathrm{m}
$$

**Neigung der Sohle**

$$
\alpha = 0{}^{\circ}
$$

**Neigung des Geländes**

$$
\beta = 0{}^{\circ}
$$

### Grundbruch

**Erweiterte Tragfähigkeitsformel** *(Kap. 9.2.10)*

$$
\sigma_f = c \, N_c s_c d_c i_c g_c b_c + \sigma_{v,0} \, N_q s_q d_q i_q g_q b_q + \tfrac{1}{2} \gamma_G \, b \, N_{\gamma} s_{\gamma} d_{\gamma} i_{\gamma} g_{\gamma} b_{\gamma} \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

#### Tragfähigkeitsfaktoren

**Tragfähigkeitsfaktor der seitlichen Auflast** *(Kap. 9.2.6)*

$$
N_q = e^{\pi \tan \varphi_{eff}} \cdot \tan^{2}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) = e^{\pi \tan 25.69{}^{\circ}} \cdot \tan^{2}\left(45^\circ + \frac{25.69{}^{\circ}}{2}\right) = 11.47
$$

**Tragfähigkeitsfaktor der Kohäsion** *(Kap. 9.2.6)*

$$
N_c = \frac{N_q - 1}{\tan \varphi_{eff}} = \frac{11.47 - 1}{\tan 25.69{}^{\circ}} = 21.77
$$

**Tragfähigkeitsfaktor des Gleitkörpergewichts** *(Kap. 9.2.6)*

$$
N_{\gamma} = 1.8 \cdot \left(N_q - 1\right) \cdot \tan \varphi_{eff} = 1.8 \cdot \left(11.47 - 1\right) \cdot \tan 25.69{}^{\circ} = 9.07
$$

#### Gleitkörper und Grundwasser

**Reichweite des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  L_{Gl} &= b \cdot \tan\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \cdot e^{\frac{\pi}{2} \tan \varphi_{eff}} \\
  &= 1.5\,\mathrm{m} \cdot \tan\left(45^\circ + \frac{25.69{}^{\circ}}{2}\right) \cdot e^{\frac{\pi}{2} \tan 25.69{}^{\circ}} \\
  &= 5.08\,\mathrm{m}
\end{aligned}
$$

**Tiefe des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  H_{Gl} &= b \cdot \frac{\cos \varphi_{eff}}{2 \cos\left(45^\circ + \frac{\varphi_{eff}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \tan \varphi_{eff}} \\
  &= 1.5\,\mathrm{m} \cdot \frac{\cos 25.69{}^{\circ}}{2 \cos\left(45^\circ + \frac{25.69{}^{\circ}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{25.69{}^{\circ}}{2}\right) \tan 25.69{}^{\circ}} \\
  &= 2.06\,\mathrm{m}
\end{aligned}
$$

**Überlagerung auf Höhe der Sohle, Lage 1: Grundwasser über der Sohle** *(Kap. 9.2.8)*

$$
\begin{aligned}
  \sigma_{v,0} &= \gamma \cdot t_1 + \gamma' \cdot \left(t - t_1\right) + q_{Ed} \\
  &= 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 0.4\,\mathrm{m} + 11\,\mathrm{kN}/\mathrm{m}^{3} \cdot \left(1\,\mathrm{m} - 0.4\,\mathrm{m}\right) + 0\,\mathrm{kPa} \\
  &= 15\,\mathrm{kPa}
\end{aligned}
$$

**Raumlast im Gleitkörper, unter Wasser** *(Kap. 9.2.8)*

$$
\gamma_G = \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

#### Form, Tiefe, Gelände und Sohle

**Formfaktor der Kohäsion** *(Kap. 9.2.12)*

$$
s_c = 1 + \frac{b}{L} \cdot \frac{N_q}{N_c} = 1 + \frac{1.5\,\mathrm{m}}{1.5\,\mathrm{m}} \cdot \frac{11.47}{21.77} = 1.53
$$

**Formfaktor der seitlichen Auflast** *(Kap. 9.2.12)*

$$
s_q = 1 + \frac{b}{L} \cdot \tan \varphi_{eff} = 1 + \frac{1.5\,\mathrm{m}}{1.5\,\mathrm{m}} \cdot \tan 25.69{}^{\circ} = 1.48
$$

**Formfaktor des Gleitkörpergewichts** *(Kap. 9.2.12)*

$$
s_{\gamma} = 1 - 0.4 \cdot \frac{b}{L} = 1 - 0.4 \cdot \frac{1.5\,\mathrm{m}}{1.5\,\mathrm{m}} = 0.6
$$

**Winkel der Einbindetiefe, in Grad** *(Kap. 9.2.13)*

$$
\vartheta_t = \arctan\frac{t}{b} = \arctan\frac{1\,\mathrm{m}}{1.5\,\mathrm{m}} = 33.7{}^{\circ}
$$

**Tiefenfaktor der Kohäsion** *(Kap. 9.2.13)*

$$
d_c = 1 + 0.007 \cdot \vartheta_t = 1 + 0.007 \cdot 33.7{}^{\circ} = 1.24
$$

**Tiefenfaktor der seitlichen Auflast** *(Kap. 9.2.13)*

$$
\begin{aligned}
  d_q &= 1 + 0.035 \cdot \tan \varphi_{eff} \cdot \left(1 - \sin \varphi_{eff}\right)^{2} \cdot \vartheta_t \\
  &= 1 + 0.035 \cdot \tan 25.69{}^{\circ} \cdot \left(1 - \sin 25.69{}^{\circ}\right)^{2} \cdot 33.7{}^{\circ} \\
  &= 1.18
\end{aligned}
$$

Der Tiefenfaktor des Gleitkörpergewichts ist d\_γ = 1.

**Geländeneigungsfaktor der Kohäsion** *(Kap. 9.2.15)*

$$
g_c = 1 - \frac{\beta}{147^\circ} = 1 - \frac{0{}^{\circ}}{147^\circ} = 1
$$

**Geländeneigungsfaktor der Auflast und des Gleitkörpers** *(Kap. 9.2.15)*

$$
g_q = \left(1 - 0.5 \cdot \tan \beta\right)^{5} = \left(1 - 0.5 \cdot \tan 0{}^{\circ}\right)^{5} = 1
$$

Für das Gleitkörpergewicht gilt derselbe Faktor: g\_γ = g\_q.

**Sohlneigungsfaktor der Kohäsion** *(Kap. 9.2.16)*

$$
b_c = 1 - \frac{\alpha}{147^\circ} = 1 - \frac{0{}^{\circ}}{147^\circ} = 1
$$

**Sohlneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.16)*

$$
b_q = e^{-0.035 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.035 \cdot 0{}^{\circ} \cdot \tan 25.69{}^{\circ}} = 1
$$

**Sohlneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.16)*

$$
b_{\gamma} = e^{-0.047 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.047 \cdot 0{}^{\circ} \cdot \tan 25.69{}^{\circ}} = 1
$$

> **Annahme:** b\_γ mit tan φ wie in Tabelle 9.2.18 -- im Text des Kapitels steht tan α; die Tabelle und die Formel für b\_q rechnen mit tan φ.

#### Grundbruch – Tragsicherheit

**Neigung der Last** *(Kap. 9.2.14)*

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}} = \arctan\frac{100\,\mathrm{kN}}{1200\,\mathrm{kN}} = 4.8{}^{\circ}
$$

**Lastneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_q &= \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{0.5 \cdot 100\,\mathrm{kN}}{1200\,\mathrm{kN} + 1.5\,\mathrm{m} \cdot 1.5\,\mathrm{m} \cdot 0\,\mathrm{kPa} \cdot \cot 25.69{}^{\circ}}\right]^{5} \\
  &= 0.81
\end{aligned}
$$

**Lastneigungsfaktor der Kohäsion** *(Kap. 9.2.14)*

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1} = 0.81 - \frac{1 - 0.81}{11.47 - 1} = 0.79
$$

**Lastneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_{\gamma} &= \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{\left(0.7 - \frac{0{}^{\circ}}{450^\circ}\right) \cdot 100\,\mathrm{kN}}{1200\,\mathrm{kN} + 1.5\,\mathrm{m} \cdot 1.5\,\mathrm{m} \cdot 0\,\mathrm{kPa} \cdot \cot 25.69{}^{\circ}}\right]^{5} \\
  &= 0.74
\end{aligned}
$$

**Bruchspannung in der Sohle** *(Kap. 9.2.10)*

$$
\begin{aligned}
  \sigma_f &= c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma} \\
  &= 0\,\mathrm{kPa} \cdot 21.77 \cdot 1.53 \cdot 1.24 \cdot 0.79 \cdot 1 \cdot 1 + 15\,\mathrm{kPa} \cdot 11.47 \cdot 1.48 \cdot 1.18 \cdot 0.81 \cdot 1 \cdot 1 + \tfrac{1}{2} \cdot 11\,\mathrm{kN}/\mathrm{m}^{3} \cdot 1.5\,\mathrm{m} \cdot 9.07 \cdot 0.6 \cdot 1 \cdot 0.74 \cdot 1 \cdot 1 \\
  &= 276.8\,\mathrm{kPa}
\end{aligned}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L = 276.8\,\mathrm{kPa} \cdot 1.5\,\mathrm{m} \cdot 1.5\,\mathrm{m} = 622.8\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
N_{Ed} = 1200\,\mathrm{kN} \quad > \quad N_{Rd} = 622.8\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GB,\text{Tragsicherheit}} = \frac{N_{Rd}}{N_{Ed}} = \frac{622.8\,\mathrm{kN}}{1200\,\mathrm{kN}} = 0.52 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

**Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ**

$$
k_{\delta} = 1
$$

### Gleiten

**Reibungswinkel der Sohlfuge** *(Kap. 9.2.18)*

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff} = 1 \cdot 25.69{}^{\circ} = 25.69{}^{\circ}
$$

#### Gleiten – Tragsicherheit

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 1200\,\mathrm{kN} \cdot \tan 25.69{}^{\circ} = 577.4\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 100\,\mathrm{kN} \quad \le \quad T_{Rd} = 577.4\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Tragsicherheit}} = \frac{T_{Rd}}{T_{Ed}} = \frac{577.4\,\mathrm{kN}}{100\,\mathrm{kN}} = 5.77 \quad \Rightarrow \quad \text{erfüllt}
$$

### Grundbruch: Kai

**Reibungswinkel, charakteristisch**

$$
\varphi_k = 28{}^{\circ}
$$

**Partialfaktor des Reibungswinkels** *(SIA 267:2013, 5.3.2.2)*

$$
\gamma_{\varphi} = 1.2
$$

**Reibungswinkel, Bemessungswert** *(SIA 267:2013, 5.3.2.1)*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 28{}^{\circ}}{1.2}\right) = 23.9{}^{\circ}
$$

**Kohäsion, charakteristisch**

$$
c_k = 3\,\mathrm{kPa}
$$

**Partialfaktor der Kohäsion**

$$
\gamma_c = 1.5
$$

**Kohäsion, Bemessungswert**

$$
c_{eff} = \frac{c_k}{\gamma_c} = \frac{3\,\mathrm{kPa}}{1.5} = 2\,\mathrm{kPa}
$$

**Raumlast des Bodens**

$$
\gamma = 21\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Wassers**

$$
\gamma_w = 10\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Bodens unter Auftrieb**

$$
\gamma' = \gamma - \gamma_w = 21\,\mathrm{kN}/\mathrm{m}^{3} - 10\,\mathrm{kN}/\mathrm{m}^{3} = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Bemessungslast neben dem Fundament**

$$
q_{Ed} = 0\,\mathrm{kPa}
$$

**Breite des Fundaments**

$$
b = 2\,\mathrm{m}
$$

**Länge des Fundaments**

$$
L = 20\,\mathrm{m}
$$

**Tiefe des höchsten Grundwasserspiegels unter Terrain**

$$
t_1 = 1.5\,\mathrm{m}
$$

**Tiefe der Sohle unter Terrain**

$$
t = 1.5\,\mathrm{m}
$$

**Neigung der Sohle**

$$
\alpha = 0{}^{\circ}
$$

**Neigung des Geländes**

$$
\beta = 0{}^{\circ}
$$

### Grundbruch

**Erweiterte Tragfähigkeitsformel** *(Kap. 9.2.10)*

$$
\sigma_f = c \, N_c s_c d_c i_c g_c b_c + \sigma_{v,0} \, N_q s_q d_q i_q g_q b_q + \tfrac{1}{2} \gamma_G \, b \, N_{\gamma} s_{\gamma} d_{\gamma} i_{\gamma} g_{\gamma} b_{\gamma} \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

#### Tragfähigkeitsfaktoren

**Tragfähigkeitsfaktor der seitlichen Auflast** *(Kap. 9.2.6)*

$$
N_q = e^{\pi \tan \varphi_{eff}} \cdot \tan^{2}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) = e^{\pi \tan 23.9{}^{\circ}} \cdot \tan^{2}\left(45^\circ + \frac{23.9{}^{\circ}}{2}\right) = 9.5
$$

**Tragfähigkeitsfaktor der Kohäsion** *(Kap. 9.2.6)*

$$
N_c = \frac{N_q - 1}{\tan \varphi_{eff}} = \frac{9.5 - 1}{\tan 23.9{}^{\circ}} = 19.19
$$

**Tragfähigkeitsfaktor des Gleitkörpergewichts** *(Kap. 9.2.6)*

$$
N_{\gamma} = 1.8 \cdot \left(N_q - 1\right) \cdot \tan \varphi_{eff} = 1.8 \cdot \left(9.5 - 1\right) \cdot \tan 23.9{}^{\circ} = 6.78
$$

#### Gleitkörper und Grundwasser

**Reichweite des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  L_{Gl} &= b \cdot \tan\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \cdot e^{\frac{\pi}{2} \tan \varphi_{eff}} \\
  &= 2\,\mathrm{m} \cdot \tan\left(45^\circ + \frac{23.9{}^{\circ}}{2}\right) \cdot e^{\frac{\pi}{2} \tan 23.9{}^{\circ}} \\
  &= 6.17\,\mathrm{m}
\end{aligned}
$$

**Tiefe des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  H_{Gl} &= b \cdot \frac{\cos \varphi_{eff}}{2 \cos\left(45^\circ + \frac{\varphi_{eff}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \tan \varphi_{eff}} \\
  &= 2\,\mathrm{m} \cdot \frac{\cos 23.9{}^{\circ}}{2 \cos\left(45^\circ + \frac{23.9{}^{\circ}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{23.9{}^{\circ}}{2}\right) \tan 23.9{}^{\circ}} \\
  &= 2.6\,\mathrm{m}
\end{aligned}
$$

**Überlagerung auf Höhe der Sohle, Lage 2: Grundwasser auf Höhe der Sohle** *(Kap. 9.2.8)*

$$
\begin{aligned}
  \sigma_{v,0} &= \gamma \cdot t_1 + \gamma' \cdot \left(t - t_1\right) + q_{Ed} \\
  &= 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 1.5\,\mathrm{m} + 11\,\mathrm{kN}/\mathrm{m}^{3} \cdot \left(1.5\,\mathrm{m} - 1.5\,\mathrm{m}\right) + 0\,\mathrm{kPa} \\
  &= 31.5\,\mathrm{kPa}
\end{aligned}
$$

**Raumlast im Gleitkörper, unter Wasser** *(Kap. 9.2.8)*

$$
\gamma_G = \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

#### Form, Tiefe, Gelände und Sohle

**Formfaktor der Kohäsion** *(Kap. 9.2.12)*

$$
s_c = 1 + \frac{b}{L} \cdot \frac{N_q}{N_c} = 1 + \frac{2\,\mathrm{m}}{20\,\mathrm{m}} \cdot \frac{9.5}{19.19} = 1.05
$$

**Formfaktor der seitlichen Auflast** *(Kap. 9.2.12)*

$$
s_q = 1 + \frac{b}{L} \cdot \tan \varphi_{eff} = 1 + \frac{2\,\mathrm{m}}{20\,\mathrm{m}} \cdot \tan 23.9{}^{\circ} = 1.04
$$

**Formfaktor des Gleitkörpergewichts** *(Kap. 9.2.12)*

$$
s_{\gamma} = 1 - 0.4 \cdot \frac{b}{L} = 1 - 0.4 \cdot \frac{2\,\mathrm{m}}{20\,\mathrm{m}} = 0.96
$$

**Winkel der Einbindetiefe, in Grad** *(Kap. 9.2.13)*

$$
\vartheta_t = \arctan\frac{t}{b} = \arctan\frac{1.5\,\mathrm{m}}{2\,\mathrm{m}} = 36.9{}^{\circ}
$$

**Tiefenfaktor der Kohäsion** *(Kap. 9.2.13)*

$$
d_c = 1 + 0.007 \cdot \vartheta_t = 1 + 0.007 \cdot 36.9{}^{\circ} = 1.26
$$

**Tiefenfaktor der seitlichen Auflast** *(Kap. 9.2.13)*

$$
\begin{aligned}
  d_q &= 1 + 0.035 \cdot \tan \varphi_{eff} \cdot \left(1 - \sin \varphi_{eff}\right)^{2} \cdot \vartheta_t \\
  &= 1 + 0.035 \cdot \tan 23.9{}^{\circ} \cdot \left(1 - \sin 23.9{}^{\circ}\right)^{2} \cdot 36.9{}^{\circ} \\
  &= 1.2
\end{aligned}
$$

Der Tiefenfaktor des Gleitkörpergewichts ist d\_γ = 1.

**Geländeneigungsfaktor der Kohäsion** *(Kap. 9.2.15)*

$$
g_c = 1 - \frac{\beta}{147^\circ} = 1 - \frac{0{}^{\circ}}{147^\circ} = 1
$$

**Geländeneigungsfaktor der Auflast und des Gleitkörpers** *(Kap. 9.2.15)*

$$
g_q = \left(1 - 0.5 \cdot \tan \beta\right)^{5} = \left(1 - 0.5 \cdot \tan 0{}^{\circ}\right)^{5} = 1
$$

Für das Gleitkörpergewicht gilt derselbe Faktor: g\_γ = g\_q.

**Sohlneigungsfaktor der Kohäsion** *(Kap. 9.2.16)*

$$
b_c = 1 - \frac{\alpha}{147^\circ} = 1 - \frac{0{}^{\circ}}{147^\circ} = 1
$$

**Sohlneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.16)*

$$
b_q = e^{-0.035 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.035 \cdot 0{}^{\circ} \cdot \tan 23.9{}^{\circ}} = 1
$$

**Sohlneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.16)*

$$
b_{\gamma} = e^{-0.047 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.047 \cdot 0{}^{\circ} \cdot \tan 23.9{}^{\circ}} = 1
$$

> **Annahme:** b\_γ mit tan φ wie in Tabelle 9.2.18 -- im Text des Kapitels steht tan α; die Tabelle und die Formel für b\_q rechnen mit tan φ.

#### Grundbruch – Tragsicherheit

**Neigung der Last** *(Kap. 9.2.14)*

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}} = \arctan\frac{80\,\mathrm{kN}}{2000\,\mathrm{kN}} = 2.3{}^{\circ}
$$

**Lastneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_q &= \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{0.5 \cdot 80\,\mathrm{kN}}{2000\,\mathrm{kN} + 2\,\mathrm{m} \cdot 20\,\mathrm{m} \cdot 2\,\mathrm{kPa} \cdot \cot 23.9{}^{\circ}}\right]^{5} \\
  &= 0.91
\end{aligned}
$$

**Lastneigungsfaktor der Kohäsion** *(Kap. 9.2.14)*

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1} = 0.91 - \frac{1 - 0.91}{9.5 - 1} = 0.9
$$

**Lastneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_{\gamma} &= \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{\left(0.7 - \frac{0{}^{\circ}}{450^\circ}\right) \cdot 80\,\mathrm{kN}}{2000\,\mathrm{kN} + 2\,\mathrm{m} \cdot 20\,\mathrm{m} \cdot 2\,\mathrm{kPa} \cdot \cot 23.9{}^{\circ}}\right]^{5} \\
  &= 0.88
\end{aligned}
$$

**Bruchspannung in der Sohle** *(Kap. 9.2.10)*

$$
\begin{aligned}
  \sigma_f &= c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma} \\
  &= 2\,\mathrm{kPa} \cdot 19.19 \cdot 1.05 \cdot 1.26 \cdot 0.9 \cdot 1 \cdot 1 + 31.5\,\mathrm{kPa} \cdot 9.5 \cdot 1.04 \cdot 1.2 \cdot 0.91 \cdot 1 \cdot 1 + \tfrac{1}{2} \cdot 11\,\mathrm{kN}/\mathrm{m}^{3} \cdot 2\,\mathrm{m} \cdot 6.78 \cdot 0.96 \cdot 1 \cdot 0.88 \cdot 1 \cdot 1 \\
  &= 451.1\,\mathrm{kPa}
\end{aligned}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L = 451.1\,\mathrm{kPa} \cdot 2\,\mathrm{m} \cdot 20\,\mathrm{m} = 18045.2\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
N_{Ed} = 2000\,\mathrm{kN} \quad \le \quad N_{Rd} = 18045.2\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GB,\text{Tragsicherheit}} = \frac{N_{Rd}}{N_{Ed}} = \frac{18045.2\,\mathrm{kN}}{2000\,\mathrm{kN}} = 9.02 \quad \Rightarrow \quad \text{erfüllt}
$$

**Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ**

$$
k_{\delta} = 1
$$

### Gleiten

**Reibungswinkel der Sohlfuge** *(Kap. 9.2.18)*

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff} = 1 \cdot 23.9{}^{\circ} = 23.9{}^{\circ}
$$

#### Gleiten – Tragsicherheit

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 2000\,\mathrm{kN} \cdot \tan 23.9{}^{\circ} = 886.2\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 80\,\mathrm{kN} \quad \le \quad T_{Rd} = 886.2\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Tragsicherheit}} = \frac{T_{Rd}}{T_{Ed}} = \frac{886.2\,\mathrm{kN}}{80\,\mathrm{kN}} = 11.08 \quad \Rightarrow \quad \text{erfüllt}
$$

### Grundbruch: Seeton

**Reibungswinkel, charakteristisch**

$$
\varphi_k = 0{}^{\circ}
$$

**Partialfaktor des Reibungswinkels** *(SIA 267:2013, 5.3.2.2)*

$$
\gamma_{\varphi} = 1.2
$$

**Reibungswinkel, Bemessungswert** *(SIA 267:2013, 5.3.2.1)*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 0{}^{\circ}}{1.2}\right) = 0{}^{\circ}
$$

**Kohäsion, charakteristisch**

$$
c_k = 40\,\mathrm{kPa}
$$

**Partialfaktor der Kohäsion**

$$
\gamma_c = 1.5
$$

**Kohäsion, Bemessungswert**

$$
c_{eff} = \frac{c_k}{\gamma_c} = \frac{40\,\mathrm{kPa}}{1.5} = 26.7\,\mathrm{kPa}
$$

**Raumlast des Bodens**

$$
\gamma = 21\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Wassers**

$$
\gamma_w = 10\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Bodens unter Auftrieb**

$$
\gamma' = \gamma - \gamma_w = 21\,\mathrm{kN}/\mathrm{m}^{3} - 10\,\mathrm{kN}/\mathrm{m}^{3} = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Bemessungslast neben dem Fundament**

$$
q_{Ed} = 0\,\mathrm{kPa}
$$

**Breite des Fundaments**

$$
b = 1.5\,\mathrm{m}
$$

**Länge des Fundaments**

$$
L = 2\,\mathrm{m}
$$

**Tiefe des höchsten Grundwasserspiegels unter Terrain**

$$
t_1 = 0\,\mathrm{m}
$$

**Tiefe der Sohle unter Terrain**

$$
t = 0.8\,\mathrm{m}
$$

**Neigung der Sohle**

$$
\alpha = 4{}^{\circ}
$$

**Neigung des Geländes**

$$
\beta = 10{}^{\circ}
$$

### Grundbruch

**Tragfähigkeitsformel undrainiert** *(Kap. 9.2.17)*

$$
\sigma_f = 5.1 \, s_u \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \left(\gamma t + q\right) \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

Mit φ = 0 ist c\_eff die undrainierte Scherfestigkeit s\_u.

**Formfaktor, undrainiert** *(Kap. 9.2.17)*

$$
s_c = 0.2 \cdot \frac{b}{L} = 0.2 \cdot \frac{1.5\,\mathrm{m}}{2\,\mathrm{m}} = 0.15
$$

**Tiefenfaktor, undrainiert, t \< b** *(Kap. 9.2.17)*

$$
d_c = 0.4 \cdot \frac{t}{b} = 0.4 \cdot \frac{0.8\,\mathrm{m}}{1.5\,\mathrm{m}} = 0.21
$$

**Geländeneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
g_c = \frac{\beta}{147^\circ} = \frac{10{}^{\circ}}{147^\circ} = 0.07
$$

**Sohlneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
b_c = \frac{\alpha}{147^\circ} = \frac{4{}^{\circ}}{147^\circ} = 0.03
$$

**Überlagerung auf Höhe der Sohle, totale Spannung** *(Kap. 9.2.17)*

$$
\sigma_{v,0} = \gamma \cdot t + q_{Ed} = 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 0.8\,\mathrm{m} + 0\,\mathrm{kPa} = 16.8\,\mathrm{kPa}
$$

#### Grundbruch – Normal

**Lastneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
i_c = 0.5 - \frac{1}{2} \sqrt{1 - \frac{T_{Ed}}{c_{eff} \cdot b \cdot L}} = 0.5 - \frac{1}{2} \sqrt{1 - \frac{40\,\mathrm{kN}}{26.7\,\mathrm{kPa} \cdot 1.5\,\mathrm{m} \cdot 2\,\mathrm{m}}} = 0.15
$$

**Bruchspannung in der Sohle, undrainiert** *(Kap. 9.2.17)*

$$
\begin{aligned}
  \sigma_f &= 5.1 \cdot c_{eff} \cdot \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \sigma_{v,0} \\
  &= 5.1 \cdot 26.7\,\mathrm{kPa} \cdot \left(1 + 0.15 + 0.21 - 0.15 - 0.03 - 0.07\right) + 16.8\,\mathrm{kPa} \\
  &= 169.3\,\mathrm{kPa}
\end{aligned}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L = 169.3\,\mathrm{kPa} \cdot 1.5\,\mathrm{m} \cdot 2\,\mathrm{m} = 508\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
N_{Ed} = 300\,\mathrm{kN} \quad \le \quad N_{Rd} = 508\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GB,\text{Normal}} = \frac{N_{Rd}}{N_{Ed}} = \frac{508\,\mathrm{kN}}{300\,\mathrm{kN}} = 1.69 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Grundbruch – Zu schräg

T\_Ed \> s\_u · b · L: die Last ist zu stark geneigt, der Lastneigungsfaktor ist nicht bestimmt -- kein Grundbruchwiderstand.

**Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ**

$$
k_{\delta} = 1
$$

### Gleiten

**Reibungswinkel der Sohlfuge** *(Kap. 9.2.18)*

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff} = 1 \cdot 0{}^{\circ} = 0{}^{\circ}
$$

Mit φ = 0 gibt die Reibung in der Sohle keinen Widerstand; eine Haftung zählt nach dem Kapitel nicht.

#### Gleiten – Normal

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 300\,\mathrm{kN} \cdot \tan 0{}^{\circ} = 0\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 40\,\mathrm{kN} \quad > \quad T_{Rd} = 0\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Normal}} = \frac{T_{Rd}}{T_{Ed}} = \frac{0\,\mathrm{kN}}{40\,\mathrm{kN}} = 0.00 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

#### Gleiten – Zu schräg

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 300\,\mathrm{kN} \cdot \tan 0{}^{\circ} = 0\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 200\,\mathrm{kN} \quad > \quad T_{Rd} = 0\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Zu schräg}} = \frac{T_{Rd}}{T_{Ed}} = \frac{0\,\mathrm{kN}}{200\,\mathrm{kN}} = 0.00 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

### Grundbruch: Schacht

**Reibungswinkel, charakteristisch**

$$
\varphi_k = 0{}^{\circ}
$$

**Partialfaktor des Reibungswinkels** *(SIA 267:2013, 5.3.2.2)*

$$
\gamma_{\varphi} = 1.2
$$

**Reibungswinkel, Bemessungswert** *(SIA 267:2013, 5.3.2.1)*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 0{}^{\circ}}{1.2}\right) = 0{}^{\circ}
$$

**Kohäsion, charakteristisch**

$$
c_k = 60\,\mathrm{kPa}
$$

**Partialfaktor der Kohäsion**

$$
\gamma_c = 1.5
$$

**Kohäsion, Bemessungswert**

$$
c_{eff} = \frac{c_k}{\gamma_c} = \frac{60\,\mathrm{kPa}}{1.5} = 40\,\mathrm{kPa}
$$

**Raumlast des Bodens**

$$
\gamma = 21\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Wassers**

$$
\gamma_w = 10\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Raumlast des Bodens unter Auftrieb**

$$
\gamma' = \gamma - \gamma_w = 21\,\mathrm{kN}/\mathrm{m}^{3} - 10\,\mathrm{kN}/\mathrm{m}^{3} = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

**Bemessungslast neben dem Fundament**

$$
q_{Ed} = 0\,\mathrm{kPa}
$$

**Breite des Fundaments**

$$
b = 1.2\,\mathrm{m}
$$

**Länge des Fundaments**

$$
L = 1.2\,\mathrm{m}
$$

**Tiefe des höchsten Grundwasserspiegels unter Terrain**

$$
t_1 = 0\,\mathrm{m}
$$

**Tiefe der Sohle unter Terrain**

$$
t = 2\,\mathrm{m}
$$

**Neigung der Sohle**

$$
\alpha = 0{}^{\circ}
$$

**Neigung des Geländes**

$$
\beta = 0{}^{\circ}
$$

### Grundbruch

**Tragfähigkeitsformel undrainiert** *(Kap. 9.2.17)*

$$
\sigma_f = 5.1 \, s_u \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \left(\gamma t + q\right) \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

Mit φ = 0 ist c\_eff die undrainierte Scherfestigkeit s\_u.

**Formfaktor, undrainiert** *(Kap. 9.2.17)*

$$
s_c = 0.2 \cdot \frac{b}{L} = 0.2 \cdot \frac{1.2\,\mathrm{m}}{1.2\,\mathrm{m}} = 0.2
$$

**Winkel der Einbindetiefe, in Grad** *(Kap. 9.2.13)*

$$
\vartheta_t = \arctan\frac{t}{b} = \arctan\frac{2\,\mathrm{m}}{1.2\,\mathrm{m}} = 59{}^{\circ}
$$

**Tiefenfaktor, undrainiert, t ≥ b** *(Kap. 9.2.17)*

$$
d_c = 0.007 \cdot \vartheta_t = 0.007 \cdot 59{}^{\circ} = 0.41
$$

**Geländeneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
g_c = \frac{\beta}{147^\circ} = \frac{0{}^{\circ}}{147^\circ} = 0
$$

**Sohlneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
b_c = \frac{\alpha}{147^\circ} = \frac{0{}^{\circ}}{147^\circ} = 0
$$

**Überlagerung auf Höhe der Sohle, totale Spannung** *(Kap. 9.2.17)*

$$
\sigma_{v,0} = \gamma \cdot t + q_{Ed} = 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 2\,\mathrm{m} + 0\,\mathrm{kPa} = 42\,\mathrm{kPa}
$$

#### Grundbruch – Tragsicherheit

**Lastneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
i_c = 0.5 - \frac{1}{2} \sqrt{1 - \frac{T_{Ed}}{c_{eff} \cdot b \cdot L}} = 0.5 - \frac{1}{2} \sqrt{1 - \frac{30\,\mathrm{kN}}{40\,\mathrm{kPa} \cdot 1.2\,\mathrm{m} \cdot 1.2\,\mathrm{m}}} = 0.15
$$

**Bruchspannung in der Sohle, undrainiert** *(Kap. 9.2.17)*

$$
\begin{aligned}
  \sigma_f &= 5.1 \cdot c_{eff} \cdot \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \sigma_{v,0} \\
  &= 5.1 \cdot 40\,\mathrm{kPa} \cdot \left(1 + 0.2 + 0.41 - 0.15 - 0 - 0\right) + 42\,\mathrm{kPa} \\
  &= 339.7\,\mathrm{kPa}
\end{aligned}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L = 339.7\,\mathrm{kPa} \cdot 1.2\,\mathrm{m} \cdot 1.2\,\mathrm{m} = 489.2\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
N_{Ed} = 900\,\mathrm{kN} \quad > \quad N_{Rd} = 489.2\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GB,\text{Tragsicherheit}} = \frac{N_{Rd}}{N_{Ed}} = \frac{489.2\,\mathrm{kN}}{900\,\mathrm{kN}} = 0.54 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

**Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ**

$$
k_{\delta} = 1
$$

### Gleiten

**Reibungswinkel der Sohlfuge** *(Kap. 9.2.18)*

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff} = 1 \cdot 0{}^{\circ} = 0{}^{\circ}
$$

Mit φ = 0 gibt die Reibung in der Sohle keinen Widerstand; eine Haftung zählt nach dem Kapitel nicht.

#### Gleiten – Tragsicherheit

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 900\,\mathrm{kN} \cdot \tan 0{}^{\circ} = 0\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 30\,\mathrm{kN} \quad > \quad T_{Rd} = 0\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Tragsicherheit}} = \frac{T_{Rd}}{T_{Ed}} = \frac{0\,\mathrm{kN}}{30\,\mathrm{kN}} = 0.00 \quad \Rightarrow \quad \text{NICHT erfüllt}
$$

### Balkensystem: Alles einmal

**Querschnittsfläche, «Balken 300×500» (Rechteck)**

$$
A_{\text{Q1}} = b_{\text{Q1}} \cdot h_{\text{Q1}} = 300\,\mathrm{mm} \cdot 500\,\mathrm{mm} = 150000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Balken 300×500» (Rechteck)**

$$
I_{\text{Q1}} = \frac{b_{\text{Q1}} \cdot \left(h_{\text{Q1}}\right)^{3}}{12} = \frac{300\,\mathrm{mm} \cdot \left(500\,\mathrm{mm}\right)^{3}}{12} = 3125\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Querschnittsfläche, «Rundstütze» (Kreis)**

$$
A_{\text{Q2}} = \frac{\pi \cdot \left(d_{\text{Q2}}\right)^{2}}{4} = \frac{\pi \cdot \left(400\,\mathrm{mm}\right)^{2}}{4} = 125664\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Rundstütze» (Kreis)**

$$
I_{\text{Q2}} = \frac{\pi \cdot \left(d_{\text{Q2}}\right)^{4}}{64} = \frac{\pi \cdot \left(400\,\mathrm{mm}\right)^{4}}{64} = 1256.64\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Querschnittsfläche, «Rohr» (Kreisring)**

$$
\begin{aligned}
  A_{\text{Q3}} &= \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{2} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{2}\right)}{4} \\
  &= \frac{\pi \cdot \left(\left(168.3\,\mathrm{mm}\right)^{2} - \left(168.3\,\mathrm{mm} - 2 \cdot 10\,\mathrm{mm}\right)^{2}\right)}{4} \\
  &= 4973\,\mathrm{mm}^{2}
\end{aligned}
$$

**Flächenträgheitsmoment, «Rohr» (Kreisring)**

$$
\begin{aligned}
  I_{\text{Q3}} &= \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{4} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{4}\right)}{64} \\
  &= \frac{\pi \cdot \left(\left(168.3\,\mathrm{mm}\right)^{4} - \left(168.3\,\mathrm{mm} - 2 \cdot 10\,\mathrm{mm}\right)^{4}\right)}{64} \\
  &= 15.64\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

**Querschnittsfläche, «Hohlprofil» (Rechteckrohr)**

$$
\begin{aligned}
  A_{\text{Q4}} &= b_{\text{Q4}} \cdot h_{\text{Q4}} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \\
  &= 200\,\mathrm{mm} \cdot 300\,\mathrm{mm} - \left(200\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right) \cdot \left(300\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right) \\
  &= 11875\,\mathrm{mm}^{2}
\end{aligned}
$$

**Flächenträgheitsmoment, «Hohlprofil» (Rechteckrohr)**

$$
\begin{aligned}
  I_{\text{Q4}} &= \frac{b_{\text{Q4}} \cdot \left(h_{\text{Q4}}\right)^{3} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right)^{3}}{12} \\
  &= \frac{200\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3} - \left(200\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right) \cdot \left(300\,\mathrm{mm} - 2 \cdot 12.5\,\mathrm{mm}\right)^{3}}{12} \\
  &= 146.71\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

**Querschnittsfläche, «Plattenbalken» (T-Querschnitt)**

$$
\begin{aligned}
  A_{\text{Q5}} &= b_{\text{Q5}} \cdot h_{f,\text{Q5}} + b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right) \\
  &= 1200\,\mathrm{mm} \cdot 200\,\mathrm{mm} + 300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right) \\
  &= 360000\,\mathrm{mm}^{2}
\end{aligned}
$$

**Abstand des Schwerpunkts vom oberen Rand, «Plattenbalken» (T-Querschnitt)**

$$
\begin{aligned}
  z_{S,\text{Q5}} &= \frac{b_{\text{Q5}} \cdot \left(h_{f,\text{Q5}}\right)^{2} / 2 + b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right) \cdot \left(h_{\text{Q5}} + h_{f,\text{Q5}}\right) / 2}{A_{\text{Q5}}} \\
  &= \frac{1200\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{2} / 2 + 300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right) \cdot \left(600\,\mathrm{mm} + 200\,\mathrm{mm}\right) / 2}{360000\,\mathrm{mm}^{2}} \\
  &= 200\,\mathrm{mm}
\end{aligned}
$$

**Flächenträgheitsmoment, «Plattenbalken» (T-Querschnitt)**

$$
\begin{aligned}
  I_{\text{Q5}} &= \frac{b_{\text{Q5}} \cdot \left(h_{f,\text{Q5}}\right)^{3}}{12} + b_{\text{Q5}} \cdot h_{f,\text{Q5}} \cdot \left(z_{S,\text{Q5}} - \frac{h_{f,\text{Q5}}}{2}\right)^{2} + \frac{b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right)^{3}}{12} + b_{w,\text{Q5}} \cdot \left(h_{\text{Q5}} - h_{f,\text{Q5}}\right) \cdot \left(\frac{h_{\text{Q5}} + h_{f,\text{Q5}}}{2} - z_{S,\text{Q5}}\right)^{2} \\
  &= \frac{1200\,\mathrm{mm} \cdot \left(200\,\mathrm{mm}\right)^{3}}{12} + 1200\,\mathrm{mm} \cdot 200\,\mathrm{mm} \cdot \left(200\,\mathrm{mm} - \frac{200\,\mathrm{mm}}{2}\right)^{2} + \frac{300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right)^{3}}{12} + 300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm} - 200\,\mathrm{mm}\right) \cdot \left(\frac{600\,\mathrm{mm} + 200\,\mathrm{mm}}{2} - 200\,\mathrm{mm}\right)^{2} \\
  &= 9600\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

**Querschnittsfläche, «Walzprofil» (Doppel-T)**

$$
\begin{aligned}
  A_{\text{Q6}} &= 2 \cdot b_{\text{Q6}} \cdot t_{f,\text{Q6}} + t_{w,\text{Q6}} \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f,\text{Q6}}\right) \\
  &= 2 \cdot 300\,\mathrm{mm} \cdot 19\,\mathrm{mm} + 11\,\mathrm{mm} \cdot \left(300\,\mathrm{mm} - 2 \cdot 19\,\mathrm{mm}\right) \\
  &= 14282\,\mathrm{mm}^{2}
\end{aligned}
$$

**Flächenträgheitsmoment, «Walzprofil» (Doppel-T)**

$$
\begin{aligned}
  I_{\text{Q6}} &= \frac{b_{\text{Q6}} \cdot \left(h_{\text{Q6}}\right)^{3} - \left(b_{\text{Q6}} - t_{w,\text{Q6}}\right) \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f,\text{Q6}}\right)^{3}}{12} \\
  &= \frac{300\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3} - \left(300\,\mathrm{mm} - 11\,\mathrm{mm}\right) \cdot \left(300\,\mathrm{mm} - 2 \cdot 19\,\mathrm{mm}\right)^{3}}{12} \\
  &= 241.87\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

**Querschnittsfläche, «Fundamentbalken» (Trapez)**

$$
A_{\text{Q7}} = \frac{\left(b_{o,\text{Q7}} + b_{u,\text{Q7}}\right) \cdot h_{\text{Q7}}}{2} = \frac{\left(600\,\mathrm{mm} + 400\,\mathrm{mm}\right) \cdot 500\,\mathrm{mm}}{2} = 250000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Fundamentbalken» (Trapez)**

$$
\begin{aligned}
  I_{\text{Q7}} &= \frac{\left(h_{\text{Q7}}\right)^{3} \cdot \left(\left(b_{o,\text{Q7}}\right)^{2} + 4 \cdot b_{o,\text{Q7}} \cdot b_{u,\text{Q7}} + \left(b_{u,\text{Q7}}\right)^{2}\right)}{36 \cdot \left(b_{o,\text{Q7}} + b_{u,\text{Q7}}\right)} \\
  &= \frac{\left(500\,\mathrm{mm}\right)^{3} \cdot \left(\left(600\,\mathrm{mm}\right)^{2} + 4 \cdot 600\,\mathrm{mm} \cdot 400\,\mathrm{mm} + \left(400\,\mathrm{mm}\right)^{2}\right)}{36 \cdot \left(600\,\mathrm{mm} + 400\,\mathrm{mm}\right)} \\
  &= 5138.89\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

**Querschnittsfläche, «Von Hand» (von Hand)**

$$
A_{\text{Q8}} = 15000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Von Hand» (von Hand)**

$$
I_{\text{Q8}} = 120\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Querschnittsfläche, «Deckenstreifen» (Platte «Decke»)**

$$
A_{\text{Q9}} = b \cdot h = 1000\,\mathrm{mm} \cdot 300\,\mathrm{mm} = 300000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Deckenstreifen» (Platte «Decke»)**

$$
I_{\text{Q9}} = \frac{b \cdot \left(h\right)^{3}}{12} = \frac{1000\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3}}{12} = 2250\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Querschnittsfläche, «Kasten» (Bruttoquerschnitt der Querschnittsanalyse «Kastenträger»)**

$$
A_{\text{Q10}} = 330000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Kasten» (Bruttoquerschnitt der Querschnittsanalyse «Kastenträger»)**

$$
I_{\text{Q10}} = 13275\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Dehnsteifigkeit, «Balken 300×500» aus C30/37**

$$
EA_{\text{Q1,C30/37}} = E_{cm} \cdot A_{\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 150000\,\mathrm{mm}^{2} = 5043\,\mathrm{MN}
$$

**Biegesteifigkeit, «Balken 300×500» aus C30/37**

$$
EI_{\text{Q1,C30/37}} = E_{cm} \cdot I_{\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 3125\,\cdot 10^{6}\,\mathrm{mm}^{4} = 105062\,\mathrm{kNm}^{2}
$$

**Dehnsteifigkeit, «Rundstütze» aus C30/37**

$$
EA_{\text{Q2,C30/37}} = E_{cm} \cdot A_{\text{Q2}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125664\,\mathrm{mm}^{2} = 4225\,\mathrm{MN}
$$

**Biegesteifigkeit, «Rundstütze» aus C30/37**

$$
EI_{\text{Q2,C30/37}} = E_{cm} \cdot I_{\text{Q2}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1256.64\,\cdot 10^{6}\,\mathrm{mm}^{4} = 42248\,\mathrm{kNm}^{2}
$$

**Dehnsteifigkeit, «Plattenbalken» aus C30/37**

$$
EA_{\text{Q5,C30/37}} = E_{cm} \cdot A_{\text{Q5}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 360000\,\mathrm{mm}^{2} = 12103\,\mathrm{MN}
$$

**Biegesteifigkeit, «Plattenbalken» aus C30/37**

$$
EI_{\text{Q5,C30/37}} = E_{cm} \cdot I_{\text{Q5}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 9600\,\cdot 10^{6}\,\mathrm{mm}^{4} = 322750\,\mathrm{kNm}^{2}
$$

**Dehnsteifigkeit, «Rohr» aus B500B**

$$
EA_{\text{Q3,B500B}} = E_s \cdot A_{\text{Q3}} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 4973\,\mathrm{mm}^{2} = 995\,\mathrm{MN}
$$

**Biegesteifigkeit, «Rohr» aus B500B**

$$
EI_{\text{Q3,B500B}} = E_s \cdot I_{\text{Q3}} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 15.64\,\cdot 10^{6}\,\mathrm{mm}^{4} = 3128\,\mathrm{kNm}^{2}
$$

**Dehnsteifigkeit, «Walzprofil» aus B500B**

$$
EA_{\text{Q6,B500B}} = E_s \cdot A_{\text{Q6}} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 14282\,\mathrm{mm}^{2} = 2856\,\mathrm{MN}
$$

**Biegesteifigkeit, «Walzprofil» aus B500B**

$$
EI_{\text{Q6,B500B}} = E_s \cdot I_{\text{Q6}} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 241.87\,\cdot 10^{6}\,\mathrm{mm}^{4} = 48374\,\mathrm{kNm}^{2}
$$

**Dehnsteifigkeit, «Fundamentbalken» aus C30/37**

$$
EA_{\text{Q7,C30/37}} = E_{cm} \cdot A_{\text{Q7}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 250000\,\mathrm{mm}^{2} = 8405\,\mathrm{MN}
$$

**Biegesteifigkeit, «Fundamentbalken» aus C30/37**

$$
EI_{\text{Q7,C30/37}} = E_{cm} \cdot I_{\text{Q7}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 5138.89\,\cdot 10^{6}\,\mathrm{mm}^{4} = 172768\,\mathrm{kNm}^{2}
$$

**Dehnsteifigkeit, «Hohlprofil» aus B500B**

$$
EA_{\text{Q4,B500B}} = E_s \cdot A_{\text{Q4}} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 11875\,\mathrm{mm}^{2} = 2375\,\mathrm{MN}
$$

**Biegesteifigkeit, «Hohlprofil» aus B500B**

$$
EI_{\text{Q4,B500B}} = E_s \cdot I_{\text{Q4}} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 146.71\,\cdot 10^{6}\,\mathrm{mm}^{4} = 29342\,\mathrm{kNm}^{2}
$$

> **Annahme:** Steifigkeit nach Vorgabe, nicht nachgeschlagen: E\_cm für Beton und E\_s für Betonstahl, am ungerissenen Bruttoquerschnitt, ohne Schubverformung; Gleichgewicht am unverformten System (Theorie 1. Ordnung).

**Stäbe**

| Stab | Knoten | $L\ [\mathrm{m}]$ | $\alpha\ [°]$ | Querschnitt | $EA\ [\mathrm{MN}]$ | $EI\ [\mathrm{kNm}^{2}]$ | Gelenk | Linienlager |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | K1 – K2 | $8.000$ | $0.0$ | Balken 300×500 | $5043$ | $105062$ | – | quer Bettung 20000 kN/m² |
| L2 | K2 – K3 | $3.000$ | $90.0$ | Rundstütze | $4225$ | $42248$ | – | – |
| L3 | K3 – K4 | $4.472$ | $26.6$ | Plattenbalken | $12103$ | $322750$ | – | – |
| L4 | K4 – K5 | $5.000$ | $-90.0$ | Rohr | $995$ | $3128$ | beide | – |
| L5 | K5 – K6 | $3.000$ | $0.0$ | Walzprofil | $2856$ | $48374$ | Anfang | – |
| L6 | K6 – K7 | $2.000$ | $0.0$ | Fundamentbalken | $8405$ | $172768$ | – | quer fest |
| L7 | K7 – K8 | $1.000$ | $-90.0$ | kein Stab | – | – | – | quer fest |
| L8 | K6 – K9 | $2.000$ | $90.0$ | Hohlprofil | $2375$ | $29342$ | – | – |

**Lager**

| Lager | Knoten | $x$ | $z$ | $\varphi$ |
| ---: | ---: | ---: | ---: | ---: |
| A1 | K1 | fest | Feder 50000 kN/m | Feder 10000 kNm/rad |
| A2 | K5 | fest | fest | frei |

**Steifigkeitsmatrix eines Stabs, in seinen Achsen**

$$
\mathbf{k} = \begin{bmatrix} \frac{EA}{L} & 0 & 0 & -\frac{EA}{L} & 0 & 0 \\ 0 & \frac{12EI}{L^3} & \frac{6EI}{L^2} & 0 & -\frac{12EI}{L^3} & \frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{4EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{2EI}{L} \\ -\frac{EA}{L} & 0 & 0 & \frac{EA}{L} & 0 & 0 \\ 0 & -\frac{12EI}{L^3} & -\frac{6EI}{L^2} & 0 & \frac{12EI}{L^3} & -\frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{2EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{4EI}{L} \end{bmatrix}
$$

**Von den Achsen des Systems in die des Stabs**

$$
\mathbf{d} = \mathbf{T} \cdot \mathbf{d}_{glob} \qquad \mathbf{T} = \begin{bmatrix} \mathbf{R} & \mathbf{0} \\ \mathbf{0} & \mathbf{R} \end{bmatrix} \qquad \mathbf{R} = \begin{bmatrix} \cos\alpha & \sin\alpha & 0 \\ -\sin\alpha & \cos\alpha & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

**Bettung eines Stabs, quer und längs**

$$
\mathbf{k}_{b} = \frac{k_{\perp} \cdot L}{420} \begin{bmatrix} 156 & 22L & 54 & -13L \\ 22L & 4L^2 & 13L & -3L^2 \\ 54 & 13L & 156 & -22L \\ -13L & -3L^2 & -22L & 4L^2 \end{bmatrix} \qquad \mathbf{k}_{b,\parallel} = \frac{k_{\parallel} \cdot L}{6} \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}
$$

**Arbeitsgleiche Knotenkräfte der Lasten auf einem Stab**

$$
f_i = \int_0^L N_i(x) \cdot p(x)\,\mathrm{d}x + \int_0^L N_i'(x) \cdot m(x)\,\mathrm{d}x + \sum_j N_i(a_j) \cdot P_j + \sum_j N_i'(a_j) \cdot M_j
$$

**Gesamtsteifigkeitsmatrix und Gleichungssystem**

$$
\mathbf{K} = \sum_{\text{Stäbe}} \mathbf{T}^{\mathsf{T}} \cdot \mathbf{k} \cdot \mathbf{T} \qquad \mathbf{K} \cdot \mathbf{x} = \mathbf{F}
$$

Ein Gelenk gibt dem Stabende eine eigene Drehung als Unbekannte; der Knoten dreht sich unabhängig davon.

> **Hinweis:** Verdrehung nicht bestimmbar, da keine Steifigkeit: K5. Alle Stäbe sind dort gelenkig angeschlossen; die Drehung ist gestrichen und null gesetzt.

**Schnittgrössen aus den Kräften an den Stabenden**

$$
N(0) = -s_{u,a} \qquad V(0) = s_{v,a} \qquad M(0) = -s_{\theta,a} \qquad \frac{\mathrm{d}N}{\mathrm{d}x} = -p_x \qquad \frac{\mathrm{d}V}{\mathrm{d}x} = p_y \qquad \frac{\mathrm{d}M}{\mathrm{d}x} = V - m
$$

**Biegelinie und Längsverschiebung**

$$
v'' = \frac{M}{EI} \qquad u' = \frac{N}{EA}
$$

39 Unbekannte.

#### Lastfall «Eigengewicht»

**Verschiebungen der Knoten**

| Knoten | $u_x\ [\mathrm{mm}]$ | $u_z\ [\mathrm{mm}]$ | $\varphi\ [\mathrm{mrad}]$ |
| ---: | ---: | ---: | ---: |
| K1 | $0.00$ | $-0.09$ | $-0.129$ |
| K2 | $0.00$ | $-1.03$ | $-0.151$ |
| K3 | $-0.08$ | $-1.04$ | $0.207$ |
| K4 | $-0.58$ | $-0.05$ | $0.290$ |
| K5 | $0.00$ | $0.00$ | nicht bestimmbar |
| K6 | $0.00$ | $0.00$ | $0.000$ |
| K7 | $0.00$ | $0.00$ | $0.000$ |
| K9 | $0.00$ | $0.00$ | $0.000$ |

**Schnittgrössen an den Stabenden**

| Stab | $N_{a}\ [\mathrm{kN}]$ | $V_{a}\ [\mathrm{kN}]$ | $M_{a}\ [\mathrm{kNm}]$ | $N_{b}\ [\mathrm{kN}]$ | $V_{b}\ [\mathrm{kN}]$ | $M_{b}\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $0.0$ | $4.4$ | $-1.3$ | $0.0$ | $8.9$ | $5.1$ |
| L2 | $-8.9$ | $0.0$ | $5.1$ | $-8.9$ | $0.0$ | $5.1$ |
| L3 | $-4.0$ | $8.0$ | $0.1$ | $4.0$ | $-8.0$ | $0.0$ |
| L4 | $-9.0$ | $0.0$ | $0.0$ | $-9.0$ | $0.0$ | $0.0$ |
| L5 | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ |
| L6 | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ |
| L8 | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ |

**Lagerkräfte, auf das Tragwerk**

| Lager | $R_x\ [\mathrm{kN}]$ | $R_z\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: |
| A1 (K1) | $0.0$ | $4.4$ | $1.3$ |
| A2 (K5) | $0.0$ | $9.0$ | $0.0$ |
| K6 | $0.0$ | $0.0$ | $0.0$ |
| K7 | $0.0$ | $0.0$ | $0.0$ |
| L6: Lasten geradewegs ins Linienlager | $0.0$ | $20.0$ | $320.0$ |
| L1: Bettung, Summe | $0.0$ | $84.5$ | $430.4$ |

Bei Linienlagern und Bettung steht die Summe; ihr Moment um den Ursprung.

**Extremwerte**

| Stab | Grösse | kleinst | $x\ [\mathrm{m}]$ | grösst | $x\ [\mathrm{m}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $N$ | $0.0\ \mathrm{kN}$ | $3.00$ | $0.0\ \mathrm{kN}$ | $4.00$ |
| L1 | $V$ | $-0.1\ \mathrm{kN}$ | $3.68$ | $8.9\ \mathrm{kN}$ | $8.00$ |
| L1 | $M$ | $-4.1\ \mathrm{kNm}$ | $6.00$ | $5.1\ \mathrm{kNm}$ | $8.00$ |
| L1 | $w$ | $-0.09\ \mathrm{mm}$ | $5.49$ | $0.01\ \mathrm{mm}$ | $1.37$ |
| L2 | $N$ | $-8.9\ \mathrm{kN}$ | $0.00$ | $-8.9\ \mathrm{kN}$ | $0.00$ |
| L2 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L2 | $M$ | $5.1\ \mathrm{kNm}$ | $0.00$ | $5.1\ \mathrm{kNm}$ | $3.00$ |
| L2 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.13\ \mathrm{mm}$ | $1.50$ |
| L3 | $N$ | $-4.0\ \mathrm{kN}$ | $0.00$ | $4.0\ \mathrm{kN}$ | $4.47$ |
| L3 | $V$ | $-8.0\ \mathrm{kN}$ | $4.47$ | $8.0\ \mathrm{kN}$ | $0.00$ |
| L3 | $M$ | $0.0\ \mathrm{kNm}$ | $4.47$ | $9.0\ \mathrm{kNm}$ | $2.23$ |
| L3 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.06\ \mathrm{mm}$ | $2.23$ |
| L4 | $N$ | $-9.0\ \mathrm{kN}$ | $0.00$ | $-9.0\ \mathrm{kN}$ | $0.00$ |
| L4 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L4 | $M$ | $0.0\ \mathrm{kNm}$ | $5.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L4 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $2.52$ |
| L5 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L5 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L5 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L5 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L6 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L6 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L6 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L6 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L8 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L8 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L8 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L8 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |

Grösste Durchbiegung gegen die Sehne: L2, w = 0.13 mm bei x = 1.50 m, L/w = 22301.

**Gleichgewichtsprobe (Moment um den Ursprung)**

|  | Lasten | Lager | Summe |  |
| ---: | ---: | ---: | ---: | ---: |
| $\sum F_x$ | $0.000$ | $0.000$ | $0.000$ | kN |
| $\sum F_z$ | $-117.889$ | $117.889$ | $0.000$ | kN |
| $\sum M_0$ | $-859.219$ | $859.219$ | $0.000$ | kNm |

#### Lastfall «Schnee und Wind»

**Verschiebungen der Knoten**

| Knoten | $u_x\ [\mathrm{mm}]$ | $u_z\ [\mathrm{mm}]$ | $\varphi\ [\mathrm{mrad}]$ |
| ---: | ---: | ---: | ---: |
| K1 | $0.00$ | $-0.01$ | $0.017$ |
| K2 | $0.03$ | $-0.43$ | $-0.394$ |
| K3 | $1.43$ | $-0.43$ | $-0.042$ |
| K4 | $1.24$ | $-0.06$ | $0.173$ |
| K5 | $0.00$ | $0.00$ | nicht bestimmbar |
| K6 | $0.00$ | $0.00$ | $0.000$ |
| K7 | $0.00$ | $0.00$ | $0.000$ |
| K9 | $0.00$ | $0.00$ | $0.000$ |

**Schnittgrössen an den Stabenden**

| Stab | $N_{a}\ [\mathrm{kN}]$ | $V_{a}\ [\mathrm{kN}]$ | $M_{a}\ [\mathrm{kNm}]$ | $N_{b}\ [\mathrm{kN}]$ | $V_{b}\ [\mathrm{kN}]$ | $M_{b}\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $18.0$ | $0.3$ | $0.2$ | $18.0$ | $0.3$ | $-19.0$ |
| L2 | $-0.3$ | $18.0$ | $-19.0$ | $-0.3$ | $10.0$ | $23.0$ |
| L3 | $-0.1$ | $0.2$ | $23.0$ | $5.3$ | $-10.5$ | $0.0$ |
| L4 | $-11.7$ | $0.0$ | $0.0$ | $-11.7$ | $0.0$ | $0.0$ |
| L5 | $0.0$ | $1.5$ | $0.0$ | $0.0$ | $1.5$ | $0.5$ |
| L6 | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ |
| L8 | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ |

**Lagerkräfte, auf das Tragwerk**

| Lager | $R_x\ [\mathrm{kN}]$ | $R_z\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: |
| A1 (K1) | $-18.0$ | $0.3$ | $-0.2$ |
| A2 (K5) | $0.0$ | $13.2$ | $0.0$ |
| K6 | $0.0$ | $-1.5$ | $0.5$ |
| K7 | $0.0$ | $0.0$ | $0.0$ |
| L1: Bettung, Summe | $0.0$ | $0.0$ | $21.3$ |

Bei Linienlagern und Bettung steht die Summe; ihr Moment um den Ursprung.

**Extremwerte**

| Stab | Grösse | kleinst | $x\ [\mathrm{m}]$ | grösst | $x\ [\mathrm{m}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $N$ | $18.0\ \mathrm{kN}$ | $4.00$ | $18.0\ \mathrm{kN}$ | $0.00$ |
| L1 | $V$ | $-5.7\ \mathrm{kN}$ | $6.29$ | $0.3\ \mathrm{kN}$ | $0.33$ |
| L1 | $M$ | $-19.0\ \mathrm{kNm}$ | $7.97$ | $0.5\ \mathrm{kNm}$ | $1.58$ |
| L1 | $w$ | $-0.36\ \mathrm{mm}$ | $5.53$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L2 | $N$ | $-0.3\ \mathrm{kN}$ | $0.00$ | $-0.3\ \mathrm{kN}$ | $0.00$ |
| L2 | $V$ | $10.0\ \mathrm{kN}$ | $1.50$ | $18.0\ \mathrm{kN}$ | $0.00$ |
| L2 | $M$ | $-19.0\ \mathrm{kNm}$ | $0.00$ | $23.0\ \mathrm{kNm}$ | $3.00$ |
| L2 | $w$ | $-0.01\ \mathrm{mm}$ | $0.17$ | $0.19\ \mathrm{mm}$ | $2.00$ |
| L3 | $N$ | $-0.1\ \mathrm{kN}$ | $0.00$ | $5.3\ \mathrm{kN}$ | $4.47$ |
| L3 | $V$ | $-10.5\ \mathrm{kN}$ | $4.47$ | $0.2\ \mathrm{kN}$ | $0.00$ |
| L3 | $M$ | $0.0\ \mathrm{kNm}$ | $4.47$ | $23.0\ \mathrm{kNm}$ | $0.10$ |
| L3 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.13\ \mathrm{mm}$ | $2.00$ |
| L4 | $N$ | $-11.7\ \mathrm{kN}$ | $0.00$ | $-11.7\ \mathrm{kN}$ | $0.00$ |
| L4 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L4 | $M$ | $0.0\ \mathrm{kNm}$ | $5.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L4 | $w$ | $0.00\ \mathrm{mm}$ | $2.60$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L5 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L5 | $V$ | $1.5\ \mathrm{kN}$ | $0.00$ | $1.5\ \mathrm{kN}$ | $0.00$ |
| L5 | $M$ | $-1.8\ \mathrm{kNm}$ | $1.50$ | $2.2\ \mathrm{kNm}$ | $1.50$ |
| L5 | $w$ | $0.00\ \mathrm{mm}$ | $2.33$ | $0.01\ \mathrm{mm}$ | $1.00$ |
| L6 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L6 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L6 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L6 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L8 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L8 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L8 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L8 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |

Grösste Durchbiegung gegen die Sehne: L1, w = -0.36 mm bei x = 5.53 m, L/w = 22002.

**Gleichgewichtsprobe (Moment um den Ursprung)**

|  | Lasten | Lager | Summe |  |
| ---: | ---: | ---: | ---: | ---: |
| $\sum F_x$ | $18.000$ | $-18.000$ | $0.000$ | kN |
| $\sum F_z$ | $-12.000$ | $12.000$ | $0.000$ | kN |
| $\sum M_0$ | $-158.000$ | $158.000$ | $0.000$ | kNm |

#### Kombination «Tragsicherheit»

1\.35 · Eigengewicht + 1.5 · Schnee und Wind

**Verschiebungen der Knoten**

| Knoten | $u_x\ [\mathrm{mm}]$ | $u_z\ [\mathrm{mm}]$ | $\varphi\ [\mathrm{mrad}]$ |
| ---: | ---: | ---: | ---: |
| K1 | $0.00$ | $-0.13$ | $-0.150$ |
| K2 | $0.04$ | $-2.04$ | $-0.796$ |
| K3 | $2.03$ | $-2.05$ | $0.217$ |
| K4 | $1.08$ | $-0.15$ | $0.651$ |
| K5 | $0.00$ | $0.00$ | nicht bestimmbar |
| K6 | $0.00$ | $0.00$ | $0.000$ |
| K7 | $0.00$ | $0.00$ | $0.000$ |
| K9 | $0.00$ | $0.00$ | $0.000$ |

**Schnittgrössen an den Stabenden**

| Stab | $N_{a}\ [\mathrm{kN}]$ | $V_{a}\ [\mathrm{kN}]$ | $M_{a}\ [\mathrm{kNm}]$ | $N_{b}\ [\mathrm{kN}]$ | $V_{b}\ [\mathrm{kN}]$ | $M_{b}\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $27.0$ | $6.4$ | $-1.5$ | $27.0$ | $12.4$ | $-21.7$ |
| L2 | $-12.4$ | $27.0$ | $-21.7$ | $-12.4$ | $15.0$ | $41.3$ |
| L3 | $-5.6$ | $11.1$ | $34.5$ | $13.3$ | $-26.6$ | $0.0$ |
| L4 | $-29.7$ | $0.0$ | $0.0$ | $-29.7$ | $0.0$ | $0.0$ |
| L5 | $0.0$ | $2.2$ | $0.0$ | $0.0$ | $2.2$ | $0.8$ |
| L6 | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ |
| L8 | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ | $0.0$ |

**Lagerkräfte, auf das Tragwerk**

| Lager | $R_x\ [\mathrm{kN}]$ | $R_z\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: |
| A1 (K1) | $-27.0$ | $6.4$ | $1.5$ |
| A2 (K5) | $0.0$ | $32.0$ | $0.0$ |
| K6 | $0.0$ | $-2.2$ | $0.8$ |
| K7 | $0.0$ | $0.0$ | $0.0$ |
| L6: Lasten geradewegs ins Linienlager | $0.0$ | $27.0$ | $432.0$ |
| L1: Bettung, Summe | $0.0$ | $114.1$ | $613.0$ |

Bei Linienlagern und Bettung steht die Summe; ihr Moment um den Ursprung.

**Extremwerte**

| Stab | Grösse | kleinst | $x\ [\mathrm{m}]$ | grösst | $x\ [\mathrm{m}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $N$ | $27.0\ \mathrm{kN}$ | $5.00$ | $27.0\ \mathrm{kN}$ | $2.00$ |
| L1 | $V$ | $-6.6\ \mathrm{kN}$ | $5.63$ | $12.4\ \mathrm{kN}$ | $8.00$ |
| L1 | $M$ | $-26.3\ \mathrm{kNm}$ | $7.18$ | $4.5\ \mathrm{kNm}$ | $2.00$ |
| L1 | $w$ | $-0.66\ \mathrm{mm}$ | $5.52$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L2 | $N$ | $-12.4\ \mathrm{kN}$ | $0.00$ | $-12.4\ \mathrm{kN}$ | $0.00$ |
| L2 | $V$ | $15.0\ \mathrm{kN}$ | $1.50$ | $27.0\ \mathrm{kN}$ | $0.00$ |
| L2 | $M$ | $-21.7\ \mathrm{kNm}$ | $0.00$ | $41.3\ \mathrm{kNm}$ | $3.00$ |
| L2 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.46\ \mathrm{mm}$ | $1.87$ |
| L3 | $N$ | $-5.6\ \mathrm{kN}$ | $0.00$ | $13.3\ \mathrm{kN}$ | $4.47$ |
| L3 | $V$ | $-26.6\ \mathrm{kN}$ | $4.47$ | $11.1\ \mathrm{kN}$ | $0.00$ |
| L3 | $M$ | $0.0\ \mathrm{kNm}$ | $4.47$ | $41.9\ \mathrm{kNm}$ | $1.32$ |
| L3 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.27\ \mathrm{mm}$ | $2.07$ |
| L4 | $N$ | $-29.7\ \mathrm{kN}$ | $0.00$ | $-29.7\ \mathrm{kN}$ | $0.00$ |
| L4 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L4 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L4 | $w$ | $0.00\ \mathrm{mm}$ | $2.24$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L5 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L5 | $V$ | $2.2\ \mathrm{kN}$ | $0.00$ | $2.2\ \mathrm{kN}$ | $0.00$ |
| L5 | $M$ | $-2.6\ \mathrm{kNm}$ | $1.50$ | $3.4\ \mathrm{kNm}$ | $1.50$ |
| L5 | $w$ | $0.00\ \mathrm{mm}$ | $2.33$ | $0.02\ \mathrm{mm}$ | $1.00$ |
| L6 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L6 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L6 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L6 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L8 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L8 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L8 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L8 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |

Grösste Durchbiegung gegen die Sehne: L1, w = -0.66 mm bei x = 5.52 m, L/w = 12114.

**Gleichgewichtsprobe (Moment um den Ursprung)**

|  | Lasten | Lager | Summe |  |
| ---: | ---: | ---: | ---: | ---: |
| $\sum F_x$ | $27.000$ | $-27.000$ | $0.000$ | kN |
| $\sum F_z$ | $-177.150$ | $177.150$ | $0.000$ | kN |
| $\sum M_0$ | $-1396.945$ | $1396.945$ | $0.000$ | kNm |

### Balkensystem: Beweglich

**Querschnittsfläche, «Rechteck» (Rechteck)**

$$
A = b \cdot h = 300\,\mathrm{mm} \cdot 600\,\mathrm{mm} = 180000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Rechteck» (Rechteck)**

$$
I = \frac{b \cdot \left(h\right)^{3}}{12} = \frac{300\,\mathrm{mm} \cdot \left(600\,\mathrm{mm}\right)^{3}}{12} = 5400\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Dehnsteifigkeit, «Rechteck» aus C30/37**

$$
EA = E_{cm} \cdot A = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 180000\,\mathrm{mm}^{2} = 6052\,\mathrm{MN}
$$

**Biegesteifigkeit, «Rechteck» aus C30/37**

$$
EI = E_{cm} \cdot I = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 5400\,\cdot 10^{6}\,\mathrm{mm}^{4} = 181547\,\mathrm{kNm}^{2}
$$

> **Annahme:** Steifigkeit nach Vorgabe, nicht nachgeschlagen: E\_cm für Beton und E\_s für Betonstahl, am ungerissenen Bruttoquerschnitt, ohne Schubverformung; Gleichgewicht am unverformten System (Theorie 1. Ordnung).

**Stäbe**

| Stab | Knoten | $L\ [\mathrm{m}]$ | $\alpha\ [°]$ | Querschnitt | $EA\ [\mathrm{MN}]$ | $EI\ [\mathrm{kNm}^{2}]$ | Gelenk | Linienlager |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | K1 – K2 | $5.000$ | $0.0$ | Rechteck | $6052$ | $181547$ | – | – |

**Lager**

| Lager | Knoten | $x$ | $z$ | $\varphi$ |
| ---: | ---: | ---: | ---: | ---: |
| A1 | K1 | frei | fest | frei |
| A2 | K2 | frei | fest | frei |

> **Warnung:** Das System ist beweglich – die Steifigkeitsmatrix ist singulär und lässt sich nicht invertieren. Ohne Widerstand bewegen sich: K1 und K2. Es fehlt ein Lager, ein Stab oder ein Gelenk ist zu viel.

**Steifigkeitsmatrix eines Stabs, in seinen Achsen**

$$
\mathbf{k} = \begin{bmatrix} \frac{EA}{L} & 0 & 0 & -\frac{EA}{L} & 0 & 0 \\ 0 & \frac{12EI}{L^3} & \frac{6EI}{L^2} & 0 & -\frac{12EI}{L^3} & \frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{4EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{2EI}{L} \\ -\frac{EA}{L} & 0 & 0 & \frac{EA}{L} & 0 & 0 \\ 0 & -\frac{12EI}{L^3} & -\frac{6EI}{L^2} & 0 & \frac{12EI}{L^3} & -\frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{2EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{4EI}{L} \end{bmatrix}
$$

**Von den Achsen des Systems in die des Stabs**

$$
\mathbf{d} = \mathbf{T} \cdot \mathbf{d}_{glob} \qquad \mathbf{T} = \begin{bmatrix} \mathbf{R} & \mathbf{0} \\ \mathbf{0} & \mathbf{R} \end{bmatrix} \qquad \mathbf{R} = \begin{bmatrix} \cos\alpha & \sin\alpha & 0 \\ -\sin\alpha & \cos\alpha & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

**Arbeitsgleiche Knotenkräfte der Lasten auf einem Stab**

$$
f_i = \int_0^L N_i(x) \cdot p(x)\,\mathrm{d}x + \int_0^L N_i'(x) \cdot m(x)\,\mathrm{d}x + \sum_j N_i(a_j) \cdot P_j + \sum_j N_i'(a_j) \cdot M_j
$$

**Gesamtsteifigkeitsmatrix und Gleichungssystem**

$$
\mathbf{K} = \sum_{\text{Stäbe}} \mathbf{T}^{\mathsf{T}} \cdot \mathbf{k} \cdot \mathbf{T} \qquad \mathbf{K} \cdot \mathbf{x} = \mathbf{F}
$$

**Steifigkeitsmatrix L1, L = 5.000 m (kN, m)**

$$
\mathbf{k}_{\text{L1}} = \begin{bmatrix} 1.210 \cdot 10^{6} & 0 & 0 & -1.210 \cdot 10^{6} & 0 & 0 \\ 0 & 17428 & 43571 & 0 & -17428 & 43571 \\ 0 & 43571 & 145237 & 0 & -43571 & 72619 \\ -1.210 \cdot 10^{6} & 0 & 0 & 1.210 \cdot 10^{6} & 0 & 0 \\ 0 & -17428 & -43571 & 0 & 17428 & -43571 \\ 0 & 43571 & 72619 & 0 & -43571 & 145237 \end{bmatrix}
$$

**Schnittgrössen aus den Kräften an den Stabenden**

$$
N(0) = -s_{u,a} \qquad V(0) = s_{v,a} \qquad M(0) = -s_{\theta,a} \qquad \frac{\mathrm{d}N}{\mathrm{d}x} = -p_x \qquad \frac{\mathrm{d}V}{\mathrm{d}x} = p_y \qquad \frac{\mathrm{d}M}{\mathrm{d}x} = V - m
$$

**Biegelinie und Längsverschiebung**

$$
v'' = \frac{M}{EI} \qquad u' = \frac{N}{EA}
$$

4 Unbekannte: 1. u\_x(K1), 2. φ(K1), 3. u\_x(K2), 4. φ(K2).

**Gesamtsteifigkeitsmatrix (kN, m)**

$$
\mathbf{K} = \begin{bmatrix} 1.210 \cdot 10^{6} & 0 & -1.210 \cdot 10^{6} & 0 \\ 0 & 145237 & 0 & 72619 \\ -1.210 \cdot 10^{6} & 0 & 1.210 \cdot 10^{6} & 0 \\ 0 & 72619 & 0 & 145237 \end{bmatrix}
$$

## Verwendete Formeln

### Querschnitt

**Bewehrungsquerschnitt über die Breite b** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h}
$$

**Höhe der Distanzhalter**

$$
h_{Dist} = \text{OK innere untere Lage} - \text{UK innere obere Lage}
$$

**Querschnitt eines Bügelschenkels** *(SIA 262:2025, 5.5.2)*

$$
A_{\varnothing,V} = \frac{\pi \cdot \left(\varnothing_{V}\right)^{2}}{4}
$$

### Beton

**Beiwert zur Berücksichtigung der Festigkeitsminderung** *(SIA 262:2025, 2.4.2.3)*

$$
\eta_{fc} = \min\left[\left(\frac{40\,\mathrm{N}/\mathrm{mm}^{2}}{f_{ck}}\right)^{1/3};\ 1.0\right]
$$

**Bemessungswert der Betondruckfestigkeit** *(SIA 262:2025, 2.4.2.3)*

$$
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}
$$

**Mittelwert der Zylinderdruckfestigkeit** *(SIA 262:2025, 3.1.2.2.2)*

$$
f_{cm} = f_{ck} + 8\,\mathrm{N}/\mathrm{mm}^{2}
$$

**Mittelwert des Elastizitätsmoduls** *(SIA 262:2025, 3.1.2.3.3)*

$$
E_{cm} = k_e \cdot \sqrt[3]{f_{cm}} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

**Bemessungswert der Schubspannungsgrenze** *(SIA 262:2025, 2.4.2.4)*

$$
\tau_{cd} = \frac{0.3 \cdot \sqrt{f_{ck}}}{\gamma_c} \quad \left(f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

**Bemessungswert des Elastizitätsmoduls** *(SIA 262:2025, 4.2.1.15)*

$$
E_{cd} = \frac{E_{cm}}{\gamma_{cE}}
$$

**Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung** *(SIA 262:2025, 4.2.1.6)*

$$
k_{\sigma} = \frac{E_{cd}}{400 \cdot f_{cd}}
$$

### Betonstahl

**Bemessungswert der Fliessgrenze** *(SIA 262:2025, 2.4.2.5)*

$$
f_{yd} = \frac{f_{yk}}{\gamma_s}
$$

**Bemessungswert der Fliessgrenze auf Druck** *(SIA 262:2025, 2.4.2.5)*

$$
f_{yd}^{-} = \frac{f_{yk}^{-}}{\gamma_s}
$$

### Biegung und Normalkraft

Druckzone als Spannungsblock der Höhe 0.85·x mit durchgehend f\_cd; gedrückter Stahl bleibt unberücksichtigt. Die Bewehrung ist je Seite zu einer Lage zusammengefasst, das Moment bezieht sich auf die halbe Querschnittshöhe.

Der Querschnitt bleibt eben (Bernoulli). Zu jeder Dehnungsebene ergeben sich Normalkraft und Moment aus den Spannungen über die Höhe; Zug ist positiv, das Moment bezieht sich auf die halbe Querschnittshöhe. Die Resistenzlinie ist der Rand aller zulässigen Ebenen: an ihm erreicht der Stahl ε\_ud, der Beton am gedrückten Rand −ε\_c2d oder, wenn der ganze Querschnitt gedrückt ist, im Punkt C −ε\_c1d.

Der Beton ist in 200 Fasern über die Höhe geteilt, die Bewehrung zählt Lage für Lage, und an ihrer Stelle zählt der Stahl statt des Betons – auch die gedrückte Bewehrung wirkt mit. Den Widerstand bei einer Einwirkung sucht die Rechnung auf dem Rand selbst, zwischen zwei benachbarten Ebenen; was dort gilt, zeigt bei jeder Kombination die Probe.

Der Beton ist in 200 Fasern über die Höhe geteilt, jede mit ihrer mittleren Spannung, die Bewehrung zählt Lage für Lage, und an ihrer Stelle zählt der Stahl statt des Betons – auch die gedrückte Bewehrung wirkt mit. Den Widerstand bei einer Einwirkung sucht die Rechnung auf dem Rand selbst, zwischen zwei benachbarten Ebenen; was dort gilt, zeigt bei jeder Kombination die Probe.

**Schwerpunkt der zusammengefassten Lage – 2. Lage Grundbewehrung + 2. Lage Zulage**

$$
z_{2,x} = \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,2,x,g} + A_{s,2,x,z}}
$$

**Bewehrungsquerschnitt der zusammengefassten Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z}
$$

**Gleichmässiger Druck, ohne Bewehrung**

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd}
$$

**Beide Lagen fliessen auf Zug**

$$
N_{Rd}^{+} = A_{s,2,x} \cdot f_{yd} + A_{s,3,x} \cdot f_{yd}
$$

**Kräfte mal Hebelarm um die halbe Höhe**

$$
M_{Rd}(N_{Rd}^{+}) = A_{s,2,x} \cdot f_{yd} \cdot \left(z_{2,x} - \tfrac{h}{2}\right) + A_{s,3,x} \cdot f_{yd} \cdot \left(z_{3,x} - \tfrac{h}{2}\right)
$$

**Statische Höhe der Lage unten, ab dem gedrückten Rand oben**

$$
d_{2,x} = z_{2,x}
$$

**Druckzonenhöhe aus dem Kräftegleichgewicht**

$$
x^{+} = \frac{A_{s,2,x} \cdot f_{yd}}{0.85 \cdot b \cdot f_{cd}}
$$

**Momentenwiderstand bei reiner Biegung**

$$
M_{Rd}(N_{Ed}=0)^{+} = A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - \frac{0.85 \cdot x^{+}}{2}\right)
$$

**Nulllinie auf halber Höhe**

$$
x^{+} = \frac{h}{2}
$$

**Dehnung der Zugbewehrung**

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}}
$$

**Stahlspannung, höchstens die Fliessgrenze**

$$
\sigma_{sd} = \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right]
$$

**Kräftegleichgewicht**

$$
N_{Rd}^{+} = -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot \sigma_{sd}
$$

**Momentengleichgewicht um die halbe Höhe**

$$
M_{Rd}^{+} = \left[f_{cd} \cdot b \cdot 0.85 \cdot x^{+} \cdot \left(\tfrac{h}{2} - \tfrac{0.85 \cdot x^{+}}{2}\right) + A_{s,2,x} \cdot \sigma_{sd} \cdot \left(d_{2,x} - \tfrac{h}{2}\right)\right]
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{3,x} = h - z_{3,x}
$$

**Widerstand bei N\_Ed – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x} = \frac{M_{Rd}}{M_{Ed}}
$$

**Widerstand bei festgehaltenem N\_Ed**

$$
M_{Rd} = M_1 + \frac{N_{Ed} - N_1}{N_2 - N_1} \cdot \left(M_2 - M_1\right)
$$

**Wirksamer Modul der Parabel**

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi}
$$

**Beiwert der Parabel, mit dem wirksamen Modul**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{c,eff}}{400 \cdot f_{ck}}\right)
$$

**Werkstoffgesetze: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{ck} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{ck} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetze: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yk}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yk}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Schnittgrössen aus der Spannungsverteilung**

$$
N = \int_A \sigma\,\mathrm{d}A \qquad M = \int_A \sigma \cdot \left(z - \tfrac{h}{2}\right)\,\mathrm{d}A
$$

**Werkstoffgesetze: Beton, Spannungsblock 0.85·x**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{cd} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werkstoffgesetze: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & \varepsilon_s \ge 0 \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & \varepsilon_s < 0 \end{cases} \qquad |\varepsilon_s| \le \varepsilon_{ud}
$$

**Bezugsgrösse der Normalkraft**

$$
N_{ref} = \max\left(\left|N_{Rd,x}^{+}\right|;\ \left|N_{Rd,x}^{-}\right|\right)
$$

**Bezugsgrösse des Moments**

$$
M_{ref} = \max\left(\left|M_{Rd,x}^{+}\right|;\ \left|M_{Rd,x}^{-}\right|\right)
$$

**Einwirkung im normierten Diagramm**

$$
\bar{E}_{d,x} = \sqrt{\left(\frac{N_{Ed}}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed}}{M_{ref}}\right)^{2}}
$$

**Kürzester Abstand zur Resistenzlinie**

$$
a = \sqrt{\left(\frac{N_{Ed} - N_P}{N_{ref}}\right)^{2} + \left(\frac{M_{Ed} - M_P}{M_{ref}}\right)^{2}}
$$

**Widerstand im normierten Diagramm**

$$
\bar{R}_{d,x} = \bar{E}_{d,x} + a
$$

### Querkraft

Querkraftwiderstand mit Querkraftbewehrung, Fachwerkmodell mit veränderlicher Neigung der Druckdiagonalen. Massgebend ist das Kleinere aus dem Widerstand der Bügel und dem der Druckdiagonalen; der Betonanteil ohne Bügel geht nicht zusätzlich ein.

Beide Anteile gelten je Laufmeter, wie die Querkraft selbst. Gesucht wird ganzgradig zwischen α\_min und α\_max die Neigung mit dem grössten Widerstand V\_Rd = min(V\_Rd,s; V\_Rd,c). Bei einer Normalzugkraft steilt sich die Druckdiagonale auf: α\_min wird dann auf 40° gesetzt und α\_max notfalls mitgehoben.

Querkraftwiderstand ohne Querkraftbewehrung. Massgebend sind die statische Höhe der gezogenen Bewehrung, die Grösstkorngrösse und die Dehnung auf halber Höhe.

Nur eine Normaldruckkraft entlastet; eine Zugkraft bleibt beim Dekompressionsmoment unberücksichtigt. Da der Widerstand über m\_Ed und N\_Ed von der Einwirkung abhängt, wird er für jede Kombination einzeln bestimmt.

**Ansatz** *(SIA 262:2025, 4.3.3.4)*

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot\alpha \qquad V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin\alpha \cdot \cos\alpha
$$

**Teilung in y aus der Stabzahl**

$$
s_{V,y} = \frac{b}{n_{V,y}}
$$

**Widerstand der Bügel**

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot \alpha
$$

**Widerstand der Druckdiagonalen**

$$
V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha
$$

**Querkraftwiderstand**

$$
V_{Rd,x} = \min\left[V_{Rd,s};\ V_{Rd,c}\right]
$$

**Ansatz** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

**Dekompressionsmoment und Dehnung**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} \qquad \varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
k_g = \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

**Wirksame Höhe, um die Einlage vermindert**

$$
d_v = d - e_{Einlage}
$$

**Dekompressionsmoment**

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6}
$$

**Dehnung auf halber Höhe**

$$
\varepsilon_v = 1.5 \cdot \frac{f_{yd}}{E_s}
$$

**Beiwert für die statische Höhe**

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

**Querkraftwiderstand** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd,x} = k_d \cdot \tau_{cd} \cdot d_v
$$

**Dehnung auf halber Höhe**

$$
\varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v = d
$$

### Duktilität

Die Druckzone muss schlank bleiben, damit der Stahl lange fliesst, bevor der Beton versagt: der Querschnitt kündigt sein Versagen an. Gerechnet wird die Druckzonenhöhe bei reiner Biegung, je Lage einzeln.

d wird von der gedrückten Randfaser aus gemessen: bei den unteren Lagen von der Oberkante, bei den oberen von der Unterkante. Grundbewehrung und Zulage einer Lage zählen mit ihrem gemeinsamen Schwerpunkt.

**Kräftegleichgewicht bei M\_Ed = 0** *(SIA 262:2025, 4.1.4.2.5)*

$$
0.85 \cdot x \cdot b \cdot f_{cd} = A_s \cdot f_{sd} \qquad \Rightarrow \qquad x = \frac{A_s \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}}
$$

**Bedingung**

$$
\frac{x}{d} \le 0.35
$$

**Druckzonenhöhe bei reiner Biegung**

$$
x = \frac{A_{s,2,x} \cdot f_{sd}}{0.85 \cdot b \cdot f_{cd}}
$$

**Bezogene Druckzonenhöhe** *(SIA 262:2025, 4.1.4.2.5)*

$$
\left(x/d\right)_{2} = \frac{x}{d_{2,x}}
$$

### Zwängung auf Normalkraft

Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick. Die Bewehrung muss die Kraft übernehmen können, die der Beton beim Reissen abgibt – erst dann kündigt sich das Versagen an.

Eine aufgezwungene Verkürzung zieht den ganzen Querschnitt: es reisst der ganze Beton, und alle Stäbe teilen sich seine Risskraft, jeder bis zu seiner zulässigen Spannung. Die rissaktive Dicke t ist die kleinere Abmessung des Betons.

Eine verschmierte Linie hat keinen Durchmesser – sie bekommt einen fiktiven, als lägen ihre Stäbe 150 mm auseinander (Annahme).

**Rissaktive Plattendicke**

$$
h_{eff} = \min\left[500\,\mathrm{mm};\ h\right]
$$

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.2)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h_{eff}} \quad \left(h_{eff}\ \text{in}\ \mathrm{m}\right)
$$

**Wirksame Zugfestigkeit**

$$
f_{ct,eff} = k_t \cdot f_{ctm}
$$

**Risskraft der gezogenen Querschnittshälfte**

$$
N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff}
$$

**Dickster Stab der Lage**

$$
\varnothing_{2,x} = \max\left[\varnothing_{2,x,g};\ \varnothing_{2,x,z}\right]
$$

**Zulässige Stahlspannung (Rissbreite w\_nom)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm,2,x} = \min\left[\sqrt{\frac{9 \cdot E_s \cdot f_{ctm} \cdot w_{nom}}{\varnothing_{2,x}}};\ f_{yk}\right]
$$

**Aufnehmbare Risskraft**

$$
N_{s,adm,2,x} = A_{s,2,x} \cdot \sigma_{s,adm,2,x}
$$

**Rissaktive Dicke: die kleinere Abmessung, höchstens 500 mm**

$$
t = \min\left[500\,\mathrm{mm};\ b;\ h\right]
$$

**Risskraft des ganzen Querschnitts**

$$
N_{Riss} = A_c \cdot f_{ct,eff}
$$

**Linie 3: verschmiert, als Stäbe mit 150 mm Teilung**

$$
\varnothing_{fikt} = \sqrt{\frac{4}{\pi} \cdot \frac{A_s}{l} \cdot s}
$$

**Aufnehmbare Risskraft**

$$
N_{s,adm} = A_{s,1} \cdot \sigma_{s,adm,1} + A_{s,2} \cdot \sigma_{s,adm,2} + A_{s,3} \cdot \sigma_{s,adm,3} + A_{s,4} \cdot \sigma_{s,adm,4}
$$

**Rissaktive Dicke: die kleinere Abmessung**

$$
t = \min\left[b;\ h\right]
$$

**Aufnehmbare Risskraft**

$$
N_{s,adm} = A_s \cdot \sigma_{s,adm}
$$

### Sprödes Versagen

Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick. Nachgewiesen wird deshalb, dass der bewehrte Querschnitt mehr trägt als der unbewehrte im Augenblick des Risses: M\_Rd(N\_Ed = 0) ≥ M\_Riss.

Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick. Nachgewiesen wird deshalb, dass der bewehrte Querschnitt mehr trägt als der unbewehrte im Augenblick des Risses: M\_Rk(N\_Ed = 0) ≥ M\_Riss.

**Beiwert für die Plattendicke** *(SIA 262:2025, 4.4.1.3)*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6}
$$

### Zwängung auf Biegung

Eine aufgezwungene Krümmung erzeugt beim Reissen ein Moment, das die Bewehrung übernehmen muss – ohne über die zulässige Stahlspannung zu kommen. Nicht zu verwechseln mit dem Nachweis gegen sprödes Versagen: dort steht der Biegewiderstand gegen das Rissmoment, hier die Stahlspannung gegen ihre Grenze.

Das Rissmoment gilt für den ungerissenen Bruttoquerschnitt – den Zustand vor dem Riss. Der Widerstand dagegen wird am gerissenen Querschnitt bestimmt, also für den Augenblick danach. Dass zwei verschiedene Querschnitte auftreten, ist genau die Frage: reicht die Bewehrung für das, was der Beton abgibt?

Das Kriechen weicht den Beton auf: E\_c,eff = E\_cm/(1+φ), und die Wertigkeit ist E\_s/E\_c,eff. Ein grösseres φ senkt damit den Hebelarm und liegt auf der sicheren Seite.

Die Betondruckspannung verläuft dreieckig – null in der Nulllinie, am grössten an der gedrückten Kante. Ihre Resultierende liegt deshalb bei x/3 von dieser Kante.

Am gezeichneten Querschnitt je Richtung: dasselbe Rissmoment wie beim spröden Versagen, gehalten gegen das Moment, bei dem der erste gezogene Stab seine zulässige Spannung erreicht. Das Rissmoment gehört dem ungerissenen Bruttoquerschnitt, das Moment der Bewehrung dem gerissenen – elastisch, ohne Normalkraft, mit der Kriechzahl dieses Nachweises; die gedrückte Bewehrung wirkt mit.

Jeder gezogene Stab hält gegen seine eigene Grenze, mit seinem Durchmesser und dem f\_ctm des Betons, in dem er liegt; massgebend ist der Stab mit dem kleinsten Erfüllungsgrad.

Gesucht wird die Ebene, die N, M\_y und M\_z zugleich trägt. Zu einer festen Zugrichtung n ist es dieselbe Aufgabe wie bei der Platte: zwei geschachtelte Halbierungen finden ε\_0 und κ, mit denen N und das Moment um die Nulllinie stimmen. Übrig bleibt das Moment entlang der Nulllinie; die Zugrichtung wird gedreht, bis auch es stimmt – bei einem symmetrischen Querschnitt steht sie senkrecht zum Moment, bei einem unsymmetrischen nicht. Nachgewiesen wird das Ergebnis: die Probe, dass die Ebene die Einwirkung erzeugt.

**Wertigkeit im gerissenen Zustand**

$$
n = \frac{E_s}{E_{cm}} \cdot \left(1 + \varphi\right)
$$

**Hilfsgrösse der Nulllinie**

$$
\rho = \frac{n \cdot A_{s,2,x}}{b}
$$

**Nulllinie des gerissenen Querschnitts**

$$
x = \sqrt{\rho^{2} + 2 \cdot d_{2,x} \cdot \rho} - \rho
$$

**Innerer Hebelarm**

$$
z = d_{2,x} - \frac{x}{3}
$$

**Aufnehmbares Moment der Bewehrung**

$$
M_{s,adm,2,x} = \sigma_{s,adm,2,x} \cdot A_{s,2,x} \cdot z
$$

**Zwängung auf Biegung, je Stab** *(SIA 262:2025, 4.4.2)*

$$
\max_i \frac{\sigma_{s,i}(M_{s,adm})}{\sigma_{s,adm,i}} = 1\qquad M_{s,adm} \ge M_{Riss}
$$

### Stahlspannung aus Rissbreite

Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Rissbreite – dieselbe Grenze wie bei der Zwängung, nur dass die Spannung hier aus den Lasten kommt und nicht aus einer aufgezwungenen Verformung. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf. Die Bewehrung wirkt auf Zug und auf Druck – nur in der Handrechnung zählt die gedrückte nicht. Gemessen wird an der am stärksten gezogenen Lage.

Drei Festlegungen stecken in jeder Zahl unten, und alle drei sind Auslegung der Norm und nicht Rechnung. Erstens das Kriechen: angesetzt wird das φ dieses Kapitels. Ein grösseres φ weicht den Beton auf, die Druckzone wächst, der Hebelarm wird kleiner und die Stahlspannung damit grösser; mit φ = 0 gehen die Spannungen zurück, und der Nachweis geht leichter auf. Mit dem Spannungsblock hängt kein Gesetz am Modul – dort wirkt φ nicht.

Zweitens die Werkstoffgesetze: sie rechnen mit den charakteristischen Festigkeiten. Der Stahl ist linear bis f\_yk und fliesst dann, der Beton trägt höchstens f\_ck. Ein Gebrauchsnachweis fragt, was der Querschnitt tut, und nicht, was er darf – der Teilsicherheitsbeiwert gehört in die Tragsicherheit. Läge das Plateau bei f\_yd, bliebe jede Stahlspannung darunter, und eine Grenze darüber könnte nie überschritten werden.

Drittens die Grenze: dieselbe wie bei der Zwängung, mit f\_yk und bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die Rissbreite. Massgebend ist der dickste Stab der Tragrichtung. Welche Lage die grösste Zugspannung trägt, wechselt mit dem Lastfall – bei einem Feldmoment die untere, bei einem Stützmoment die obere –, und der dickste Stab gibt die kleinste zulässige Spannung. Das liegt für beide auf der sicheren Seite.

Fliesst die Bewehrung, bleibt ihre Spannung am Plateau stehen, während die Dehnung weiterwächst. Verglichen wird dann die Dehnung: ε\_s gegen ε\_s,adm = σ\_s,adm / E\_s. Solange der Stahl elastisch bleibt, ist das genau der Spannungsvergleich; fliesst er, fällt der Nachweis durch, und zwar um so deutlicher, je weiter er gedehnt ist.

Die Dehnungsebene wird gesucht, nicht hergeleitet. Eine ebene Dehnungsverteilung hat zwei Unbekannte – die Dehnung in der Mittelebene ε\_m und die Krümmung χ – und ihnen stehen zwei Gleichgewichtsbedingungen gegenüber: N und M. Geschlossen auflösen lässt sich das nicht, weil die Werkstoffgesetze nichtlinear sind.

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet, jede mit der Spannung in ihrer Mitte; der Stahl kommt Lage für Lage dazu, und die von ihm verdrängte Betonfläche wird abgezogen, damit dieselbe Fläche nicht zweimal zählt.

Gesucht wird in zwei geschachtelten Halbierungen. Innen: zu einer festgehaltenen Krümmung χ wird ε\_m so lange halbiert, bis N\_int die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr Zug bedeutet. Aussen: mit diesem ε\_m bleibt ein Moment übrig, und χ wird so lange halbiert, bis auch M\_int stimmt – hier trägt die Monotonie, dass mehr Krümmung mehr Moment heisst.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.0 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Halbierung liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Nachgewiesen wird deshalb nicht der Weg, sondern das Ergebnis: dass die gefundene Ebene genau die angegebenen Schnittgrössen erzeugt. Diese Probe steht bei jedem Fall.

Erzeugt die gefundene Ebene die Einwirkung nicht, gibt es zu ihr keine Ebene, und der Nachweis sagt das, statt die Probe abzuhaken. Das kommt vor, wo ein Gesetz springt wie der Spannungsblock: bei viel Druck und wenig Moment liegt der Block immer ganz an einem Rand und gibt mehr Moment, als einwirkt.

Mit dem Spannungsblock trägt der Beton unter (1 − 0.85)·ε\_c2d nichts. Unter Gebrauchslast liegt die Druckresultierende damit am Rand, und der Hebelarm wird beinahe d – die Stahlspannung kleiner, als der Querschnitt sie hat. Der Block ist ein Modell für den Bruch.

Mit der Handrechnung rechnet der Querschnitt wie die Resistenzlinie aus Handrechnung: der Beton als Spannungsblock, die gedrückte Bewehrung weggelassen, die Bewehrung jeder Seite zu einer Lage in ihrem Schwerpunkt zusammengefasst, und der Beton auch dort gezählt, wo der Stahl liegt.

Das Integral über den Beton wird als Summe über 60 Fasern gleicher Dicke gebildet; der Stahl kommt Lage für Lage dazu. Wie in der Handrechnung zählt der Beton auch dort, wo der Stahl liegt.

Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Rissbreite – dieselbe Grenze wie bei der Zwängung, nur dass die Spannung hier aus den Lasten kommt und nicht aus einer aufgezwungenen Verformung. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf, die Bewehrung wirkt auf Zug und auf Druck. Jeder gezogene Stab hält gegen seine Grenze; massgebend ist der mit dem kleinsten Erfüllungsgrad.

Drittens die Grenze: dieselbe wie bei der Zwängung, mit f\_yk und bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die Rissbreite. Jeder gezogene Stab hält gegen seine eigene Grenze, mit seinem Durchmesser und dem f\_ctm des Betons, in dem er liegt; massgebend ist der Stab mit dem kleinsten Erfüllungsgrad.

Einachsig bleibt die Nulllinie waagrecht, und M\_z zählt nicht – wie in der Tragsicherheit.

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

**Zulässige Stahlspannung (normale Anforderung)** *(SIA 262:2025, 4.4.2)*

$$
\sigma_{s,adm} = f_{yk}
$$

**Grösste Zugdehnung in der Bewehrung**

$$
\varepsilon_y = \frac{f_{yk}}{E_s}
$$

**Zulässige Dehnung**

$$
\varepsilon_{s,adm} = \frac{\sigma_{s,adm}}{E_s}
$$

**Werkstoffgesetze im Gebrauchszustand: Beton, Spannungsblock 0.85·x**

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{ck} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

**Werkstoffgesetze im Gebrauchszustand: Stahl, nur auf Zug**

$$
\sigma_s = \begin{cases} \min\left(E_s \cdot \varepsilon_s;\ f_{yk}\right) & \varepsilon_s > 0 \\[1ex] 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen}) \end{cases}
$$

### Stahlspannung gegen Fliessen

Unter häufiger Einwirkung darf die Bewehrung nicht fliessen – sonst bleiben Risse und Durchbiegung dauerhaft. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf. Die Bewehrung wirkt auf Zug und auf Druck – nur in der Handrechnung zählt die gedrückte nicht. Gemessen wird an der am stärksten gezogenen Lage.

Drittens die Grenze: sie rechnet mit dem Bemessungswert, σ\_s,adm = f\_yd − 80 N/mm², und nicht mit f\_yk − 80. Die Norm sagt an dieser Stelle nicht eindeutig, welcher Wert gemeint ist; f\_yd ist die strengere Wahl – die Grenze liegt rund 15 % tiefer –, gewählt ist deshalb die Seite, auf der man nicht danebenliegen kann. Das ist etwas anderes als das Fliessplateau oben: dort geht es darum, was der Stahl tut, hier darum, wie viel Abstand man davon verlangt.

Unter häufiger Einwirkung darf die Bewehrung nicht fliessen – sonst bleiben Risse und Durchbiegung dauerhaft. Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug auf, die Bewehrung wirkt auf Zug und auf Druck. Jeder gezogene Stab hält gegen seine Grenze; massgebend ist der mit dem kleinsten Erfüllungsgrad.

**Zulässige Stahlspannung** *(SIA 262:2025, Tabelle 17)*

$$
\sigma_{s,adm} = f_{yd} - 80\,\mathrm{N}/\mathrm{mm}^{2}
$$

### Verformung

Eine Durchbiegung, mit der Steifigkeit E\_cm ermittelt, gilt für die ungerissene Platte. Die gerissene ist weicher, und unter Dauerlast kriecht der Beton; um wie viel beides die Durchbiegung vergrössert, schätzt der Faktor ω\_w. Er hängt nur an der Platte und an der Seite, die gezogen wird: ω\_w für Zug unten, ω\_w′ für Zug oben.

Gerechnet in x, je Seite mit x-Bewehrung – einmal je Platte, nicht je Fall. ρ gehört zur gezogenen Seite, ρ′ zur Gegenseite; d′ reicht vom gezogenen Rand bis zur Gegenlage und ist damit deren statische Höhe – ρ′ der einen Seite ist das ρ der anderen. Die x-Bewehrung einer Seite zählt zusammen, in ihrem Schwerpunkt.

Die Durchbiegung w ist mit der Steifigkeit E\_cm ermittelt: elastisch, am ungerissenen Querschnitt. Der Faktor ω\_w der gezogenen Seite führt sie auf die gerissene Platte unter Dauerlast; die so vergrösserte Durchbiegung hält der Nachweis gegen L/350.

**Vergrösserungsfaktor der Durchbiegung – allgemein** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

**Schwerpunkt der x-Bewehrung unten**

$$
z_{u} = \frac{A_{s,2,x,g} \cdot z_{2,x,g} + A_{s,2,x,z} \cdot z_{2,x,z}}{A_{s,u}}
$$

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,u}}{b \cdot d_{u}}
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3}
$$

**Wirksame Durchbiegung, Zug unten**

$$
w_{eff} = \omega_w \cdot w
$$

**Grenzwert der Durchbiegung, nach Vorgabe**

$$
w_{max} = \frac{L}{350}
$$

### Knicken

Nachgewiesen wird am verformten System. Die Ausmitte zweiter Ordnung hängt von der Krümmung ab, die Krümmung vom Moment und das Moment wieder von der Ausmitte – also wird die Folge so lange durchlaufen, bis sie einläuft. Läuft sie nicht ein, gibt es keine Gleichgewichtslage: das System knickt.

Der Erfüllungsgrad ist ein Verhältnis von Normalkräften: N\_Rd ist die grösste Druckkraft, unter der der Stab noch steht. Über Momente zu vergleichen ginge nur, solange es ein Gleichgewicht gibt – beim Knicken ist gerade das der Fall, der fehlt.

Die Verformung rechnet präzise, mit der Parabel; Kriechzahl und Werte wählt das Kapitel. Das Kriechen weicht den Beton auf: er verformt sich mehr, die Ausmitte zweiter Ordnung wächst, und der Stab knickt früher – φ = 0 läge dann auf der unsicheren Seite. Im Bereich der Gebrauchslasten unterscheidet sich die Parabel kaum vom linearen Gesetz, in der Nähe der Grenzlast erheblich, und genau dort entscheidet sich, ob es noch eine Gleichgewichtslage gibt. Den Spannungsblock gibt es hier nicht: mit ihm trüge auf flachen Stücken jede Krümmung dasselbe Moment, und die Ausmitte wäre nicht eindeutig.

Gesucht wird in zwei geschachtelten Suchen. Innen: zu einer festgehaltenen Krümmung χ wird ε\_m gesucht, bis N\_int die verlangte Normalkraft trifft – das geht sicher, weil mehr Dehnung immer mehr Zug bedeutet. Aussen: mit diesem ε\_m bleibt ein Moment übrig, und χ wird gesucht, bis auch M\_int stimmt – hier trägt die Monotonie, dass mehr Krümmung mehr Moment heisst. Beide Suchen beginnen bei der Ebene, die zuletzt gefunden wurde, grenzen die Stelle mit wachsenden Schritten ein und treffen sie dann mit dem Illinois-Verfahren: einer Sekante, die abwechselnd von beiden Seiten herankommt.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.5 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Halbierung liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Die Ausmitten-Iteration darüber steht dagegen vollständig da, Durchlauf für Durchlauf: sie ist das Verfahren selbst, und dass sie einläuft, ist die Aussage des Nachweises.

Zu jedem Moment wird die Dehnungsebene gesucht, die es im Gleichgewicht hält; aus deren Krümmung folgt die nächste Ausmitte. Begonnen wird mit e\_2d = 0, also ohne Verformung.

Gesucht wird die grösste Druckkraft mit Gleichgewichtslage. Die gewollte Ausmitte e\_1d bleibt dabei fest – sie gehört zum System und nicht zur Last, M\_Ed,1 wächst also mit. Bei N = 0 trägt der Stab immer; von dort aus wird das Fenster halbiert, bis getragene und nicht getragene Kraft zusammenfallen.

Am gezeichneten Querschnitt gilt jeder Knickfall in einer Richtung: der Zugseite, zu der sich der Stab biegt. Die Nulllinie bleibt dabei parallel zur Achse; das Moment um die andere Achse, das ein unsymmetrischer Querschnitt weckt, zählt nicht. d reicht vom gedrückten Rand bis zum entferntesten Stab in Zugrichtung.

Der Momentenwiderstand bei einer Druckkraft ist der Bruchzustand des Querschnitts in Biegerichtung, mit den Gesetzen des Widerstands – wie in der Tragsicherheit, mit der Nulllinie parallel zur Achse.

Die Dehnung wächst linear in Zugrichtung, ε = ε\_m + χ·v mit v ab dem Schwerpunkt. Zu jeder Druckkraft und jedem Moment finden zwei geschachtelte Suchen ε\_m und χ, wie bei der Platte. Die Ausmitten-Iteration darüber steht vollständig da, Durchlauf für Durchlauf: sie ist das Verfahren selbst, und dass sie einläuft, ist die Aussage des Nachweises.

**Ungewollte Ausmitte – allgemein** *(SIA 262:2025, 4.3.7)*

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \qquad e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

**Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}\right)
$$

**Werkstoffgesetze der Verformung: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Schiefstellung** *(SIA 262:2025, 4.3.7)*

$$
\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ \frac{1}{300}\right);\ \frac{1}{200}\right] \quad \left(l\ \text{in}\ \mathrm{m}\right)
$$

**Ungewollte Ausmitte** *(SIA 262:2025, 4.3.7)*

$$
e_{0d} = \max\left(\frac{d}{30};\ \frac{\alpha_i \cdot l_{cr}}{2}\right)
$$

**Gewollte Ausmitte**

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right|
$$

**Das Verfahren** *(SIA 262:2025, 4.3.7)*

$$
e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}^{(k-1)}\right)
$$

### Querschnittsanalyse

Der Querschnitt ist gezeichnet: Polygone, jedes mit seinem Material. Liegt ein Polygon ganz in einem anderen, ersetzt es dieses dort -- eine Aussparung nimmt die Fläche weg. y zeigt nach rechts, z nach oben; alle Masse in Millimetern.

**Fläche und Schwerpunkt eines Polygons (Satz von Gauss)**

$$
A = \frac{1}{2} \sum_i c_i \qquad y_S = \frac{1}{6A} \sum_i (y_i + y_{i+1})\, c_i \qquad z_S = \frac{1}{6A} \sum_i (z_i + z_{i+1})\, c_i \qquad c_i = y_i\, z_{i+1} - y_{i+1}\, z_i
$$

**Trägheitsmomente eines Polygons, bezogen auf den Schwerpunkt**

$$
I_y = \frac{1}{12} \sum_i (z_i^2 + z_i z_{i+1} + z_{i+1}^2)\, c_i - A\, z_S^2\qquad I_z = \frac{1}{12} \sum_i (y_i^2 + y_i y_{i+1} + y_{i+1}^2)\, c_i - A\, y_S^2
$$

**Teilung einer Stablinie: gleiche Felder, auf die Länge gerundet**

$$
s = \frac{L}{m} \qquad m = \mathrm{runde}\left(\frac{L}{s_{gewählt}}\right)
$$

**Bügelquerschnitt je Länge einer Schubwand (n Schnitte)**

$$
\frac{A_{sw}}{s} = \frac{n \cdot \pi\, \varnothing^2 / 4}{s}
$$

### Querkraft und Torsion

Jede Schubwand trägt eine Kraft entlang ihrer Achse; ihre Länge ist der Hebelarm des Fachwerks. Verteilt wird elastisch: der Querschnitt verschiebt sich, und jede Wand wehrt sich wie eine Feder mit der Steifigkeit b\_w·l. Das Moment dieser Querkraftanteile um den Schwerpunkt ist der Versatz ΔT; den Rest der Torsion tragen die geschlossenen Zellen als Umlauf-Schubfluss nach Bredt, mehrzellig mit gleicher Verdrillung aller Zellen. Ohne Zelle trägt die Torsion über dieselben Federn mit Drehung. Die Wandkräfte ergeben so immer V\_y, V\_z und um den Schwerpunkt T.

**Querkraft über die Federn der Wände**

$$
k_i = b_{w,i} \cdot l_i \qquad \sum_i k_i\, e_i e_i^T\, u = V \qquad V_i = k_i\, e_i \cdot u \qquad \Delta T = \sum_i V_i\, r_i
$$

**Torsion in den Zellen (Bredt, mehrzellig)**

$$
T - \Delta T = \sum_k 2 A_k\, q_k \qquad \oint_k \frac{q}{b_w}\, \mathrm{d}s = 2 A_k\, \theta
$$

**Widerstand je Länge einer Wand (Fachwerk)** *(SIA 262:2025, 4.3.3.4)*

$$
v_{Rd,s} = \frac{A_{sw}}{s}\, f_{sd} \cot\alpha \qquad v_{Rd,c} = b_w\, k_c\, f_{cd} \sin\alpha \cos\alpha \qquad v_{Rd} = \max_\alpha \min(v_{Rd,s};\ v_{Rd,c})
$$

**Versatz: Moment der Querkraftanteile um den Schwerpunkt**

$$
\Delta T = \sum_i V_i \cdot r_i
$$

**Was die Zellen tragen**

$$
T_{Zellen} = T_{Ed} - \Delta T
$$

### Schiefe Biegung

Der Querschnitt bleibt eben (Bernoulli). Die Dehnung hängt nur vom Abstand v in Zugrichtung n ab, gemessen ab dem Schwerpunkt; die Nulllinie steht senkrecht zu n und darf schräg liegen. Zu jeder Dehnungsebene ergeben sich N, M\_y und M\_z durch Integration über die Fläche -- als Summe über Streifen quer zu n, deren Grenzen auf jede Polygonecke fallen, und Stab für Stab.

Der Bruchzustand: jede Dehnungsebene, bei der ein Werkstoff an seiner Grenze steht und keiner darüber. Der Beton wird an seinem gedrücktesten Punkt bis -ε\_c2d gestaucht, ganz gedrückt am C-Punkt bis -ε\_c1d; die Bewehrung bis ±ε\_ud. Gesucht wird die Ebene mit N = N\_Ed, deren Moment in die Richtung der Einwirkung zeigt. Nachgewiesen wird nicht die Suche, sondern ihre Probe: die Kräfte jedes Teils und ihre Summen.

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

**Erfüllungsgrad bei fester Normalkraft und fester Richtung**

$$
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}
$$

**Probe: Normalkraft**

$$
N_{Rd} = \sum F_i
$$

**Probe: Moment um y**

$$
M_{y,Rd} = -\sum F_i \cdot (z_i - z_S)
$$

**Probe: Moment um z**

$$
M_{z,Rd} = -\sum F_i \cdot (y_i - y_S)
$$

**Widerstand in der Richtung der Einwirkung**

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}}
$$

### Duktilität je Richtung

Ein Querschnitt kündigt sein Versagen an, wenn die Bewehrung fliesst, bevor der Beton bricht -- dann ist die Druckzone klein. Gemessen wird das an x/d bei reiner Biegung: x ist der Abstand der Nulllinie vom gedrücktesten Betonpunkt, d der des entferntesten gezogenen Stabs, beide senkrecht zur Nulllinie.

**Duktilität** *(SIA 262:2025, 4.1.4.2.5)*

$$
\frac{x}{d} \le \left(\frac{x}{d}\right)_{max}
$$

**Bezogene Druckzonenhöhe bei reiner Biegung**

$$
x/d = \frac{x}{d}
$$

### Sprödes Versagen je Richtung

Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick. Darum muss der bewehrte Querschnitt mehr tragen als der unbewehrte im Augenblick des Risses: M\_Rd bei N = 0 mindestens das Rissmoment. Das Rissmoment gehört dem ungerissenen Bruttoquerschnitt; bei unsymmetrischer Form mit dem Deviationsmoment.

**Spannung im ungerissenen Querschnitt**

$$
\sigma(y, z) = -\frac{M_y\,(I_z z' - I_{yz} y') + M_z\,(I_y y' - I_{yz} z')}{I_y I_z - I_{yz}^2}\qquad y' = y - y_S,\ z' = z - z_S
$$

**Sprödes Versagen** *(SIA 262:2025, 4.4.1.3)*

$$
M_{Rd}(N = 0) \ge M_{Riss} = f_{ct,eff} \cdot W
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot y' - I_z \cdot z'}
$$

**Rissmoment des ungerissenen Querschnitts**

$$
M_{Riss} = f_{ct,eff} \cdot W
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_z \cdot z' - I_{yz} \cdot y'}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot z' - I_y \cdot y'}
$$

**Widerstandsmoment zum gezogensten Betonpunkt**

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_y \cdot y' - I_{yz} \cdot z'}
$$

### Fundament

**Reibungswinkel, Bemessungswert** *(SIA 267:2013, 5.3.2.1)*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right)
$$

**Kohäsion, Bemessungswert**

$$
c_{eff} = \frac{c_k}{\gamma_c}
$$

**Raumlast des Bodens unter Auftrieb**

$$
\gamma' = \gamma - \gamma_w
$$

### Grundbruch

Unter der Sohle bildet sich beim Grundbruch ein Gleitkörper, der den Boden seitlich hinaus und nach oben drückt. Die erweiterte Tragfähigkeitsformel setzt seinen Widerstand aus drei Teilen zusammen: der Kohäsion, der seitlichen Auflast neben dem Fundament und dem Gewicht des Gleitkörpers -- je mit einem Tragfähigkeitsfaktor und den Korrekturen für Form, Tiefe, Lastneigung, Geländeneigung und Sohlneigung.

Wird ein gesättigter Ton schnell belastet, kann das Porenwasser nicht entweichen: es gilt φ = 0, und an die Stelle der Kohäsion tritt die undrainierte Scherfestigkeit s\_u. Die Korrekturen stehen dann nicht als Faktoren, sondern als Summanden in der Klammer.

**Erweiterte Tragfähigkeitsformel** *(Kap. 9.2.10)*

$$
\sigma_f = c \, N_c s_c d_c i_c g_c b_c + \sigma_{v,0} \, N_q s_q d_q i_q g_q b_q + \tfrac{1}{2} \gamma_G \, b \, N_{\gamma} s_{\gamma} d_{\gamma} i_{\gamma} g_{\gamma} b_{\gamma} \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

**Tragfähigkeitsfaktor der seitlichen Auflast** *(Kap. 9.2.6)*

$$
N_q = e^{\pi \tan \varphi_{eff}} \cdot \tan^{2}\left(45^\circ + \frac{\varphi_{eff}}{2}\right)
$$

**Tragfähigkeitsfaktor der Kohäsion** *(Kap. 9.2.6)*

$$
N_c = \frac{N_q - 1}{\tan \varphi_{eff}}
$$

**Tragfähigkeitsfaktor des Gleitkörpergewichts** *(Kap. 9.2.6)*

$$
N_{\gamma} = 1.8 \cdot \left(N_q - 1\right) \cdot \tan \varphi_{eff}
$$

**Reichweite des Gleitkörpers** *(Kap. 9.2.10)*

$$
L_{Gl} = b \cdot \tan\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \cdot e^{\frac{\pi}{2} \tan \varphi_{eff}}
$$

**Tiefe des Gleitkörpers** *(Kap. 9.2.10)*

$$
H_{Gl} = b \cdot \frac{\cos \varphi_{eff}}{2 \cos\left(45^\circ + \frac{\varphi_{eff}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \tan \varphi_{eff}}
$$

**Überlagerung auf Höhe der Sohle, Grundwasser tiefer** *(Kap. 9.2.8)*

$$
\sigma_{v,0} = \gamma \cdot t + q_{Ed}
$$

**Abstand des Grundwassers unter der Sohle** *(Kap. 9.2.8)*

$$
T = t_1 - t
$$

**Raumlast im Gleitkörper, unter Wasser** *(Kap. 9.2.8)*

$$
\gamma_G = \gamma'
$$

**Formfaktor der Kohäsion** *(Kap. 9.2.12)*

$$
s_c = 1 + \frac{b}{L} \cdot \frac{N_q}{N_c}
$$

**Formfaktor der seitlichen Auflast** *(Kap. 9.2.12)*

$$
s_q = 1 + \frac{b}{L} \cdot \tan \varphi_{eff}
$$

**Formfaktor des Gleitkörpergewichts** *(Kap. 9.2.12)*

$$
s_{\gamma} = 1 - 0.4 \cdot \frac{b}{L}
$$

**Winkel der Einbindetiefe, in Grad** *(Kap. 9.2.13)*

$$
\vartheta_t = \arctan\frac{t}{b}
$$

**Tiefenfaktor der Kohäsion** *(Kap. 9.2.13)*

$$
d_c = 1 + 0.007 \cdot \vartheta_t
$$

**Tiefenfaktor der seitlichen Auflast** *(Kap. 9.2.13)*

$$
d_q = 1 + 0.035 \cdot \tan \varphi_{eff} \cdot \left(1 - \sin \varphi_{eff}\right)^{2} \cdot \vartheta_t
$$

**Geländeneigungsfaktor der Kohäsion** *(Kap. 9.2.15)*

$$
g_c = 1 - \frac{\beta}{147^\circ}
$$

**Geländeneigungsfaktor der Auflast und des Gleitkörpers** *(Kap. 9.2.15)*

$$
g_q = \left(1 - 0.5 \cdot \tan \beta\right)^{5}
$$

**Sohlneigungsfaktor der Kohäsion** *(Kap. 9.2.16)*

$$
b_c = 1 - \frac{\alpha}{147^\circ}
$$

**Sohlneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.16)*

$$
b_q = e^{-0.035 \cdot \alpha \cdot \tan \varphi_{eff}}
$$

**Sohlneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.16)*

$$
b_{\gamma} = e^{-0.047 \cdot \alpha \cdot \tan \varphi_{eff}}
$$

**Neigung der Last** *(Kap. 9.2.14)*

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}}
$$

**Lastneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.14)*

$$
i_q = \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5}
$$

**Lastneigungsfaktor der Kohäsion** *(Kap. 9.2.14)*

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1}
$$

**Lastneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.14)*

$$
i_{\gamma} = \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5}
$$

**Bruchspannung in der Sohle** *(Kap. 9.2.10)*

$$
\sigma_f = c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L
$$

**Überlagerung auf Höhe der Sohle, Lage 1: Grundwasser über der Sohle** *(Kap. 9.2.8)*

$$
\sigma_{v,0} = \gamma \cdot t_1 + \gamma' \cdot \left(t - t_1\right) + q_{Ed}
$$

**Tragfähigkeitsformel undrainiert** *(Kap. 9.2.17)*

$$
\sigma_f = 5.1 \, s_u \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \left(\gamma t + q\right) \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

**Formfaktor, undrainiert** *(Kap. 9.2.17)*

$$
s_c = 0.2 \cdot \frac{b}{L}
$$

**Tiefenfaktor, undrainiert, t \< b** *(Kap. 9.2.17)*

$$
d_c = 0.4 \cdot \frac{t}{b}
$$

**Geländeneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
g_c = \frac{\beta}{147^\circ}
$$

**Sohlneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
b_c = \frac{\alpha}{147^\circ}
$$

**Lastneigungsfaktor, undrainiert** *(Kap. 9.2.17)*

$$
i_c = 0.5 - \frac{1}{2} \sqrt{1 - \frac{T_{Ed}}{c_{eff} \cdot b \cdot L}}
$$

**Bruchspannung in der Sohle, undrainiert** *(Kap. 9.2.17)*

$$
\sigma_f = 5.1 \cdot c_{eff} \cdot \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \sigma_{v,0}
$$

**Tiefenfaktor, undrainiert, t ≥ b** *(Kap. 9.2.17)*

$$
d_c = 0.007 \cdot \vartheta_t
$$

### Gleiten

Die Kraft T in der Sohle muss durch Reibung zwischen Fundament und Boden aufgenommen werden. Der Reibungswinkel δ\* der Sohlfuge liegt meist zwischen 2/3 φ und φ; ein Erdwiderstand vor dem Fundament wird nicht angesetzt.

**Reibungswinkel der Sohlfuge** *(Kap. 9.2.18)*

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff}
$$

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*}
$$

### Kennzahlen

Was die Platte in x aufnimmt, ohne Bezug auf eine Einwirkung: die Eckwerte der Handrechnung mit Bemessungswerten und der Querkraftwiderstand ohne Normalkraft. Wo eine Seite massgebend ist, gilt das Kleinere beider Seiten.

Mit Bügeln trägt das Fachwerk; gesucht wird ganzgradig zwischen α\_min und α\_max die Neigung mit dem grössten Widerstand. Ohne Normalkraft bleiben die Grenzen, wie sie eingegeben sind.

Ohne Bügel hängt der Widerstand am Moment: am grössten bei M\_Ed = 0, wo die Dehnung null ist, am kleinsten bei M\_Ed = M\_Rd, wo die Bewehrung zu fliessen beginnt und die Dehnung f\_yd/E\_s erreicht. Je Seite gilt ihre statische Höhe.

**Zugwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{+}(M_{Ed} = 0) = N_1 + \frac{M_{Ed} - M_1}{M_2 - M_1} \cdot \left(N_2 - N_1\right)
$$

**Druckwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-}
$$

**Querkraftwiderstand mit Bügeln, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.4)*

$$
V_{Rd}(\alpha_{opt}) = \min\left[V_{Rd}^{+}(\alpha_{opt});\ V_{Rd}^{-}(\alpha_{opt})\right]
$$

**Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+}
$$

**Zug unten, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{+} = \frac{f_{yd}}{E_s}
$$

### Stabquerschnitte

**Querschnittsfläche, «Balken 300×500» (Rechteck)**

$$
A_{\text{Q1}} = b_{\text{Q1}} \cdot h_{\text{Q1}}
$$

**Flächenträgheitsmoment, «Balken 300×500» (Rechteck)**

$$
I_{\text{Q1}} = \frac{b_{\text{Q1}} \cdot \left(h_{\text{Q1}}\right)^{3}}{12}
$$

**Querschnittsfläche, «Rundstütze» (Kreis)**

$$
A_{\text{Q2}} = \frac{\pi \cdot \left(d_{\text{Q2}}\right)^{2}}{4}
$$

**Flächenträgheitsmoment, «Rundstütze» (Kreis)**

$$
I_{\text{Q2}} = \frac{\pi \cdot \left(d_{\text{Q2}}\right)^{4}}{64}
$$

**Querschnittsfläche, «Rohr» (Kreisring)**

$$
A_{\text{Q3}} = \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{2} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{2}\right)}{4}
$$

**Flächenträgheitsmoment, «Rohr» (Kreisring)**

$$
I_{\text{Q3}} = \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{4} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{4}\right)}{64}
$$

**Querschnittsfläche, «Hohlprofil» (Rechteckrohr)**

$$
A_{\text{Q4}} = b_{\text{Q4}} \cdot h_{\text{Q4}} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right)
$$

**Flächenträgheitsmoment, «Hohlprofil» (Rechteckrohr)**

$$
I_{\text{Q4}} = \frac{b_{\text{Q4}} \cdot \left(h_{\text{Q4}}\right)^{3} - \left(b_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right) \cdot \left(h_{\text{Q4}} - 2 \cdot t_{\text{Q4}}\right)^{3}}{12}
$$

**Querschnittsfläche, «Plattenbalken» (T-Querschnitt)**

$$
A_{\text{Q5}} = b_{\text{Q5}} \cdot h_{f} + b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right)
$$

**Abstand des Schwerpunkts vom oberen Rand, «Plattenbalken» (T-Querschnitt)**

$$
z_{S} = \frac{b_{\text{Q5}} \cdot \left(h_{f}\right)^{2} / 2 + b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right) \cdot \left(h_{\text{Q5}} + h_{f}\right) / 2}{A_{\text{Q5}}}
$$

**Flächenträgheitsmoment, «Plattenbalken» (T-Querschnitt)**

$$
I_{\text{Q5}} = \frac{b_{\text{Q5}} \cdot \left(h_{f}\right)^{3}}{12} + b_{\text{Q5}} \cdot h_{f} \cdot \left(z_{S} - \frac{h_{f}}{2}\right)^{2} + \frac{b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right)^{3}}{12} + b_{w} \cdot \left(h_{\text{Q5}} - h_{f}\right) \cdot \left(\frac{h_{\text{Q5}} + h_{f}}{2} - z_{S}\right)^{2}
$$

**Querschnittsfläche, «Walzprofil» (Doppel-T)**

$$
A_{\text{Q6}} = 2 \cdot b_{\text{Q6}} \cdot t_{f} + t_{w} \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f}\right)
$$

**Flächenträgheitsmoment, «Walzprofil» (Doppel-T)**

$$
I_{\text{Q6}} = \frac{b_{\text{Q6}} \cdot \left(h_{\text{Q6}}\right)^{3} - \left(b_{\text{Q6}} - t_{w}\right) \cdot \left(h_{\text{Q6}} - 2 \cdot t_{f}\right)^{3}}{12}
$$

**Querschnittsfläche, «Fundamentbalken» (Trapez)**

$$
A_{\text{Q7}} = \frac{\left(b_{o} + b_{u}\right) \cdot h_{\text{Q7}}}{2}
$$

**Flächenträgheitsmoment, «Fundamentbalken» (Trapez)**

$$
I_{\text{Q7}} = \frac{\left(h_{\text{Q7}}\right)^{3} \cdot \left(\left(b_{o}\right)^{2} + 4 \cdot b_{o} \cdot b_{u} + \left(b_{u}\right)^{2}\right)}{36 \cdot \left(b_{o} + b_{u}\right)}
$$

**Dehnsteifigkeit, «Balken 300×500» aus C30/37**

$$
EA_{\text{Q1,C30/37}} = E_{cm} \cdot A_{\text{Q1}}
$$

**Biegesteifigkeit, «Balken 300×500» aus C30/37**

$$
EI_{\text{Q1,C30/37}} = E_{cm} \cdot I_{\text{Q1}}
$$

### Steifigkeitsmethode

**Steifigkeitsmatrix eines Stabs, in seinen Achsen**

$$
\mathbf{k} = \begin{bmatrix} \frac{EA}{L} & 0 & 0 & -\frac{EA}{L} & 0 & 0 \\ 0 & \frac{12EI}{L^3} & \frac{6EI}{L^2} & 0 & -\frac{12EI}{L^3} & \frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{4EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{2EI}{L} \\ -\frac{EA}{L} & 0 & 0 & \frac{EA}{L} & 0 & 0 \\ 0 & -\frac{12EI}{L^3} & -\frac{6EI}{L^2} & 0 & \frac{12EI}{L^3} & -\frac{6EI}{L^2} \\ 0 & \frac{6EI}{L^2} & \frac{2EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{4EI}{L} \end{bmatrix}
$$

**Von den Achsen des Systems in die des Stabs**

$$
\mathbf{d} = \mathbf{T} \cdot \mathbf{d}_{glob} \qquad \mathbf{T} = \begin{bmatrix} \mathbf{R} & \mathbf{0} \\ \mathbf{0} & \mathbf{R} \end{bmatrix} \qquad \mathbf{R} = \begin{bmatrix} \cos\alpha & \sin\alpha & 0 \\ -\sin\alpha & \cos\alpha & 0 \\ 0 & 0 & 1 \end{bmatrix}
$$

**Bettung eines Stabs, quer und längs**

$$
\mathbf{k}_{b} = \frac{k_{\perp} \cdot L}{420} \begin{bmatrix} 156 & 22L & 54 & -13L \\ 22L & 4L^2 & 13L & -3L^2 \\ 54 & 13L & 156 & -22L \\ -13L & -3L^2 & -22L & 4L^2 \end{bmatrix} \qquad \mathbf{k}_{b,\parallel} = \frac{k_{\parallel} \cdot L}{6} \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}
$$

**Arbeitsgleiche Knotenkräfte der Lasten auf einem Stab**

$$
f_i = \int_0^L N_i(x) \cdot p(x)\,\mathrm{d}x + \int_0^L N_i'(x) \cdot m(x)\,\mathrm{d}x + \sum_j N_i(a_j) \cdot P_j + \sum_j N_i'(a_j) \cdot M_j
$$

**Gesamtsteifigkeitsmatrix und Gleichungssystem**

$$
\mathbf{K} = \sum_{\text{Stäbe}} \mathbf{T}^{\mathsf{T}} \cdot \mathbf{k} \cdot \mathbf{T} \qquad \mathbf{K} \cdot \mathbf{x} = \mathbf{F}
$$

**Schnittgrössen aus den Kräften an den Stabenden**

$$
N(0) = -s_{u,a} \qquad V(0) = s_{v,a} \qquad M(0) = -s_{\theta,a} \qquad \frac{\mathrm{d}N}{\mathrm{d}x} = -p_x \qquad \frac{\mathrm{d}V}{\mathrm{d}x} = p_y \qquad \frac{\mathrm{d}M}{\mathrm{d}x} = V - m
$$

**Biegelinie und Längsverschiebung**

$$
v'' = \frac{M}{EI} \qquad u' = \frac{N}{EA}
$$

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
| Risse: Zwängung Normalkraft | 3. Lage | $N_{s,adm,3,x} = 351.6\,\mathrm{kN}$ | $N_{Riss} = 378.3\,\mathrm{kN}$ | $0.93$ |
| Sprödes Versagen | 3. Lage | $M_{Rd,x}(N_{Ed} = 0)_{3} = 79.9\,\mathrm{kNm}$ | $M_{Riss} = 41.4\,\mathrm{kNm}$ | $1.93$ |
| Risse: Zwängung Biegung | 3. Lage | $M_{s,adm,3,x} = 80.4\,\mathrm{kNm}$ | $M_{Riss} = 41.4\,\mathrm{kNm}$ | $1.94$ |
| Risse: Quasi-ständige Lastfälle | Feld (60 %) | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 175\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.18$ |
| Risse: Quasi-ständige Lastfälle | Feld mit Druck (60 %) | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 106\,\mathrm{N}/\mathrm{mm}^{2}$ | $3.60$ |
| Risse: Quasi-ständige Lastfälle | Stütze (60 %) | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 212\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.79$ |
| Risse: Quasi-ständige Lastfälle | Dauerlast | $\sigma_{s,adm} = 381\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 136\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.80$ |
| Risse: Häufige Lastfälle | Feld (70 %) | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 204\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.74$ |
| Risse: Häufige Lastfälle | Feld mit Druck (70 %) | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 123\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.88$ |
| Risse: Häufige Lastfälle | Stütze (70 %) | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 248\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.43$ |
| Risse: Häufige Lastfälle | Gebrauch | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 175\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.03$ |
| Verformung | Feld | $w_{max} = 17.1\,\mathrm{mm}$ | $w_{eff} = 12.0\,\mathrm{mm}$ | $1.43$ |
| Verformung | Kragarm | $w_{max} = 7.1\,\mathrm{mm}$ | $w_{eff} = 6.0\,\mathrm{mm}$ | $1.19$ |
| Knicken | Wand | $N_{Rd,K} = 4496.7\,\mathrm{kN}$ | $N_{Ed} = 800.0\,\mathrm{kN}$ | $5.62$ |

> **Warnung:** Risse: Zwängung Normalkraft – 3. Lage: nicht erfüllt. N\_s,adm = 754 mm² · 466 N/mm² = 351.6 kN \< N\_Riss = 378.3 kN.

**Kennzahlen**

| Kennzahl | Zeichen | Wert |
| :--- | :--- | ---: |
| Bewehrungsmass | $\mu_s$ | $123\,\mathrm{kg}/\mathrm{m}^{3}$ |
| Höhe der Distanzhalter | $h_{Dist}$ | $186\,\mathrm{mm}$ |
| Vergrösserungsfaktor, Zug unten | $\omega_w$ | $4.00$ |
| Vergrösserungsfaktor, Zug oben | $\omega_w'$ | $7.52$ |
| Momentenwiderstand, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $235.9\,\mathrm{kNm}$ |
| Momentenwiderstand, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-79.9\,\mathrm{kNm}$ |
| Zugwiderstand | $N_{Rd}^{+}(M_{Ed} = 0)$ | $737.5\,\mathrm{kN}$ |
| Druckwiderstand | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-6000\,\mathrm{kN}$ |
| Bezogene Druckzonenhöhe, Zug unten | $\left(x/d\right)^{+}$ | $0.253$ |
| Bezogene Druckzonenhöhe, Zug oben | $\left(x/d\right)^{-}$ | $0.077$ |
| Querkraftwiderstand mit Bügeln | $V_{Rd}(\alpha_{opt})$ | $212.1\,\mathrm{kN}/\mathrm{m}$ |

### Dach

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 200\,\mathrm{mm} \qquad b_x = 500\,\mathrm{mm} \qquad b_y = 1000\,\mathrm{mm}
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
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 18.1\,\mathrm{kNm}$ | $M_{Ed,x} = 40.0\,\mathrm{kNm}$ | $0.45$ |
| Biegung und Normalkraft | Rand | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 18.1\,\mathrm{kNm}$ | $M_{Ed,x} = 10.0\,\mathrm{kNm}$ | $1.81$ |
| Querkraft | Feld | $V_{Rd,x}(M_{Ed} = 40\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 83.2\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 40.0\,\mathrm{kN}/\mathrm{m}$ | $2.08$ |
| Querkraft | Rand | $V_{Rd,x}(M_{Ed} = 10\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 110.7\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 30.0\,\mathrm{kN}/\mathrm{m}$ | $3.69$ |
| Risse: Quasi-ständige Lastfälle | Dauerlast | $\varepsilon_{s,adm} = 2.50\,\text{‰}$ | $\varepsilon_{s,x} = 4.67\,\text{‰}$ | $0.54$ |
| Verformung | Feld | $w_{max} = 14.3\,\mathrm{mm}$ | $w_{eff} = 16.8\,\mathrm{mm}$ | $0.85$ |

> **Warnung:** Biegung und Normalkraft – Feld: nicht erfüllt. M\_Rd = 18.1 kNm bei N\_Ed = 0 kN.

> **Warnung:** Risse: Quasi-ständige Lastfälle – Dauerlast: nicht erfüllt. ε\_m = 2.3198 ‰, χ = 0.03612 1/m. Stahl fliesst (ε\_s = 4.67 ‰ \> ε\_y = 2.50 ‰): ε\_s \> ε\_s,adm = 2.50 ‰.

> **Warnung:** Verformung – Feld: nicht erfüllt. w\_eff = ω\_w · w = 8.42 · 2 mm = 16.8 mm \> w\_max = L/350 = 14.3 mm.

> **Hinweis:** Risse: Zwängung Normalkraft – 1. Lage: nicht erfüllt (α\_eff = 0.99), ausgeschaltet. N\_s,adm = 262 mm² · 500 N/mm² = 130.9 kN \< N\_Riss = 131.8 kN.

**Kennzahlen**

| Kennzahl | Zeichen | Wert |
| :--- | :--- | ---: |
| Bewehrungsmass | $\mu_s$ | $67\,\mathrm{kg}/\mathrm{m}^{3}$ |
| Höhe der Distanzhalter | $h_{Dist}$ | $104\,\mathrm{mm}$ |
| Vergrösserungsfaktor, Zug unten | $\omega_w$ | $8.42$ |
| Vergrösserungsfaktor, Zug oben | $\omega_w'$ | $8.42$ |
| Momentenwiderstand, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $18.1\,\mathrm{kNm}$ |
| Momentenwiderstand, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-18.1\,\mathrm{kNm}$ |
| Zugwiderstand | $N_{Rd}^{+}(M_{Ed} = 0)$ | $227.7\,\mathrm{kN}$ |
| Druckwiderstand | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-2000\,\mathrm{kN}$ |
| Bezogene Druckzonenhöhe, Zug unten | $\left(x/d\right)^{+}$ | $0.081$ |
| Bezogene Druckzonenhöhe, Zug oben | $\left(x/d\right)^{-}$ | $0.081$ |
| Querkraftwiderstand ohne Bügel, grösster | $V_{Rd,max}$ | $136.9\,\mathrm{kN}/\mathrm{m}$ |
| Querkraftwiderstand ohne Bügel, kleinster | $V_{Rd,min}$ | $95.7\,\mathrm{kN}/\mathrm{m}$ |

### Parabel

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 250\,\mathrm{mm} \qquad b_x = 1000\,\mathrm{mm}
$$

**Bewehrung von oben nach unten**

| Lage | Richtung | Bewehrung | Stahl |
| :--- | :--- | :--- | :--- |
| Überdeckung oben | – | $30\,\mathrm{mm}$ | – |
| 4. Lage | y | $\varnothing 10@150$ | B500B |
| 3. Lage | x | $\varnothing 10@150$ | B500B |
| 2. Lage | x | $\varnothing 12@150$ | B500B |
| 1. Lage | y | $\varnothing 10@150$ | B500B |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rk,x}(N_{Ed} = -200\,\mathrm{kN}) = 99.6\,\mathrm{kNm}$ | $M_{Ed,x} = 60.0\,\mathrm{kNm}$ | $1.66$ |
| Querkraft | Feld | $V_{Rd,x}(M_{Ed} = 60\,\mathrm{kNm},\ N_{Ed} = -200\,\mathrm{kN}) = 171.7\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 50.0\,\mathrm{kN}/\mathrm{m}$ | $3.43$ |
| Sprödes Versagen | 3. Lage | $M_{Rk,x}(N_{Ed} = 0)_{3} = 63.7\,\mathrm{kNm}$ | $M_{Riss} = 29.0\,\mathrm{kNm}$ | $2.20$ |
| Risse: Quasi-ständige Lastfälle | Dauerlast | $\sigma_{s,adm} = 466\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 203\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.29$ |
| Risse: Häufige Lastfälle | Gebrauch | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 323\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.10$ |
| Knicken | Stütze | $N_{Rd,K} = 4156.2\,\mathrm{kN}$ | $N_{Ed} = 600.0\,\mathrm{kN}$ | $6.93$ |

> **Hinweis:** Risse: Zwängung Normalkraft – 3. Lage: nicht erfüllt (α\_eff = 0.81), ausgeschaltet. N\_s,adm = 524 mm² · 500 N/mm² = 261.8 kN \< N\_Riss = 322.2 kN.

**Kennzahlen**

| Kennzahl | Zeichen | Wert |
| :--- | :--- | ---: |
| Bewehrungsmass | $\mu_s$ | $73\,\mathrm{kg}/\mathrm{m}^{3}$ |
| Höhe der Distanzhalter | $h_{Dist}$ | $148\,\mathrm{mm}$ |
| Vergrösserungsfaktor, Zug unten | $\omega_w$ | $8.37$ |
| Vergrösserungsfaktor, Zug oben | $\omega_w'$ | $10.42$ |
| Momentenwiderstand, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $64.2\,\mathrm{kNm}$ |
| Momentenwiderstand, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-45.4\,\mathrm{kNm}$ |
| Zugwiderstand | $N_{Rd}^{+}(M_{Ed} = 0)$ | $475\,\mathrm{kN}$ |
| Druckwiderstand | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-5000\,\mathrm{kN}$ |
| Bezogene Druckzonenhöhe, Zug unten | $\left(x/d\right)^{+}$ | $0.095$ |
| Bezogene Druckzonenhöhe, Zug oben | $\left(x/d\right)^{-}$ | $0.065$ |
| Querkraftwiderstand ohne Bügel, grösster | $V_{Rd,max}$ | $223.5\,\mathrm{kN}/\mathrm{m}$ |
| Querkraftwiderstand ohne Bügel, kleinster | $V_{Rd,min}$ | $145.9\,\mathrm{kN}/\mathrm{m}$ |

### Block

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 220\,\mathrm{mm} \qquad b_x = 1000\,\mathrm{mm}
$$

**Bewehrung von oben nach unten**

| Lage | Richtung | Bewehrung | Stahl |
| :--- | :--- | :--- | :--- |
| Überdeckung oben | – | $30\,\mathrm{mm}$ | – |
| 4. Lage | y | $\varnothing 8@150$ | B500B |
| 3. Lage | x | $\varnothing 10@150$ | B500B |
| 2. Lage | x | $\varnothing 10@150$ | B500B |
| 1. Lage | y | $\varnothing 8@150$ | B500B |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 44.8\,\mathrm{kNm}$ | $M_{Ed,x} = 25.0\,\mathrm{kNm}$ | $1.79$ |
| Biegung und Normalkraft | Rand | $N_{Rd,x}(M_{Ed} = -15\,\mathrm{kNm}) = -4649.2\,\mathrm{kN}$ | $N_{Ed,x} = -100.0\,\mathrm{kN}$ | $46.49$ |
| Querkraft | Feld | $V_{Rd,x}(M_{Ed} = 25\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 154.2\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 30.0\,\mathrm{kN}/\mathrm{m}$ | $5.14$ |
| Risse: Quasi-ständige Lastfälle | Dauerlast | $\sigma_{s,adm} = 500\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_{s,x} = 131\,\mathrm{N}/\mathrm{mm}^{2}$ | $3.82$ |
| Knicken | Wand | $N_{Rd,K} = 3508.6\,\mathrm{kN}$ | $N_{Ed} = 400.0\,\mathrm{kN}$ | $8.77$ |

> **Hinweis:** Risse: Zwängung Normalkraft – 2. Lage: nicht erfüllt (α\_eff = 0.91), ausgeschaltet. N\_s,adm = 524 mm² · 500 N/mm² = 261.8 kN \< N\_Riss = 287.4 kN.

**Kennzahlen**

| Kennzahl | Zeichen | Wert |
| :--- | :--- | ---: |
| Bewehrungsmass | $\mu_s$ | $61\,\mathrm{kg}/\mathrm{m}^{3}$ |
| Höhe der Distanzhalter | $h_{Dist}$ | $124\,\mathrm{mm}$ |
| Vergrösserungsfaktor, Zug unten | $\omega_w$ | $10.11$ |
| Vergrösserungsfaktor, Zug oben | $\omega_w'$ | $10.11$ |
| Momentenwiderstand, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $39\,\mathrm{kNm}$ |
| Momentenwiderstand, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-39\,\mathrm{kNm}$ |
| Zugwiderstand | $N_{Rd}^{+}(M_{Ed} = 0)$ | $455.3\,\mathrm{kN}$ |
| Druckwiderstand | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-4400\,\mathrm{kN}$ |
| Bezogene Druckzonenhöhe, Zug unten | $\left(x/d\right)^{+}$ | $0.076$ |
| Bezogene Druckzonenhöhe, Zug oben | $\left(x/d\right)^{-}$ | $0.076$ |
| Querkraftwiderstand ohne Bügel, grösster | $V_{Rd,max}$ | $193.9\,\mathrm{kN}/\mathrm{m}$ |
| Querkraftwiderstand ohne Bügel, kleinster | $V_{Rd,min}$ | $132.6\,\mathrm{kN}/\mathrm{m}$ |

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

> **Hinweis:** Biegung und Normalkraft – Feld, Querkraft – Feld: Keine Bewehrung in x-Richtung → Widerstand 0, nicht erfüllt.

**Kennzahlen**

| Kennzahl | Zeichen | Wert |
| :--- | :--- | ---: |
| Bewehrungsmass | $\mu_s$ | $47\,\mathrm{kg}/\mathrm{m}^{3}$ |
| Höhe der Distanzhalter | $h_{Dist}$ | $166\,\mathrm{mm}$ |

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
| 1. Lage | y | $\varnothing 40@150$ | B500B |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 54.4\,\mathrm{kNm}$ | $M_{Ed,x} = 40.0\,\mathrm{kNm}$ | $1.36$ |
| Biegung und Normalkraft | Schräg | $\bar{R}_{d,x} = 0.336$ | $\bar{E}_{d,x} = 0.195$ | $1.72$ |
| Querkraft | Feld | $V_{Rd,x}(M_{Ed} = 40\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) = 142.9\,\mathrm{kN}/\mathrm{m}$ | $V_{Ed,x} = 50.0\,\mathrm{kN}/\mathrm{m}$ | $2.86$ |

**Kennzahlen**

| Kennzahl | Zeichen | Wert |
| :--- | :--- | ---: |
| Bewehrungsmass | $\mu_s$ | $327\,\mathrm{kg}/\mathrm{m}^{3}$ |
| Höhe der Distanzhalter | $h_{Dist}$ | $116\,\mathrm{mm}$ |
| Vergrösserungsfaktor, Zug unten | $\omega_w$ | $11.77$ |
| Vergrösserungsfaktor, Zug oben | $\omega_w'$ | $8.05$ |
| Momentenwiderstand, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $54.4\,\mathrm{kNm}$ |
| Momentenwiderstand, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-64.2\,\mathrm{kNm}$ |
| Zugwiderstand | $N_{Rd}^{+}(M_{Ed} = 0)$ | $555.2\,\mathrm{kN}$ |
| Druckwiderstand | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-5000\,\mathrm{kN}$ |
| Bezogene Druckzonenhöhe, Zug unten | $\left(x/d\right)^{+}$ | $0.111$ |
| Bezogene Druckzonenhöhe, Zug oben | $\left(x/d\right)^{-}$ | $0.095$ |
| Querkraftwiderstand ohne Bügel, grösster | $V_{Rd,max}$ | $190.6\,\mathrm{kN}/\mathrm{m}$ |
| Querkraftwiderstand ohne Bügel, kleinster | $V_{Rd,min}$ | $131.1\,\mathrm{kN}/\mathrm{m}$ |

### Kastenträger

**Angaben zum Querschnitt**

$$
\text{C30/37} \qquad A = 330000\,\mathrm{mm}^2 \qquad y_S = 400.0\,\mathrm{mm} \qquad z_S = 300.0\,\mathrm{mm}
$$

**Bewehrung und Schubwände**

| Element | Bewehrung | Stahl |
| :--- | :--- | :--- |
| Stab 1 | $\varnothing 20$ | B500B |
| Linie 1 | $6 \varnothing 16$ | B500B |
| Linie 2 | $4 \varnothing 12$ | B500B |
| Linie 3 | $400\,\mathrm{mm}^2$ | B500B |
| Wand 1 | $b_w = 150,\ 1 \times \varnothing 10\ @\ 150$ | B500B |
| Wand 2 | $b_w = 150,\ 1 \times \varnothing 10\ @\ 150$ | B500B |
| Wand 3 | $b_w = 150,\ 1 \times \varnothing 10\ @\ 150$ | B500B |
| Wand 4 | $b_w = 150,\ 1 \times \varnothing 10\ @\ 150$ | B500B |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Querkraft und Torsion | Feld | $v_{Rd} = 394.3\,\mathrm{kN}/\mathrm{m}$ | $q_{Ed} = 380.3\,\mathrm{kN}/\mathrm{m}$ | $1.04$ |
| Querkraft und Torsion | Schief | $v_{Rd} = 394.3\,\mathrm{kN}/\mathrm{m}$ | $q_{Ed} = 76.9\,\mathrm{kN}/\mathrm{m}$ | $5.13$ |
| Biegung und Normalkraft | Feld | $M_{Rd} = 188.6\,\mathrm{kNm}$ | $M_{Ed} = 304.5\,\mathrm{kNm}$ | $0.62$ |
| Biegung und Normalkraft | Schief | $M_{Rd} = 666.6\,\mathrm{kNm}$ | $M_{Ed} = 291.5\,\mathrm{kNm}$ | $2.29$ |
| Duktilität | Zug links | $\left(x/d\right)_{max} = 0.35$ | $x/d = 0.135$ | $2.59$ |
| Sprödes Versagen | Zug oben | $M_{Rd} = 194.7\,\mathrm{kNm}$ | $M_{Riss} = 116.7\,\mathrm{kNm}$ | $1.67$ |
| Risse: Zwängung Normalkraft | ganzer Querschnitt | $N_{s,adm} = 973.5\,\mathrm{kN}$ | $N_{Riss} = 765.6\,\mathrm{kN}$ | $1.27$ |
| Risse: Zwängung Biegung | Zug oben | $M_{s,adm} = 151.1\,\mathrm{kNm}$ | $M_{Riss} = 116.7\,\mathrm{kNm}$ | $1.30$ |
| Risse: Quasi-ständige Lastfälle | Feld (60 %) | $\sigma_{s,adm,2} = 404\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_s = 253\,\mathrm{N}/\mathrm{mm}^{2}$ | $1.60$ |
| Risse: Quasi-ständige Lastfälle | Schief (60 %) | $\sigma_{s,adm,2} = 404\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_s = 15\,\mathrm{N}/\mathrm{mm}^{2}$ | $26.63$ |
| Risse: Quasi-ständige Lastfälle | Dauer | $\sigma_{s,adm,2} = 404\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_s = 90\,\mathrm{N}/\mathrm{mm}^{2}$ | $4.50$ |
| Risse: Häufige Lastfälle | Häufig schief | $\sigma_{s,adm} = 355\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_s = 150\,\mathrm{N}/\mathrm{mm}^{2}$ | $2.37$ |

> **Warnung:** Biegung und Normalkraft – Feld: nicht erfüllt. Bei N\_Ed = 664.0 kN, in der Richtung des Moments.

### Stütze

**Angaben zum Querschnitt**

$$
\text{C30/37} \qquad A = 160000\,\mathrm{mm}^2 \qquad y_S = 200.0\,\mathrm{mm} \qquad z_S = 200.0\,\mathrm{mm}
$$

**Bewehrung und Schubwände**

| Element | Bewehrung | Stahl |
| :--- | :--- | :--- |
| Linie 1 | $3 \varnothing 20$ | B500B |
| Linie 2 | $3 \varnothing 20$ | B500B |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Druck | $M_{Rd} = 348.9\,\mathrm{kNm}$ | $M_{Ed} = 120.0\,\mathrm{kNm}$ | $2.91$ |
| Biegung und Normalkraft | Zug | $N_{Rd}^{+} = 942.5\,\mathrm{kN}$ | $N_{Ed} = 400.0\,\mathrm{kN}$ | $2.36$ |
| Risse: Zwängung Normalkraft | ganzer Querschnitt | $N_{s,adm} = 942.5\,\mathrm{kN}$ | $N_{Riss} = 386.7\,\mathrm{kN}$ | $2.44$ |
| Risse: Quasi-ständige Lastfälle | Dauer | $\sigma_{s,adm} = 500\,\mathrm{N}/\mathrm{mm}^{2}$ | $\sigma_s = 31\,\mathrm{N}/\mathrm{mm}^{2}$ | $16.04$ |
| Knicken | Stütze | $N_{Rd,K} = 3032.2\,\mathrm{kN}$ | $N_{Ed} = 1500.0\,\mathrm{kN}$ | $2.02$ |
| Knicken | Seitlich | $N_{Rd,K} = 3266.6\,\mathrm{kN}$ | $N_{Ed} = 1200.0\,\mathrm{kN}$ | $2.72$ |

### Hang

**Angaben zum Fundament**

$$
\begin{aligned} & \varphi_{eff} = 28.42{}^{\circ} \qquad c_{eff} = 4\,\mathrm{kPa} \qquad \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3} \qquad \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3} \\ & b = 1.6\,\mathrm{m} \qquad L = 4\,\mathrm{m} \qquad t = 0.8\,\mathrm{m} \qquad t_1 = 2\,\mathrm{m} \end{aligned}
$$

**Tragfähigkeitsfaktoren**

| Kohäsion |  | Seitliche Auflast |  | Gewicht Gleitkörper |  |
| :--- | ---: | :--- | ---: | :--- | ---: |
| $N_{c}$ | $26.64$ | $N_{q}$ | $15.42$ | $N_{\gamma}$ | $14.05$ |
| $s_{c}$ | $1.23$ | $s_{q}$ | $1.22$ | $s_{\gamma}$ | $0.84$ |
| $d_{c}$ | $1.19$ | $d_{q}$ | $1.14$ | $d_{\gamma}$ | $1.00$ |
| $i_{c,\ \text{Normal}}$ | $0.70$ | $i_{q,\ \text{Normal}}$ | $0.72$ | $i_{\gamma,\ \text{Normal}}$ | $0.63$ |
| $i_{c,\ \text{Steil}}$ | $-0.07$ | $i_{q,\ \text{Steil}}$ | $0.00$ | $i_{\gamma,\ \text{Steil}}$ | $0.00$ |
| $g_{c}$ | $0.90$ | $g_{q}$ | $0.49$ | $g_{\gamma}$ | $0.49$ |
| $b'_{c}$ | $0.97$ | $b'_{q}$ | $0.91$ | $b'_{\gamma}$ | $0.88$ |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Grundbruch | Normal | $N_{Rd} = 1956.7\,\mathrm{kN}$ | $N_{Ed} = 900.0\,\mathrm{kN}$ | $2.17$ |
| Grundbruch | Steil | $N_{Rd} = 0.0\,\mathrm{kN}$ | $N_{Ed} = 150.0\,\mathrm{kN}$ | $0.00$ |
| Gleiten | Normal | $T_{Rd} = 310.6\,\mathrm{kN}$ | $T_{Ed} = 120.0\,\mathrm{kN}$ | $2.59$ |
| Gleiten | Steil | $T_{Rd} = 51.8\,\mathrm{kN}$ | $T_{Ed} = 300.0\,\mathrm{kN}$ | $0.17$ |

> **Warnung:** Grundbruch – Steil: nicht erfüllt. N\_Rd = 0 kN \< N\_Ed = 150 kN.

> **Warnung:** Gleiten – Steil: nicht erfüllt. T\_Rd = 51.8 kN \< T\_Ed = 300 kN.

### Ufer

**Angaben zum Fundament**

$$
\begin{aligned} & \varphi_{eff} = 25.69{}^{\circ} \qquad c_{eff} = 0\,\mathrm{kPa} \qquad \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3} \qquad \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3} \\ & b = 1.5\,\mathrm{m} \qquad L = 1.5\,\mathrm{m} \qquad t = 1\,\mathrm{m} \qquad t_1 = 0.4\,\mathrm{m} \end{aligned}
$$

**Tragfähigkeitsfaktoren**

| Kohäsion |  | Seitliche Auflast |  | Gewicht Gleitkörper |  |
| :--- | ---: | :--- | ---: | :--- | ---: |
| $N_{c}$ | $21.77$ | $N_{q}$ | $11.47$ | $N_{\gamma}$ | $9.07$ |
| $s_{c}$ | $1.53$ | $s_{q}$ | $1.48$ | $s_{\gamma}$ | $0.60$ |
| $d_{c}$ | $1.24$ | $d_{q}$ | $1.18$ | $d_{\gamma}$ | $1.00$ |
| $i_{c}$ | $0.79$ | $i_{q}$ | $0.81$ | $i_{\gamma}$ | $0.74$ |
| $g_{c}$ | $1.00$ | $g_{q}$ | $1.00$ | $g_{\gamma}$ | $1.00$ |
| $b'_{c}$ | $1.00$ | $b'_{q}$ | $1.00$ | $b'_{\gamma}$ | $1.00$ |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Grundbruch | Tragsicherheit | $N_{Rd} = 622.8\,\mathrm{kN}$ | $N_{Ed} = 1200.0\,\mathrm{kN}$ | $0.52$ |
| Gleiten | Tragsicherheit | $T_{Rd} = 577.4\,\mathrm{kN}$ | $T_{Ed} = 100.0\,\mathrm{kN}$ | $5.77$ |

> **Warnung:** Grundbruch – Tragsicherheit: nicht erfüllt. N\_Rd = 622.8 kN \< N\_Ed = 1200 kN.

### Kai

**Angaben zum Fundament**

$$
\begin{aligned} & \varphi_{eff} = 23.9{}^{\circ} \qquad c_{eff} = 2\,\mathrm{kPa} \qquad \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3} \qquad \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3} \\ & b = 2\,\mathrm{m} \qquad L = 20\,\mathrm{m} \qquad t = 1.5\,\mathrm{m} \qquad t_1 = 1.5\,\mathrm{m} \end{aligned}
$$

**Tragfähigkeitsfaktoren**

| Kohäsion |  | Seitliche Auflast |  | Gewicht Gleitkörper |  |
| :--- | ---: | :--- | ---: | :--- | ---: |
| $N_{c}$ | $19.19$ | $N_{q}$ | $9.50$ | $N_{\gamma}$ | $6.78$ |
| $s_{c}$ | $1.05$ | $s_{q}$ | $1.04$ | $s_{\gamma}$ | $0.96$ |
| $d_{c}$ | $1.26$ | $d_{q}$ | $1.20$ | $d_{\gamma}$ | $1.00$ |
| $i_{c}$ | $0.90$ | $i_{q}$ | $0.91$ | $i_{\gamma}$ | $0.88$ |
| $g_{c}$ | $1.00$ | $g_{q}$ | $1.00$ | $g_{\gamma}$ | $1.00$ |
| $b'_{c}$ | $1.00$ | $b'_{q}$ | $1.00$ | $b'_{\gamma}$ | $1.00$ |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Grundbruch | Tragsicherheit | $N_{Rd} = 18045.2\,\mathrm{kN}$ | $N_{Ed} = 2000.0\,\mathrm{kN}$ | $9.02$ |
| Gleiten | Tragsicherheit | $T_{Rd} = 886.2\,\mathrm{kN}$ | $T_{Ed} = 80.0\,\mathrm{kN}$ | $11.08$ |

### Seeton

**Angaben zum Fundament**

$$
\begin{aligned} & \varphi_{eff} = 0{}^{\circ} \qquad c_{eff} = 26.7\,\mathrm{kPa} \qquad \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3} \qquad \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3} \\ & b = 1.5\,\mathrm{m} \qquad L = 2\,\mathrm{m} \qquad t = 0.8\,\mathrm{m} \qquad t_1 = 0\,\mathrm{m} \end{aligned}
$$

**Tragfähigkeitsfaktoren**

| Kohäsion |  | Seitliche Auflast |  | Gewicht Gleitkörper |  |
| :--- | ---: | :--- | ---: | :--- | ---: |
| $N_{c}$ | $5.10$ | – | – | – | – |
| $s_{c}$ | $0.15$ | – | – | – | – |
| $d_{c}$ | $0.21$ | – | – | – | – |
| $i_{c,\ \text{Normal}}$ | $0.15$ | – | – | – | – |
| $i_{c,\ \text{Zu schräg}}$ | – | – | – | – | – |
| $g_{c}$ | $0.07$ | – | – | – | – |
| $b'_{c}$ | $0.03$ | – | – | – | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Grundbruch | Normal | $N_{Rd} = 508.0\,\mathrm{kN}$ | $N_{Ed} = 300.0\,\mathrm{kN}$ | $1.69$ |
| Grundbruch | Zu schräg | $N_{Rd} = 0.0\,\mathrm{kN}$ | $N_{Ed} = 300.0\,\mathrm{kN}$ | $0.00$ |
| Gleiten | Normal | $T_{Rd} = 0.0\,\mathrm{kN}$ | $T_{Ed} = 40.0\,\mathrm{kN}$ | $0.00$ |
| Gleiten | Zu schräg | $T_{Rd} = 0.0\,\mathrm{kN}$ | $T_{Ed} = 200.0\,\mathrm{kN}$ | $0.00$ |

> **Hinweis:** Grundbruch – Zu schräg: T\_Ed \> s\_u · b · L: die Last ist zu stark geneigt, der Lastneigungsfaktor ist nicht bestimmt -- kein Grundbruchwiderstand.

> **Warnung:** Gleiten – Normal: nicht erfüllt. T\_Rd = 0 kN \< T\_Ed = 40 kN.

> **Warnung:** Gleiten – Zu schräg: nicht erfüllt. T\_Rd = 0 kN \< T\_Ed = 200 kN.

### Schacht

**Angaben zum Fundament**

$$
\begin{aligned} & \varphi_{eff} = 0{}^{\circ} \qquad c_{eff} = 40\,\mathrm{kPa} \qquad \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3} \qquad \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3} \\ & b = 1.2\,\mathrm{m} \qquad L = 1.2\,\mathrm{m} \qquad t = 2\,\mathrm{m} \qquad t_1 = 0\,\mathrm{m} \end{aligned}
$$

**Tragfähigkeitsfaktoren**

| Kohäsion |  | Seitliche Auflast |  | Gewicht Gleitkörper |  |
| :--- | ---: | :--- | ---: | :--- | ---: |
| $N_{c}$ | $5.10$ | – | – | – | – |
| $s_{c}$ | $0.20$ | – | – | – | – |
| $d_{c}$ | $0.41$ | – | – | – | – |
| $i_{c}$ | $0.15$ | – | – | – | – |
| $g_{c}$ | $0.00$ | – | – | – | – |
| $b'_{c}$ | $0.00$ | – | – | – | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Grundbruch | Tragsicherheit | $N_{Rd} = 489.2\,\mathrm{kN}$ | $N_{Ed} = 900.0\,\mathrm{kN}$ | $0.54$ |
| Gleiten | Tragsicherheit | $T_{Rd} = 0.0\,\mathrm{kN}$ | $T_{Ed} = 30.0\,\mathrm{kN}$ | $0.00$ |

> **Warnung:** Grundbruch – Tragsicherheit: nicht erfüllt. N\_Rd = 489.2 kN \< N\_Ed = 900 kN.

> **Warnung:** Gleiten – Tragsicherheit: nicht erfüllt. T\_Rd = 0 kN \< T\_Ed = 30 kN.

Mindestens ein Nachweis ist nicht erfüllt.

> **Warnung:** Platte 'Ohne x': ohne x-Bewehrung kein Verformungsnachweis.

## Werte

| Bezeichnung | Symbol | Wert | Einheit | Herkunft |
| :--- | :--- | ---: | :--- | :--- |
| Querschnittsfläche, Balken 300×500 | $A_{\text{Q1}}$ | $150000$ | mm² | berechnet |
| Flächenträgheitsmoment, Balken 300×500 | $I_{\text{Q1}}$ | $3125$ | ·10⁶ mm⁴ | berechnet |
| Breite, Balken 300×500 | $b_{\text{Q1}}$ | $300$ | mm | Vorgabe |
| Dehnsteifigkeit, Balken 300×500, C30/37 | $EA_{\text{Q1,C30/37}}$ | $5043$ | MN | berechnet |
| Biegesteifigkeit, Balken 300×500, C30/37 | $EI_{\text{Q1,C30/37}}$ | $105062$ | kNm² | berechnet |
| Höhe, Balken 300×500 | $h_{\text{Q1}}$ | $500$ | mm | Vorgabe |
| Querschnittsfläche, Kasten | $A_{\text{Q10}}$ | $330000$ | mm² | berechnet |
| Flächenträgheitsmoment, Kasten | $I_{\text{Q10}}$ | $13275$ | ·10⁶ mm⁴ | berechnet |
| Querschnittsfläche, Rundstütze | $A_{\text{Q2}}$ | $125664$ | mm² | berechnet |
| Flächenträgheitsmoment, Rundstütze | $I_{\text{Q2}}$ | $1256.64$ | ·10⁶ mm⁴ | berechnet |
| Dehnsteifigkeit, Rundstütze, C30/37 | $EA_{\text{Q2,C30/37}}$ | $4225$ | MN | berechnet |
| Biegesteifigkeit, Rundstütze, C30/37 | $EI_{\text{Q2,C30/37}}$ | $42248$ | kNm² | berechnet |
| Durchmesser, Rundstütze | $d_{\text{Q2}}$ | $400$ | mm | Vorgabe |
| Querschnittsfläche, Rohr | $A_{\text{Q3}}$ | $4973$ | mm² | berechnet |
| Aussendurchmesser, Rohr | $D_{\text{Q3}}$ | $168.3$ | mm | Vorgabe |
| Flächenträgheitsmoment, Rohr | $I_{\text{Q3}}$ | $15.64$ | ·10⁶ mm⁴ | berechnet |
| Dehnsteifigkeit, Rohr, B500B | $EA_{\text{Q3,B500B}}$ | $995$ | MN | berechnet |
| Biegesteifigkeit, Rohr, B500B | $EI_{\text{Q3,B500B}}$ | $3128$ | kNm² | berechnet |
| Wanddicke, Rohr | $t_{\text{Q3}}$ | $10$ | mm | Vorgabe |
| Querschnittsfläche, Hohlprofil | $A_{\text{Q4}}$ | $11875$ | mm² | berechnet |
| Flächenträgheitsmoment, Hohlprofil | $I_{\text{Q4}}$ | $146.71$ | ·10⁶ mm⁴ | berechnet |
| Breite, Hohlprofil | $b_{\text{Q4}}$ | $200$ | mm | Vorgabe |
| Höhe, Hohlprofil | $h_{\text{Q4}}$ | $300$ | mm | Vorgabe |
| Dehnsteifigkeit, Hohlprofil, B500B | $EA_{\text{Q4,B500B}}$ | $2375$ | MN | berechnet |
| Biegesteifigkeit, Hohlprofil, B500B | $EI_{\text{Q4,B500B}}$ | $29342$ | kNm² | berechnet |
| Wanddicke, Hohlprofil | $t_{\text{Q4}}$ | $12.5$ | mm | Vorgabe |
| Querschnittsfläche, Plattenbalken | $A_{\text{Q5}}$ | $360000$ | mm² | berechnet |
| Flächenträgheitsmoment, Plattenbalken | $I_{\text{Q5}}$ | $9600$ | ·10⁶ mm⁴ | berechnet |
| Flanschbreite, Plattenbalken | $b_{\text{Q5}}$ | $1200$ | mm | Vorgabe |
| Dehnsteifigkeit, Plattenbalken, C30/37 | $EA_{\text{Q5,C30/37}}$ | $12103$ | MN | berechnet |
| Biegesteifigkeit, Plattenbalken, C30/37 | $EI_{\text{Q5,C30/37}}$ | $322750$ | kNm² | berechnet |
| Stegbreite, Plattenbalken | $b_{w,\text{Q5}}$ | $300$ | mm | Vorgabe |
| Höhe, Plattenbalken | $h_{\text{Q5}}$ | $600$ | mm | Vorgabe |
| Flanschdicke, Plattenbalken | $h_{f,\text{Q5}}$ | $200$ | mm | Vorgabe |
| Abstand des Schwerpunkts vom oberen Rand, Plattenbalken | $z_{S,\text{Q5}}$ | $200$ | mm | berechnet |
| Querschnittsfläche, Walzprofil | $A_{\text{Q6}}$ | $14282$ | mm² | berechnet |
| Flächenträgheitsmoment, Walzprofil | $I_{\text{Q6}}$ | $241.87$ | ·10⁶ mm⁴ | berechnet |
| Flanschbreite, Walzprofil | $b_{\text{Q6}}$ | $300$ | mm | Vorgabe |
| Höhe, Walzprofil | $h_{\text{Q6}}$ | $300$ | mm | Vorgabe |
| Dehnsteifigkeit, Walzprofil, B500B | $EA_{\text{Q6,B500B}}$ | $2856$ | MN | berechnet |
| Biegesteifigkeit, Walzprofil, B500B | $EI_{\text{Q6,B500B}}$ | $48374$ | kNm² | berechnet |
| Flanschdicke, Walzprofil | $t_{f,\text{Q6}}$ | $19$ | mm | Vorgabe |
| Stegdicke, Walzprofil | $t_{w,\text{Q6}}$ | $11$ | mm | Vorgabe |
| Querschnittsfläche, Fundamentbalken | $A_{\text{Q7}}$ | $250000$ | mm² | berechnet |
| Flächenträgheitsmoment, Fundamentbalken | $I_{\text{Q7}}$ | $5138.89$ | ·10⁶ mm⁴ | berechnet |
| Dehnsteifigkeit, Fundamentbalken, C30/37 | $EA_{\text{Q7,C30/37}}$ | $8405$ | MN | berechnet |
| Biegesteifigkeit, Fundamentbalken, C30/37 | $EI_{\text{Q7,C30/37}}$ | $172768$ | kNm² | berechnet |
| Breite oben, Fundamentbalken | $b_{o,\text{Q7}}$ | $600$ | mm | Vorgabe |
| Breite unten, Fundamentbalken | $b_{u,\text{Q7}}$ | $400$ | mm | Vorgabe |
| Höhe, Fundamentbalken | $h_{\text{Q7}}$ | $500$ | mm | Vorgabe |
| Querschnittsfläche, Von Hand | $A_{\text{Q8}}$ | $15000$ | mm² | Eingabe |
| Flächenträgheitsmoment, Von Hand | $I_{\text{Q8}}$ | $120$ | ·10⁶ mm⁴ | Eingabe |
| Querschnittsfläche, Deckenstreifen | $A_{\text{Q9}}$ | $300000$ | mm² | berechnet |
| Flächenträgheitsmoment, Deckenstreifen | $I_{\text{Q9}}$ | $2250$ | ·10⁶ mm⁴ | berechnet |
| Querschnittsfläche, Rechteck | $A$ | $180000$ | mm² | berechnet |
| Flächenträgheitsmoment, Rechteck | $I$ | $5400$ | ·10⁶ mm⁴ | berechnet |
| Breite, Rechteck | $b$ | $300$ | mm | Vorgabe |
| Dehnsteifigkeit, Rechteck, C30/37 | $EA$ | $6052$ | MN | berechnet |
| Biegesteifigkeit, Rechteck, C30/37 | $EI$ | $181547$ | kNm² | berechnet |
| Höhe, Rechteck | $h$ | $600$ | mm | Vorgabe |
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
| Länge des Fundaments | $L$ | $4$ | m | Vorgabe |
| Neigung der Sohle | $\alpha$ | $5$ | ° | Vorgabe |
| Breite des Fundaments | $b$ | $1.6$ | m | Vorgabe |
| Neigung des Geländes | $\beta$ | $15$ | ° | Vorgabe |
| Kohäsion, Bemessungswert | $c_{eff}$ | $4$ | kPa | berechnet |
| Kohäsion, charakteristisch | $c_k$ | $6$ | kPa | Vorgabe |
| Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ | $k_{\delta}$ | $0.67$ |  | Vorgabe |
| Raumlast des Bodens | $\gamma$ | $21$ | kN/m³ | Vorgabe |
| Raumlast des Bodens unter Auftrieb | $\gamma'$ | $11$ | kN/m³ | berechnet |
| Partialfaktor der Kohäsion | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Partialfaktor des Reibungswinkels | $\gamma_{\varphi}$ | $1.2$ |  | Vorgabe |
| Raumlast des Wassers | $\gamma_w$ | $10$ | kN/m³ | Vorgabe |
| Erfüllungsgrad Gleiten – Normal | $\alpha_{eff,GL,\text{Normal}}$ | $2.59$ |  | berechnet |
| Erfüllungsgrad Gleiten – Steil | $\alpha_{eff,GL,\text{Steil}}$ | $0.17$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Normal | $\alpha_{eff,GB,\text{Normal}}$ | $2.17$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Steil | $\alpha_{eff,GB,\text{Steil}}$ | $0.00$ |  | berechnet |
| Reibungswinkel, Bemessungswert | $\varphi_{eff}$ | $28.42$ | ° | berechnet |
| Reibungswinkel, charakteristisch | $\varphi_k$ | $33$ | ° | Vorgabe |
| Bemessungslast neben dem Fundament | $q_{Ed}$ | $10$ | kPa | Vorgabe |
| Tiefe der Sohle unter Terrain | $t$ | $0.8$ | m | Vorgabe |
| Tiefe des höchsten Grundwasserspiegels unter Terrain | $t_1$ | $2$ | m | Vorgabe |
| Länge des Fundaments | $L$ | $1.5$ | m | Vorgabe |
| Neigung der Sohle | $\alpha$ | $0$ | ° | Vorgabe |
| Breite des Fundaments | $b$ | $1.5$ | m | Vorgabe |
| Neigung des Geländes | $\beta$ | $0$ | ° | Vorgabe |
| Kohäsion, Bemessungswert | $c_{eff}$ | $0$ | kPa | berechnet |
| Kohäsion, charakteristisch | $c_k$ | $0$ | kPa | Vorgabe |
| Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ | $k_{\delta}$ | $1$ |  | Vorgabe |
| Raumlast des Bodens | $\gamma$ | $21$ | kN/m³ | Vorgabe |
| Raumlast des Bodens unter Auftrieb | $\gamma'$ | $11$ | kN/m³ | berechnet |
| Partialfaktor der Kohäsion | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Partialfaktor des Reibungswinkels | $\gamma_{\varphi}$ | $1.2$ |  | Vorgabe |
| Raumlast des Wassers | $\gamma_w$ | $10$ | kN/m³ | Vorgabe |
| Erfüllungsgrad Gleiten – Tragsicherheit | $\alpha_{eff,GL,\text{Tragsicherheit}}$ | $5.77$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Tragsicherheit | $\alpha_{eff,GB,\text{Tragsicherheit}}$ | $0.52$ |  | berechnet |
| Reibungswinkel, Bemessungswert | $\varphi_{eff}$ | $25.69$ | ° | berechnet |
| Reibungswinkel, charakteristisch | $\varphi_k$ | $30$ | ° | Vorgabe |
| Bemessungslast neben dem Fundament | $q_{Ed}$ | $0$ | kPa | Vorgabe |
| Tiefe der Sohle unter Terrain | $t$ | $1$ | m | Vorgabe |
| Tiefe des höchsten Grundwasserspiegels unter Terrain | $t_1$ | $0.4$ | m | Vorgabe |
| Länge des Fundaments | $L$ | $20$ | m | Vorgabe |
| Neigung der Sohle | $\alpha$ | $0$ | ° | Vorgabe |
| Breite des Fundaments | $b$ | $2$ | m | Vorgabe |
| Neigung des Geländes | $\beta$ | $0$ | ° | Vorgabe |
| Kohäsion, Bemessungswert | $c_{eff}$ | $2$ | kPa | berechnet |
| Kohäsion, charakteristisch | $c_k$ | $3$ | kPa | Vorgabe |
| Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ | $k_{\delta}$ | $1$ |  | Vorgabe |
| Raumlast des Bodens | $\gamma$ | $21$ | kN/m³ | Vorgabe |
| Raumlast des Bodens unter Auftrieb | $\gamma'$ | $11$ | kN/m³ | berechnet |
| Partialfaktor der Kohäsion | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Partialfaktor des Reibungswinkels | $\gamma_{\varphi}$ | $1.2$ |  | Vorgabe |
| Raumlast des Wassers | $\gamma_w$ | $10$ | kN/m³ | Vorgabe |
| Erfüllungsgrad Gleiten – Tragsicherheit | $\alpha_{eff,GL,\text{Tragsicherheit}}$ | $11.08$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Tragsicherheit | $\alpha_{eff,GB,\text{Tragsicherheit}}$ | $9.02$ |  | berechnet |
| Reibungswinkel, Bemessungswert | $\varphi_{eff}$ | $23.9$ | ° | berechnet |
| Reibungswinkel, charakteristisch | $\varphi_k$ | $28$ | ° | Vorgabe |
| Bemessungslast neben dem Fundament | $q_{Ed}$ | $0$ | kPa | Vorgabe |
| Tiefe der Sohle unter Terrain | $t$ | $1.5$ | m | Vorgabe |
| Tiefe des höchsten Grundwasserspiegels unter Terrain | $t_1$ | $1.5$ | m | Vorgabe |
| Länge des Fundaments | $L$ | $2$ | m | Vorgabe |
| Neigung der Sohle | $\alpha$ | $4$ | ° | Vorgabe |
| Breite des Fundaments | $b$ | $1.5$ | m | Vorgabe |
| Neigung des Geländes | $\beta$ | $10$ | ° | Vorgabe |
| Kohäsion, Bemessungswert | $c_{eff}$ | $26.7$ | kPa | berechnet |
| Kohäsion, charakteristisch | $c_k$ | $40$ | kPa | Vorgabe |
| Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ | $k_{\delta}$ | $1$ |  | Vorgabe |
| Raumlast des Bodens | $\gamma$ | $21$ | kN/m³ | Vorgabe |
| Raumlast des Bodens unter Auftrieb | $\gamma'$ | $11$ | kN/m³ | berechnet |
| Partialfaktor der Kohäsion | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Partialfaktor des Reibungswinkels | $\gamma_{\varphi}$ | $1.2$ |  | Vorgabe |
| Raumlast des Wassers | $\gamma_w$ | $10$ | kN/m³ | Vorgabe |
| Erfüllungsgrad Gleiten – Normal | $\alpha_{eff,GL,\text{Normal}}$ | $0.00$ |  | berechnet |
| Erfüllungsgrad Gleiten – Zu schräg | $\alpha_{eff,GL,\text{Zu schräg}}$ | $0.00$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Normal | $\alpha_{eff,GB,\text{Normal}}$ | $1.69$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Zu schräg | $\alpha_{eff,GB,\text{Zu schräg}}$ | $0.00$ |  | berechnet |
| Reibungswinkel, Bemessungswert | $\varphi_{eff}$ | $0$ | ° | berechnet |
| Reibungswinkel, charakteristisch | $\varphi_k$ | $0$ | ° | Vorgabe |
| Bemessungslast neben dem Fundament | $q_{Ed}$ | $0$ | kPa | Vorgabe |
| Tiefe der Sohle unter Terrain | $t$ | $0.8$ | m | Vorgabe |
| Tiefe des höchsten Grundwasserspiegels unter Terrain | $t_1$ | $0$ | m | Vorgabe |
| Länge des Fundaments | $L$ | $1.2$ | m | Vorgabe |
| Neigung der Sohle | $\alpha$ | $0$ | ° | Vorgabe |
| Breite des Fundaments | $b$ | $1.2$ | m | Vorgabe |
| Neigung des Geländes | $\beta$ | $0$ | ° | Vorgabe |
| Kohäsion, Bemessungswert | $c_{eff}$ | $40$ | kPa | berechnet |
| Kohäsion, charakteristisch | $c_k$ | $60$ | kPa | Vorgabe |
| Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ | $k_{\delta}$ | $1$ |  | Vorgabe |
| Raumlast des Bodens | $\gamma$ | $21$ | kN/m³ | Vorgabe |
| Raumlast des Bodens unter Auftrieb | $\gamma'$ | $11$ | kN/m³ | berechnet |
| Partialfaktor der Kohäsion | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Partialfaktor des Reibungswinkels | $\gamma_{\varphi}$ | $1.2$ |  | Vorgabe |
| Raumlast des Wassers | $\gamma_w$ | $10$ | kN/m³ | Vorgabe |
| Erfüllungsgrad Gleiten – Tragsicherheit | $\alpha_{eff,GL,\text{Tragsicherheit}}$ | $0.00$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Tragsicherheit | $\alpha_{eff,GB,\text{Tragsicherheit}}$ | $0.54$ |  | berechnet |
| Reibungswinkel, Bemessungswert | $\varphi_{eff}$ | $0$ | ° | berechnet |
| Reibungswinkel, charakteristisch | $\varphi_k$ | $0$ | ° | Vorgabe |
| Bemessungslast neben dem Fundament | $q_{Ed}$ | $0$ | kPa | Vorgabe |
| Tiefe der Sohle unter Terrain | $t$ | $2$ | m | Vorgabe |
| Tiefe des höchsten Grundwasserspiegels unter Terrain | $t_1$ | $0$ | m | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $123$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $186$ | mm | berechnet |
| Plattendicke | $h$ | $300$ | mm | Vorgabe |
| Abminderung der Betondruckfestigkeit in der Druckdiagonalen | $k_c$ | $0.55$ |  | Vorgabe |
| Momentenwiderstand bei N\_Ed = 0, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-79.9$ | kNm | berechnet |
| Momentenwiderstand bei N\_Ed = 0, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $235.9$ | kNm | berechnet |
| Druckwiderstand bei M\_Ed = 0 | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-6000$ | kN | berechnet |
| Zugwiderstand bei M\_Ed = 0 | $N_{Rd}^{+}(M_{Ed} = 0)$ | $737.5$ | kN | berechnet |
| Querkraftwiderstand mit Bügeln bei der günstigsten Neigung, N\_Ed = 0 | $V_{Rd}(\alpha_{opt})$ | $212.1$ | kN/m | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben | $\left(x/d\right)^{-}$ | $0.077$ |  | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten | $\left(x/d\right)^{+}$ | $0.253$ |  | berechnet |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,y,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,y,g}$ | $12$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 1. Lage Grundbewehrung ab Oberkante | $z_{1,y,g}$ | $264$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,x,g}$ | $1696$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,x,g}$ | $18$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 2. Lage Grundbewehrung ab Oberkante | $z_{2,x,g}$ | $249$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Zulage | $A_{s,2,x,z}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Zulage | $\varnothing_{2,x,z}$ | $12$ | mm | Vorgabe |
| Teilung 2. Lage Zulage | $s_{2,x,z}$ | $150$ | mm | Vorgabe |
| Tiefe 2. Lage Zulage ab Oberkante | $z_{2,x,z}$ | $246$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,x,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,x,g}$ | $12$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 3. Lage Grundbewehrung ab Oberkante | $z_{3,x,g}$ | $48$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,y,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,y,g}$ | $12$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 4. Lage Grundbewehrung ab Oberkante | $z_{4,y,g}$ | $36$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 2. Lage | $\alpha_{eff,D,2}$ | $1.39$ |  | berechnet |
| Bezogene Druckzonenhöhe – 2. Lage | $\left(x/d\right)_{2}$ | $0.253$ |  | berechnet |
| Erfüllungsgrad Duktilität – 3. Lage | $\alpha_{eff,D,3}$ | $4.57$ |  | berechnet |
| Bezogene Druckzonenhöhe – 3. Lage | $\left(x/d\right)_{3}$ | $0.077$ |  | berechnet |
| Erfüllungsgrad Knicken – Wand | $\alpha_{eff,K,\text{Wand}}$ | $5.62$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $235.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $1.57$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld mit Druck | $M_{Rd,x}(N_{Ed})_{\text{Feld mit Druck}}$ | $253.8$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld mit Druck | $\alpha_{eff,x,\text{Feld mit Druck}}$ | $2.12$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-79.9$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $235.9$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $324.4$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-253.4$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-6000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $1393.2$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Stütze | $M_{Rd,x}(N_{Ed})_{\text{Stütze}}$ | $79.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Stütze | $\alpha_{eff,x,\text{Stütze}}$ | $1.33$ |  | berechnet |
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
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Dauerlast | $\alpha_{eff,\sigma,w,x,\text{Dauerlast}}$ | $2.80$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $2.18$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld mit Druck (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld mit Druck (60 \%)}}$ | $3.60$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Stütze (60 %) | $\alpha_{eff,\sigma,w,x,\text{Stütze (60 \%)}}$ | $1.79$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $5.69$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $1.93$ |  | berechnet |
| Erfüllungsgrad Verformung – Feld | $\alpha_{eff,w,\text{Feld}}$ | $1.43$ |  | berechnet |
| Erfüllungsgrad Verformung – Kragarm | $\alpha_{eff,w,\text{Kragarm}}$ | $1.19$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $4.76$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $1.94$ |  | berechnet |
| Querschnitt eines Bügelschenkels | $A_{\varnothing,V}$ | $50.3$ | mm² | berechnet |
| Grösste Neigung der Druckdiagonalen | $\alpha_{max}$ | $45$ | ° | Vorgabe |
| Kleinste Neigung der Druckdiagonalen | $\alpha_{min}$ | $30$ | ° | Vorgabe |
| Bügelzahl über die betrachtete Breite | $n_{V,y}$ | $5$ |  | Vorgabe |
| Bügeldurchmesser | $\varnothing_{V}$ | $8$ | mm | Vorgabe |
| Bügelteilung in x-Richtung | $s_{V,x}$ | $200$ | mm | Vorgabe |
| Vergrösserungsfaktor der Durchbiegung, Zug oben | $\omega_w'$ | $7.52$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug unten | $\omega_w$ | $4$ |  | berechnet |
| Grösstkorndurchmesser | $D_{max}$ | $32$ | mm | Vorgabe |
| Betrachtete Breite (x) | $b$ | $500$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $67$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $104$ | mm | berechnet |
| Höhe der Einlage | $e_{Einlage}$ | $40$ | mm | Vorgabe |
| Plattendicke | $h$ | $200$ | mm | Vorgabe |
| Momentenwiderstand bei N\_Ed = 0, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-18.1$ | kNm | berechnet |
| Momentenwiderstand bei N\_Ed = 0, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $18.1$ | kNm | berechnet |
| Druckwiderstand bei M\_Ed = 0 | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-2000$ | kN | berechnet |
| Zugwiderstand bei M\_Ed = 0 | $N_{Rd}^{+}(M_{Ed} = 0)$ | $227.7$ | kN | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = 0 und N\_Ed = 0 | $V_{Rd,max}$ | $136.9$ | kN/m | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd und N\_Ed = 0 | $V_{Rd,min}$ | $95.7$ | kN/m | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben | $\left(x/d\right)^{-}$ | $0.081$ |  | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten | $\left(x/d\right)^{+}$ | $0.081$ |  | berechnet |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,x,g}$ | $262$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,x,g}$ | $10$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 1. Lage Grundbewehrung ab Oberkante | $z_{1,x,g}$ | $165$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,y,g}$ | $335$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,y,g}$ | $8$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 2. Lage Grundbewehrung ab Oberkante | $z_{2,y,g}$ | $156$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,y,g}$ | $335$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,y,g}$ | $8$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 3. Lage Grundbewehrung ab Oberkante | $z_{3,y,g}$ | $44$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,x,g}$ | $262$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,x,g}$ | $10$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 4. Lage Grundbewehrung ab Oberkante | $z_{4,x,g}$ | $35$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 1. Lage | $\alpha_{eff,D,1}$ | $4.31$ |  | berechnet |
| Bezogene Druckzonenhöhe – 1. Lage | $\left(x/d\right)_{1}$ | $0.081$ |  | berechnet |
| Erfüllungsgrad Duktilität – 4. Lage | $\alpha_{eff,D,4}$ | $4.31$ |  | berechnet |
| Bezogene Druckzonenhöhe – 4. Lage | $\left(x/d\right)_{4}$ | $0.081$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $18.1$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $0.45$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-18.1$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $18.1$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $56.3$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-56.3$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-2000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $227.7$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Rand | $M_{Rd,x}(N_{Ed})_{\text{Rand}}$ | $18.1$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Rand | $\alpha_{eff,x,\text{Rand}}$ | $1.81$ |  | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Feld | $\alpha_{eff,V,x,\text{Feld}}$ | $2.08$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Feld | $V_{Rd,x}$ | $83.2$ | kN/m | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Rand | $\alpha_{eff,V,x,\text{Rand}}$ | $3.69$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Rand | $V_{Rd,x}$ | $110.7$ | kN/m | berechnet |
| Erfüllungsgrad Rissnormalkraft – 1. Lage x | $\alpha_{eff,NR,1,x}$ | $0.99$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 4. Lage x | $\alpha_{eff,NR,4,x}$ | $0.99$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Dauerlast | $\alpha_{eff,\sigma,w,x,\text{Dauerlast}}$ | $0.54$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $0.00$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Rand (60 %) | $\alpha_{eff,\sigma,w,x,\text{Rand (60 \%)}}$ | $3.23$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 1. Lage x | $\alpha_{eff,SV,1,x}$ | $1.94$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 4. Lage x | $\alpha_{eff,SV,4,x}$ | $1.94$ |  | berechnet |
| Erfüllungsgrad Verformung – Feld | $\alpha_{eff,w,\text{Feld}}$ | $0.85$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 1. Lage x | $\alpha_{eff,ZB,1,x}$ | $2.17$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 4. Lage x | $\alpha_{eff,ZB,4,x}$ | $2.17$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug oben | $\omega_w'$ | $8.42$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug unten | $\omega_w$ | $8.42$ |  | berechnet |
| Grösstkorndurchmesser | $D_{max}$ | $32$ | mm | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $73$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $148$ | mm | berechnet |
| Höhe der Einlage | $e_{Einlage}$ | $0$ | mm | Vorgabe |
| Plattendicke | $h$ | $250$ | mm | Vorgabe |
| Momentenwiderstand bei N\_Ed = 0, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-45.4$ | kNm | berechnet |
| Momentenwiderstand bei N\_Ed = 0, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $64.2$ | kNm | berechnet |
| Druckwiderstand bei M\_Ed = 0 | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-5000$ | kN | berechnet |
| Zugwiderstand bei M\_Ed = 0 | $N_{Rd}^{+}(M_{Ed} = 0)$ | $475$ | kN | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = 0 und N\_Ed = 0 | $V_{Rd,max}$ | $223.5$ | kN/m | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd und N\_Ed = 0 | $V_{Rd,min}$ | $145.9$ | kN/m | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben | $\left(x/d\right)^{-}$ | $0.065$ |  | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten | $\left(x/d\right)^{+}$ | $0.095$ |  | berechnet |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,y,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,y,g}$ | $10$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 1. Lage Grundbewehrung ab Oberkante | $z_{1,y,g}$ | $215$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,x,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,x,g}$ | $12$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 2. Lage Grundbewehrung ab Oberkante | $z_{2,x,g}$ | $204$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,x,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,x,g}$ | $10$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 3. Lage Grundbewehrung ab Oberkante | $z_{3,x,g}$ | $45$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,y,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,y,g}$ | $10$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 4. Lage Grundbewehrung ab Oberkante | $z_{4,y,g}$ | $35$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 2. Lage | $\alpha_{eff,D,2}$ | $3.70$ |  | berechnet |
| Bezogene Druckzonenhöhe – 2. Lage | $\left(x/d\right)_{2}$ | $0.095$ |  | berechnet |
| Erfüllungsgrad Duktilität – 3. Lage | $\alpha_{eff,D,3}$ | $5.36$ |  | berechnet |
| Bezogene Druckzonenhöhe – 3. Lage | $\left(x/d\right)_{3}$ | $0.065$ |  | berechnet |
| Erfüllungsgrad Knicken – Stütze | $\alpha_{eff,K,\text{Stütze}}$ | $6.93$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rk,x}(N_{Ed})_{\text{Feld}}$ | $99.6$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $1.66$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rk,x}(N=0)^{-}$ | $-63.7$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rk,x}(N=0)^{+}$ | $81.3$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rk,x}^{+}$ | $261.6$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rk,x}^{-}$ | $-263.9$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rk,x}^{-}$ | $-7972.7$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rk,x}^{+}$ | $638.8$ | kN | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Feld | $\alpha_{eff,V,x,\text{Feld}}$ | $3.43$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Feld | $V_{Rd,x}$ | $171.7$ | kN/m | berechnet |
| Erfüllungsgrad Rissnormalkraft – 2. Lage x | $\alpha_{eff,NR,2,x}$ | $1.09$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 3. Lage x | $\alpha_{eff,NR,3,x}$ | $0.81$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen x-Richtung – Feld (70 %) | $\alpha_{eff,\sigma,x,\text{Feld (70 \%)}}$ | $1.72$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen x-Richtung – Gebrauch | $\alpha_{eff,\sigma,x,\text{Gebrauch}}$ | $1.10$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Dauerlast | $\alpha_{eff,\sigma,w,x,\text{Dauerlast}}$ | $2.29$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $3.11$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $2.80$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $2.20$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $2.32$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $1.75$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug oben | $\omega_w'$ | $10.42$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug unten | $\omega_w$ | $8.37$ |  | berechnet |
| Grösstkorndurchmesser | $D_{max}$ | $32$ | mm | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $61$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $124$ | mm | berechnet |
| Höhe der Einlage | $e_{Einlage}$ | $0$ | mm | Vorgabe |
| Plattendicke | $h$ | $220$ | mm | Vorgabe |
| Momentenwiderstand bei N\_Ed = 0, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-39$ | kNm | berechnet |
| Momentenwiderstand bei N\_Ed = 0, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $39$ | kNm | berechnet |
| Druckwiderstand bei M\_Ed = 0 | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-4400$ | kN | berechnet |
| Zugwiderstand bei M\_Ed = 0 | $N_{Rd}^{+}(M_{Ed} = 0)$ | $455.3$ | kN | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = 0 und N\_Ed = 0 | $V_{Rd,max}$ | $193.9$ | kN/m | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd und N\_Ed = 0 | $V_{Rd,min}$ | $132.6$ | kN/m | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben | $\left(x/d\right)^{-}$ | $0.076$ |  | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten | $\left(x/d\right)^{+}$ | $0.076$ |  | berechnet |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,y,g}$ | $335$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,y,g}$ | $8$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 1. Lage Grundbewehrung ab Oberkante | $z_{1,y,g}$ | $186$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,x,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,x,g}$ | $10$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 2. Lage Grundbewehrung ab Oberkante | $z_{2,x,g}$ | $177$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,x,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,x,g}$ | $10$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 3. Lage Grundbewehrung ab Oberkante | $z_{3,x,g}$ | $43$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,y,g}$ | $335$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,y,g}$ | $8$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 4. Lage Grundbewehrung ab Oberkante | $z_{4,y,g}$ | $34$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 2. Lage | $\alpha_{eff,D,2}$ | $4.63$ |  | berechnet |
| Bezogene Druckzonenhöhe – 2. Lage | $\left(x/d\right)_{2}$ | $0.076$ |  | berechnet |
| Erfüllungsgrad Duktilität – 3. Lage | $\alpha_{eff,D,3}$ | $4.63$ |  | berechnet |
| Bezogene Druckzonenhöhe – 3. Lage | $\left(x/d\right)_{3}$ | $0.076$ |  | berechnet |
| Erfüllungsgrad Knicken – Wand | $\alpha_{eff,K,\text{Wand}}$ | $8.77$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $44.8$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $1.79$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-44.8$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $44.8$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $147.5$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-147.5$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-4797.9$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $455.3$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Rand | $M_{Rd,x}(N_{Ed})_{\text{Rand}}$ | $52.4$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Rand | $\alpha_{eff,x,\text{Rand}}$ | $46.49$ |  | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Feld | $\alpha_{eff,V,x,\text{Feld}}$ | $5.14$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Feld | $V_{Rd,x}$ | $154.2$ | kN/m | berechnet |
| Erfüllungsgrad Rissnormalkraft – 2. Lage x | $\alpha_{eff,NR,2,x}$ | $0.91$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 3. Lage x | $\alpha_{eff,NR,3,x}$ | $0.91$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Dauerlast | $\alpha_{eff,\sigma,w,x,\text{Dauerlast}}$ | $3.82$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $3.06$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Rand (60 %) | $\alpha_{eff,\sigma,w,x,\text{Rand (60 \%)}}$ | $18.27$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $1.99$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $1.99$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $1.94$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $1.94$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug oben | $\omega_w'$ | $10.11$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug unten | $\omega_w$ | $10.11$ |  | berechnet |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $47$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $166$ | mm | berechnet |
| Plattendicke | $h$ | $250$ | mm | Vorgabe |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,y,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,y,g}$ | $12$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 1. Lage Grundbewehrung ab Oberkante | $z_{1,y,g}$ | $214$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,y,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,y,g}$ | $12$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 4. Lage Grundbewehrung ab Oberkante | $z_{4,y,g}$ | $36$ | mm | berechnet |
| Erfüllungsgrad M-N x-Richtung – Feld (keine Bewehrung) | $\alpha_{eff,M-N,x,\text{Feld}}$ | $0.00$ |  | berechnet |
| Erfüllungsgrad V x-Richtung – Feld (keine Bewehrung) | $\alpha_{eff,V,x,\text{Feld}}$ | $0.00$ |  | berechnet |
| Grösstkorndurchmesser | $D_{max}$ | $32$ | mm | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $327$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $116$ | mm | berechnet |
| Höhe der Einlage | $e_{Einlage}$ | $0$ | mm | Vorgabe |
| Plattendicke | $h$ | $250$ | mm | Vorgabe |
| Momentenwiderstand bei N\_Ed = 0, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-64.2$ | kNm | berechnet |
| Momentenwiderstand bei N\_Ed = 0, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $54.4$ | kNm | berechnet |
| Druckwiderstand bei M\_Ed = 0 | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-5000$ | kN | berechnet |
| Zugwiderstand bei M\_Ed = 0 | $N_{Rd}^{+}(M_{Ed} = 0)$ | $555.2$ | kN | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = 0 und N\_Ed = 0 | $V_{Rd,max}$ | $190.6$ | kN/m | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd und N\_Ed = 0 | $V_{Rd,min}$ | $131.1$ | kN/m | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug oben | $\left(x/d\right)^{-}$ | $0.095$ |  | berechnet |
| Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten | $\left(x/d\right)^{+}$ | $0.111$ |  | berechnet |
| Bewehrungsquerschnitt 1. Lage Grundbewehrung | $A_{s,1,y,g}$ | $8378$ | mm² | berechnet |
| Stabdurchmesser 1. Lage Grundbewehrung | $\varnothing_{1,y,g}$ | $40$ | mm | Vorgabe |
| Teilung 1. Lage Grundbewehrung | $s_{1,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 1. Lage Grundbewehrung ab Oberkante | $z_{1,y,g}$ | $200$ | mm | berechnet |
| Bewehrungsquerschnitt 2. Lage Grundbewehrung | $A_{s,2,x,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 2. Lage Grundbewehrung | $\varnothing_{2,x,g}$ | $12$ | mm | Vorgabe |
| Teilung 2. Lage Grundbewehrung | $s_{2,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 2. Lage Grundbewehrung ab Oberkante | $z_{2,x,g}$ | $174$ | mm | berechnet |
| Bewehrungsquerschnitt 3. Lage Grundbewehrung | $A_{s,3,x,g}$ | $754$ | mm² | berechnet |
| Stabdurchmesser 3. Lage Grundbewehrung | $\varnothing_{3,x,g}$ | $12$ | mm | Vorgabe |
| Teilung 3. Lage Grundbewehrung | $s_{3,x,g}$ | $150$ | mm | Vorgabe |
| Tiefe 3. Lage Grundbewehrung ab Oberkante | $z_{3,x,g}$ | $46$ | mm | berechnet |
| Bewehrungsquerschnitt 4. Lage Grundbewehrung | $A_{s,4,y,g}$ | $524$ | mm² | berechnet |
| Stabdurchmesser 4. Lage Grundbewehrung | $\varnothing_{4,y,g}$ | $10$ | mm | Vorgabe |
| Teilung 4. Lage Grundbewehrung | $s_{4,y,g}$ | $150$ | mm | Vorgabe |
| Tiefe 4. Lage Grundbewehrung ab Oberkante | $z_{4,y,g}$ | $35$ | mm | berechnet |
| Erfüllungsgrad Duktilität – 2. Lage | $\alpha_{eff,D,2}$ | $3.16$ |  | berechnet |
| Bezogene Druckzonenhöhe – 2. Lage | $\left(x/d\right)_{2}$ | $0.111$ |  | berechnet |
| Erfüllungsgrad Duktilität – 3. Lage | $\alpha_{eff,D,3}$ | $3.70$ |  | berechnet |
| Bezogene Druckzonenhöhe – 3. Lage | $\left(x/d\right)_{3}$ | $0.095$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $54.4$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $1.36$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-64.2$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $54.4$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $162.9$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-178.6$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-5000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $655.6$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Schräg | $M_{Rd,x}(N_{Ed})_{\text{Schräg}}$ | $82.6$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Schräg | $\alpha_{eff,x,\text{Schräg}}$ | $1.72$ |  | berechnet |
| Erfüllungsgrad Querkraft x-Richtung – Feld | $\alpha_{eff,V,x,\text{Feld}}$ | $2.86$ |  | berechnet |
| Querkraftwiderstand x-Richtung – Feld | $V_{Rd,x}$ | $142.9$ | kN/m | berechnet |
| Erfüllungsgrad Rissnormalkraft – 2. Lage x | $\alpha_{eff,NR,2,x}$ | $1.17$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 3. Lage x | $\alpha_{eff,NR,3,x}$ | $1.17$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $2.58$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Schräg (60 %) | $\alpha_{eff,\sigma,w,x,\text{Schräg (60 \%)}}$ | $\infty$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $1.87$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $2.21$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $2.11$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $2.48$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug oben | $\omega_w'$ | $8.05$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug unten | $\omega_w$ | $11.77$ |  | berechnet |
| Fläche des Bruttoquerschnitts | $A$ | $330000$ | mm² | berechnet |
| Stahlfläche der Bewehrung | $A_{s,tot}$ | $2373$ | mm² | berechnet |
| Trägheitsmoment um y | $I_y$ | $13275$ | ·10⁶ mm⁴ | berechnet |
| Deviationsmoment | $I_{yz}$ | $0$ | ·10⁶ mm⁴ | berechnet |
| Trägheitsmoment um z | $I_z$ | $22475$ | ·10⁶ mm⁴ | berechnet |
| Grösste Neigung der Druckdiagonalen | $\alpha_{max}$ | $45$ | ° | Vorgabe |
| Kleinste Neigung der Druckdiagonalen | $\alpha_{min}$ | $30$ | ° | Vorgabe |
| Abminderung der Betondruckfestigkeit in der Druckdiagonalen | $k_c$ | $0.55$ |  | Vorgabe |
| Erfüllungsgrad Duktilität – Zug links | $\alpha_{eff,x/d,\text{Zug links}}$ | $2.59$ |  | berechnet |
| Erfüllungsgrad Duktilität – Zug oben | $\alpha_{eff,x/d,\text{Zug oben}}$ | $4.09$ |  | berechnet |
| Erfüllungsgrad Duktilität – Zug rechts | $\alpha_{eff,x/d,\text{Zug rechts}}$ | $2.67$ |  | berechnet |
| Erfüllungsgrad Duktilität – Zug unten | $\alpha_{eff,x/d,\text{Zug unten}}$ | $3.02$ |  | berechnet |
| Erfüllungsgrad Biegung und Normalkraft – Feld | $\alpha_{eff,\text{Feld}}$ | $0.62$ |  | berechnet |
| Grösste aufnehmbare Druckkraft | $N_{Rd}^{-}$ | $-7501.7$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft | $N_{Rd}^{+}$ | $1031.7$ | kN | berechnet |
| Erfüllungsgrad Biegung und Normalkraft – Schief | $\alpha_{eff,\text{Schief}}$ | $2.29$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – ganzer Querschnitt | $\alpha_{eff,NR}$ | $1.27$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen – Feld (70 %) | $\alpha_{eff,\sigma,\text{Feld (70 \%)}}$ | $1.20$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen – Häufig schief | $\alpha_{eff,\sigma,\text{Häufig schief}}$ | $2.37$ |  | berechnet |
| Erfüllungsgrad Stahlspannung gegen Fliessen – Schief (70 %) | $\alpha_{eff,\sigma,\text{Schief (70 \%)}}$ | $20.05$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite – Dauer | $\alpha_{eff,\sigma,w,\text{Dauer}}$ | $4.50$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite – Feld (60 %) | $\alpha_{eff,\sigma,w,\text{Feld (60 \%)}}$ | $1.60$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite – Schief (60 %) | $\alpha_{eff,\sigma,w,\text{Schief (60 \%)}}$ | $26.63$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug links | $\alpha_{eff,Riss,\text{Zug links}}$ | $2.70$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug oben | $\alpha_{eff,Riss,\text{Zug oben}}$ | $1.67$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug rechts | $\alpha_{eff,Riss,\text{Zug rechts}}$ | $2.52$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug unten | $\alpha_{eff,Riss,\text{Zug unten}}$ | $3.08$ |  | berechnet |
| Moment der Längszugkraft um y – Feld | $\Delta M_y$ | $0$ | kNm | berechnet |
| Moment der Längszugkraft um z – Feld | $\Delta M_z$ | $-52$ | kNm | berechnet |
| Längszugkraft aus Querkraft und Torsion – Feld | $\Delta N$ | $664$ | kN | berechnet |
| Erfüllungsgrad Querkraft und Torsion – Feld | $\alpha_{eff,V,\text{Feld}}$ | $1.04$ |  | berechnet |
| Moment der Längszugkraft um y – Schief | $\Delta M_y$ | $0$ | kNm | berechnet |
| Moment der Längszugkraft um z – Schief | $\Delta M_z$ | $0$ | kNm | berechnet |
| Längszugkraft aus Querkraft und Torsion – Schief | $\Delta N$ | $173.2$ | kN | berechnet |
| Erfüllungsgrad Querkraft und Torsion – Schief | $\alpha_{eff,V,\text{Schief}}$ | $5.13$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug links | $\alpha_{eff,ZB,\text{Zug links}}$ | $1.73$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug oben | $\alpha_{eff,ZB,\text{Zug oben}}$ | $1.30$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug rechts | $\alpha_{eff,ZB,\text{Zug rechts}}$ | $1.45$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug unten | $\alpha_{eff,ZB,\text{Zug unten}}$ | $2.38$ |  | berechnet |
| Schwerpunkt, y | $y_S$ | $400$ | mm | berechnet |
| Schwerpunkt, z | $z_S$ | $300$ | mm | berechnet |
| Fläche des Bruttoquerschnitts | $A$ | $160000$ | mm² | berechnet |
| Stahlfläche der Bewehrung | $A_{s,tot}$ | $1885$ | mm² | berechnet |
| Trägheitsmoment um y | $I_y$ | $2133.3$ | ·10⁶ mm⁴ | berechnet |
| Deviationsmoment | $I_{yz}$ | $0$ | ·10⁶ mm⁴ | berechnet |
| Trägheitsmoment um z | $I_z$ | $2133.3$ | ·10⁶ mm⁴ | berechnet |
| Erfüllungsgrad Duktilität – Zug oben | $\alpha_{eff,x/d,\text{Zug oben}}$ | $2.52$ |  | berechnet |
| Erfüllungsgrad Duktilität – Zug unten | $\alpha_{eff,x/d,\text{Zug unten}}$ | $2.52$ |  | berechnet |
| Erfüllungsgrad Knicken – Seitlich | $\alpha_{eff,K,\text{Seitlich}}$ | $2.72$ |  | berechnet |
| Erfüllungsgrad Knicken – Stütze | $\alpha_{eff,K,\text{Stütze}}$ | $2.02$ |  | berechnet |
| Erfüllungsgrad Biegung und Normalkraft – Druck | $\alpha_{eff,\text{Druck}}$ | $2.91$ |  | berechnet |
| Grösste aufnehmbare Druckkraft | $N_{Rd}^{-}$ | $-5497.4$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft | $N_{Rd}^{+}$ | $942.5$ | kN | berechnet |
| Erfüllungsgrad Biegung und Normalkraft – Zug | $\alpha_{eff,\text{Zug}}$ | $2.36$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – ganzer Querschnitt | $\alpha_{eff,NR}$ | $2.44$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite – Dauer | $\alpha_{eff,\sigma,w,\text{Dauer}}$ | $16.04$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite – Druck (60 %) | $\alpha_{eff,\sigma,w,\text{Druck (60 \%)}}$ | $\infty$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite – Zug (60 %) | $\alpha_{eff,\sigma,w,\text{Zug (60 \%)}}$ | $3.93$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug oben | $\alpha_{eff,Riss,\text{Zug oben}}$ | $5.37$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug unten | $\alpha_{eff,Riss,\text{Zug unten}}$ | $5.37$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug oben | $\alpha_{eff,ZB,\text{Zug oben}}$ | $5.20$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug unten | $\alpha_{eff,ZB,\text{Zug unten}}$ | $5.20$ |  | berechnet |
| Schwerpunkt, y | $y_S$ | $200$ | mm | berechnet |
| Schwerpunkt, z | $z_S$ | $200$ | mm | berechnet |
