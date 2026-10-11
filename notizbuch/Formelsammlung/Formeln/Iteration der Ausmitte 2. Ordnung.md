---
erzeugt: cae84df960a5
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.7"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.7

*In der Herleitung: «Das Verfahren»*

$$
e_{2d}^{(k)} = \left|\chi^{(k)}\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II}^{(k)} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}^{(k-1)}\right)
$$

## Im Code

- [[opencivil.nachweis.knicken#Knicken._protokoll_iteration|Knicken._protokoll_iteration]]

## Themen

- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Verfahren selbst. Begonnen wird ohne Verformung, $e_{2d} = 0$. Dann:

1. das Moment aus der Normalkraft und allen Ausmitten des letzten
   Durchlaufs;
2. die Dehnungsebene, die dieses Moment trägt (siehe
   [[Dehnungsebene und innere Kräfte]]), und ihre Krümmung;
3. aus der Krümmung die neue Ausmitte zweiter Ordnung.

Ändert sie sich nicht mehr, steht der Stab: das ist die Gleichgewichtslage.
Wächst sie, bis der Querschnitt das Moment nicht mehr tragen kann, gibt es
keine -- der Stab knickt. Die Herleitung zeigt die Folge Durchlauf für
Durchlauf, weil ihr Einlaufen die Aussage des Nachweises ist.
