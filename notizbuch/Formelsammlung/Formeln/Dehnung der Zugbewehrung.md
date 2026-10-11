---
erzeugt: 714569cc6d08
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |
| $x^{+}$ | Druckzonenhöhe | mm | [[Nulllinie auf halber Höhe]] |
| $\varepsilon_{c2d}$ | – | ‰ | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\varepsilon_s^{+} = \left(d_{2,x} - x^{+}\right) \cdot \frac{\varepsilon_{c2d}}{x^{+}} = \left(248.1\,\mathrm{mm} - 150\,\mathrm{mm}\right) \cdot \frac{3.5\,\text{‰}}{150\,\mathrm{mm}} = 2.29\,\text{‰}
$$

## Gebraucht von

- [[Stahlspannung, höchstens die Fliessgrenze]]

## Im Code

- `opencivil.nachweis.handrechnung:Handrechnung._halbe_hoehe`

## Themen

- [[Biegung und Normalkraft]]
- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
