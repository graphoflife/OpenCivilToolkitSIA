---
erzeugt: e211630c00a9
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
x = \sqrt{\rho^{2} + 2 \cdot d_{2,x} \cdot \rho} - \rho
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\rho$ | – | mm | [[Hilfsgrösse der Nulllinie]] |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  x &= \sqrt{\rho^{2} + 2 \cdot d_{2,x} \cdot \rho} - \rho \\
  &= \sqrt{\left(43.73\,\mathrm{mm}\right)^{2} + 2 \cdot 248.1\,\mathrm{mm} \cdot 43.73\,\mathrm{mm}} - 43.73\,\mathrm{mm} \\
  &= 109.9\,\mathrm{mm}
\end{aligned}
$$

## Gebraucht von

- [[Innerer Hebelarm]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#ZwaengungBiegung|ZwaengungBiegung._protokoll_lage]]

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im gerissenen Querschnitt trägt der Beton nur auf Druck, die Bewehrung auf
Zug. Die Nulllinie liegt dort, wo das statische Moment des gedrückten
Betons gleich dem der umgerechneten Bewehrung ist:
$b\,x^2/2 = n A_s\,(d - x)$. Mit $\rho = n A_s / b$ ist das die quadratische
Gleichung $x^2 + 2\rho x - 2\rho d = 0$, deren positive Lösung hier steht.
