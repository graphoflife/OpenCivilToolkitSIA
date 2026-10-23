# Beispiel

103 Berechnungen ausgeführt, 156 Werte bestimmt.

## Herleitung

### Plattenanalyse: Decke über EG

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
M_{Ed} = 100\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 235.9\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{235.9\,\mathrm{kNm}}{100\,\mathrm{kNm}} = 2.36 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Feld mit Druck

**Einwirkung**

$$
M_{Ed} = 100\,\mathrm{kNm} \qquad N_{Ed} = -300\,\mathrm{kN}
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
\alpha_{eff,x,\text{Feld mit Druck}} = \frac{M_{Rd}}{M_{Ed}} = \frac{253.8\,\mathrm{kNm}}{100\,\mathrm{kNm}} = 2.54 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Stütze

**Einwirkung**

$$
M_{Ed} = -50\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{-} = -79.9\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,x,\text{Stütze}} = \frac{M_{Rd}}{M_{Ed}} = \frac{79.9\,\mathrm{kNm}}{50\,\mathrm{kNm}} = 1.60 \quad \Rightarrow \quad \text{erfüllt}
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

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,2,x}}{b \cdot d_{2,x}} = \frac{2450\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 248.1\,\mathrm{mm}} = 0.00988
$$

**Statische Höhe der Lage oben, ab dem gedrückten Rand unten**

$$
d_{3,x,g} = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}
$$

**Bewehrungsgehalt oben**

$$
\rho_{o} = \frac{A_{s,3,x,g}}{b \cdot d_{3,x,g}} = \frac{754\,\mathrm{mm}^{2}}{1000\,\mathrm{mm} \cdot 252\,\mathrm{mm}} = 0.00299
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{2,x}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00299}{10 \cdot 0.00988^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{300\,\mathrm{mm}}{248.1\,\mathrm{mm}}\right)^{3} \\
  &= 4
\end{aligned}
$$

**Vergrösserungsfaktor, Zug oben** *(SIA 262:2025, 4.4.3.2.5)*

$$
\begin{aligned}
  \omega_w' &= \frac{1 - 20 \cdot \rho_{u}}{10 \cdot \rho_{o}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{3,x,g}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00988}{10 \cdot 0.00299^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{300\,\mathrm{mm}}{252\,\mathrm{mm}}\right)^{3} \\
  &= 7.52
\end{aligned}
$$

### Verformung

> **Annahme:** w ist mit der Steifigkeit E\_cm ermittelt. Grenzwert w\_max = L/350 nach Vorgabe, nicht nachgeschlagen.

#### Verformung – Feld

**Wirksame Durchbiegung, Zug unten**

$$
w_{eff} = \omega_w \cdot w = 4 \cdot 3.5\,\mathrm{mm} = 14\,\mathrm{mm}
$$

**Grenzwert der Durchbiegung, nach Vorgabe**

$$
w_{max} = \frac{L}{350} = \frac{6\,\mathrm{m}}{350} = 17.1\,\mathrm{mm}
$$

**Durchbiegung gegen Grenzwert**

$$
w_{eff} = 14\,\mathrm{mm} \quad \le \quad w_{max} = 17.1\,\mathrm{mm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,w,\text{Feld}} = \frac{w_{max}}{w_{eff}} = \frac{17.1\,\mathrm{mm}}{14\,\mathrm{mm}} = 1.22 \quad \Rightarrow \quad \text{erfüllt}
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
d^{+} = z_{2,x,g} = 249\,\mathrm{mm}
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{+} = d^{+} = 249\,\mathrm{mm}
$$

**Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} = 272.8\,\mathrm{kN}/\mathrm{m}
$$

**Zug unten, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{+} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 249 \cdot 1.2} = 0.6062 \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug unten, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) &= k_d^{+} \cdot \tau_{cd} \cdot d_v^{+} \\
  &= 0.6062 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} \\
  &= 165.4\,\mathrm{kN}/\mathrm{m}
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

**Zug oben, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{-}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{-} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 252\,\mathrm{mm} = 276.1\,\mathrm{kN}/\mathrm{m}
$$

**Zug oben, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{-} = \frac{f_{yd}}{E_s} = \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 2.174\,\text{‰}
$$

**Beiwert für die statische Höhe**

$$
k_d^{-} = \frac{1}{1 + \varepsilon_v^{-} \cdot d^{-} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 252 \cdot 1.2} = 0.6034 \quad \left(d^{-}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug oben, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-}) &= k_d^{-} \cdot \tau_{cd} \cdot d_v^{-} \\
  &= 0.6034 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 252\,\mathrm{mm} \\
  &= 166.6\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = 0, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,max} &= \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right] \\
  &= \min\left[272.8\,\mathrm{kN}/\mathrm{m};\ 276.1\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 272.8\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
\begin{aligned}
  V_{Rd,min} &= \min\left[V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+});\ V_{Rd}^{-}(M_{Ed} = M_{Rd}^{-})\right] \\
  &= \min\left[165.4\,\mathrm{kN}/\mathrm{m};\ 166.6\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 165.4\,\mathrm{kN}/\mathrm{m}
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

### Querschnittsanalyse: Unterzug

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
| Polygon 1 | C30/37 | – | $4$ | $180000$ | $150.0$ | $300.0$ |

**Fläche des Bruttoquerschnitts**

$$
A = 180000\,\mathrm{mm}^{2}
$$

**Schwerpunkt, y**

$$
y_S = 150\,\mathrm{mm}
$$

**Schwerpunkt, z**

$$
z_S = 300\,\mathrm{mm}
$$

**Trägheitsmoment um y**

$$
I_y = 5400\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Trägheitsmoment um z**

$$
I_z = 1350\,\cdot 10^{6}\,\mathrm{mm}^{4}
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
| Linie 1 | $(50;\ 50) \rightarrow (250;\ 50)$ | $3 \varnothing 20\ @\ 100.0$ | B500B | $942$ |
| Linie 2 | $(50;\ 550) \rightarrow (250;\ 550)$ | $2 \varnothing 12\ @\ 200.0$ | B500B | $226$ |

**Stahlfläche der Bewehrung**

$$
A_{s,tot} = 1169\,\mathrm{mm}^{2}
$$

**Bügelquerschnitt je Länge einer Schubwand (n Schnitte)**

$$
\frac{A_{sw}}{s} = \frac{n \cdot \pi\, \varnothing^2 / 4}{s}
$$

**Schubwände**

| Wand | $\text{Achse}\ [\mathrm{mm}]$ | $l\ [\mathrm{mm}]$ | $b_w\ [\mathrm{mm}]$ | Bügel | $A_{sw}/s\ [\mathrm{mm}^2/\mathrm{m}]$ |
| :--- | :--- | ---: | ---: | :--- | ---: |
| Wand 1 | $(50;\ 50) \rightarrow (250;\ 50)$ | $200$ | $100$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |
| Wand 2 | $(250;\ 50) \rightarrow (250;\ 550)$ | $500$ | $100$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |
| Wand 3 | $(250;\ 550) \rightarrow (50;\ 550)$ | $200$ | $100$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |
| Wand 4 | $(50;\ 550) \rightarrow (50;\ 50)$ | $500$ | $100$ | $1 \times \varnothing 10\ @\ 150$ | $524$ |

**Dehnungsebene und innere Kräfte**

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

**Erfüllungsgrad bei fester Normalkraft und fester Richtung**

$$
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}
$$

**Werkstoffgesetz C30/37, Bemessungswerte: Beiwert der Parabel**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{cm}}{400 \cdot f_{cd}}\right) = \max\left(1;\ \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}}\right) = 4.2
$$

**Werkstoffgesetz C30/37, Bemessungswerte: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & |\varepsilon_c| > \varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetz C30/37, Bemessungswerte: Werte des Betons**

$$
f_{cd} = 20\,\mathrm{N}/\mathrm{mm}^{2} \quad \varepsilon_{c1d} = 2\,\text{‰} \quad \varepsilon_{c2d} = 3.5\,\text{‰}
$$

**Werkstoffgesetz B500B, Bemessungswerte: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & 0 \le \varepsilon_s \le \varepsilon_{ud} \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & -\varepsilon_{ud} \le \varepsilon_s < 0 \\[1ex] 0 & |\varepsilon_s| > \varepsilon_{ud} \quad (\text{jenseits der Bruchdehnung}) \end{cases}
$$

**Werkstoffgesetz B500B, Bemessungswerte: Werte des Stahls**

$$
f_{yd} = 435\,\mathrm{N}/\mathrm{mm}^{2} \quad f_{yd}^{-} = 435\,\mathrm{N}/\mathrm{mm}^{2} \quad E_s = 200000\,\mathrm{N}/\mathrm{mm}^{2} \quad \varepsilon_{ud} = 4.5\,\%
$$

**Reine Normalkraft**

| Grenze | Wert |
| :--- | ---: |
| reiner Zug, gleichmässig | $N_{Rd}^{+} = 508.1\,\mathrm{kN}$ |
| reiner Druck, gleichmässig | $N_{Rd}^{-} = -4044.1\,\mathrm{kN}$ |

#### Feld

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| N\_Ed | $0.0$ | kN |
| M\_y,Ed | $150.0$ | kNm |
| M\_z,Ed | $0.0$ | kNm |

Bruchzustand: Zugrichtung n = (0.000; -1.000), -90.0° gegen die y-Achse. Die Nulllinie steht senkrecht zur Zugrichtung, 229.4 mm auf der Druckseite des Schwerpunkts.

**Dehnungsebene**

| $\varepsilon_0\ [\text{‰}]$ | $\kappa\ [\mathrm{1/m}]$ |
| ---: | ---: |
| $11.371$ | $0.04957$ |

**Kräfte im Bruchzustand -- Beton als Resultierende, Bewehrung je Element**

