---
erzeugt: f1c78bdf5269
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/erdbebendaten.py
> was die Oberflaeche von einem Gebaeude im Erdbeben zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/erdbebendaten.py)

## VERANTWORTUNG

Je Gebaeude die Zahlen der Ansicht, in den Einheiten der Anzeige – m, kN,
kNm und t: Hoehe, Gewicht und Masse jedes Geschosses, auch solange es noch
nicht rechnet – man sieht die Massen, sobald man Geschosse eingibt –, je
Richtung die Kraefte F_d,i, Querkraft und Moment unter jedem Geschoss und was jeder
getrennte Teil des Kerns am Fuss traegt. Dazu je Geschoss, warum sein Kern
nicht rechnet, und je Kern, der rechnet, sein Umriss im Grundriss, in mm um
seinen Schwerpunkt, mit den Teilen; die Meldungen – rot, was falsch ist,
grau, was fehlt oder hier nicht gerechnet wird – und die Legenden unter den
Bildern ([[opencivil.web.anzeige]]). Namen, Hoehen und Kerne der
Geschosse liest die Oberflaeche aus dem Eintrag; was der Kern daraus macht,
kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: Querkraefte und
Momente kommen aus [[opencivil.erdbeben.kragarm#querkraefte|opencivil.erdbeben.kragarm.querkraefte]] und
[[opencivil.erdbeben.kragarm#momente|momente]], wie in der Tabelle der
Herleitung, der Grund eines Kerns aus
[[opencivil.projekt.aufbau.erdbeben#kerne|opencivil.projekt.aufbau.erdbeben.kerne]], wie beim Bauen, und sein
Umriss aus derselben Zeichnung wie das Bild seiner Analyse
([[opencivil.web.diagrammdaten#zeichnung|opencivil.web.diagrammdaten.zeichnung]]). Das Gewicht eines
Geschosses kommt aus dem Befund, solange es keinen gibt aus derselben Regel
([[opencivil.erdbeben.ersatzkraft#gewicht|opencivil.erdbeben.ersatzkraft.gewicht]]); die Masse ist das Gewicht
durch g, wie beim Eigengewicht ([[opencivil.material.basis#Konstanten|ERDBESCHLEUNIGUNG]]).

## Inhalt

### ansicht

```python
def ansicht(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Ansicht eines Gebaeudes braucht. Ohne Nachweis – es fehlt ein
Geschoss oder ein Kern – nur, was fehlt, und die Kerne, die rechnen.

### _geschosse

```python
def _geschosse(z: Sequence[float], W: Sequence[float]) -> List[dict]
```

Je Geschoss, von unten, die Hoehe seiner Decke in m, sein Gewicht in kN, seine Masse in t.

### _kernmeldungen

```python
def _kernmeldungen(namen: Sequence[str], befunde: Sequence[Kernbefund]) -> List[dict]
```

Je Grund, warum ein Kern nicht rechnet, ein Satz – mit allen Geschossen, die er trifft.

### _grundriss

```python
def _grundriss(kern: Kerndaten, analyse: Any) -> Dict[str, Any]
```

Ein Kern im Grundriss, in mm: die Flaechen seiner Analyse um deren
Schwerpunkt, wie gezeichnet – y der Analyse nach rechts, in x des
Gebaeudes, z nach oben. Wo er aus getrennten Teilen besteht, je Teil
seine Nummer und sein Schwerpunkt.

### _verlaufslegende

```python
def _verlaufslegende(namen: Sequence[str], befunde: Sequence[Kernbefund], befund: Erdbebenbefund) -> List[list]
```

Was das Bild der Kerne, Querkraefte und Momente zeigt – die Kerne mit ihren Geschossen.

### _richtung

```python
def _richtung(b: Richtungsbefund, z: Sequence[float]) -> Dict[str, Any]
```

Eine Richtung in den Einheiten der Anzeige: Kraefte, Querkraefte und
Momente von unten, die Teile am Fuss. `z` sind die Hoehen der Decken, m.

### _legende

```python
def _legende(b: Richtungsbefund, nachweis, loesung: Loesung) -> List[list]
```

Je Richtung: T_1 gegen 4 T_C mit dem Urteil (39), dann F_d und M_0 – mit q und mit q = 1.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.erdbeben.kern]]
- [[opencivil.erdbeben.kragarm]]
- [[opencivil.material.basis]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.web.anzeige]]
- [[opencivil.web.diagrammdaten]]

## Gebraucht von

- [[opencivil.web.zeichendaten]]
