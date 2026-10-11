---
erzeugt: 416b8533489f
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Beton, Spannungsblock 0.85·x»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{ck} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

*In der Herleitung: «Werkstoffgesetze der Verformung: Beton, Spannungsblock 0.85·x»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} 0 & \varepsilon_c > -(1 - 0.85) \cdot \varepsilon_{c2d} \\[1ex] -f_{cd} & -\varepsilon_{c2d} \le \varepsilon_c \le -(1 - 0.85) \cdot \varepsilon_{c2d} \end{cases}
$$

## Im Code

- `opencivil.nachweis.rechenwahl:protokoll_betongesetz`
- `opencivil.querschnitt.analyse:Querschnittsanalyse.werkstoffe_protokollieren`
- `opencivil.spannungsanalyse:_herleitung`

## Themen

- [[Stahlspannung aus Rissbreite]]
- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Schiefe Biegung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