| Teil | $F\ [\mathrm{kN}]$ | $y\ [\mathrm{mm}]$ | $z\ [\mathrm{mm}]$ | $\varepsilon\ [\text{‰}]$ | $\sigma\ [\mathrm{N/mm^2}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: |
| C30/37 | $-367.6$ | $150.0$ | $568.8$ | – | – |
| Linie 1 | $409.8$ | $150.0$ | $50.0$ | $23.76$ | $435$ |
| Linie 2 | $-42.2$ | $150.0$ | $550.0$ | $-1.02$ | $-204$ |

**Probe: Normalkraft**

$$
N_{Rd} = \sum F_i = 0\,\mathrm{kN}
$$

**Probe: Moment um y**

$$
M_{y,Rd} = -\sum F_i \cdot (z_i - z_S) = 211.8\,\mathrm{kNm}
$$

**Probe: Moment um z**

$$
M_{z,Rd} = -\sum F_i \cdot (y_i - y_S) = 0\,\mathrm{kNm}
$$

**Widerstand in der Richtung der Einwirkung**

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}} = \sqrt{\left(211.8\,\mathrm{kNm}\right)^{2} + \left(0\,\mathrm{kNm}\right)^{2}} = 211.8\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{211.8\,\mathrm{kNm}}{150\,\mathrm{kNm}} = 1.41 \quad \Rightarrow \quad \text{erfüllt}
$$

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
| Wand 1 | $200$ | $100$ | $20000$ | $524$ | 1 |
| Wand 2 | $500$ | $100$ | $50000$ | $524$ | 1 |
| Wand 3 | $200$ | $100$ | $20000$ | $524$ | 1 |
| Wand 4 | $500$ | $100$ | $50000$ | $524$ | 1 |

#### Feld

**Einwirkung**

| Einwirkung | Wert |  |
| :--- | ---: | :--- |
| V\_y,Ed | $0.0$ | kN |
| V\_z,Ed | $150.0$ | kN |
| T\_Ed | $15.0$ | kNm |

**Versatz: Moment der Querkraftanteile um den Schwerpunkt**

$$
\Delta T = \sum_i V_i \cdot r_i = 0\,\mathrm{kNm}
$$

**Was die Zellen tragen**

$$
T_{Zellen} = T_{Ed} - \Delta T = 15\,\mathrm{kNm} - 0\,\mathrm{kNm} = 15\,\mathrm{kNm}
$$

**Umlauf-Schubfluss der Zellen (Bredt)**

| Zelle | $A_k\ [\mathrm{mm}^2]$ | $q_k\ [\mathrm{kN/m}]$ |
| :--- | ---: | ---: |
| Zelle 1 | $100000$ | $75.0$ |

**Je Wand: Kraft aus der Querkraft, stärkster Schubfluss, Widerstand**

| Wand | $V_i\ [\mathrm{kN}]$ | $\vert q_{Ed}\vert \ [\mathrm{kN/m}]$ | $\alpha\ [{}^{\circ}]$ | $v_{Rd,s}\ [\mathrm{kN/m}]$ | $v_{Rd,c}\ [\mathrm{kN/m}]$ | $v_{Rd}\ [\mathrm{kN/m}]$ | $\alpha_{eff}$ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wand 1 | $0.0$ | $75.0$ | $30$ | $394.3$ | $476.3$ | $394.3$ | $5.26$ |
| Wand 2 | $75.0$ | $225.0$ | $30$ | $394.3$ | $476.3$ | $394.3$ | $1.75$ |
| Wand 3 | $0.0$ | $75.0$ | $30$ | $394.3$ | $476.3$ | $394.3$ | $5.26$ |
| Wand 4 | $-75.0$ | $75.0$ | $30$ | $394.3$ | $476.3$ | $394.3$ | $5.26$ |

Massgebend: Wand 2.

**Erfüllungsgrad**

$$
\alpha_{eff,V,\text{Feld}} = \frac{v_{Rd}}{q_{Ed}} = \frac{394.3\,\mathrm{kN}/\mathrm{m}}{225\,\mathrm{kN}/\mathrm{m}} = 1.75 \quad \Rightarrow \quad \text{erfüllt}
$$

### Grundbruch: Fundament Stütze

**Reibungswinkel, charakteristisch**

$$
\varphi_k = 32{}^{\circ}
$$

**Partialfaktor des Reibungswinkels** *(SIA 267:2013, 5.3.2.2)*

$$
\gamma_{\varphi} = 1.2
$$

**Reibungswinkel, Bemessungswert** *(SIA 267:2013, 5.3.2.1)*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 32{}^{\circ}}{1.2}\right) = 27.51{}^{\circ}
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
b = 2\,\mathrm{m}
$$

**Länge des Fundaments**

$$
L = 2.5\,\mathrm{m}
$$

**Tiefe des höchsten Grundwasserspiegels unter Terrain**

$$
t_1 = 5\,\mathrm{m}
$$

**Tiefe der Sohle unter Terrain**

$$
t = 1.2\,\mathrm{m}
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
N_q = e^{\pi \tan \varphi_{eff}} \cdot \tan^{2}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) = e^{\pi \tan 27.51{}^{\circ}} \cdot \tan^{2}\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right) = 13.95
$$

**Tragfähigkeitsfaktor der Kohäsion** *(Kap. 9.2.6)*

$$
N_c = \frac{N_q - 1}{\tan \varphi_{eff}} = \frac{13.95 - 1}{\tan 27.51{}^{\circ}} = 24.86
$$

**Tragfähigkeitsfaktor des Gleitkörpergewichts** *(Kap. 9.2.6)*

$$
N_{\gamma} = 1.8 \cdot \left(N_q - 1\right) \cdot \tan \varphi_{eff} = 1.8 \cdot \left(13.95 - 1\right) \cdot \tan 27.51{}^{\circ} = 12.14
$$

#### Gleitkörper und Grundwasser

**Reichweite des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  L_{Gl} &= b \cdot \tan\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \cdot e^{\frac{\pi}{2} \tan \varphi_{eff}} \\
  &= 2\,\mathrm{m} \cdot \tan\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right) \cdot e^{\frac{\pi}{2} \tan 27.51{}^{\circ}} \\
  &= 7.47\,\mathrm{m}
\end{aligned}
$$

**Tiefe des Gleitkörpers** *(Kap. 9.2.10)*

$$
\begin{aligned}
  H_{Gl} &= b \cdot \frac{\cos \varphi_{eff}}{2 \cos\left(45^\circ + \frac{\varphi_{eff}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \tan \varphi_{eff}} \\
  &= 2\,\mathrm{m} \cdot \frac{\cos 27.51{}^{\circ}}{2 \cos\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right) \tan 27.51{}^{\circ}} \\
  &= 2.92\,\mathrm{m}
\end{aligned}
$$

**Überlagerung auf Höhe der Sohle, Grundwasser tiefer** *(Kap. 9.2.8)*

$$
\sigma_{v,0} = \gamma \cdot t + q_{Ed} = 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 1.2\,\mathrm{m} + 0\,\mathrm{kPa} = 25.2\,\mathrm{kPa}
$$

**Abstand des Grundwassers unter der Sohle** *(Kap. 9.2.8)*

$$
T = t_1 - t = 5\,\mathrm{m} - 1.2\,\mathrm{m} = 3.8\,\mathrm{m}
$$

**Lage 3: Grundwasser tiefer als der Gleitkörper**

$$
T = 3.8\,\mathrm{m} \quad \ge \quad H_{Gl} = 2.92\,\mathrm{m}
$$

**Raumlast im Gleitkörper, über dem Wasser** *(Kap. 9.2.8)*

$$
\gamma_G = \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3}
$$

#### Form, Tiefe, Gelände und Sohle

**Formfaktor der Kohäsion** *(Kap. 9.2.12)*

$$
s_c = 1 + \frac{b}{L} \cdot \frac{N_q}{N_c} = 1 + \frac{2\,\mathrm{m}}{2.5\,\mathrm{m}} \cdot \frac{13.95}{24.86} = 1.45
$$

**Formfaktor der seitlichen Auflast** *(Kap. 9.2.12)*

$$
s_q = 1 + \frac{b}{L} \cdot \tan \varphi_{eff} = 1 + \frac{2\,\mathrm{m}}{2.5\,\mathrm{m}} \cdot \tan 27.51{}^{\circ} = 1.42
$$

**Formfaktor des Gleitkörpergewichts** *(Kap. 9.2.12)*

$$
s_{\gamma} = 1 - 0.4 \cdot \frac{b}{L} = 1 - 0.4 \cdot \frac{2\,\mathrm{m}}{2.5\,\mathrm{m}} = 0.68
$$

**Winkel der Einbindetiefe, in Grad** *(Kap. 9.2.13)*

$$
\vartheta_t = \arctan\frac{t}{b} = \arctan\frac{1.2\,\mathrm{m}}{2\,\mathrm{m}} = 31{}^{\circ}
$$

**Tiefenfaktor der Kohäsion** *(Kap. 9.2.13)*

$$
d_c = 1 + 0.007 \cdot \vartheta_t = 1 + 0.007 \cdot 31{}^{\circ} = 1.22
$$

**Tiefenfaktor der seitlichen Auflast** *(Kap. 9.2.13)*

$$
\begin{aligned}
  d_q &= 1 + 0.035 \cdot \tan \varphi_{eff} \cdot \left(1 - \sin \varphi_{eff}\right)^{2} \cdot \vartheta_t \\
  &= 1 + 0.035 \cdot \tan 27.51{}^{\circ} \cdot \left(1 - \sin 27.51{}^{\circ}\right)^{2} \cdot 31{}^{\circ} \\
  &= 1.16
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
b_q = e^{-0.035 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.035 \cdot 0{}^{\circ} \cdot \tan 27.51{}^{\circ}} = 1
$$

**Sohlneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.16)*

$$
b_{\gamma} = e^{-0.047 \cdot \alpha \cdot \tan \varphi_{eff}} = e^{-0.047 \cdot 0{}^{\circ} \cdot \tan 27.51{}^{\circ}} = 1
$$

> **Annahme:** b\_γ mit tan φ wie in Tabelle 9.2.18 -- im Text des Kapitels steht tan α; die Tabelle und die Formel für b\_q rechnen mit tan φ.

#### Grundbruch – Tragsicherheit

**Neigung der Last** *(Kap. 9.2.14)*

$$
\delta_R = \arctan\frac{T_{Ed}}{N_{Ed}} = \arctan\frac{150\,\mathrm{kN}}{1500\,\mathrm{kN}} = 5.7{}^{\circ}
$$

