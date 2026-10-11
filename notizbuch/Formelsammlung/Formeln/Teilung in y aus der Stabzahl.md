---
erzeugt: 95faad4a4e2a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
s_{V,y} = \frac{b}{n_{V,y}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $n_{V,y}$ | Bügelzahl über die betrachtete Breite | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
s_{V,y} = \frac{b}{n_{V,y}} = \frac{1000\,\mathrm{mm}}{5} = 200\,\mathrm{mm}
$$

## Gebraucht von

- [[Widerstand der Bügel]]

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft|Querkraft._protokoll_ansatz_buegel]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bügel stehen in zwei Richtungen verteilt: in Tragrichtung mit der Teilung
$s_{V,x}$, quer dazu mit $n_{V,y}$ Bügeln über die betrachtete Breite. Daraus
die Teilung quer, $s_{V,y} = b / n_{V,y}$. Zusammen sagen beide Teilungen, wie
viel Bügelfläche je Quadratmeter Platte steht:
$A_{\varnothing,V} / (s_{V,x} \cdot s_{V,y})$.
