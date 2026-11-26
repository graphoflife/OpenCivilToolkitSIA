---
erzeugt: c38b6cfeb315
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 2.2.6; SIA 265:2012, 3.3.2; 3.4.2.2"
---
> [!info] Normstelle
> SIA 265:2012, 2.2.6; SIA 265:2012, 3.3.2; 3.4.2.2

*In der Herleitung: «Stossartige Einwirkung: η\_t die Bemessungswerte»*

$$
\eta = \eta_w \cdot \eta_t
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $\eta_t$ | Beiwert der Einwirkungsdauer | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\eta = \eta_w \cdot \eta_t = 0.8 \cdot 1.4 = 1.12
$$

## Im Code

- [[opencivil.nachweis.qa_holz_werte#beiwert|beiwert]]

## Themen

- [[Holzquerschnitt]]
- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Bemessungswerte der Tabellen 6 und 7 gelten für Holz in
Feuchteklasse 1 unter einer Einwirkung, die nicht stossartig ist. Zwei
Beiwerte passen sie dem Fall an: $\eta_w$ mindert sie mit der Feuchte –
nasses Holz ist weicher und weniger fest –, $\eta_t = 1.4$ hebt sie unter
einer stossartigen Einwirkung, etwa einem Anprall: Holz trägt kurz mehr
als lange. Ihr Produkt $\eta$ multipliziert jede Festigkeit des Falls;
ohne Stoss ist $\eta = \eta_w$. Siehe [[Bemessungswerte des Holzes]].