**Lastneigungsfaktor der seitlichen Auflast** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_q &= \left[1 - \frac{0.5 \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{0.5 \cdot 150\,\mathrm{kN}}{1500\,\mathrm{kN} + 2\,\mathrm{m} \cdot 2.5\,\mathrm{m} \cdot 0\,\mathrm{kPa} \cdot \cot 27.51{}^{\circ}}\right]^{5} \\
  &= 0.77
\end{aligned}
$$

**Lastneigungsfaktor der Kohäsion** *(Kap. 9.2.14)*

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1} = 0.77 - \frac{1 - 0.77}{13.95 - 1} = 0.76
$$

**Lastneigungsfaktor des Gleitkörpergewichts** *(Kap. 9.2.14)*

$$
\begin{aligned}
  i_{\gamma} &= \left[1 - \frac{\left(0.7 - \frac{\alpha}{450^\circ}\right) \cdot T_{Ed}}{N_{Ed} + b \cdot L \cdot c_{eff} \cdot \cot \varphi_{eff}}\right]^{5} \\
  &= \left[1 - \frac{\left(0.7 - \frac{0{}^{\circ}}{450^\circ}\right) \cdot 150\,\mathrm{kN}}{1500\,\mathrm{kN} + 2\,\mathrm{m} \cdot 2.5\,\mathrm{m} \cdot 0\,\mathrm{kPa} \cdot \cot 27.51{}^{\circ}}\right]^{5} \\
  &= 0.7
\end{aligned}
$$

**Bruchspannung in der Sohle** *(Kap. 9.2.10)*

$$
\begin{aligned}
  \sigma_f &= c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma} \\
  &= 0\,\mathrm{kPa} \cdot 24.86 \cdot 1.45 \cdot 1.22 \cdot 0.76 \cdot 1 \cdot 1 + 25.2\,\mathrm{kPa} \cdot 13.95 \cdot 1.42 \cdot 1.16 \cdot 0.77 \cdot 1 \cdot 1 + \tfrac{1}{2} \cdot 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 2\,\mathrm{m} \cdot 12.14 \cdot 0.68 \cdot 1 \cdot 0.7 \cdot 1 \cdot 1 \\
  &= 568.8\,\mathrm{kPa}
\end{aligned}
$$

**Grundbruchwiderstand** *(Kap. 9.2.10)*

$$
N_{Rd} = \sigma_f \cdot b \cdot L = 568.8\,\mathrm{kPa} \cdot 2\,\mathrm{m} \cdot 2.5\,\mathrm{m} = 2843.8\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
N_{Ed} = 1500\,\mathrm{kN} \quad \le \quad N_{Rd} = 2843.8\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GB,\text{Tragsicherheit}} = \frac{N_{Rd}}{N_{Ed}} = \frac{2843.8\,\mathrm{kN}}{1500\,\mathrm{kN}} = 1.90 \quad \Rightarrow \quad \text{erfüllt}
$$

**Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ**

$$
k_{\delta} = 1
$$

### Gleiten

**Reibungswinkel der Sohlfuge** *(Kap. 9.2.18)*

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff} = 1 \cdot 27.51{}^{\circ} = 27.51{}^{\circ}
$$

#### Gleiten – Tragsicherheit

**Gleitwiderstand** *(Kap. 9.2.18)*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 1500\,\mathrm{kN} \cdot \tan 27.51{}^{\circ} = 781.1\,\mathrm{kN}
$$

**Einwirkung gegen Widerstand**

$$
T_{Ed} = 150\,\mathrm{kN} \quad \le \quad T_{Rd} = 781.1\,\mathrm{kN}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,GL,\text{Tragsicherheit}} = \frac{T_{Rd}}{T_{Ed}} = \frac{781.1\,\mathrm{kN}}{150\,\mathrm{kN}} = 5.21 \quad \Rightarrow \quad \text{erfüllt}
$$

### Setzung: Fundament Stütze

**Breite des Fundaments**

$$
B = 2\,\mathrm{m}
$$

**Länge des Fundaments**

$$
L = 2.5\,\mathrm{m}
$$

**Pressung aus Wiederbelastung**

$$
q_W = 24\,\mathrm{kN}/\mathrm{m}^{2}
$$

**Pressung aus Erstbelastung**

$$
q_E = 196\,\mathrm{kN}/\mathrm{m}^{2}
$$

**Zulässige Setzung**

$$
s_{zul} = 25\,\mathrm{mm}
$$

**Grösste Dicke einer Teilschicht**

$$
\Delta z_{max} = 0.5\,\mathrm{m}
$$

**Dicke der Schicht 1**

$$
d_{1} = 2\,\mathrm{m}
$$

**M\_E-Wert der Schicht 1, Erstbelastung**

$$
M_{E,1} = 60\,\mathrm{MN}/\mathrm{m}^{2}
$$

**M\_E-Wert der Schicht 1, Wiederbelastung**

$$
M'_{E,1} = 180\,\mathrm{MN}/\mathrm{m}^{2}
$$

**Dicke der Schicht 2**

$$
d_{2} = 3\,\mathrm{m}
$$

**M\_E-Wert der Schicht 2, Erstbelastung**

$$
M_{E,2} = 15\,\mathrm{MN}/\mathrm{m}^{2}
$$

**M\_E-Wert der Schicht 2, Wiederbelastung**

$$
M'_{E,2} = 45\,\mathrm{MN}/\mathrm{m}^{2}
$$

**Dicke der Schicht 3**

$$
d_{3} = 4\,\mathrm{m}
$$

**M\_E-Wert der Schicht 3, Erstbelastung**

$$
M_{E,3} = 100\,\mathrm{MN}/\mathrm{m}^{2}
$$

**M\_E-Wert der Schicht 3, Wiederbelastung**

$$
M'_{E,3} = 250\,\mathrm{MN}/\mathrm{m}^{2}
$$

### Setzung

**Setzung einer Teilschicht** *(Kap. 8.5)*

$$
\Delta s = \frac{\bar{J} \, q_W \, \Delta z}{M'_E} + \frac{\bar{J} \, q_E \, \Delta z}{M_E} \qquad \bar{J} = \frac{J_o + J_u}{2} \qquad s = \sum \Delta s
$$

#### Einflussfaktor unter dem Punkt K

Starres Fundament: gerechnet wird im kennzeichnenden Punkt K -- dort setzt sich die schlaffe Last so stark, wie sich das starre Fundament im Mittel setzt.

**Abstand des Punktes K von der Ecke, längs L** *(Kap. 8.10, Bild 8.15)*

$$
x_K = 0.13 \cdot L = 0.13 \cdot 2.5\,\mathrm{m} = 0.33\,\mathrm{m}
$$

**Abstand des Punktes K von der Ecke, längs B** *(Kap. 8.10, Bild 8.15)*

$$
y_K = 0.13 \cdot B = 0.13 \cdot 2\,\mathrm{m} = 0.26\,\mathrm{m}
$$

**Einflussfaktor nach Boussinesq in der Tiefe z: die vier Rechtecke, die sich im Punkt treffen** *(Kap. 8.2)*

$$
\begin{aligned} J &= J_E(x, y) + J_E(L - x, y) + J_E(x, B - y) + J_E(L - x, B - y) \\ J_E(a, b) &= \frac{1}{2\pi} \left[\arctan\frac{a \, b}{z \, R} + \frac{a \, b \, z}{R} \left(\frac{1}{a^2 + z^2} + \frac{1}{b^2 + z^2}\right)\right] \qquad R = \sqrt{a^2 + b^2 + z^2} \end{aligned}
$$

#### Teilschichten

Jede Schicht in gleich dicke Teilschichten von höchstens Δz\_max = 0.5 m; J an Ober- und Unterkante, gemittelt. z ab der Sohle.

**Setzung je Teilschicht**

| Schicht | $z_o\ [\mathrm{m}]$ | $z_u\ [\mathrm{m}]$ | $J_o$ | $J_u$ | $\bar{J}$ | $\Delta s_W\ [\mathrm{mm}]$ | $\Delta s_E\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kies, sandig | $0.00$ | $0.50$ | $1.000$ | $0.654$ | $0.827$ | $0.06$ | $1.35$ |
| Kies, sandig | $0.50$ | $1.00$ | $0.654$ | $0.438$ | $0.546$ | $0.04$ | $0.89$ |
| Kies, sandig | $1.00$ | $1.50$ | $0.438$ | $0.332$ | $0.385$ | $0.03$ | $0.63$ |
| Kies, sandig | $1.50$ | $2.00$ | $0.332$ | $0.260$ | $0.296$ | $0.02$ | $0.48$ |
| Silt, tonig | $2.00$ | $2.50$ | $0.260$ | $0.206$ | $0.233$ | $0.06$ | $1.52$ |
| Silt, tonig | $2.50$ | $3.00$ | $0.206$ | $0.166$ | $0.186$ | $0.05$ | $1.22$ |
| Silt, tonig | $3.00$ | $3.50$ | $0.166$ | $0.135$ | $0.150$ | $0.04$ | $0.98$ |
| Silt, tonig | $3.50$ | $4.00$ | $0.135$ | $0.111$ | $0.123$ | $0.03$ | $0.80$ |
| Silt, tonig | $4.00$ | $4.50$ | $0.111$ | $0.093$ | $0.102$ | $0.03$ | $0.67$ |
| Silt, tonig | $4.50$ | $5.00$ | $0.093$ | $0.078$ | $0.085$ | $0.02$ | $0.56$ |
| Moräne | $5.00$ | $5.50$ | $0.078$ | $0.067$ | $0.072$ | $0.00$ | $0.07$ |
| Moräne | $5.50$ | $6.00$ | $0.067$ | $0.057$ | $0.062$ | $0.00$ | $0.06$ |
| Moräne | $6.00$ | $6.50$ | $0.057$ | $0.050$ | $0.054$ | $0.00$ | $0.05$ |
| Moräne | $6.50$ | $7.00$ | $0.050$ | $0.044$ | $0.047$ | $0.00$ | $0.05$ |
| Moräne | $7.00$ | $7.50$ | $0.044$ | $0.039$ | $0.041$ | $0.00$ | $0.04$ |
| Moräne | $7.50$ | $8.00$ | $0.039$ | $0.034$ | $0.036$ | $0.00$ | $0.04$ |
| Moräne | $8.00$ | $8.50$ | $0.034$ | $0.031$ | $0.032$ | $0.00$ | $0.03$ |
| Moräne | $8.50$ | $9.00$ | $0.031$ | $0.028$ | $0.029$ | $0.00$ | $0.03$ |

**Setzung je Schicht**

| Schicht | $z_o\ [\mathrm{m}]$ | $z_u\ [\mathrm{m}]$ | $M'_E\ [\mathrm{MN}/\mathrm{m}^{2}]$ | $M_E\ [\mathrm{MN}/\mathrm{m}^{2}]$ | $s_W\ [\mathrm{mm}]$ | $s_E\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kies, sandig | $0.00$ | $2.00$ | $180.0$ | $60.0$ | $0.14$ | $3.36$ | $3.49$ |
| Silt, tonig | $2.00$ | $5.00$ | $45.0$ | $15.0$ | $0.23$ | $5.75$ | $5.98$ |
| Moräne | $5.00$ | $9.00$ | $250.0$ | $100.0$ | $0.02$ | $0.37$ | $0.38$ |

Am Fuss der untersten Schicht, z = 9.00 m unter der Sohle, kommt noch J = 0.028 der Pressung an; darunter gilt der Baugrund als unzusammendrückbar (Kap. 8.4).

#### Setzung gegen zulässige Setzung

**Setzung aus Wiederbelastung** *(Kap. 8.5)*

$$
s_W = \sum \Delta s_W = 0.4\,\mathrm{mm}
$$

**Setzung aus Erstbelastung** *(Kap. 8.5)*

$$
s_E = \sum \Delta s_E = 9.5\,\mathrm{mm}
$$

**Setzung** *(Kap. 8.2)*

$$
s = s_W + s_E = 0.4\,\mathrm{mm} + 9.5\,\mathrm{mm} = 9.9\,\mathrm{mm}
$$

**Setzung gegen zulässige Setzung**

$$
s = 9.9\,\mathrm{mm} \quad \le \quad s_{zul} = 25\,\mathrm{mm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff,s} = \frac{s_{zul}}{s} = \frac{25\,\mathrm{mm}}{9.9\,\mathrm{mm}} = 2.54 \quad \Rightarrow \quad \text{erfüllt}
$$

### Balkensystem: Rahmen

**Querschnittsfläche, «Stütze 300×300» (Rechteck)**

$$
A_{\text{Q1}} = b_{\text{Q1}} \cdot h_{\text{Q1}} = 300\,\mathrm{mm} \cdot 300\,\mathrm{mm} = 90000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Stütze 300×300» (Rechteck)**

$$
I_{\text{Q1}} = \frac{b_{\text{Q1}} \cdot \left(h_{\text{Q1}}\right)^{3}}{12} = \frac{300\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3}}{12} = 675\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Querschnittsfläche, «Unterzug» (Bruttoquerschnitt der Querschnittsanalyse «Unterzug»)**

