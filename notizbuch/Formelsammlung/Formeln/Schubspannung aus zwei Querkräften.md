---
erzeugt: 96d71c2f85ea
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Beide Querkräfte zusammen»*

$$
\tau_d = \sqrt{\tau_{y,d}^2 + \tau_{z,d}^2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\tau_{y,d}$ | Schubspannung aus V\_y | N/mm² | [[Schubspannung aus Querkraft im Holz]] |
| $\tau_{z,d}$ | Schubspannung aus V\_z | N/mm² | [[Schubspannung aus Querkraft im Holz]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\tau_d = \sqrt{\tau_{y,d}^2 + \tau_{z,d}^2} = \sqrt{\left(0.12\,\mathrm{N}/\mathrm{mm}^{2}\right)^2 + \left(0.94\,\mathrm{N}/\mathrm{mm}^{2}\right)^2} = 0.94\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Schubwiderstand neben Torsion im Holz]]

## Im Code

- [[opencivil.nachweis.qa_holz#HolzSchubQA._querkraft|HolzSchubQA._querkraft]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Mit Querkraft in y und in z addiert das Werkzeug die beiden grössten
Schubspannungen als Vektor, als lägen sie an derselben Stelle. Beim
Rechteck liegt die eine auf der waagrechten, die andere auf der
senkrechten Mittellinie – zusammen werden beide nur in der Mitte gross.
Das liegt auf der sicheren Seite; nach Vorgabe, nicht nachgeschlagen.
