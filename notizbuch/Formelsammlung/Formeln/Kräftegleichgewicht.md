---
erzeugt: fd66e2286fbf
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
N_{Rd}^{+} = -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot \sigma_{sd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{cd}$ | – | N/mm² | Zwischenwert |
| $b$ | – | mm | Zwischenwert |
| $x^{+}$ | Druckzonenhöhe | mm | [[Nulllinie auf halber Höhe]] |
| $A_{s,2,x}$ | – | mm² | Zwischenwert |
| $\sigma_{sd}$ | Stahlspannung | N/mm² | [[Stahlspannung, höchstens die Fliessgrenze]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  N_{Rd}^{+} &= -f_{cd} \cdot b \cdot 0.85 \cdot x^{+} + A_{s,2,x} \cdot \sigma_{sd} \\
  &= -20\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 0.85 \cdot 150\,\mathrm{mm} + 2450\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= -1484.6\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._halbe_hoehe|Handrechnung._halbe_hoehe]]

## Themen

- [[Biegung und Normalkraft]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Normalkraft des Eckpunkts: was der Spannungsblock an Druck liefert,
negativ, plus was der Stahl an Zug liefert. Weil die Nulllinie hier
vorgegeben ist und nicht gesucht, ergibt sich die Normalkraft -- meist ein
Druck, denn der Block über der halben Höhe drückt mehr, als der Stahl zieht.