$$
A_{\text{Q2}} = 180000\,\mathrm{mm}^{2}
$$

**Flächenträgheitsmoment, «Unterzug» (Bruttoquerschnitt der Querschnittsanalyse «Unterzug»)**

$$
I_{\text{Q2}} = 5400\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

**Dehnsteifigkeit, «Stütze 300×300» aus C30/37**

$$
EA_{\text{Q1}} = E_{cm} \cdot A_{\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 90000\,\mathrm{mm}^{2} = 3026\,\mathrm{MN}
$$

**Biegesteifigkeit, «Stütze 300×300» aus C30/37**

$$
EI_{\text{Q1}} = E_{cm} \cdot I_{\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 675\,\cdot 10^{6}\,\mathrm{mm}^{4} = 22693\,\mathrm{kNm}^{2}
$$

**Dehnsteifigkeit, «Unterzug» aus C30/37**

$$
EA_{\text{Q2}} = E_{cm} \cdot A_{\text{Q2}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 180000\,\mathrm{mm}^{2} = 6052\,\mathrm{MN}
$$

**Biegesteifigkeit, «Unterzug» aus C30/37**

$$
EI_{\text{Q2}} = E_{cm} \cdot I_{\text{Q2}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 5400\,\cdot 10^{6}\,\mathrm{mm}^{4} = 181547\,\mathrm{kNm}^{2}
$$

> **Annahme:** Steifigkeit nach Vorgabe, nicht nachgeschlagen: E\_cm für Beton und E\_s für Betonstahl, am ungerissenen Bruttoquerschnitt, ohne Schubverformung; Gleichgewicht am unverformten System (Theorie 1. Ordnung).

**Stäbe**

| Stab | Knoten | $L\ [\mathrm{m}]$ | $\alpha\ [°]$ | Querschnitt | $EA\ [\mathrm{MN}]$ | $EI\ [\mathrm{kNm}^{2}]$ | Gelenk | Linienlager |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | K1 – K2 | $4.000$ | $90.0$ | Stütze 300×300 | $3026$ | $22693$ | – | – |
| L2 | K2 – K3 | $6.000$ | $0.0$ | Unterzug | $6052$ | $181547$ | – | – |
| L3 | K3 – K4 | $4.000$ | $-90.0$ | Stütze 300×300 | $3026$ | $22693$ | Anfang | – |

**Lager**

| Lager | Knoten | $x$ | $z$ | $\varphi$ |
| ---: | ---: | ---: | ---: | ---: |
| A1 | K1 | fest | fest | fest |
| A2 | K4 | fest | fest | frei |

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

Ein Gelenk gibt dem Stabende eine eigene Drehung als Unbekannte; der Knoten dreht sich unabhängig davon.

**Steifigkeitsmatrix L1, L = 4.000 m (kN, m)**

$$
\mathbf{k}_{\text{L1}} = \begin{bmatrix} 756444 & 0 & 0 & -756444 & 0 & 0 \\ 0 & 4255 & 8510 & 0 & -4255 & 8510 \\ 0 & 8510 & 22693 & 0 & -8510 & 11347 \\ -756444 & 0 & 0 & 756444 & 0 & 0 \\ 0 & -4255 & -8510 & 0 & 4255 & -8510 \\ 0 & 8510 & 11347 & 0 & -8510 & 22693 \end{bmatrix}
$$

**Steifigkeitsmatrix L2, L = 6.000 m (kN, m)**

$$
\mathbf{k}_{\text{L2}} = \begin{bmatrix} 1.009 \cdot 10^{6} & 0 & 0 & -1.009 \cdot 10^{6} & 0 & 0 \\ 0 & 10086 & 30258 & 0 & -10086 & 30258 \\ 0 & 30258 & 121031 & 0 & -30258 & 60516 \\ -1.009 \cdot 10^{6} & 0 & 0 & 1.009 \cdot 10^{6} & 0 & 0 \\ 0 & -10086 & -30258 & 0 & 10086 & -30258 \\ 0 & 30258 & 60516 & 0 & -30258 & 121031 \end{bmatrix}
$$

**Steifigkeitsmatrix L3, L = 4.000 m (kN, m)**

$$
\mathbf{k}_{\text{L3}} = \begin{bmatrix} 756444 & 0 & 0 & -756444 & 0 & 0 \\ 0 & 4255 & 8510 & 0 & -4255 & 8510 \\ 0 & 8510 & 22693 & 0 & -8510 & 11347 \\ -756444 & 0 & 0 & 756444 & 0 & 0 \\ 0 & -4255 & -8510 & 0 & 4255 & -8510 \\ 0 & 8510 & 11347 & 0 & -8510 & 22693 \end{bmatrix}
$$

**Schnittgrössen aus den Kräften an den Stabenden**

$$
N(0) = -s_{u,a} \qquad V(0) = s_{v,a} \qquad M(0) = -s_{\theta,a} \qquad \frac{\mathrm{d}N}{\mathrm{d}x} = -p_x \qquad \frac{\mathrm{d}V}{\mathrm{d}x} = p_y \qquad \frac{\mathrm{d}M}{\mathrm{d}x} = V - m
$$

**Biegelinie und Längsverschiebung**

$$
v'' = \frac{M}{EI} \qquad u' = \frac{N}{EA}
$$

8 Unbekannte: 1. u\_x(K2), 2. u\_z(K2), 3. φ(K2), 4. u\_x(K3), 5. u\_z(K3), 6. φ(K3), 7. φ(L3, Anfang), 8. φ(K4).

**Gesamtsteifigkeitsmatrix (kN, m)**

$$
\mathbf{K} = \begin{bmatrix} 1.013 \cdot 10^{6} & 0 & 8510 & -1.009 \cdot 10^{6} & 0 & 0 & 0 & 0 \\ 0 & 766530 & 30258 & 0 & -10086 & 30258 & 0 & 0 \\ 8510 & 30258 & 143724 & 0 & -30258 & 60516 & 0 & 0 \\ -1.009 \cdot 10^{6} & 0 & 0 & 1.013 \cdot 10^{6} & 0 & 0 & 8510 & 8510 \\ 0 & -10086 & -30258 & 0 & 766530 & -30258 & 0 & 0 \\ 0 & 30258 & 60516 & 0 & -30258 & 121031 & 0 & 0 \\ 0 & 0 & 0 & 8510 & 0 & 0 & 22693 & 11347 \\ 0 & 0 & 0 & 8510 & 0 & 0 & 11347 & 22693 \end{bmatrix}
$$

#### Lastfall «Eigengewicht»

**Lastvektor (kN, kNm) und Lösung (m, rad)**

$$
\mathbf{F} = \begin{bmatrix} 0 \\ -75.00 \\ -75.00 \\ 0 \\ -75.00 \\ 75.00 \\ 0 \\ 0 \end{bmatrix} \qquad \mathbf{x} = \mathbf{K}^{-1} \cdot \mathbf{F} = \begin{bmatrix} 0.002332 \\ -1.006 \cdot 10^{-4} \\ -0.001166 \\ 0.002332 \\ -9.769 \cdot 10^{-5} \\ 0.001203 \\ -5.830 \cdot 10^{-4} \\ -5.830 \cdot 10^{-4} \end{bmatrix}
$$

**Verschiebungen der Knoten**

| Knoten | $u_x\ [\mathrm{mm}]$ | $u_z\ [\mathrm{mm}]$ | $\varphi\ [\mathrm{mrad}]$ |
| ---: | ---: | ---: | ---: |
| K1 | $0.00$ | $0.00$ | $0.000$ |
| K2 | $2.33$ | $-0.10$ | $-1.166$ |
| K3 | $2.33$ | $-0.10$ | $1.203$ |
| K4 | $0.00$ | $0.00$ | $-0.583$ |

**Schnittgrössen an den Stabenden**

| Stab | $N_{a}\ [\mathrm{kN}]$ | $V_{a}\ [\mathrm{kN}]$ | $M_{a}\ [\mathrm{kNm}]$ | $N_{b}\ [\mathrm{kN}]$ | $V_{b}\ [\mathrm{kN}]$ | $M_{b}\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $-76.1$ | $0.0$ | $-6.6$ | $-76.1$ | $0.0$ | $-6.6$ |
| L2 | $0.0$ | $76.1$ | $-6.6$ | $0.0$ | $-73.9$ | $0.0$ |
| L3 | $-73.9$ | $0.0$ | $0.0$ | $-73.9$ | $0.0$ | $0.0$ |

**Lagerkräfte, auf das Tragwerk**

| Lager | $R_x\ [\mathrm{kN}]$ | $R_z\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: |
| A1 (K1) | $0.0$ | $76.1$ | $6.6$ |
| A2 (K4) | $0.0$ | $73.9$ | $0.0$ |

**Extremwerte**

| Stab | Grösse | kleinst | $x\ [\mathrm{m}]$ | grösst | $x\ [\mathrm{m}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $N$ | $-76.1\ \mathrm{kN}$ | $0.00$ | $-76.1\ \mathrm{kN}$ | $0.00$ |
| L1 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L1 | $M$ | $-6.6\ \mathrm{kNm}$ | $0.00$ | $-6.6\ \mathrm{kNm}$ | $4.00$ |
| L1 | $w$ | $-0.58\ \mathrm{mm}$ | $2.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L2 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L2 | $V$ | $-73.9\ \mathrm{kN}$ | $6.00$ | $76.1\ \mathrm{kN}$ | $0.00$ |
| L2 | $M$ | $-6.6\ \mathrm{kNm}$ | $0.00$ | $109.2\ \mathrm{kNm}$ | $3.04$ |
| L2 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $2.24\ \mathrm{mm}$ | $3.02$ |
| L3 | $N$ | $-73.9\ \mathrm{kN}$ | $0.00$ | $-73.9\ \mathrm{kN}$ | $0.00$ |
| L3 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L3 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $4.00$ |
| L3 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |

Grösste Durchbiegung gegen die Sehne: L2, w = 2.24 mm bei x = 3.02 m, L/w = 2676.

**Gleichgewichtsprobe (Moment um den Ursprung)**

|  | Lasten | Lager | Summe |  |
| ---: | ---: | ---: | ---: | ---: |
| $\sum F_x$ | $0.000$ | $0.000$ | $0.000$ | kN |
| $\sum F_z$ | $-150.000$ | $150.000$ | $0.000$ | kN |
| $\sum M_0$ | $-450.000$ | $450.000$ | $0.000$ | kNm |

#### Lastfall «Wind»

**Lastvektor (kN, kNm) und Lösung (m, rad)**

$$
\mathbf{F} = \begin{bmatrix} 6.000 \\ 0 \\ 4.000 \\ 0 \\ 0 \\ 0 \\ 0 \\ 0 \end{bmatrix} \qquad \mathbf{x} = \mathbf{K}^{-1} \cdot \mathbf{F} = \begin{bmatrix} 0.001577 \\ 1.658 \cdot 10^{-6} \\ -8.347 \cdot 10^{-5} \\ 0.001577 \\ -1.658 \cdot 10^{-6} \\ 4.090 \cdot 10^{-5} \\ -3.943 \cdot 10^{-4} \\ -3.943 \cdot 10^{-4} \end{bmatrix}
$$

**Verschiebungen der Knoten**

| Knoten | $u_x\ [\mathrm{mm}]$ | $u_z\ [\mathrm{mm}]$ | $\varphi\ [\mathrm{mrad}]$ |
| ---: | ---: | ---: | ---: |
| K1 | $0.00$ | $0.00$ | $0.000$ |
| K2 | $1.58$ | $0.00$ | $-0.083$ |
| K3 | $1.58$ | $0.00$ | $0.041$ |
| K4 | $0.00$ | $0.00$ | $-0.394$ |

**Schnittgrössen an den Stabenden**

| Stab | $N_{a}\ [\mathrm{kN}]$ | $V_{a}\ [\mathrm{kN}]$ | $M_{a}\ [\mathrm{kNm}]$ | $N_{b}\ [\mathrm{kN}]$ | $V_{b}\ [\mathrm{kN}]$ | $M_{b}\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $1.3$ | $12.0$ | $-16.5$ | $1.3$ | $0.0$ | $7.5$ |
| L2 | $0.0$ | $-1.3$ | $7.5$ | $0.0$ | $-1.3$ | $0.0$ |
| L3 | $-1.3$ | $0.0$ | $0.0$ | $-1.3$ | $0.0$ | $0.0$ |

**Lagerkräfte, auf das Tragwerk**

| Lager | $R_x\ [\mathrm{kN}]$ | $R_z\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: |
| A1 (K1) | $-12.0$ | $-1.3$ | $16.5$ |
| A2 (K4) | $0.0$ | $1.3$ | $0.0$ |

**Extremwerte**

| Stab | Grösse | kleinst | $x\ [\mathrm{m}]$ | grösst | $x\ [\mathrm{m}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $N$ | $1.3\ \mathrm{kN}$ | $0.00$ | $1.3\ \mathrm{kN}$ | $0.00$ |
| L1 | $V$ | $0.0\ \mathrm{kN}$ | $4.00$ | $12.0\ \mathrm{kN}$ | $0.00$ |
| L1 | $M$ | $-16.5\ \mathrm{kNm}$ | $0.00$ | $7.5\ \mathrm{kNm}$ | $4.00$ |
| L1 | $w$ | $-0.13\ \mathrm{mm}$ | $0.72$ | $0.15\ \mathrm{mm}$ | $3.00$ |
| L2 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L2 | $V$ | $-1.3\ \mathrm{kN}$ | $0.00$ | $-1.3\ \mathrm{kN}$ | $0.00$ |
| L2 | $M$ | $0.0\ \mathrm{kNm}$ | $6.00$ | $7.5\ \mathrm{kNm}$ | $0.00$ |
| L2 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.10\ \mathrm{mm}$ | $2.54$ |
| L3 | $N$ | $-1.3\ \mathrm{kN}$ | $0.00$ | $-1.3\ \mathrm{kN}$ | $0.00$ |
| L3 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L3 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $0.00$ |
| L3 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $0.00$ |

Grösste Durchbiegung gegen die Sehne: L1, w = 0.15 mm bei x = 3.00 m, L/w = 26583.

**Gleichgewichtsprobe (Moment um den Ursprung)**

|  | Lasten | Lager | Summe |  |
| ---: | ---: | ---: | ---: | ---: |
| $\sum F_x$ | $12.000$ | $-12.000$ | $0.000$ | kN |
| $\sum F_z$ | $0.000$ | $0.000$ | $0.000$ | kN |
| $\sum M_0$ | $-24.000$ | $24.000$ | $0.000$ | kNm |

#### Kombination «Tragsicherheit»

1\.35 · Eigengewicht + 1.5 · Wind

**Lastvektor (kN, kNm) und Lösung (m, rad)**

$$
\mathbf{F} = \begin{bmatrix} 9.000 \\ -101.2 \\ -95.25 \\ 0 \\ -101.3 \\ 101.3 \\ 0 \\ 0 \end{bmatrix} \qquad \mathbf{x} = \mathbf{K}^{-1} \cdot \mathbf{F} = \begin{bmatrix} 0.005514 \\ -1.333 \cdot 10^{-4} \\ -0.001699 \\ 0.005514 \\ -1.344 \cdot 10^{-4} \\ 0.001686 \\ -0.001378 \\ -0.001378 \end{bmatrix}
$$

**Verschiebungen der Knoten**

| Knoten | $u_x\ [\mathrm{mm}]$ | $u_z\ [\mathrm{mm}]$ | $\varphi\ [\mathrm{mrad}]$ |
| ---: | ---: | ---: | ---: |
| K1 | $0.00$ | $0.00$ | $0.000$ |
| K2 | $5.51$ | $-0.13$ | $-1.699$ |
| K3 | $5.51$ | $-0.13$ | $1.686$ |
| K4 | $0.00$ | $0.00$ | $-1.378$ |

**Schnittgrössen an den Stabenden**

| Stab | $N_{a}\ [\mathrm{kN}]$ | $V_{a}\ [\mathrm{kN}]$ | $M_{a}\ [\mathrm{kNm}]$ | $N_{b}\ [\mathrm{kN}]$ | $V_{b}\ [\mathrm{kN}]$ | $M_{b}\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $-100.9$ | $18.0$ | $-33.6$ | $-100.9$ | $0.0$ | $2.4$ |
| L2 | $0.0$ | $100.9$ | $2.4$ | $0.0$ | $-101.6$ | $0.0$ |
| L3 | $-101.6$ | $0.0$ | $0.0$ | $-101.6$ | $0.0$ | $0.0$ |

**Lagerkräfte, auf das Tragwerk**

| Lager | $R_x\ [\mathrm{kN}]$ | $R_z\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| ---: | ---: | ---: | ---: |
| A1 (K1) | $-18.0$ | $100.9$ | $33.6$ |
| A2 (K4) | $0.0$ | $101.6$ | $0.0$ |

**Extremwerte**

| Stab | Grösse | kleinst | $x\ [\mathrm{m}]$ | grösst | $x\ [\mathrm{m}]$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| L1 | $N$ | $-100.9\ \mathrm{kN}$ | $0.00$ | $-100.9\ \mathrm{kN}$ | $0.00$ |
| L1 | $V$ | $0.0\ \mathrm{kN}$ | $4.00$ | $18.0\ \mathrm{kN}$ | $0.00$ |
| L1 | $M$ | $-33.6\ \mathrm{kNm}$ | $0.00$ | $2.4\ \mathrm{kNm}$ | $4.00$ |
| L1 | $w$ | $-0.81\ \mathrm{mm}$ | $1.38$ | $0.00\ \mathrm{mm}$ | $0.00$ |
| L2 | $N$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L2 | $V$ | $-101.6\ \mathrm{kN}$ | $6.00$ | $100.9\ \mathrm{kN}$ | $0.00$ |
| L2 | $M$ | $0.0\ \mathrm{kNm}$ | $6.00$ | $153.1\ \mathrm{kNm}$ | $2.99$ |
| L2 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $3.17\ \mathrm{mm}$ | $3.00$ |
| L3 | $N$ | $-101.6\ \mathrm{kN}$ | $0.00$ | $-101.6\ \mathrm{kN}$ | $0.00$ |
| L3 | $V$ | $0.0\ \mathrm{kN}$ | $0.00$ | $0.0\ \mathrm{kN}$ | $0.00$ |
| L3 | $M$ | $0.0\ \mathrm{kNm}$ | $0.00$ | $0.0\ \mathrm{kNm}$ | $4.00$ |
| L3 | $w$ | $0.00\ \mathrm{mm}$ | $0.00$ | $0.00\ \mathrm{mm}$ | $2.44$ |

Grösste Durchbiegung gegen die Sehne: L2, w = 3.17 mm bei x = 3.00 m, L/w = 1895.

**Gleichgewichtsprobe (Moment um den Ursprung)**

|  | Lasten | Lager | Summe |  |
| ---: | ---: | ---: | ---: | ---: |
| $\sum F_x$ | $18.000$ | $-18.000$ | $0.000$ | kN |
| $\sum F_z$ | $-202.500$ | $202.500$ | $0.000$ | kN |
| $\sum M_0$ | $-643.500$ | $643.500$ | $0.000$ | kNm |

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

### Verformung

Eine Durchbiegung, mit der Steifigkeit E\_cm ermittelt, gilt für die ungerissene Platte. Die gerissene ist weicher, und unter Dauerlast kriecht der Beton; um wie viel beides die Durchbiegung vergrössert, schätzt der Faktor ω\_w. Er hängt nur an der Platte und an der Seite, die gezogen wird: ω\_w für Zug unten, ω\_w′ für Zug oben.

Gerechnet in x, je Seite mit x-Bewehrung – einmal je Platte, nicht je Fall. ρ gehört zur gezogenen Seite, ρ′ zur Gegenseite; d′ reicht vom gezogenen Rand bis zur Gegenlage und ist damit deren statische Höhe – ρ′ der einen Seite ist das ρ der anderen. Die x-Bewehrung einer Seite zählt zusammen, in ihrem Schwerpunkt.

Die Durchbiegung w ist mit der Steifigkeit E\_cm ermittelt: elastisch, am ungerissenen Querschnitt. Der Faktor ω\_w der gezogenen Seite führt sie auf die gerissene Platte unter Dauerlast; die so vergrösserte Durchbiegung hält der Nachweis gegen L/350.

**Vergrösserungsfaktor der Durchbiegung – allgemein** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

**Bewehrungsgehalt unten**

$$
\rho_{u} = \frac{A_{s,2,x}}{b \cdot d_{2,x}}
$$

**Vergrösserungsfaktor, Zug unten** *(SIA 262:2025, 4.4.3.2.5)*

$$
\omega_w = \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{2,x}}\right)^{3}
$$

**Wirksame Durchbiegung, Zug unten**

$$
w_{eff} = \omega_w \cdot w
$$

**Grenzwert der Durchbiegung, nach Vorgabe**

$$
w_{max} = \frac{L}{350}
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

**Werkstoffgesetz C30/37, Bemessungswerte: Beiwert der Parabel**

$$
k_{\sigma} = \max\left(1;\ \frac{E_{cm}}{400 \cdot f_{cd}}\right)
$$

**Werkstoffgesetz C30/37, Bemessungswerte: Beton, Parabel-Rechteck** *(SIA 262:2025, 4.2.1.6)*

$$
\sigma_c(\varepsilon_c) = \begin{cases} -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta} & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ \eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex] -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex] 0 & |\varepsilon_c| > \varepsilon_{c2d} \quad (\text{jenseits der Bruchstauchung}) \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

**Werkstoffgesetz B500B, Bemessungswerte: Stahl, bilinear** *(SIA 262:2025, 4.2.2.4)*

$$
\sigma_s(\varepsilon_s) = \begin{cases} \min(E_s\,\varepsilon_s;\ f_{yd}) & 0 \le \varepsilon_s \le \varepsilon_{ud} \\[1ex] \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & -\varepsilon_{ud} \le \varepsilon_s < 0 \\[1ex] 0 & |\varepsilon_s| > \varepsilon_{ud} \quad (\text{jenseits der Bruchdehnung}) \end{cases}
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

**Raumlast im Gleitkörper, über dem Wasser** *(Kap. 9.2.8)*

$$
\gamma_G = \gamma
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

### Setzung

Unter der Last drückt sich das Korngerüst des Bodens zusammen. Je Teilschicht zählt die Zusatzspannung, die von der Pressung in der Sohle in ihrer Tiefe noch ankommt, und der M\_E-Wert ihrer Schicht: was den Boden nur wieder so stark belastet, wie er schon einmal belastet war, mit dem Modul der Wiederbelastung M'\_E, was darüber hinausgeht, mit dem der Erstbelastung M\_E. Unter der untersten Schicht gilt der Baugrund als unzusammendrückbar.

**Setzung einer Teilschicht** *(Kap. 8.5)*

$$
\Delta s = \frac{\bar{J} \, q_W \, \Delta z}{M'_E} + \frac{\bar{J} \, q_E \, \Delta z}{M_E} \qquad \bar{J} = \frac{J_o + J_u}{2} \qquad s = \sum \Delta s
$$

**Abstand des Punktes K von der Ecke, längs L** *(Kap. 8.10, Bild 8.15)*

$$
x_K = 0.13 \cdot L
$$

**Abstand des Punktes K von der Ecke, längs B** *(Kap. 8.10, Bild 8.15)*

$$
y_K = 0.13 \cdot B
$$

**Einflussfaktor nach Boussinesq in der Tiefe z: die vier Rechtecke, die sich im Punkt treffen** *(Kap. 8.2)*

$$
\begin{aligned} J &= J_E(x, y) + J_E(L - x, y) + J_E(x, B - y) + J_E(L - x, B - y) \\ J_E(a, b) &= \frac{1}{2\pi} \left[\arctan\frac{a \, b}{z \, R} + \frac{a \, b \, z}{R} \left(\frac{1}{a^2 + z^2} + \frac{1}{b^2 + z^2}\right)\right] \qquad R = \sqrt{a^2 + b^2 + z^2} \end{aligned}
$$

**Setzung aus Wiederbelastung** *(Kap. 8.5)*

$$
s_W = \sum \Delta s_W
$$

**Setzung aus Erstbelastung** *(Kap. 8.5)*

$$
s_E = \sum \Delta s_E
$$

**Setzung** *(Kap. 8.2)*

$$
s = s_W + s_E
$$

### Kennzahlen

Was die Platte in x aufnimmt, ohne Bezug auf eine Einwirkung: die Eckwerte der Handrechnung mit Bemessungswerten und der Querkraftwiderstand ohne Normalkraft. Wo eine Seite massgebend ist, gilt das Kleinere beider Seiten.

Ohne Bügel hängt der Widerstand am Moment: am grössten bei M\_Ed = 0, wo die Dehnung null ist, am kleinsten bei M\_Ed = M\_Rd, wo die Bewehrung zu fliessen beginnt und die Dehnung f\_yd/E\_s erreicht. Je Seite gilt ihre statische Höhe.

**Bezogene Druckzonenhöhe bei N\_Ed = 0, Zug unten**

$$
\left(x/d\right)^{+} = \frac{x^{+}}{d_{2,x}}
$$

**Zugwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{+}(M_{Ed} = 0) = N_1 + \frac{M_{Ed} - M_1}{M_2 - M_1} \cdot \left(N_2 - N_1\right)
$$

**Druckwiderstand bei M\_Ed = 0**

$$
N_{Rd}^{-}(M_{Ed} = 0) = N_{Rd}^{-}
$$

**Beiwert der Gesteinskörnung** *(SIA 262:2025, 4.3.3.2.1)*

$$
k_g = \max\left[1.20;\ \frac{48}{16 + D_{max} \cdot \min\left[1.0;\ \left(\frac{60}{f_{ck}}\right)^{2}\right]}\right] \quad \left(D_{max}\ \text{in}\ \mathrm{mm},\ f_{ck}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

**Wirksame Höhe (Einlage nicht massgebend)**

$$
d_v^{+} = d^{+}
$$

**Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+}
$$

**Zug unten, M\_Ed = M\_Rd: Dehnung beim Fliessbeginn**

$$
\varepsilon_v^{+} = \frac{f_{yd}}{E_s}
$$

**Beiwert für die statische Höhe**

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

**Zug unten, M\_Ed = M\_Rd** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) = k_d^{+} \cdot \tau_{cd} \cdot d_v^{+}
$$

**Querkraftwiderstand ohne Bügel bei M\_Ed = 0, das Kleinere beider Seiten** *(SIA 262:2025, 4.3.3.2.1)*

$$
V_{Rd,max} = \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right]
$$

