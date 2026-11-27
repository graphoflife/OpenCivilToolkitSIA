---
erzeugt: 8961f1215611
art: formel
tags: [formel]
normstelle: "nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Schubfluss aus der Kraft im abgetrennten Teil»*

$$
v = \frac{\left|F'(M + \Delta M) - F'(M)\right|}{\Delta x}, \qquad \Delta M = V \cdot \Delta x, \qquad \tau = \frac{v}{b_i}
$$

*In der Herleitung: «Schubfluss – die Kraft im abgetrennten Teil bei M und daneben»*

$$
v = \frac{\left|F'_1 - F'_0\right|}{\Delta x}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $F'_1$ | Kraft im abgetrennten Teil daneben, Zug positiv | kN | Zwischenwert |
| $F'_0$ | Kraft im abgetrennten Teil bei M, Zug positiv | kN | Zwischenwert |
| $\Delta x$ | Abstand der beiden Zustände längs des Bauteils, nach Vorgabe | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
v = \frac{\left|F'_1 - F'_0\right|}{\Delta x} = \frac{\left|-1182.05\,\mathrm{kN} - \left(-1174.98\,\mathrm{kN}\right)\right|}{10\,\mathrm{mm}} = 706.8\,\mathrm{kN}/\mathrm{m}
$$

## Gebraucht von

- [[Schubspannung im Schnitt]]

## Im Code

- [[opencivil.nachweis.qa_schubfluss#SchubflussQA._fall|SchubflussQA._fall]]
- [[opencivil.nachweis.qa_schubfluss#SchubflussQA.rechne|SchubflussQA.rechne]]

## Themen

- [[Schubfluss]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Gleichgewicht des abgetrennten Teils längs des Bauteils: zwischen zwei
Schnitten im Abstand $\Delta x$ trägt er bei $M$ die Kraft $F'_0$, daneben
$F'_1$. Den Unterschied kann nur der Schnitt liefern,
$v = |F'_1 - F'_0|/\Delta x$; bei kleinem $\Delta x$ ist das
$V \cdot dF'/dM$.

Beide Kräfte gehören zu Dehnungsebenen des ganzen Querschnitts, nicht des
Teils allein: der Teil liest die Ebene, mit der der Querschnitt $N$ und $M$
im Gleichgewicht hält. Darum braucht es keinen angenommenen Hebelarm, und
$N$ darf mitwirken.

Elastisch ergibt das $V \cdot S'/I$. Ein I-Profil 400 mm hoch, Flansche
200 × 20 mm, Steg 10 mm: ein Schnitt im Steg dicht unter dem oberen Flansch
trennt diesen ab, $S' = 200 \cdot 20 \cdot 190 = 760\,000$ mm³, und
$I = 3.28 \cdot 10^8$ mm⁴. Bei $V = 100$ kN gehen
$100 \cdot 760\,000/3.28 \cdot 10^8 = 0.232$ kN/mm, also 232 kN/m, durch
den Steg.

Gibt es zu $N$ und $M$ keine Gleichgewichtslage, nimmt der Querschnitt sie
nicht auf: dann gibt es kein $v$, die Tabelle zeigt «–», und darunter steht
warum.
