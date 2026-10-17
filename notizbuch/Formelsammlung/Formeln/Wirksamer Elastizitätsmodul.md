---
erzeugt: 8c858554dbc7
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $\varphi$ | – | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
E_{c,eff} = \frac{E_{cm}}{1 + \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 2} = 11207\,\mathrm{N}/\mathrm{mm}^{2} \qquad n = 17.85
$$

## Im Code

- [[opencivil.nachweis.querschnittsloeser#protokoll_wirksamer_modul|protokoll_wirksamer_modul]]
- [[opencivil.spannungsanalyse.herleitung#herleitung|herleitung]]

## Themen

- [[Stahlspannung aus Rissbreite]]
- [[Stahlspannung gegen Fliessen]]
- [[Knicken]]
- [[Biegung und Normalkraft]]
- [[Zwängung auf Biegung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unter Dauerlast kriecht Beton: die Dehnung wächst mit der Zeit auf das
$(1+\varphi)$-fache der elastischen, bei gleicher Spannung. Wer mit einem
einzigen Modul rechnen will, teilt ihn darum durch $1 + \varphi$ -- der
wirksame Modul $E_{c,eff}$. Mit $\varphi = 2$ ist der Beton dreimal so weich
wie unter kurzer Last.

Die Kriechzahl wählt jedes Kapitel selbst. Sie wirkt dort, wo der Beton
elastisch oder mit der Parabel rechnet -- bei den Stahlspannungen im
Gebrauch, bei der Verformung des Knickens und in der
Spannung-Dehnung-Analyse.
