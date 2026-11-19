---
erzeugt: 8c8086324d3f
art: modul
tags: [modul]
---
> [!abstract] opencivil/geotechnik/tragfaehigkeit.py
> die Tragfähigkeitsfaktoren N_q und N_c.
> Paket [[opencivil.geotechnik]] · [Quelltext](../../opencivil/geotechnik/tragfaehigkeit.py)

## VERANTWORTUNG

N_q und N_c für einen Reibungswinkel phi, nach Kap. 9.2.6 in Lang, Huder,
Amann, Puzrin: Bodenmechanik und Grundbau, 8. Aufl. 2007:

```
N_q = e^(pi tan phi) · tan²(45° + phi/2)
N_c = (N_q - 1) / tan phi
```

Unter einem Fundament ([[opencivil.geotechnik.grundbruch|grundbruch]]) und am Fuss
eines Pfahls ([[opencivil.pfahl.aussen|aussen]]) dieselben Formeln -- darum in
einem Modul, das keinem der beiden gehört.


## EINHEITEN

SI-Basis; der Winkel in rad.

## Inhalt

### tragfaehigkeitsfaktoren

```python
def tragfaehigkeitsfaktoren(p: Protokoll, werte: Zwischenwerte, phi: Wert) -> Tuple[Wert, Wert]
```

N_q und N_c für den Reibungswinkel `phi` (Kap. 9.2.6), in die
Herleitung geschrieben -- unter einem Fundament und am Fuss eines Pfahls
dieselben Formeln ([[opencivil.pfahl.aussen]]). `phi` grösser als null.


## Konstanten

- `KAP_FAKTOREN = 'Kap. 9.2.6'` – Die Tragfähigkeitsfaktoren im Buch.

## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.pfahl.aussen]]

## Formeln aus diesem Modul

- [[Tragfähigkeitsfaktor N_c]] · `tragfaehigkeitsfaktoren`
- [[Tragfähigkeitsfaktor N_q]] · `tragfaehigkeitsfaktoren`
