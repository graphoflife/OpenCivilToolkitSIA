---
erzeugt: 817f343ff0e5
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Normalkraft, mit der der Querschnitt biegt»*

$$
N_V = N - F_{tVd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N$ | Normalkraft dort, Druck positiv | kN | Zwischenwert |
| $F_{tVd}$ | Längszugkraft aus der Querkraft | kN | [[Längszugkraft aus der Querkraft]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
N_V = N - F_{tVd} = 1747.1\,\mathrm{kN} - 8\,\mathrm{kN} = 1739.1\,\mathrm{kN}
$$

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._biegung|InnererQuerwiderstand._biegung]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Längszugkraft aus der Querkraft wirkt zwischen den beiden Gurten. Hier
zählt sie als Zug in der Achse: der Querschnitt biegt mit N − F_tVd, Druck
positiv. Verglichen mit der Hälfte je Gurt bekommt so der Zuggurt etwas mehr
Zug und der Druckgurt etwas weniger Entlastung, denn der Druckgurt liegt
weiter von der Achse als der Zuggurt. Das liegt auf der sicheren Seite und
ist nach Vorgabe, nicht nachgeschlagen.

Im Bohrpfahl unter mässigem Druck trägt der Querschnitt mit weniger
Normalkraft weniger Moment. ⌀ 900 mm mit 12 ⌀ 20, eingespannt, N = 1000 kN
und H = 100 kN am Kopf: mit N allein 742 kNm, mit N − 173 kN nur 699 kNm.
