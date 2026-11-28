---
erzeugt: a5c92e154cf3
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/stufen.py
> Plattenbereiche um die Stütze: d an ihr, Schnitte an den Stufen.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/stufen.py)

## VERANTWORTUNG

Liegt die Stütze in Bereichen mit eigener Dicke ([[opencivil.durchstanzen.bereiche|.bereiche]]), gilt an
ihr deren statische Höhe, und ein Schnitt weiter aussen kann massgebend
sein: an einer Stufe, mit der kleineren statischen Höhe der dünneren Platte
(SIA 262:2025, 4.3.6.2.7). Gerechnet werden alle möglichen Schnitte, es
gilt der schwächste, und jeder hat sein Urteil. Hier steht, welche
statische Höhe an der Stütze und für ψ gilt ([[opencivil.durchstanzen.stufen#an_der_stuetze|an_der_stuetze]]), je
Stufe ihr Schnitt ([[opencivil.durchstanzen.stufen#Stufe|Stufe]], [[opencivil.durchstanzen.stufen#stufen|stufen]]) und wie die Herleitung
das zeigt – mit denselben Schritten wie der Schnitt um die Stütze
([[opencivil.durchstanzen.herleitung|.herleitung]]).


## WO DER SCHNITT AN EINER STUFE LIEGT (Figur 24)

In der Mitte des Risses, der durch die Ecke der Stufe läuft, von der
Druckseite schräg zur Zugbewehrung der dünneren Platte; d_v ist das der
dünneren Platte.

- Zur Stütze hin (Figur 24a): der Riss beginnt an der Stufe auf der
  Druckseite – der Schnitt liegt 0.5·d_v ausserhalb des Bereichs, um seine
  konvexe Hülle (Figur 22c), mit Bögen um ihre Ecken.
- Gegenseite (Figur 24c): der Riss endet an der Stufe auf der Zugseite –
  der Schnitt liegt 0.5·d_v innerhalb des Bereichs, und mindestens 0.5·d_v
  neben der Stütze. Ist dafür kein Platz, gibt es an dieser Stufe keinen
  eigenen Schnitt.

Ein dünnerer Bereich gibt keinen Schnitt an seiner Stufe: jenseits ist die
Platte dicker, und jeder Schnitt dort trägt mehr als der innen.


## DIE PLATTENROTATION

ψ rechnet mit der kleinsten statischen Höhe um die Stütze – meist der der
Platte ausserhalb der Bereiche: mit ihr dreht sich die Platte am meisten,
das liegt auf der sicheren Seite (Benutzer, 2026-11-27). Dasselbe ψ gilt an
jedem Schnitt; k_r (59) rechnet je Schnitt mit dessen d.


## NACH VORGABE, NICHT NACHGESCHLAGEN

- Ein Bereich zählt an seiner Stufe wie eine grosse gestützte Fläche: von
  einer Geraden des Schnitts zählt nur, was höchstens 1.5·d_v von einer Ecke
  entfernt liegt (Figur 23a) – zur Stütze hin wie am Stahlpilz, auf der
  Gegenseite an den Ecken des Schnitts selbst.
- Ist ein Bereich auf der Gegenseite dicker, gilt sein d an einem Schnitt
  innen nur, wenn er weiter als d_v über dessen Fläche hinausreicht: sonst
  endete der Riss jenseits der Stufe, wo die Zugbewehrung höher liegt, und
  es gilt das d dort ([[opencivil.durchstanzen.bereiche#Dicken.wirksam|.bereiche.Dicken.wirksam]]). Das gilt am
  Schnitt um die Stütze und an jeder Stufe zur Stütze hin.


## EINHEITEN

SI-Basis; Kräfte in N.

## Inhalt

### Stuetzenhoehe

```python
@dataclass(frozen=True)
class Stuetzenhoehe
```

Welche Bereiche die Stütze umschliessen und welche statischen Höhen
daraus folgen: an der Stütze und für ψ – siehe Dateikopf.

- `um: Tuple[Plattenbereich, ...]` – Die Bereiche um die Stütze, der innerste zuerst.
- `wirksam: Optional[Plattenbereich]` – Wessen d an der Stütze gilt – `None`: das der Platte.
- `rotation: Optional[Plattenbereich]` – Wessen d ψ rechnet: das kleinste um die Stütze – `None`: das der Platte.

### an_der_stuetze

```python
def an_der_stuetze(dicken: Dicken, stuetze: Stuetzenflaeche) -> Stuetzenhoehe
```

Was an der Stütze gilt – siehe [[opencivil.durchstanzen.stufen#Stuetzenhoehe|Stuetzenhoehe]].

### Stufe

```python
@dataclass(frozen=True)
class Stufe
```

Eine Stufe um die Stütze, wo der Bereich dicker ist als das, was jenseits
liegt, und der Schnitt neben ihr – `pruefung` fehlt, wo auf der
Gegenseite kein Platz für einen ist.

- `bereich: Plattenbereich`
- `jenseits: Optional[Plattenbereich]` – Was jenseits der Stufe liegt – `None`: die Platte.
- `wirksam: Optional[Plattenbereich]` – Wessen d der Schnitt rechnet – meist das jenseits der Stufe.
- `d: float`
- `pruefung: Optional[Schnittpruefung]`

#### Stufe.index

```python
@property
def index(self) -> Index
```

Wie ihre Werte heissen: u_{0,B1}, V_{Rd,c,B1}.

#### Stufe.V_Rd_c

```python
def V_Rd_c(self, psi: float, k_g: float, tau_cd: float) -> float
```

Der Widerstand an der Stufe, still: k_r (59) mit ihrem d – für die Kennzahl.

### stufen

```python
def stufen(dicken: Dicken, hoehe: Stuetzenhoehe, stuetze: Stuetzenflaeche, *, raender: Sequence[Halbebene], achse: Punkt, aussparungen: Sequence[Sequence[Punkt]], regel: KeRegel, V_d: float, q_d: float) -> Tuple[Stufe, ...]
```

Die Stufen um die Stütze, die innerste zuerst, je mit ihrem Schnitt – still.

### _innerhalb

```python
def _innerhalb(bereich: Plattenbereich, d: float, stuetze: Stuetzenflaeche, raender: Sequence[Halbebene]) -> Optional[Kandidat]
```

Der Schnitt 0.5·d innerhalb der Stufe auf der Gegenseite (Figur 24c) –
oder nichts, wo er näher als 0.5·d an die Stütze käme. Seine Geraden
zählen je 1.5·d von ihren Ecken.

### Bereichswerte

```python
@dataclass(frozen=True)
class Bereichswerte
```

Was die Herleitung von den Bereichen um die Stütze zeigt: je Bereich
seine Dicke als Wert, d an der Stütze und, wo es nicht das der Platte
ist, d für ψ mit den beiden Lagen.

- `dicken: Dict[str, Wert]`
- `d_S: Wert`
- `d_psi: Optional[Wert] = None`
- `lagen_psi: Optional[Dict[Richtung, Wert]] = None`

### bereiche_schreiben

```python
def bereiche_schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, dicken: Dicken, hoehe: Stuetzenhoehe, d: Wert, lagen: Dict[Richtung, Wert]) -> Bereichswerte
```

Die Bereiche um die Stütze, die statische Höhe an ihr und die, mit der
ψ rechnet. `d` und `lagen` sind die der Platte.

### _d_im

```python
def _d_im(p: Protokoll, w: Zwischenwerte, e: Eingaben, werte: Dict[str, Wert], d: Wert, b: Optional[Plattenbereich], name: str, symbol: str, *, titel: str) -> Wert
```

d im Bereich `b`: d der Platte, um den Unterschied der Dicke verschoben.

### rotation_schreiben

```python
def rotation_schreiben(p: Protokoll, hoehe: Stuetzenhoehe) -> None
```

Der Satz, mit welchem d ψ rechnet – nur, wo die Stütze in Bereichen steht.

### stufe_schreiben

```python
def stufe_schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, st: Stufe, *, d: Wert, werte: Bereichswerte, psi: Wert, k_g: Wert, tau_cd: Wert, k_e_stuetze: Wert, last: str, V_d: Optional[Wert]=None) -> Optional[Tuple[Wert, Wert]]
```

Der Schnitt an einer Stufe mit denselben Schritten wie um die Stütze:
zurück kommen die Querkraft in ihm und sein Widerstand – oder nichts,
wo er fehlt. `d` ist das d der Platte, `V_d` die Stützenkraft, wo es
nicht die eingegebene ist (die Kennzahl).

### vergleich_schreiben

```python
def vergleich_schreiben(p: Protokoll, st: Stufe, V: Wert, V_Rd_c: Wert) -> Vergleich
```

Der Vergleich an der Stufe – sein Urteil gibt der Nachweis.


## Konstanten

- `REFERENZ = 'SIA 262:2025, 4.3.6.2.7, Figur 24'` – Wo die Norm die Bereiche regelt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.bereiche]]
- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.durchstanzen.kennzahl]]
- [[opencivil.durchstanzen.nachweis]]
