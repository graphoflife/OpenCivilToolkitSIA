---
erzeugt: 5f91a815a1e0
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Äquivalenter E-Modul, «Kasten»»*

$$
E_{eq} = \frac{M}{I_c \cdot \left(\chi - \chi_0\right)}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M$ | Moment | kNm | Zwischenwert |
| $I_c$ | reiner Betonquerschnitt | ·10⁶ mm⁴ | Zwischenwert |
| $\chi$ | Krümmung bei M | 1/m | Zwischenwert |
| $\chi_0$ | Krümmung ohne Moment | 1/m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
E_{eq} = \frac{M}{I_c \cdot \left(\chi - \chi_0\right)} = \frac{200\,\mathrm{kNm}}{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(0.00281\,\mathrm{m}^{-1} - 0\,\mathrm{m}^{-1}\right)} = 5353\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.spannungsanalyse.modul#ModulProzedur|ModulProzedur._schreiben]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Derselbe äquivalente Modul wie die Linie
[[Äquivalenter E-Modul über dem Moment]] -- nicht als Linie, sondern an
einer Stelle: bei der Normalkraft N und dem Moment M, die der Benutzer am
Querschnitt eines Balkensystems eingibt (Benutzer, 2026-10-23). Ein Stab mit diesem Querschnitt rechnet dann
mit $EA = E_{eq} \cdot A$ und $EI = E_{eq} \cdot I$ -- ein E für beides.

Wie die Linie: ungerissen bis zum Rissmoment bei N, darüber gerissen;
gezählt ab der Krümmung $\chi_0$ ohne Moment. Bei M = 0 gilt der Wert, mit
dem die Linie beginnt -- ungerissen ist der Querschnitt linear. Positives M
zieht unten, an der gestrichelten Faser des Stabs. Gerechnet wird mit
Kriechzahl, Wertesatz und Rechenart wie in einer Spannung-Dehnung-Analyse.

Liegt M über dem Biegewiderstand bei N, gibt es kein E_eq: das System sagt
es und rechnet nicht, der Rest des Projekts schon.
