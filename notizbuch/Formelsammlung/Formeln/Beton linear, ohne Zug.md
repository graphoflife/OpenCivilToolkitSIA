---
erzeugt: acdd93b1b89a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Werkstoffgesetze im Gebrauchszustand: Beton, linear ohne Zug»*

$$
\sigma_c(\varepsilon_c) = \begin{cases} \max\left(E_{c,eff} \cdot \varepsilon_c;\ -f_{ck}\right) & \varepsilon_c \le 0 \\[1ex] 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen}) \end{cases}
$$

## Im Code

- [[opencivil.nachweis.rechenwahl#protokoll_gesetze|protokoll_gesetze]]
- [[opencivil.querschnitt.schnittanalyse#protokoll_gesetze_nach_wahl|protokoll_gesetze_nach_wahl]]

## Themen

- [[Stahlspannung aus Rissbreite]]
- [[Stahlspannung gegen Fliessen]]
- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im gerissenen Gebrauchszustand trägt der Beton keinen Zug, und im Druck liegt
seine Spannung weit unter der Festigkeit -- dort ist die
Parabel-Rechteck-Beziehung praktisch eine Gerade. Gerechnet wird darum linear
mit dem wirksamen Modul E_c,eff = E_cm/(1+φ), der das Kriechen enthält.
Erreicht eine Druckzone doch die Festigkeit, bleibt die Spannung dort stehen:
mehr, als der Wertesatz hergibt -- im Gebrauchszustand f_ck --, nimmt der Beton
nicht auf.
