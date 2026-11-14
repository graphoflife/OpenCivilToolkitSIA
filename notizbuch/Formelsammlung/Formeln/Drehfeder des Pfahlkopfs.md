---
erzeugt: a708f79a38e4
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Drehfeder, Kopf nicht verschoben: aus k\_h = K\_HH − K\_HM² / K\_MM»*

$$
K_{MM} = \frac{K_{HM}^{2}}{K_{HH} - k_h}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $K_{HM}$ | Kopplung am Kopf | MN | [[Kopplung am Pfahlkopf]] |
| $K_{HH}$ | Querfeder, Kopf eingespannt | MN/m | [[Querfeder des eingespannten Pfahlkopfs]] |
| $k_h$ | Querfeder, Kopf frei drehbar | MN/m | [[Querfeder des frei drehbaren Pfahlkopfs]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
K_{MM} = \frac{K_{HM}^{2}}{K_{HH} - k_h} = \frac{\left(-249.35\,\mathrm{MN}\right)^{2}}{149.93\,\mathrm{MN}/\mathrm{m} - 66.26\,\mathrm{MN}/\mathrm{m}} = 743.14\,\mathrm{MNm}/\mathrm{rad}
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit|Pfahlsteifigkeit._federn]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich der Kopf gegen ein Drehen wehrt, wenn er sich nicht
verschiebt: das dritte Glied der Steifigkeitsmatrix. Das Werkzeug gewinnt es
aus den beiden Querfedern ohne eigene Rechnung: der frei drehbare Kopf ist
der eingespannte, an dem das Moment null ist, und daraus folgt
K_MM = K_HM² / (K_HH − k_h).

Für einen langen Pfahl in gleichmässigem Boden ergibt das k_s · D / (2λ³).
⌀ 900 mm aus C30/37 in E_s,k = 30 MN/m²: K_MM ≈ 625 MNm/rad.
