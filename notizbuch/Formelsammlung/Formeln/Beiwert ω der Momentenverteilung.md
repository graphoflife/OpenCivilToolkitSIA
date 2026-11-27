---
erzeugt: 9eb687f0046a
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.9.1; 5.1.10.3"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.9.1; 5.1.10.3

*In der Herleitung: «Beiwert der Momentenverteilung um y»*

$$
\omega_{y} = \max\left(0.4;\ 0.6 + 0.4 \cdot \psi_{y}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\psi_{y}$ | Verhältnis der Endmomente | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\omega_{y} = \max\left(0.4;\ 0.6 + 0.4 \cdot \psi_{y}\right) = \max\left(0.4;\ 0.6 + 0.4 \cdot 0\right) = 0.6
$$

## Gebraucht von

- [[Abgeminderter Kippwiderstand im Stab]]
- [[Vergrösserungsfaktor einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung._omega|_Herleitung._omega]]
- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweite_ordnung|_Fall._zweite_ordnung]]

## Themen

- [[Knicken und Kippen]]
- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Nachweise für Druck und Biegung im Stab rechnen mit dem grössten
Moment. Liegt es nur an einem Ende und fällt zum anderen ab, ist der
Stab dort, wo er am weitesten ausbiegt, weniger beansprucht; $\omega$
mindert das Moment dafür ab. Beim konstanten Moment ist es eins, beim
dreieckigen 0.6, nie unter 0.4.

Mit Querlast oder in einem verschieblichen Rahmen gilt $\omega = 1$
(5.1.10.3) – im Werkzeug mit $\psi = 1$.
