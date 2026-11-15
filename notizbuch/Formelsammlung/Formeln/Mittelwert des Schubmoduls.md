---
erzeugt: 65520ec69320
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
G_{cm} = \frac{E_{cm}}{2 \cdot \left(1 + \nu_c\right)}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $\nu_c$ | Querdehnungszahl des Betons | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
G_{cm} = \frac{E_{cm}}{2 \cdot \left(1 + \nu_c\right)} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{2 \cdot \left(1 + 0.2\right)} = 14008\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Torsionssteifigkeit]]

## Im Code

- [[opencivil.material.beton]]

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bei einem Werkstoff, der sich in alle Richtungen gleich verhält, hängen
Schub- und Elastizitätsmodul über die Querdehnungszahl zusammen: wer einen
Würfel schert, staucht ihn in der einen Diagonale und dehnt ihn in der
anderen. Für den Beton im elastischen Bereich nimmt die Norm in erster
Näherung $\nu_c = 0.20$ an (SIA 262:2025, 3.1.2.3.5); damit ist
$G_{cm} = E_{cm} / 2.4$. Den Schubmodul selbst nennt die Norm nicht.

Im Stabwerk im Raum gibt er den Betonstäben ihre Torsionssteifigkeit
$G \cdot I_T$. Gerechnet wird ungerissen: ein Stab, der unter Torsion
reisst, verliert viel davon, und das System gibt ihm dann mehr Torsion, als
er tatsächlich trägt.
