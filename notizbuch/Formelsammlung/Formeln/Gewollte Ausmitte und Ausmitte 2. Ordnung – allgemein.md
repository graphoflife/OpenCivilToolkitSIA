---
erzeugt: a6e778003f39
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.7.6, (76); 4.3.7.7, (77); 4.3.7.12, (81); 4.3.7.3, (73); 4.3.7.4, (74)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.7.6, (76); 4.3.7.7, (77); 4.3.7.12, (81); 4.3.7.3, (73); 4.3.7.4, (74)

$$
e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} \qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot \left(e_{0d} + e_{1d} + e_{2d}\right)
$$

## Im Code

- [[opencivil.nachweis.knicken#Knickverfahren._protokoll_verfahren|Knickverfahren._protokoll_verfahren]]

## Themen

- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das ganze Moment am verformten Stab, in einer Zeile: die Normalkraft mal der
Summe dreier Ausmitten. Die gewollte kommt aus dem Moment erster Ordnung, die
zweiter Ordnung aus der Krümmung. Für eine sinusförmige Biegelinie ist die
grösste Ausbiegung die Krümmung mal $l_{cr}^2/\pi^2$ -- daher diese Beziehung
zwischen Krümmung und Ausmitte.
