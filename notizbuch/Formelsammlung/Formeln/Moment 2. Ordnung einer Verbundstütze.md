---
erzeugt: b3053ae211fe
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1

*In der Herleitung: «Moment nach Theorie 2. Ordnung um y»*

$$
M_{y,Ed,II} = k_{y} \cdot |M_{y,Ed}| + k_{0,y} \cdot |N_{Ed}| \cdot e_{0,y}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_{y}$ | Vergrösserungsfaktor | – | [[Vergrösserungsfaktor einer Verbundstütze]] |
| $\vert M_{y,Ed}\vert $ | Moment 1. Ordnung | kNm | Zwischenwert |
| $k_{0,y}$ | Vergrösserungsfaktor der Imperfektion | – | [[Vergrösserungsfaktor der Imperfektion einer Verbundstütze]] |
| $\vert N_{Ed}\vert $ | Druckkraft | kN | Zwischenwert |
| $e_{0,y}$ | Ersatzimperfektion | mm | [[Ersatzimperfektion einer Verbundstütze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{y,Ed,II} &= k_{y} \cdot |M_{y,Ed}| + k_{0,y} \cdot |N_{Ed}| \cdot e_{0,y} \\
  &= 1.32 \cdot 200\,\mathrm{kNm} + 1.32 \cdot 6000\,\mathrm{kN} \cdot 30\,\mathrm{mm} \\
  &= 501.4\,\mathrm{kNm}
\end{aligned}
$$

## Gebraucht von

- [[Zweiachsige Biegung einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweite_ordnung|_Fall._zweite_ordnung]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, das die Stütze tragen muss: das grösste Moment 1. Ordnung,
vergrössert mit k, und das Moment der Ersatzimperfektion, vergrössert mit
k₀. Um eine gehaltene Achse wächst nichts, und es gibt keine Imperfektion:
dort bleibt das Moment 1. Ordnung.

Es steht gegen
[[Widerstand einer Verbundstütze nach (25)]] oder, zweiachsig, in
[[Zweiachsige Biegung einer Verbundstütze]].
