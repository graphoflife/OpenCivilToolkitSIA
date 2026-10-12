Geprüft am 2026-10-12, auf Frage des Benutzers: Die M_Rd im M-χ-Bild der
Stahlbetonplatte stimmen nicht immer mit dem M_Rd des Tragwiderstands überein.
Warum?

Gerechnet habe ich die Platte des Beispiels (C30/37, B500B, h = 300 mm, unten
⌀18 + ⌀12 @ 150, oben ⌀12 @ 150) und eine symmetrisch bewehrte (⌀18 @ 150 oben
und unten). Geprüft sind φ = 0 und 2, Bemessungs- und charakteristische Werte
und alle drei Rechenarten. Die Namen der Rechenarten sind die neuen
(«Handrechnung», «0.85·x-Vereinfachung», «Präzise ohne Vereinfachung»).

## Kurz

- **Hauptgrund: ein Name.** Im Bild hiess der Fliessbeginn «M_Rd» und das
  Ende der Linie «M_Rd,u». Der Tragwiderstand ist das *Ende*. Seit
  2026-10-12 heisst der Fliessbeginn M_y und das Ende M_Rd.
- **Gleiche Rechenwahl, gleiche Zahl.** Mit 0.85·x und präzise trifft das
  Ende der Linie den Tragwiderstand in jedem geprüften Fall auf 0.05 %. Ein
  Test hält das fest.
- **Die Handrechnung** ist ein Polygon durch vier Eckpunkte. Dazwischen liegt
  sie auf der sicheren Seite, unter Druck bis rund 20 %. In der Analyse gibt
  es sie seit 2026-10-12 nicht mehr.
- **Verschiedene Wahl je Kapitel** gibt verschiedene Zahlen, und das zu Recht.
  Die Tragsicherheit beginnt mit der Handrechnung, eine Analyse präzise.

## Tragwiderstand gegen das Ende der M-χ-Linie

Platte des Beispiels, Bemessungswerte, M in kNm. «Fliessbeginn» ist der
Punkt, der bis 2026-10-12 im Bild «M_Rd» hiess.

| Rechenart | φ | N [kN] | Tragwiderstand | Ende der Linie | Fliessbeginn |
|---|---|---|---|---|---|
| Handrechnung | 0 | 0 | 235.93 | 235.87 | 235.87 |
| Handrechnung | 0 | −300 | 253.81 | 262.64 | – |
| Handrechnung | 0 | +100 | 224.09 | 225.95 | – |
| 0.85·x | 0 und 2 | 0 | 236.18 | 236.16 | 234.95 |
| 0.85·x | 0 und 2 | −300 | 265.25 | 265.23 | – |
| 0.85·x | 0 und 2 | +100 | 225.94 | 225.92 | – |
| präzise | 0 | 0 | 235.74 | 235.75 | 228.05 |
| präzise | 2 | 0 | 235.39 | 235.39 | – |
| präzise | 0 | −300 | 264.54 | 264.50 | – |
| präzise | 2 | −300 | 264.35 | 264.33 | – |
| präzise | 0 | +100 | 225.59 | 225.57 | – |

Symmetrisch bewehrt, φ = 0:

| Rechenart | Werte | N [kN] | Tragwiderstand | Ende der Linie |
|---|---|---|---|---|
| Handrechnung | Bemessung | 0 | 170.06 | 170.97 |
| Handrechnung | charakteristisch | 0 | 199.22 | 203.59 |
| 0.85·x | Bemessung | 0 | 170.99 | 170.97 |
| 0.85·x | charakteristisch | 0 | 203.66 | 203.59 |
| präzise | Bemessung | 0 | 170.80 | 170.78 |
| präzise | charakteristisch | 0 | 203.10 | 203.06 |
| Handrechnung | Bemessung | −1000 | 237.87 | 258.12 |
| 0.85·x | Bemessung | −1000 | 268.36 | 268.30 |
| präzise | Bemessung | −1000 | 267.40 | 267.39 |
| Handrechnung | Bemessung | −3000 | 209.88 | 254.45 |
| 0.85·x | Bemessung | −3000 | 350.39 | 350.34 |
| präzise | Bemessung | −3000 | 349.20 | 349.18 |

Die Zeilen «Handrechnung» der Spalte «Ende der Linie» stammen von vor
2026-10-12, als die Analyse die Handrechnung noch anbot.

## Was die Unterschiede erklärt

