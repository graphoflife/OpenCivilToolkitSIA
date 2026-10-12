---
erzeugt: 20b70d8925e2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\sigma_{sd} = \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_s$ | – | N/mm² | Zwischenwert |
| $\varepsilon_s^{+}$ | Dehnung der Zugbewehrung | ‰ | [[Dehnung der Zugbewehrung]] |
| $f_{yd}$ | – | N/mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  \sigma_{sd} &= \min\left[E_s \cdot \varepsilon_s^{+};\ f_{yd}\right] \\
  &= \min\left[200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2.29\,\text{‰};\ 435\,\mathrm{N}/\mathrm{mm}^{2}\right] \\
  &= 435\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Kräftegleichgewicht]]
- [[Momentengleichgewicht um die halbe Höhe]]

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._halbe_hoehe|Handrechnung._halbe_hoehe]]

## Themen

- [[Biegung und Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aus der Dehnung die Spannung, nach der
[[Bilineare Beziehung des Betonstahls|bilinearen Beziehung]]: elastisch
$E_s \varepsilon_s$, höchstens aber $f_{yd}$. Ist die Dehnung grösser als die
[[Fliessdehnung]], fliesst der Stahl.
