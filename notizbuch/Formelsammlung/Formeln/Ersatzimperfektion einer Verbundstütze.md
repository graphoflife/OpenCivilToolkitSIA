---
erzeugt: 52a7ef33ef99
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.1.4; Tabelle 7"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.1.4; Tabelle 7

*In der Herleitung: «Ersatzimperfektion um y: Kurve b, L/200»*

$$
e_{0,y} = \frac{L}{200}
$$

*In der Herleitung: «Ersatzimperfektion um z: Kurve c, L/150»*

$$
e_{0,z} = \frac{L}{150}
$$

*In der Herleitung: «Ersatzimperfektion um y: Kurve a, L/300»*

$$
e_{0,y} = \frac{L}{300}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L$ | Länge der Stütze | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
e_{0,y} = \frac{L}{200} = \frac{6000\,\mathrm{mm}}{200} = 30\,\mathrm{mm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
e_{0,z} = \frac{L}{150} = \frac{6000\,\mathrm{mm}}{150} = 40\,\mathrm{mm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
e_{0,y} = \frac{L}{300} = \frac{3500\,\mathrm{mm}}{300} = 11.7\,\mathrm{mm}
$$

## Gebraucht von

- [[Moment 2. Ordnung einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweite_ordnung|_Fall._zweite_ordnung]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Statt jede Abweichung der wirklichen Stütze einzeln zu erfassen, setzt man
eine Vorkrümmung an. Ihr Pfeil hängt an der Kurve der Tabelle 7: L/300 bei
Kurve a, L/200 bei b, L/150 bei c (5.3.1.4). Sie wirkt um die Achse mit
Moment; zweiachsig wirkt sie in beiden Achsen zugleich – das ist nach
Vorgabe, nicht nachgeschlagen, und steht im [[TODO]].
