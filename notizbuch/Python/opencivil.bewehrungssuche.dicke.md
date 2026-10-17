---
erzeugt: 9a18082975fa
art: modul
tags: [modul]
---
> [!abstract] opencivil/bewehrungssuche/dicke.py
> die duennste Platte suchen.
> Paket [[opencivil.bewehrungssuche]] · [Quelltext](../../opencivil/bewehrungssuche/dicke.py)

## VERANTWORTUNG

Mit «Plattendicke optimieren» (`automatik_dicke`) wird zusaetzlich die
Dicke gesucht. Je Dicke laeuft dieselbe Bewehrungssuche
([[opencivil.bewehrungssuche.laengs#suche|suche]]) im gewaehlten Modus;
gesucht wird die duennste Platte, bei der sie eine Loesung findet.

## Inhalt

### Dickenversuch

```python
@dataclass
class Dickenversuch
```

Eine gepruefte Dicke -- fuer die Meldung, welche es waren.

- `h: float` – Plattendicke in mm.
- `geht: bool`

### Dickenergebnis

```python
@dataclass
class Dickenergebnis
```

Die duennste Platte -- und die Bewehrungssuche bei ihr.

- `modus: Suchmodus`
- `h: Optional[float] = None` – Gefundene Dicke in mm -- `None`: keine gefunden.
- `suche: Optional[Suchergebnis] = None` – Die Bewehrungssuche bei der gefundenen Dicke, sonst bei der letzten.
- `versuche: List[Dickenversuch] = field(default_factory=list)`
- `begruendung: str = ''`

#### Dickenergebnis.gefunden

```python
@property
def gefunden(self) -> bool
```

### dicke_suchen

```python
def dicke_suchen(projekt, kennung: str, *, modus: Suchmodus, **wie) -> Dickenergebnis
```

Die duennste Platte auf dem Zentimeter, bei der die Bewehrungssuche eine
Loesung findet -- mit allen eingeschalteten Nachweisen, innerhalb der
Obergrenze, und mit Duktilitaet, wenn sie eingeschaltet ist.

Von der eingegebenen Dicke aus: geht es, wird halbiert, bis es nicht mehr
geht -- nie unter die Mindestdicke der Platte (`automatik_mindestdicke`);
geht schon sie, ist sie das Ergebnis. Geht es nicht, wird verdoppelt, bis
es geht -- hoechstens bis [[opencivil.bewehrungssuche.dicke#Konstanten|DICKE_HOECHSTENS]]. Eine Platte, die
duenner eingegeben ist als die Mindestdicke, beginnt bei ihr. Dazwischen
Bisektion auf dem Raster. Das setzt
voraus, dass es innerhalb einer Verdopplung nur einmal von «geht nicht»
zu «geht» wechselt: bei Biegung und Querkraft sicher, bei der
Mindestbewehrung, die mit der Dicke waechst, erst bei sehr dicken Platten
nicht mehr.

`wie` geht an [[opencivil.bewehrungssuche.laengs#suche|suche]] (Teilungen, Durchmesser); das Projekt
bleibt unberuehrt. Was an der Platte nicht stimmen kann, meldet sich
vorab, mit ihrer eingegebenen Dicke ([[opencivil.bewehrungssuche.bewertung#vorab_pruefen|vorab_pruefen]]).

### _versuche_text

```python
def _versuche_text(ergebnis: Dickenergebnis) -> str
```

«300 ✓, 150 ✗, 220 ✓» -- die geprueften Dicken in mm, der Reihe nach.


## Konstanten

- `DICKENRASTER = 10.0` – Das Raster der Plattendicke in mm. Gefunden wird die kleinste Dicke auf diesem Raster, bei der alles aufgeht -- also auf den Zentimeter aufgerundet.
- `DICKE_HOECHSTENS = 2000.0` – Bis wohin beim Verdoppeln gesucht wird, in mm. Dicker ist nicht immer leichter: die Mindestbewehrung waechst mit der Dicke, und mit einer Obergrenze kann eine sehr dicke Platte wieder durchfallen.

## Braucht

- [[opencivil.bewehrungssuche.bewertung]]
- [[opencivil.bewehrungssuche.laengs]]

## Gebraucht von

- [[opencivil.bewehrungssuche]]