### Stabquerschnitte

**Querschnittsfläche, «Stütze 300×300» (Rechteck)**

$$
A_{\text{Q1}} = b_{\text{Q1}} \cdot h_{\text{Q1}}
$$

**Flächenträgheitsmoment, «Stütze 300×300» (Rechteck)**

$$
I_{\text{Q1}} = \frac{b_{\text{Q1}} \cdot \left(h_{\text{Q1}}\right)^{3}}{12}
$$

**Dehnsteifigkeit, «Stütze 300×300» aus C30/37**

$$
EA_{\text{Q1}} = E_{cm} \cdot A_{\text{Q1}}
$$

**Biegesteifigkeit, «Stütze 300×300» aus C30/37**

$$
EI_{\text{Q1}} = E_{cm} \cdot I_{\text{Q1}}
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

### Decke über EG

**Angaben zur Platte**

$$
\text{Beton C30/37} \qquad h = 300\,\mathrm{mm} \qquad b_x = 1000\,\mathrm{mm}
$$

**Bewehrung von oben nach unten**

| Lage | Richtung | Bewehrung | Stahl | Höhe ab UK [mm] |
| :--- | :--- | :--- | :--- | ---: |
| Überdeckung oben | – | $30\,\mathrm{mm}$ | – | – |
| 4. Lage | y | $\varnothing 12@150$ | B500B | $264$ |
| 3. Lage | x | $\varnothing 12@150$ | B500B | $252$ |
| 2. Lage | x | $\varnothing 18@150 + \varnothing 12@150$ | B500B | $51 / 54$ |
| 1. Lage | y | $\varnothing 12@150$ | B500B | $36$ |
| Überdeckung unten | – | $30\,\mathrm{mm}$ | – | – |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 235.9\,\mathrm{kNm}$ | $M_{Ed,x} = 100.0\,\mathrm{kNm}$ | $2.36$ |
| Biegung und Normalkraft | Feld mit Druck | $M_{Rd,x}(N_{Ed} = -300\,\mathrm{kN}) = 253.8\,\mathrm{kNm}$ | $M_{Ed,x} = 100.0\,\mathrm{kNm}$ | $2.54$ |
| Biegung und Normalkraft | Stütze | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = -79.9\,\mathrm{kNm}$ | $M_{Ed,x} = -50.0\,\mathrm{kNm}$ | $1.60$ |
| Verformung | Feld | $w_{max} = 17.1\,\mathrm{mm}$ | $w_{eff} = 14.0\,\mathrm{mm}$ | $1.22$ |

