---
erzeugt: 91e3e97c926d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Stahl, nur auf Zug»*

$$
\sigma_s = \begin{cases} \min\left(E_s \cdot \varepsilon_s;\ f_{yk}\right) & \varepsilon_s > 0 \\[1ex] 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen}) \end{cases}
$$

*In der Herleitung: «Stahl in der Handrechnung: nur auf Zug»*

$$
\sigma_s = \begin{cases} \min\left(E_s \cdot \varepsilon_s;\ f_{yd}\right) & \varepsilon_s > 0 \\[1ex] 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen}) \end{cases}
$$

## Im Code

- `opencivil.nachweis.rechenwahl:protokoll_gesetze`
- `opencivil.spannungsanalyse:_herleitung`

## Themen

- [[Stahlspannung aus Rissbreite]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
