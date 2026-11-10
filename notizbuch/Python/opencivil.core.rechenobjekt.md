---
erzeugt: 3ad6ed512e2d
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/rechenobjekt.py
> was ein Bauteil im Rechenwerk ist.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/rechenobjekt.py)

## VERANTWORTUNG

Ein Rechenobjekt -- ein Fundament, eine Platte, ein Balkensystem, ein
Baustoff -- traegt seine Werte nach Kurzname (`definitionen`) und seine
Berechnungen (`berechnungen`) und meldet beides beim Rechenwerk an, nach
den Baustoffen, die es braucht. [[opencivil.core.rechenobjekt#Rechenobjekt|Rechenobjekt]] sagt das einmal: die
Kennung eines Werts ([[opencivil.core.rechenobjekt#Rechenobjekt.id_von|id_von]]) und das Anmelden
([[opencivil.core.rechenobjekt#Rechenobjekt.ins_rechenwerk|ins_rechenwerk]]).

Bis 2026-11-10 schrieben sieben Klassen beides von Hand. Zwei nannten bei
einem unbekannten Kurznamen die bekannten, die uebrigen warfen einen
blanken `KeyError` mit dem Kurznamen allein.

## Inhalt

### Rechenobjekt

```python
class Rechenobjekt
```

Siehe Dateikopf. Wer erbt, hat `name`, `definitionen` und
`berechnungen` -- als Felder seiner Datenklasse oder aus seinem
`__init__`.

- `WAS: ClassVar[str] = 'Bauteil'` – Wie eine Meldung das Objekt nennt: «Querschnitt 'Decke' kennt …».
- `name: str`
- `definitionen: Dict[str, 'WertDef']`
- `berechnungen: List['Berechnung']`

#### Rechenobjekt.id_von

```python
def id_von(self, kurzname: str) -> str
```

Die Wert-ID zu einem Kurznamen, etwa `f_cd` -> `beton.C30_37.f_cd`.

#### Rechenobjekt.baustoffe

```python
@property
def baustoffe(self) -> Sequence[Any]
```

Die Baustoffe, die es braucht -- angemeldet vor ihm. Ohne Angabe keine.

#### Rechenobjekt.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> Any
```

Meldet erst die Baustoffe an, dann die eigenen Werte und Berechnungen.
Einen Baustoff zweimal anzumelden ist wirkungslos -- eine Platte weiss
nicht, ob eine andere ihren Beton schon angemeldet hat.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.durchstanzen.stelle]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.stabwerk.rechnung]]
