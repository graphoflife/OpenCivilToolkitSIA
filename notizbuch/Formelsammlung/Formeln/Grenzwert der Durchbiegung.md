---
erzeugt: 1ef0af3dd900
art: formel
tags: [formel]
normstelle: "SIA 260:2013, Anhang A, Tabelle 3"
---
> [!info] Normstelle
> SIA 260:2013, Anhang A, Tabelle 3

$$
w_{max} = \frac{L}{350}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L$ | Spannweite | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
w_{max} = \frac{L}{350} = \frac{6\,\mathrm{m}}{350} = 17.1\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.verformung#Verformung|Verformung._einen_fall]]

## Themen

- [[Verformung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Durchbiegung wird gegen einen Bruchteil der Spannweite gehalten: je
länger das Feld, desto mehr Durchbiegung ist erträglich. $L/350$ ist der
Richtwert aus SIA 260:2013, Anhang A, Tabelle 3, unter häufiger Last: für
Einbauten, die sich verformen dürfen, für Nutzung und Betrieb und für den
Komfort. Dieselbe Tabelle nennt $L/500$ für spröde Einbauten unter
seltener Last und $L/300$ fürs Aussehen unter quasi-ständiger Last.

Die Tabelle meint je Zeile nur einen Teil der Durchbiegung: was nach dem
Einbau dazukommt, was die veränderlichen Lasten bewirken, oder alles
abzüglich einer Überhöhung. Gehalten wird hier die ganze Durchbiegung samt
Kriechen -- strenger als jede dieser Zeilen ausser $L/500$. Welche Grenze
für ein Bauteil gilt, hängt davon ab, was es trägt und was an ihm hängt;
das legt das Projekt fest.
