---
erzeugt: eb635aa087b3
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Hebel des Moments über dem Kopf»*

$$
e = \frac{M_{Ed}}{H_{Ed}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{Ed}$ | Moment am Kopf | kNm | Zwischenwert |
| $H_{Ed}$ | Querkraft am Kopf | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
e = \frac{M_{Ed}}{H_{Ed}} = \frac{80\,\mathrm{kNm}}{150\,\mathrm{kN}} = 0.53\,\mathrm{m}
$$

## Im Code

- [[opencivil.pfahl.quer#AeussererQuerwiderstand|AeussererQuerwiderstand._querkraft]]

## Themen

- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Am frei drehbaren Kopf ist ein Moment Einwirkung. Für die Brüche wirkt es
wie ein Hebel: dieselbe Querkraft, um e = M_Ed / H_Ed über dem Kopf
angreifend, tut dasselbe. Dreht das Moment wie H über dem Kopf, ist e
positiv und der Widerstand kleiner; dreht es dagegen, wird er grösser.

H_Ed = 150 kN mit M_Ed = 80 kNm: e = 0.53 m. Mit p_E überall gleich c und
einem langen Pfahl wird H = c · s_h, mit s_h = −e + √(e² + 2 · M_R / c).
