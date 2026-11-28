---
erzeugt: f9be4e71e548
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 3.1.4.1"
---
> [!info] Normstelle
> SIA 266:2015, 3.1.4.1

$$
E_{xk} = 1000 \cdot f_{xk}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{xk}$ | Druckfestigkeit senkrecht zu den Lagerfugen, kennzeichnend | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
E_{xk} = 1000 \cdot f_{xk} = 1000 \cdot 7\,\mathrm{N}/\mathrm{mm}^{2} = 7000\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Bemessungswert des Elastizitätsmoduls senkrecht zu den Lagerfugen]]
- [[Schubmodul, kennzeichnend]]

## Im Code

- [[opencivil.material.mauerwerk]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Steifigkeit des Mauerwerks senkrecht zu den Lagerfugen wächst mit seiner
Festigkeit. Für Standardmauerwerk nimmt das Werkzeug sie nach 3.1.4.1 als
Vielfaches der Druckfestigkeit: $E_{xk} = 1000 \cdot f_{xk}$, bei Backstein
mit 7 N/mm² also 7000 N/mm². Bei deklariertem Mauerwerk lässt sich die Zahl
der Deklaration eintragen; sie muss mindestens 1800 N/mm² betragen
(3.1.3.1).

Mit diesem Wert rechnen die Verformungen im Gebrauch, für lange Dauer um den
Faktor $1 + \varphi$ vergrössert (4.2.2.1); die Tragsicherheit rechnet mit
dem Bemessungswert
([[Bemessungswert des Elastizitätsmoduls senkrecht zu den Lagerfugen]]).
