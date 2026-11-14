---
erzeugt: f490db0b9f6e
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/buch.py
> die Zahlen des Buches zum Einzelpfahl.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/buch.py)

## VERANTWORTUNG

Was Lang, Huder, Amann und Puzrin für Pfähle als Bild oder Beiwert geben,
als Zahlen: der Form- und Tiefenfaktor X am Pfahlfuss (Bild 12.4), der
Tragfähigkeitsfaktor N_c undrainiert (Bild 12.5), der Anteil von φ und c beim
örtlichen Abscheren (Kap. 9.2.7) und der Ruhedruckbeiwert (Kap. 2.7). Die
Bilder sind abgelesen, nicht nachgerechnet: auf etwa ±0.02 genau.


## AUSSERHALB DER BILDER

Bild 12.4 reicht von h/D = 2.5 bis 30 und von φ' = 15° bis 40°, Bild 12.5 bis
L/D = 12. Ausserhalb gilt der Wert am Rand des Bildes -- nach Vorgabe, nicht
nachgeschlagen; [[opencivil.pfahl.buch#ausserhalb|ausserhalb]] sagt, wo das greift. Bild 12.5 endet bei
N_c = 9: höchstens so viel, sagt der Text dazu.


## QUELLE

Lang, H.-J., Huder, J., Amann, P., Puzrin, A. M.: Bodenmechanik und
Grundbau. 8. Aufl., Springer, Berlin 2007.


## EINHEITEN

Winkel in Grad, Verhältnisse ohne Einheit.

## Inhalt

### _stelle

```python
def _stelle(achse: Sequence[float], wert: float) -> Tuple[int, float]
```

Der Abschnitt der Achse und der Anteil darin; am Rand festgehalten.

### faktor_x

```python
def faktor_x(phi_grad: float, h_durch_d: float) -> float
```

X aus Bild 12.4, zwischen den Kurven und Stützstellen linear.

### faktor_n_c_undrainiert

```python
def faktor_n_c_undrainiert(l_durch_d: float) -> float
```

N_c aus Bild 12.5.

### ruhedruckbeiwert

```python
def ruhedruckbeiwert(phi: float) -> float
```

K_0 ≈ 1 − sin φ (Kap. 2.7) -- `phi` in rad.

### ausserhalb

```python
def ausserhalb(phi_grad: float, h_durch_d: float) -> List[str]
```

Wo X die Grenzen von Bild 12.4 verlässt, je als Satz für eine Warnung.
Unter den Grenzen ist der Wert am Rand zu gross, über ihnen zu klein.


## Konstanten

- `KAP_RUHEDRUCK = 'Kap. 2.7'`
- `KAP_LASTTRANSPORT = 'Kap. 12.4, Bild 12.3'`
- `KAP_SPITZE = 'Kap. 12.5, Bild 12.4'`
- `KAP_SPITZE_UNDRAINIERT = 'Kap. 12.5, Bild 12.5'`
- `KAP_MANTEL = 'Kap. 12.5'`
- `KAP_ABSCHEREN = 'Kap. 9.2.7, 12.5'`
- `X_H_D = (2.5, 3.0, 4.0, 5.0, 7.5, 10.0, 12.5, 15.0, 20.0, 25.0, 30.0)`
- `X_PHI = (15.0, 25.0, 30.0, 32.5, 35.0, 37.5, 40.0)`
- `X_WERTE = ((1.6, 1.63, 1.68, 1.73, 1.8, 1.83, 1.84, 1.85, 1.87, 1.89, 1.91), (1…`
- `NC_L_D = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12…`
- `NC_WERTE = (6.2, 6.6, 7.0, 7.3, 7.6, 7.8, 8.1, 8.35, 8.55, 8.7, 8.8, 8.9, 9.0, 9…`
- `ABSCHEREN = 2.0 / 3.0` – Auf diesen Teil sinken φ und c, wenn der Boden am Fuss nur örtlich abschert.

## Gebraucht von

- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.pfahl]]
