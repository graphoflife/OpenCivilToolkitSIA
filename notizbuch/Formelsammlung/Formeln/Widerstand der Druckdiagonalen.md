---
erzeugt: 19f1de1b4bc8
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.6, (47)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.6, (47)

$$
V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | [[Statische Höhe]] |
| $k_c$ | Abminderung der Betondruckfestigkeit in der Druckdiagonalen | – | Vorgabe |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |
| $\alpha$ | – | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,c} &= 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha \\
  &= 0.9 \cdot 248.1\,\mathrm{mm} \cdot 0.55 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30{}^{\circ} \cdot \cos 30{}^{\circ} \\
  &= 1063.5\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

## Gebraucht von

- [[Querkraftwiderstand mit Querkraftbewehrung]]

## Im Code

- [[opencivil.nachweis.querkraft_buegel#protokoll_mit_buegeln|protokoll_mit_buegeln]]

## Themen

- [[Querkraft]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckdiagonalen tragen die Querkraft schräg ab. Ihr Querschnitt je
Laufmeter ist $0.9\,d \cdot \cos\alpha$, ihre Kraft wirkt unter $\alpha$ --
daher $\sin\alpha \cdot \cos\alpha$, am grössten bei 45°. Der Beton der
Diagonalen ist längs gerissen, und die Bügel kreuzen ihn schief; er trägt
darum weniger als ein ungestört gedrückter. $k_c = 0.55$, der Wert der
Norm für solche Stege, mindert seine Festigkeit entsprechend.
