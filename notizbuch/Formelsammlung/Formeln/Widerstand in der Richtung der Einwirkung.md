---
erzeugt: b28a2fe1bd33
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{y,Rd}$ | – | kNm | Zwischenwert |
| $M_{z,Rd}$ | – | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}} = \sqrt{\left(211.8\,\mathrm{kNm}\right)^{2} + \left(0\,\mathrm{kNm}\right)^{2}} = 211.8\,\mathrm{kNm}
$$

## Gebraucht von

- [[Erfüllungsgrad]]

## Im Code

- [[opencivil.nachweis.schiefe_biegung#SchiefeBiegung|SchiefeBiegung._ein_fall]]

## Themen

- [[Schiefe Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Betrag des Momentenvektors der gefundenen Ebene. Weil die Ebene so
gesucht ist, dass ihr Moment in dieselbe Richtung zeigt wie die Einwirkung,
ist das der Widerstand in genau dieser Richtung -- und der Erfüllungsgrad das
Verhältnis der Beträge.