> **Hinweis:** Risse: Zwängung Normalkraft – 3. Lage: nicht erfüllt (α\_eff = 0.996), ausgeschaltet. N\_s,adm = 754 mm² · 500 N/mm² = 377.0 kN \< N\_Riss = 378.3 kN.

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
| Querkraftwiderstand ohne Bügel, grösster | $V_{Rd,max}$ | $272.8\,\mathrm{kN}/\mathrm{m}$ |
| Querkraftwiderstand ohne Bügel, kleinster | $V_{Rd,min}$ | $165.4\,\mathrm{kN}/\mathrm{m}$ |

### Unterzug

**Angaben zum Querschnitt**

$$
\text{C30/37} \qquad A = 180000\,\mathrm{mm}^2 \qquad y_S = 150.0\,\mathrm{mm} \qquad z_S = 300.0\,\mathrm{mm}
$$

**Bewehrung und Schubwände**

| Element | Bewehrung | Stahl |
| :--- | :--- | :--- |
| Linie 1 | $3 \varnothing 20$ | B500B |
| Linie 2 | $2 \varnothing 12$ | B500B |
| Wand 1 | $b_w = 100,\ 1 \times \varnothing 10\ @\ 150$ | B500B |
| Wand 2 | $b_w = 100,\ 1 \times \varnothing 10\ @\ 150$ | B500B |
| Wand 3 | $b_w = 100,\ 1 \times \varnothing 10\ @\ 150$ | B500B |
| Wand 4 | $b_w = 100,\ 1 \times \varnothing 10\ @\ 150$ | B500B |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd} = 211.8\,\mathrm{kNm}$ | $M_{Ed} = 150.0\,\mathrm{kNm}$ | $1.41$ |
| Querkraft und Torsion | Feld | $v_{Rd} = 394.3\,\mathrm{kN}/\mathrm{m}$ | $q_{Ed} = 225.0\,\mathrm{kN}/\mathrm{m}$ | $1.75$ |

