# Beispiel

43 Berechnungen ausgeführt, 73 Werte bestimmt.

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

**Bewehrungsquerschnitt je Laufmeter** *(SIA 262:2025, 5.5.2)*

$$
A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}
$$

**Bewehrungsmass je Kubikmeter Beton**

$$
\mu_s = \frac{A_{s,tot} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{b \cdot h} = \frac{4712.39\,\mathrm{mm}^{2} \cdot 7850\,\mathrm{kg}/\mathrm{m}^{3}}{1000\,\mathrm{mm} \cdot 300\,\mathrm{mm}} = 123\,\mathrm{kg}/\mathrm{m}^{3}
$$

**Höhe der Distanzhalter**

$$
h_{Dist} = \text{OK innere untere Lage} - \text{UK innere obere Lage} = 240.0\,\mathrm{mm} - 54.0\,\mathrm{mm} = 186.0\,\mathrm{mm}
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
d_{2,x} = \frac{A_{s,2,x,g} \cdot f_{yd} \cdot d_{2,x,g} + A_{s,2,x,z} \cdot f_{yd} \cdot d_{2,x,z}}{A_{s,2,x,g} \cdot f_{yd} + A_{s,2,x,z} \cdot f_{yd}}
= \frac{1696 \cdot 435 \cdot 249.0 + 754 \cdot 435 \cdot 246.0}{1696 \cdot 435 + 754 \cdot 435} = 248.1\,\mathrm{mm}
$$

**Bewehrungsquerschnitt der zusammengefassten Lage**

$$
A_{s,2,x} = A_{s,2,x,g} + A_{s,2,x,z} = 1696 + 754 = 2450\,\mathrm{mm}^{2}
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
M_{Ed} = 100\,\mathrm{kNm} \qquad N_{Ed} = 0\,\mathrm{kN}
$$

**Widerstand bei N\_Ed = 0.0 kN – ein Eckpunkt liegt genau dort**

$$
M_{Rd} = M_{Rd}(N_{Ed}=0)^{+} = 235.9\,\mathrm{kNm}
$$

**Erfüllungsgrad**

$$
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} = \frac{235.9}{100.0} = 2.36 \quad \Rightarrow \quad \text{erfüllt}
$$

#### Nachweis – Feld mit Druck

**Einwirkung**

$$
M_{Ed} = 100\,\mathrm{kNm} \qquad N_{Ed} = -300\,\mathrm{kN}
$$

**Widerstand bei festgehaltenem N\_Ed = -300.0 kN**

$$
M_{Rd} = M_1 + \frac{N_{Ed} - N_1}{N_2 - N_1} \cdot \left(M_2 - M_1\right)
= 324.4 + \frac{-300.0 - \left(-1484.6\right)}{0.0 - \left(-1484.6\right)} \cdot \left(235.9 - 324.4\right) = 253.8\,\mathrm{kNm}
$$

**Stützpunkte der Interpolation**

| Punkt | $N\ [\mathrm{kN}]$ | $M\ [\mathrm{kNm}]$ |
| :--- | ---: | ---: |
| $M_{Rd}(x=\tfrac{h}{2})^{+}$ | $-1484.6$ | $324.4$ |
| $M_{Rd}(N_{Ed}=0)^{+}$ | $0.0$ | $235.9$ |

**Erfüllungsgrad**

$$
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} = \frac{253.8}{100.0} = 2.54 \quad \Rightarrow \quad \text{erfüllt}
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
\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} = \frac{79.9}{50.0} = 1.60 \quad \Rightarrow \quad \text{erfüllt}
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
E_{cm} = k_e \cdot \sqrt[3]{f_{cm}} = 10000 \cdot \sqrt[3]{38\,\mathrm{N}/\mathrm{mm}^{2}} = 33620\,\mathrm{N}/\mathrm{mm}^{2}
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

## Nachweise

### Decke über EG

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

