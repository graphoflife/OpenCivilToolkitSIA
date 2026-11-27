---
erzeugt: fe2923bdfc5f
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.2.6, (15); SIA 263:2013, 4.5.1.4, (8)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.2.6, (15); SIA 263:2013, 4.5.1.4, (8)

*In der Herleitung: «Knickwiderstand um z»*

$$
N_{K,z,Rd} = \chi_{K,z} \cdot N_{pl,Rd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\chi_{K,z}$ | Abminderung beim Knicken | – | [[Abminderungsfaktor beim Knicken und Kippen]] |
| $N_{pl,Rd}$ | Plastischer Normalkraftwiderstand | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{K,z,Rd} = \chi_{K,z} \cdot N_{pl,Rd} = 0.686 \cdot 9563.9\,\mathrm{kN} = 6557.5\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall|_Fall._knicken]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Um eine Achse ohne Moment trägt die Stütze χ_K mal ihren plastischen
Normalkraftwiderstand (15). χ_K kommt aus SIA 263, mit der Kurve, die
Tabelle 7 der Art des Querschnitts gibt: ein ganz einbetoniertes oder
kammerbetoniertes Profil um seine starke Achse b, um die schwache c; ein
gefülltes Rohr a bis 3 % Betonstahl, darüber b. In χ_K stecken die
Imperfektionen der Stütze.

Der Erfüllungsgrad ist N_K,Rd/|N_Ed|.
