---
erzeugt: cd919c987508
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Biegesteifigkeit, «Stütze 300×300» aus C30/37»*

$$
EI_{\text{Q1}} = E_{cm} \cdot I_{\text{Q1}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $I_{\text{Q1}}$ | Flächenträgheitsmoment, Stütze 300×300 | ·10⁶ mm⁴ | [[Flächenträgheitsmoment eines Rechtecks]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
EI_{\text{Q1}} = E_{cm} \cdot I_{\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 675\,\cdot 10^{6}\,\mathrm{mm}^{4} = 22693\,\mathrm{kNm}^{2}
$$

## Im Code

- [[opencivil.stabwerk.rechnung|_biegesteifigkeit]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich ein Stab gegen Biegung wehrt: $M = EI \cdot \chi$, mit der
Krümmung $\chi$. Wie bei der [[Dehnsteifigkeit]] mit dem Mittelwert des
E-Moduls am ungerissenen Bruttoquerschnitt -- nach Vorgabe, nicht
nachgeschlagen.

Für die Schnittgrössen eines statisch bestimmten Systems ist sie gleichgültig;
bei einem unbestimmten zählt nur, wie steif die Stäbe im Verhältnis
zueinander sind. Die Verschiebungen dagegen hängen an ihrem Betrag.