### Fundament Stütze

**Angaben zum Fundament**

$$
\begin{aligned} & \varphi_{eff} = 27.51{}^{\circ} \qquad c_{eff} = 0\,\mathrm{kPa} \qquad \gamma = 21\,\mathrm{kN}/\mathrm{m}^{3} \qquad \gamma' = 11\,\mathrm{kN}/\mathrm{m}^{3} \\ & b = 2\,\mathrm{m} \qquad L = 2.5\,\mathrm{m} \qquad t = 1.2\,\mathrm{m} \qquad t_1 = 5\,\mathrm{m} \end{aligned}
$$

**Tragfähigkeitsfaktoren**

| Kohäsion |  | Seitliche Auflast |  | Gewicht Gleitkörper |  |
| :--- | ---: | :--- | ---: | :--- | ---: |
| $N_{c}$ | $24.86$ | $N_{q}$ | $13.95$ | $N_{\gamma}$ | $12.14$ |
| $s_{c}$ | $1.45$ | $s_{q}$ | $1.42$ | $s_{\gamma}$ | $0.68$ |
| $d_{c}$ | $1.22$ | $d_{q}$ | $1.16$ | $d_{\gamma}$ | $1.00$ |
| $i_{c}$ | $0.76$ | $i_{q}$ | $0.77$ | $i_{\gamma}$ | $0.70$ |
| $g_{c}$ | $1.00$ | $g_{q}$ | $1.00$ | $g_{\gamma}$ | $1.00$ |
| $b'_{c}$ | $1.00$ | $b'_{q}$ | $1.00$ | $b'_{\gamma}$ | $1.00$ |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Grundbruch | Tragsicherheit | $N_{Rd} = 2843.8\,\mathrm{kN}$ | $N_{Ed} = 1500.0\,\mathrm{kN}$ | $1.90$ |
| Gleiten | Tragsicherheit | $T_{Rd} = 781.1\,\mathrm{kN}$ | $T_{Ed} = 150.0\,\mathrm{kN}$ | $5.21$ |

### Fundament Stütze

**Angaben zum Fundament**

$$
B = 2\,\mathrm{m} \qquad L = 2.5\,\mathrm{m} \qquad q_W = 24\,\mathrm{kN}/\mathrm{m}^{2} \qquad q_E = 196\,\mathrm{kN}/\mathrm{m}^{2} \qquad \text{starr, Punkt K}
$$

**Schichten**

| Schicht | $z\ [\mathrm{m}]$ | $M_E\ [\mathrm{MN}/\mathrm{m}^{2}]$ | $M'_E\ [\mathrm{MN}/\mathrm{m}^{2}]$ | $s_W\ [\mathrm{mm}]$ | $s_E\ [\mathrm{mm}]$ | $s\ [\mathrm{mm}]$ |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Kies, sandig | $0.00 – 2.00$ | $60.0$ | $180.0$ | $0.1$ | $3.4$ | $3.5$ |
| Silt, tonig | $2.00 – 5.00$ | $15.0$ | $45.0$ | $0.2$ | $5.7$ | $6.0$ |
| Moräne | $5.00 – 9.00$ | $100.0$ | $250.0$ | $0.0$ | $0.4$ | $0.4$ |

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Setzung | starr, Punkt K | $s_{zul} = 25.0\,\mathrm{mm}$ | $s = 9.9\,\mathrm{mm}$ | $2.54$ |

Alle geführten Nachweise sind erfüllt.

## Werte

