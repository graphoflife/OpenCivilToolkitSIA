---
erzeugt: e88b18255ace
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1

*In der Herleitung: «Vergrösserungsfaktor um y»*

$$
k_{y} = \max\left(1;\ \frac{\omega_{y}}{1 - |N_{Ed}| / N_{cr,eff,y}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\omega_{y}$ | Beiwert der Momentenverteilung | – | [[Beiwert ω der Momentenverteilung]] |
| $\vert N_{Ed}\vert $ | Druckkraft | kN | Zwischenwert |
| $N_{cr,eff,y}$ | Kritische Normalkraft für die Bemessung | kN | [[Kritische Normalkraft einer Verbundstütze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  k_{y} &= \max\left(1;\ \frac{\omega_{y}}{1 - |N_{Ed}| / N_{cr,eff,y}}\right) \\
  &= \max\left(1;\ \frac{1}{1 - 6000\,\mathrm{kN} / 24776.6\,\mathrm{kN}}\right) \\
  &= 1.32
\end{aligned}
$$

## Gebraucht von

- [[Moment 2. Ordnung einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweite_ordnung|_Fall._zweite_ordnung]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Normalkraft biegt die gebogene Stütze weiter aus und vergrössert so
ihr Moment. (24) fasst das in einen Faktor: ω berücksichtigt, wie die
Endmomente verteilt sind, wie in SIA 263, der Bruch, wie nahe die
Normalkraft der Knicklast kommt. k ist mindestens 1. Mit Querlast oder
konstantem Moment ist ψ = 1 und damit ω = 1 – siehe
[[Beiwert ω der Momentenverteilung]].

Für das Moment der Imperfektion gilt
[[Vergrösserungsfaktor der Imperfektion einer Verbundstütze]].
