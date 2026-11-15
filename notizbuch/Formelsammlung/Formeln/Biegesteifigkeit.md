---
erzeugt: 9c11fe931cc9
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Biegesteifigkeit, «Stütze 300×300» aus C30/37»*

$$
EI_{\text{Q1}} = E_{cm} \cdot I_{y}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $I_{y}$ | Flächenträgheitsmoment um y, Stütze 300×300 | ·10⁶ mm⁴ | [[Flächenträgheitsmoment eines Rechtecks]], [[Flächenträgheitsmoment eines Kreises]], [[Flächenträgheitsmoment eines T-Querschnitts]], [[Flächenträgheitsmoment eines Kreisrings]], [[Flächenträgheitsmoment eines I-Profils um y]], [[Flächenträgheitsmoment eines Trapezes]], [[Flächenträgheitsmoment eines Rechteckrohrs]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
EI_{\text{Q1}} = E_{cm} \cdot I_{y,\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 675\,\cdot 10^{6}\,\mathrm{mm}^{4} = 22693\,\mathrm{kNm}^{2}
$$

## Im Code

- [[opencivil.stabwerk.rechnung#_modul_mal_kennwert|_modul_mal_kennwert]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich ein Stab gegen Biegung wehrt: $M = EI \cdot \chi$, mit der
Krümmung $\chi$. Wie bei der [[Dehnsteifigkeit]] mit dem Mittelwert des
E-Moduls am ungerissenen Bruttoquerschnitt, wie es die Norm für die Analyse
in der Regel vorsieht.

Für die Schnittgrössen eines statisch bestimmten Systems ist sie gleichgültig;
bei einem unbestimmten zählt, wie steif die Stäbe im Verhältnis zueinander
und zu Federn und Bettung sind. Eine kleinere Steifigkeit kann darum günstig
oder ungünstig wirken. Die Verschiebungen hängen an ihrem Betrag.