| Bezeichnung | Symbol | Wert | Einheit | Herkunft |
| :--- | :--- | ---: | :--- | :--- |
| Querschnittsfläche, Stütze 300×300 | $A_{\text{Q1}}$ | $90000$ | mm² | berechnet |
| Flächenträgheitsmoment, Stütze 300×300 | $I_{\text{Q1}}$ | $675$ | ·10⁶ mm⁴ | berechnet |
| Breite, Stütze 300×300 | $b_{\text{Q1}}$ | $300$ | mm | Vorgabe |
| Dehnsteifigkeit, Stütze 300×300, C30/37 | $EA_{\text{Q1}}$ | $3026$ | MN | berechnet |
| Biegesteifigkeit, Stütze 300×300, C30/37 | $EI_{\text{Q1}}$ | $22693$ | kNm² | berechnet |
| Höhe, Stütze 300×300 | $h_{\text{Q1}}$ | $300$ | mm | Vorgabe |
| Querschnittsfläche, Unterzug | $A_{\text{Q2}}$ | $180000$ | mm² | berechnet |
| Flächenträgheitsmoment, Unterzug | $I_{\text{Q2}}$ | $5400$ | ·10⁶ mm⁴ | berechnet |
| Dehnsteifigkeit, Unterzug, C30/37 | $EA_{\text{Q2}}$ | $6052$ | MN | berechnet |
| Biegesteifigkeit, Unterzug, C30/37 | $EI_{\text{Q2}}$ | $181547$ | kNm² | berechnet |
| Mittelwert des Elastizitätsmoduls | $E_{cm}$ | $33620$ | N/mm² | berechnet |
| Dehnung am Ende des ansteigenden Astes | $\varepsilon_{c1d}$ | $2$ | ‰ | Vorgabe |
| Bruchdehnung des Betons | $\varepsilon_{c2d}$ | $3.5$ | ‰ | Vorgabe |
| Beiwert zur Berücksichtigung der Festigkeitsminderung | $\eta_{fc}$ | $1$ |  | berechnet |
| Bemessungswert der Betondruckfestigkeit | $f_{cd}$ | $20$ | N/mm² | berechnet |
| Charakteristische Zylinderdruckfestigkeit | $f_{ck}$ | $30$ | N/mm² | Vorgabe |
| Mittelwert der Zylinderdruckfestigkeit | $f_{cm}$ | $38$ | N/mm² | berechnet |
| Mittelwert der Zugfestigkeit | $f_{ctm}$ | $2.9$ | N/mm² | Vorgabe |
| Teilsicherheitsbeiwert für Beton | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Beiwert für die Gesteinskörnung | $k_e$ | $10000$ |  | Vorgabe |
| Bemessungswert der Schubspannungsgrenze | $\tau_{cd}$ | $1.1$ | N/mm² | berechnet |
| Elastizitätsmodul des Betonstahls | $E_s$ | $200000$ | N/mm² | Vorgabe |
| Bemessungswert der Dehnung bei Höchstlast | $\varepsilon_{ud}$ | $4.5$ | % | Vorgabe |
| Bemessungswert der Fliessgrenze | $f_{yd}$ | $435$ | N/mm² | berechnet |
| Bemessungswert der Fliessgrenze auf Druck | $f_{yd}^{-}$ | $435$ | N/mm² | berechnet |
| Charakteristische Fliessgrenze | $f_{yk}$ | $500$ | N/mm² | Vorgabe |
| Charakteristische Fliessgrenze auf Druck | $f_{yk}^{-}$ | $500$ | N/mm² | Vorgabe |
| Teilsicherheitsbeiwert für Betonstahl | $\gamma_s$ | $1.15$ |  | Vorgabe |
| Länge des Fundaments | $L$ | $2.5$ | m | Vorgabe |
| Neigung der Sohle | $\alpha$ | $0$ | ° | Vorgabe |
| Breite des Fundaments | $b$ | $2$ | m | Vorgabe |
| Neigung des Geländes | $\beta$ | $0$ | ° | Vorgabe |
| Kohäsion, Bemessungswert | $c_{eff}$ | $0$ | kPa | berechnet |
| Kohäsion, charakteristisch | $c_k$ | $0$ | kPa | Vorgabe |
| Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ | $k_{\delta}$ | $1$ |  | Vorgabe |
| Raumlast des Bodens | $\gamma$ | $21$ | kN/m³ | Vorgabe |
| Raumlast des Bodens unter Auftrieb | $\gamma'$ | $11$ | kN/m³ | berechnet |
| Partialfaktor der Kohäsion | $\gamma_c$ | $1.5$ |  | Vorgabe |
| Partialfaktor des Reibungswinkels | $\gamma_{\varphi}$ | $1.2$ |  | Vorgabe |
| Raumlast des Wassers | $\gamma_w$ | $10$ | kN/m³ | Vorgabe |
| Erfüllungsgrad Gleiten – Tragsicherheit | $\alpha_{eff,GL,\text{Tragsicherheit}}$ | $5.21$ |  | berechnet |
| Erfüllungsgrad Grundbruch – Tragsicherheit | $\alpha_{eff,GB,\text{Tragsicherheit}}$ | $1.90$ |  | berechnet |
| Reibungswinkel, Bemessungswert | $\varphi_{eff}$ | $27.51$ | ° | berechnet |
| Reibungswinkel, charakteristisch | $\varphi_k$ | $32$ | ° | Vorgabe |
| Bemessungslast neben dem Fundament | $q_{Ed}$ | $0$ | kPa | Vorgabe |
| Tiefe der Sohle unter Terrain | $t$ | $1.2$ | m | Vorgabe |
| Tiefe des höchsten Grundwasserspiegels unter Terrain | $t_1$ | $5$ | m | Vorgabe |
| Grösstkorndurchmesser | $D_{max}$ | $32$ | mm | Vorgabe |
| Betrachtete Breite (x) | $b$ | $1000$ | mm | Vorgabe |
| Betrachtete Breite (y) | $b_y$ | $1000$ | mm | Vorgabe |
| Bewehrungsmass je Kubikmeter Beton | $\mu_s$ | $123$ | kg/m³ | berechnet |
| Überdeckung oben | $c_{nom,o}$ | $30$ | mm | Vorgabe |
| Überdeckung unten | $c_{nom,u}$ | $30$ | mm | Vorgabe |
| Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage) | $h_{Dist}$ | $186$ | mm | berechnet |
| Höhe der Einlage | $e_{Einlage}$ | $0$ | mm | Vorgabe |
| Plattendicke | $h$ | $300$ | mm | Vorgabe |
| Momentenwiderstand bei N\_Ed = 0, Zug oben | $M_{Rd}^{-}(N_{Ed} = 0)$ | $-79.9$ | kNm | berechnet |
| Momentenwiderstand bei N\_Ed = 0, Zug unten | $M_{Rd}^{+}(N_{Ed} = 0)$ | $235.9$ | kNm | berechnet |
| Druckwiderstand bei M\_Ed = 0 | $N_{Rd}^{-}(M_{Ed} = 0)$ | $-6000$ | kN | berechnet |
| Zugwiderstand bei M\_Ed = 0 | $N_{Rd}^{+}(M_{Ed} = 0)$ | $737.5$ | kN | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = 0 und N\_Ed = 0 | $V_{Rd,max}$ | $272.8$ | kN/m | berechnet |
| Querkraftwiderstand ohne Bügel bei M\_Ed = M\_Rd und N\_Ed = 0 | $V_{Rd,min}$ | $165.4$ | kN/m | berechnet |
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
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $235.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $2.36$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld mit Druck | $M_{Rd,x}(N_{Ed})_{\text{Feld mit Druck}}$ | $253.8$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld mit Druck | $\alpha_{eff,x,\text{Feld mit Druck}}$ | $2.54$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-79.9$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $235.9$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $324.4$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-253.4$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-6000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $1393.2$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Stütze | $M_{Rd,x}(N_{Ed})_{\text{Stütze}}$ | $79.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Stütze | $\alpha_{eff,x,\text{Stütze}}$ | $1.60$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 2. Lage x | $\alpha_{eff,NR,2,x}$ | $3.24$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 3. Lage x | $\alpha_{eff,NR,3,x}$ | $0.996$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $4.54$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld mit Druck (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld mit Druck (60 \%)}}$ | $6.80$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Stütze (60 %) | $\alpha_{eff,\sigma,w,x,\text{Stütze (60 \%)}}$ | $3.02$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $5.69$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $1.93$ |  | berechnet |
| Erfüllungsgrad Verformung – Feld | $\alpha_{eff,w,\text{Feld}}$ | $1.22$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $6.63$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $2.16$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug oben | $\omega_w'$ | $7.52$ |  | berechnet |
| Vergrösserungsfaktor der Durchbiegung, Zug unten | $\omega_w$ | $4$ |  | berechnet |
| Fläche des Bruttoquerschnitts | $A$ | $180000$ | mm² | berechnet |
| Stahlfläche der Bewehrung | $A_{s,tot}$ | $1169$ | mm² | berechnet |
| Trägheitsmoment um y | $I_y$ | $5400$ | ·10⁶ mm⁴ | berechnet |
| Deviationsmoment | $I_{yz}$ | $0$ | ·10⁶ mm⁴ | berechnet |
| Trägheitsmoment um z | $I_z$ | $1350$ | ·10⁶ mm⁴ | berechnet |
| Grösste Neigung der Druckdiagonalen | $\alpha_{max}$ | $45$ | ° | Vorgabe |
| Kleinste Neigung der Druckdiagonalen | $\alpha_{min}$ | $30$ | ° | Vorgabe |
| Abminderung der Betondruckfestigkeit in der Druckdiagonalen | $k_c$ | $0.55$ |  | Vorgabe |
| Erfüllungsgrad Duktilität – Zug links | $\alpha_{eff,x/d,\text{Zug links}}$ | $1.60$ |  | berechnet |
| Erfüllungsgrad Duktilität – Zug oben | $\alpha_{eff,x/d,\text{Zug oben}}$ | $4.56$ |  | berechnet |
| Erfüllungsgrad Duktilität – Zug rechts | $\alpha_{eff,x/d,\text{Zug rechts}}$ | $1.60$ |  | berechnet |
| Erfüllungsgrad Duktilität – Zug unten | $\alpha_{eff,x/d,\text{Zug unten}}$ | $2.73$ |  | berechnet |
| Erfüllungsgrad Biegung und Normalkraft – Feld | $\alpha_{eff,\text{Feld}}$ | $1.41$ |  | berechnet |
| Grösste aufnehmbare Druckkraft | $N_{Rd}^{-}$ | $-4044.1$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft | $N_{Rd}^{+}$ | $508.1$ | kN | berechnet |
| Erfüllungsgrad Rissnormalkraft – ganzer Querschnitt | $\alpha_{eff,NR}$ | $1.29$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite – Feld (60 %) | $\alpha_{eff,\sigma,w,\text{Feld (60 \%)}}$ | $2.66$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug links | $\alpha_{eff,Riss,\text{Zug links}}$ | $2.45$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug oben | $\alpha_{eff,Riss,\text{Zug oben}}$ | $1.18$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug rechts | $\alpha_{eff,Riss,\text{Zug rechts}}$ | $2.45$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – Zug unten | $\alpha_{eff,Riss,\text{Zug unten}}$ | $4.46$ |  | berechnet |
| Erfüllungsgrad Querkraft und Torsion – Feld | $\alpha_{eff,V,\text{Feld}}$ | $1.75$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug links | $\alpha_{eff,ZB,\text{Zug links}}$ | $1.99$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug oben | $\alpha_{eff,ZB,\text{Zug oben}}$ | $1.25$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug rechts | $\alpha_{eff,ZB,\text{Zug rechts}}$ | $1.99$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – Zug unten | $\alpha_{eff,ZB,\text{Zug unten}}$ | $5.05$ |  | berechnet |
| Schwerpunkt, y | $y_S$ | $150$ | mm | berechnet |
| Schwerpunkt, z | $z_S$ | $300$ | mm | berechnet |
| Breite des Fundaments | $B$ | $2$ | m | Vorgabe |
| Länge des Fundaments | $L$ | $2.5$ | m | Vorgabe |
| M\_E-Wert der Schicht 1, Erstbelastung | $M_{E,1}$ | $60$ | MN/m² | Vorgabe |
| M\_E-Wert der Schicht 2, Erstbelastung | $M_{E,2}$ | $15$ | MN/m² | Vorgabe |
| M\_E-Wert der Schicht 3, Erstbelastung | $M_{E,3}$ | $100$ | MN/m² | Vorgabe |
| M\_E-Wert der Schicht 1, Wiederbelastung | $M'_{E,1}$ | $180$ | MN/m² | Vorgabe |
| M\_E-Wert der Schicht 2, Wiederbelastung | $M'_{E,2}$ | $45$ | MN/m² | Vorgabe |
| M\_E-Wert der Schicht 3, Wiederbelastung | $M'_{E,3}$ | $250$ | MN/m² | Vorgabe |
| Dicke der Schicht 1 | $d_{1}$ | $2$ | m | Vorgabe |
| Dicke der Schicht 2 | $d_{2}$ | $3$ | m | Vorgabe |
| Dicke der Schicht 3 | $d_{3}$ | $4$ | m | Vorgabe |
| Grösste Dicke einer Teilschicht | $\Delta z_{max}$ | $0.5$ | m | Vorgabe |
| Erfüllungsgrad Setzung | $\alpha_{eff,s}$ | $2.54$ |  | berechnet |
| Pressung aus Erstbelastung | $q_E$ | $196$ | kN/m² | Vorgabe |
| Pressung aus Wiederbelastung | $q_W$ | $24$ | kN/m² | Vorgabe |
| Zulässige Setzung | $s_{zul}$ | $25$ | mm | Vorgabe |
