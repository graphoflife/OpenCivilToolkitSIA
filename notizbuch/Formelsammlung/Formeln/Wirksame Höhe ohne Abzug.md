---
erzeugt: fb0db215e10f
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.1, Figur 21"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.1, Figur 21

*In der Herleitung: «Wirksame Höhe (Einlage nicht massgebend)»*

$$
d_v^{+} = d^{+}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d^{+}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
d_v^{+} = d^{+} = 249\,\mathrm{mm}
$$

## Gebraucht von

- [[Durchstanzwiderstand ohne Durchstanzbewehrung]]
- [[Nachweisschnitt im Abstand d_v∕2]]
- [[Nachweisschnitt um das Wandende – 1.5·d_v entlang der Wand]]
- [[Nachweisschnitt um die Wandecke – je 1.5·d_v entlang der Wände]]
- [[Querkraftwiderstand ohne Bügel bei M_Ed = 0]]
- [[Querkraftwiderstand ohne Querkraftbewehrung]]
- [[Widerstand der ersten Betondruckdiagonale]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._statische_hoehe|Durchstanzen._statische_hoehe]]
- [[opencivil.nachweis.querkraft#protokoll_hoehen|protokoll_hoehen]]

## Themen

- [[Kennzahlen]]
- [[Querkraft]]
- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ohne Einlage, oder mit einer Einlage, die zu klein ist, um zu stören, ist die
wirksame Höhe für die Querkraft die statische Höhe der gezogenen
Bewehrung. Mit einer störenden Einlage siehe
[[Wirksame Höhe, um die Einlage vermindert]].

Beim Durchstanzen ist $d$ das Mittel der beiden Lagen der Zugbewehrung
([[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]]). Die
wirksame Höhe $d_v$ ist kleiner, wenn die gestützte Fläche in die Platte
reicht (Figur 21); reicht sie nicht hinein, ist $d_v = d$.

Bis 2026-10-30 hiess die Seite «Wirksame Höhe (Einlage nicht massgebend)» --
seit das Durchstanzen dieselbe Formel schreibt, trägt sie einen Namen, der
für beide passt.
