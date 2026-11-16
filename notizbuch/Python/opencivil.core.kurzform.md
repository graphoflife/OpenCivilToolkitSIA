---
erzeugt: 8377c2d14dd3
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/kurzform.py
> ein Nachweis in zwei, drei Formeln.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/kurzform.py)

## VERANTWORTUNG

Das Auge in der Zusammenfassung zeigt einen Nachweis mit allem, was er
braucht: Baustoffe, Bewehrung, jeden Zwischenschritt. Fuer den Bericht in
Word will man meist nur die Formeln, die ihn fuehren --
`M_Rd = A_s f_yd (d - A_s f_yd / (2 b f_cd))` und den Erfuellungsgrad. Die
Kurzform baut sie aus der Mitschrift: vom Ergebnis des Nachweises aus
rueckwaerts, je Platzhalter die Zeile, die seinen Wert rechnet.

Was eine Zeile dort ist, sagt die Berechnung, die sie schreibt
([[opencivil.core.protokoll#Kurz|Kurz]]):

```
EINSETZEN  ihre Formel geht in die ein, die ihren Wert braucht -- solange
           diese nicht breiter wird als KURZBREITE und kein Bruch dabei in
           Zaehler oder Nenner eines anderen geraet, wo er klein gesetzt
           wird; sonst steht sie als eigene Zeile davor
ZEILE      steht als eigene Zeile davor
```

Jeder andere Wert bleibt ein Symbol mit seiner Zahl. Eine Zeile, die einen
Wert nur weitergibt (`M_Rd = M_Rd(N_Ed=0)`), wird uebersprungen; die Zeile
dahinter steht dann unter dem Symbol, unter dem der Wert gebraucht wird.

Jede eingesetzte Formel wird nachgerechnet ([[opencivil.core.formelbaum#rechnen|formelbaum.rechnen]]):
gibt sie nicht das Ergebnis ihrer Zeile, bleibt es bei den einzelnen Zeilen.
Die Kurzform rechnet also nichts Neues -- sie schreibt dieselbe Rechnung
kuerzer auf.

## Inhalt

### kurzform

```python
def kurzform(protokoll: Protokoll, ziel: str) -> List[GleichungBlock]
```

Die Kurzform des Nachweises, dessen Ergebnis der Wert `ziel` ist -- leer,
wenn sie nur die Zeile waere, die ihn ohnehin abschliesst.

### _Bau

```python
class _Bau
```

Die Zeilen der Mitschrift, nach dem Wert, den sie rechnen.

#### _Bau.anfuegen

```python
def anfuegen(self, block: GleichungBlock, symbol: str, heraus: List[GleichungBlock]) -> None
```

Die Zeile von `block` unter `symbol` ans Ende -- nach dem, was sie braucht.

#### _Bau.ausgebaut

```python
def ausgebaut(self, block: GleichungBlock, davor: List[GleichungBlock]) -> Tuple[Ausdruck, List[GleichungBlock]]
```

Der Baum von `block` mit allem, was in ihn eingesetzt werden darf,
und die Zeilen, die eingesetzt sind. Was als eigene Zeile vor ihm
steht, kommt nach `davor`. [[opencivil.core.formelbaum#Unlesbar|Unlesbar]], wenn er es selbst ist.

#### _Bau.versuch

```python
def versuch(self, baum: Ausdruck, blatt: Blatt, quelle: GleichungBlock, resultat: Optional[Wert]) -> Optional[Tuple[Ausdruck, List[GleichungBlock], List[GleichungBlock]]]
```

`baum` mit der Formel von `quelle` fuer `blatt` -- samt den
eingesetzten Zeilen und denen, die davor stehen muessen. None, wenn
er zu breit wuerde, einen Bruch im Bruch bekaeme oder nicht mehr
`resultat` ergaebe.

#### _Bau.quelle

```python
def quelle(self, blatt: Blatt) -> Tuple[Optional[GleichungBlock], bool]
```

Die Zeile, die den Wert eines Blatts rechnet -- ueber Zeilen hinweg,
die ihn nur weitergeben, solange die Zahl dieselbe bleibt; und ob es
solche gab.

### _stimmt

```python
def _stimmt(baum: Ausdruck, resultat: Optional[Wert]) -> bool
```

Ergibt der Baum genau das Ergebnis der Zeile?

### _unter

```python
def _unter(block: GleichungBlock, symbol: str) -> GleichungBlock
```

Der Block, wie er ist -- unter dem Symbol, unter dem sein Wert gebraucht wird.

### _gesetzt

```python
def _gesetzt(block: GleichungBlock, baum: Ausdruck, eingesetzt: List[GleichungBlock], symbol: str) -> GleichungBlock
```

Die Zeile von `block` mit den eingesetzten Formeln. Sie hat keine
Vorlage mehr -- eine solche Formel steht nicht in der Formelsammlung --,
dafuer die Normstellen aller Zeilen, die in ihr aufgingen.

### normstellen

```python
def normstellen(referenzen: Iterable[str]) -> str
```

Die Normstellen mehrerer Zeilen in einer, jede einmal und die Norm nicht
wiederholt: `SIA 262:2025, 4.3.3.2.1, (35); 4.3.3.2.3, (41)`. Die Norm
ist, was vor dem ersten Komma steht.


## Konstanten

- `KURZBREITE = 40.0` – Wie breit eine Formel mit Symbolen hoechstens werden darf, wenn eine andere in sie eingesetzt wird -- in Zeichen, wie [[opencivil.core.latex#sichtbare_breite|sichtbare_breite]] sie zaehlt. Breiter liest sie sich nicht mehr auf einen Blick.

## Braucht

- [[opencivil.core.formelbaum]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.web.api]]