| Nachweis | Bezeichnung | Widerstand | Einwirkung | $\alpha_{eff}$ |
| :--- | :--- | ---: | ---: | ---: |
| Biegung und Normalkraft | Feld | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = 235.9\,\mathrm{kNm}$ | $M_{Ed,x} = 100.0\,\mathrm{kNm}$ | $2.36$ |
| Biegung und Normalkraft | Feld mit Druck | $M_{Rd,x}(N_{Ed} = -300\,\mathrm{kN}) = 253.8\,\mathrm{kNm}$ | $M_{Ed,x} = 100.0\,\mathrm{kNm}$ | $2.54$ |
| Biegung und Normalkraft | Stütze | $M_{Rd,x}(N_{Ed} = 0\,\mathrm{kN}) = -79.9\,\mathrm{kNm}$ | $M_{Ed,x} = -50.0\,\mathrm{kNm}$ | $1.60$ |

> **Hinweis:** Zwängung auf Normalkraft – 3. Lage: nicht erfüllt (α\_eff = 0.996). Dieser Nachweis ist ausgeschaltet und steht nicht in der Herleitung. A\_s = 754 mm² bei σ\_s,adm = 500 N/mm² ergibt N\_s,adm = 377.0 kN gegen N\_Riss = 378.3 kN.

Alle geführten Nachweise sind erfüllt.

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
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld | $M_{Rd,x}(N_{Ed})_{\text{Feld}}$ | $235.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld | $\alpha_{eff,x,\text{Feld}}$ | $2.359$ |  | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Feld mit Druck | $M_{Rd,x}(N_{Ed})_{\text{Feld mit Druck}}$ | $253.8$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Feld mit Druck | $\alpha_{eff,x,\text{Feld mit Druck}}$ | $2.538$ |  | berechnet |
| Momentenwiderstand bei N = 0, negativ (x-Richtung) | $M_{Rd,x}(N=0)^{-}$ | $-79.9$ | kNm | berechnet |
| Momentenwiderstand bei N = 0, positiv (x-Richtung) | $M_{Rd,x}(N=0)^{+}$ | $235.9$ | kNm | berechnet |
| Grösster positiver Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{+}$ | $324.4$ | kNm | berechnet |
| Grösster negativer Momentenwiderstand (x-Richtung) | $M_{Rd,x}^{-}$ | $-253.4$ | kNm | berechnet |
| Grösste aufnehmbare Druckkraft (x-Richtung) | $N_{Rd,x}^{-}$ | $-6000$ | kN | berechnet |
| Grösste aufnehmbare Zugkraft (x-Richtung) | $N_{Rd,x}^{+}$ | $1393.2$ | kN | berechnet |
| Momentenwiderstand bei N\_Ed (x-Richtung) – Stütze | $M_{Rd,x}(N_{Ed})_{\text{Stütze}}$ | $79.9$ | kNm | berechnet |
| Erfüllungsgrad x-Richtung – Stütze | $\alpha_{eff,x,\text{Stütze}}$ | $1.598$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 2. Lage x | $\alpha_{eff,NR,2,x}$ | $3.24$ |  | berechnet |
| Erfüllungsgrad Rissnormalkraft – 3. Lage x | $\alpha_{eff,NR,3,x}$ | $1$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}$ | $4.29$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Feld mit Druck (60 %) | $\alpha_{eff,\sigma,w,x,\text{Feld mit Druck (60 \%)}}$ | $6.05$ |  | berechnet |
| Erfüllungsgrad Stahlspannung aus Rissbreite x-Richtung – Stütze (60 %) | $\alpha_{eff,\sigma,w,x,\text{Stütze (60 \%)}}$ | $2.82$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 2. Lage x | $\alpha_{eff,SV,2,x}$ | $5.69$ |  | berechnet |
| Erfüllungsgrad sprödes Versagen – 3. Lage x | $\alpha_{eff,SV,3,x}$ | $1.93$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 2. Lage x | $\alpha_{eff,ZB,2,x}$ | $6.25$ |  | berechnet |
| Erfüllungsgrad Zwängung auf Biegung – 3. Lage x | $\alpha_{eff,ZB,3,x}$ | $2.08$ |  | berechnet |