1. **Fliessbeginn statt Widerstand.** Präzise bei N = 0 stand im Bild «M_Rd =
   228.1», der Tragwiderstand ist 235.7 kNm. Der Fliessbeginn liegt immer
   darunter: Danach wächst das Moment noch, weil die Druckzone kleiner und
   der Hebelarm grösser wird. Der Name ist jetzt M_y.
2. **Handrechnung.** Der Tragwiderstand mit Handrechnung ist ein Polygon aus
   reinem Druck, M_Rd bei N = 0, dem Punkt mit x = h/2 und reinem Zug,
   dazwischen gerade. Die alte M-χ-Linie mit Handrechnung integrierte
   dasselbe Modell genau: Spannungsblock, Druckstahl weggelassen, je Seite
   eine Lage. Bei N = 0, einem Eckpunkt, stimmen beide; dazwischen liegt das
   Polygon tiefer, bei N = −3000 kN um 18 %. Das ist die Handrechnung und kein
   Fehler. Die Analyse bietet sie nicht mehr an, weil sie N genau rechnet.
3. **φ** wirkt nur präzise, über `E_c,eff = E_cm/(1+φ)` im Beiwert k_σ der
   Parabel. Das gilt in beiden Rechnungen gleich: M_Rd 235.74 → 235.39 kNm.
   Bei 0.85·x hängt kein Modul am Gesetz; φ wirkt dort nur auf den
   ungerissenen Teil der Linie.
4. **Wertesatz.** Mit charakteristischen Werten heisst das Ende M_Rk. Es
   stimmt mit dem M_Rk der Tragsicherheit überein, wenn diese
   charakteristisch rechnet.
5. **Druckbewehrung.** Die Handrechnung lässt sie weg, 0.85·x und präzise
   zählen sie – überall, wie gewünscht. Am deutlichsten beim negativen
   Moment, wo die starke untere Lage gedrückt ist: M_Rd(N = 0)⁻ = 79.9
   (Hand) gegen 90.1 (0.85·x) und 90.0 kNm (präzise).
6. **Rest bis 0.05 %.** Der Tragwiderstand integriert über 200 Fasern, die
   Linie über 60; beide suchen ihre Ebene bis auf eine Schranke. Das
   bleibt.

## N-ε-Linie gegen den Tragwiderstand

Das Ende der N-ε-Linie bei M = 0 ist **nicht** N_Rd,zug des
Tragwiderstands:

- **N_Rd,zug = 1393 kN** ist der Zugpunkt der Interaktionslinie. Dort
  fliessen beide Lagen, und bei unsymmetrischer Bewehrung gehört dazu ein
  Moment.
- **Die N-ε-Linie hält M = 0 fest.** Die starke Lage kann dann nicht ganz
  fliessen, ohne dass ein Moment entsteht.
- **Gleiche Frage, gleiche Zahl.** Fragt man die Tragsicherheit dasselbe,
  also eine Einwirkung mit festem Moment («M konstant»), ist es dieselbe
  Zahl: 874.7 (0.85·x) und 873.7 kN (präzise) gegen 874.4 und 873.5 kN am
  Ende der Linie. Mit Handrechnung 737.5 kN, aus dem Polygon.

## Was sich geändert hat

- Fliessbeginn heisst **M_y** bzw. **N_y**, das Ende **M_Rd** bzw. **N_Rd**
  (M_Rk mit charakteristischen Werten).
- **Handrechnung** nur noch in Tragsicherheit und Stahlspannungen. Knicken
  und Analysen rechnen N genau.
  - Der Widerstand beim Knicken nimmt nun als Vorgabe 0.85·x und damit eine
    eigene, genaue Linie mit Druckbewehrung.
  - Im Prüfprojekt steigt N_Rd,K der Decke dadurch von 3900.6 auf 4496.7 kN.
  - Die Stütze der Platte «Parabel» knickt jetzt präzise: 3488.4 → 4099.5 kN.
- **Linie «ungerissen»** nur bis zum Riss. Die Zugfestigkeit zählt nur dort.
- **E_eq-Bild:** jede Ecke mit Modul und Vielfachem von E_cm.

## Offen

- **Gemischte Stahlsorten.** Bei verschiedenen Stahlsorten in einer Richtung
  nimmt die Analyse ein ε_ud für alle Lagen, das der ersten Sorte. Die
  Tragsicherheit nimmt es je Sorte. Bei den Normsorten des Beispiels ist es
  dasselbe; siehe [[TODO]].
