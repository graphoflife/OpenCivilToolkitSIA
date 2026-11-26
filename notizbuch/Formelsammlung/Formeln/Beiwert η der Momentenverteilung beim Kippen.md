---
erzeugt: 6feba4cf7c50
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.6, (94); Figur 41"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.6, (94); Figur 41

*In der Herleitung: «Beiwert der Momentenverteilung»*

$$
\eta = 1.75 - 1.05 \cdot \psi + 0.3 \cdot \psi^2
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\psi$ | Verhältnis der Endmomente | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\eta = 1.75 - 1.05 \cdot \psi + 0.3 \cdot \psi^2 = 1.75 - 1.05 \cdot 0 + 0.3 \cdot 0^2 = 1.75
$$

## Gebraucht von

- [[Reduzierte Kipplänge]]
- [[Saint-Venant-Anteil der Kippspannung]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Formeln für die Kippspannung gehen von einem Moment aus, das über
die ganze Kipplänge gleich gross ist. Das ist der ungünstigste Fall: der
Druckgurt ist überall gleich stark gedrückt. Fällt das Moment zu einem
Ende hin ab, kippt der Träger erst bei einem grösseren Moment; $\eta$
sagt, um wie viel. Es hängt vom Verhältnis $\psi$ der Endmomente ab:
1 beim konstanten Moment, 1.75 beim dreieckigen ($\psi = 0$), 2.35 bei
$\psi = -0.5$. Darunter bleibt das Werkzeug bei 2.35.

$\eta$ vergrössert den [[Saint-Venant-Anteil der Kippspannung]] direkt und
verkürzt im Wölbanteil die Kipplänge zur
[[Reduzierte Kipplänge|reduzierten]].
