---
erzeugt: 5eff9a407e9e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Probe: Moment um y»*

$$
M_{y,Rd} = -\sum F_i \cdot (z_i - z_S)
$$

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
M_{y,Rd} = -\sum F_i \cdot (z_i - z_S) = 211.8\,\mathrm{kNm}
$$

## Gebraucht von

- [[Plastischer Biegewiderstand mit β]]
- [[Widerstand in der Richtung der Einwirkung]]

## Im Code

- [[opencivil.nachweis.qa_stahl#probe|probe]]
- [[opencivil.nachweis.qa_verbund_kennzahlen#KennzahlenVerbundQA|KennzahlenVerbundQA._biegung]]
- [[opencivil.nachweis.schiefe_biegung#SchiefeBiegung|SchiefeBiegung._protokoll_bruchzustand]]

## Themen

- [[Schiefe Biegung]]
- [[Stahlquerschnitt]]
- [[Kennzahlen]]
- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kräfte aller Teile mal ihrem Abstand zum Schwerpunkt in $z$: das Moment um
die $y$-Achse. Die Vorzeichen folgen der Konvention der Querschnittsanalyse --
Zug positiv, $y$ nach rechts, $z$ nach oben; ein positives $M_y$ zieht unten.
