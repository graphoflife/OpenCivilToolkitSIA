---
erzeugt: c6fbaa1370cb
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Beton und Betonstahl ausserhalb der Profile bei voller Verdübelung, zusammen gedrückt»*

$$
N_{c,f} = \left|\sum F_{i}\right|_{\mathrm{Beton,\ Betonstahl}}
$$

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{c,f} = \left|\sum F_{i}\right|_{\mathrm{Beton,\ Betonstahl}} = 2857\,\mathrm{kN}
$$

## Gebraucht von

- [[Dübel für volle Verdübelung]]

## Im Code

- [[opencivil.nachweis.qa_verbund#VerbundBiegungQA._verduebelung|VerbundBiegungQA._verduebelung]]

## Themen

- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im plastischen Zustand bei voller Verdübelung haben Beton und Betonstahl
ausserhalb der Profile zusammen eine Kraft: gedrückt im positiven Moment,
gezogen im negativen, wo nur der Betonstahl trägt. Diese Kraft müssen die
Dübel zwischen dem Schnitt und dem Momentennullpunkt übertragen, damit
Stahl und Beton ohne Schlupf zusammen tragen.

Beton in der Kammer eines Profils zählt zum Stahl: er ist mit dem Steg
verbunden, nicht über die Dübel der Fuge (nach Vorgabe). Daraus folgen die
[[Dübel für volle Verdübelung]].
