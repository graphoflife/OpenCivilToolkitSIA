---
erzeugt: a3c9a6c305f0
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
n = \frac{E_s}{E_{cm}} \cdot \left(1 + \varphi\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $\varphi$ | – | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
n = \frac{E_s}{E_{cm}} \cdot \left(1 + \varphi\right) = \frac{200000\,\mathrm{N}/\mathrm{mm}^{2}}{33620\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \left(1 + 2\right) = 17.85
$$

## Im Code

- `opencivil.nachweis.mindestbewehrung:ZwaengungBiegung._protokoll_ansatz`

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
