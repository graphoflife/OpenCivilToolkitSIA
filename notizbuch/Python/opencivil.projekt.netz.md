---
erzeugt: 7b6fbb0a280a
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/netz.py
> Knoten mit Kennungen, und wie neue dazukommen.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/netz.py)

## VERANTWORTUNG

Eine Zeichnung aus Knoten und Elementen, die auf sie verweisen, braucht zwei
Regeln. Jede steht hier einmal:

1. **Eine Kennung kommt nie wieder** (Benutzer, 2026-11-19). Wer Kennungen
   vergibt – das Projekt, ein Bauteil –, merkt sich je Vorsilbe die
   hoechste je vergebene Nummer (`vergeben`); die neue liegt darueber. Nach
   K1, K2, K7 kommt K8, nicht K3 – und nach dem Loeschen von K8 kommt K9,
   nicht wieder K8. Bis 2026-11-19 zaehlte nur, was noch da war. Eine
   Meldung, eine Auswahl oder eine Diagrammzeile, die auf ein geloeschtes
   Element zeigt, zeigt dann ins Leere – und nicht auf ein anderes, das
   zufaellig dieselbe Kennung erbte. Wer Kennungen selbst schreibt, statt
   sie vergeben zu lassen – der MCP-Zugang –, haelt sich an dieselbe
   Regel ([[opencivil.projekt.netz#von_hand|von_hand]]).
2. **Gleiche Koordinaten sind ein Knoten.** Wer einen Punkt anlegt, der genau
   auf einem bestehenden Knoten liegt, bekommt diesen. So haengen Elemente,
   die sich in einem Punkt treffen, am selben Knoten und bewegen sich
   gemeinsam.

Genau gleich, nicht beinahe: was zusammengehoert, faengt das Zeichenfenster
beim Zeichnen. Eine Toleranz hier wuerde zwei Punkte, die jemand absichtlich
einen Hundertstelmillimeter auseinander gesetzt hat, stillschweigend vereinen.

Allgemein gehalten: der Baukasten kennt weder Beton noch Querschnitt, nur
Knoten mit Kennung und Koordinaten – zwei in der Ebene, drei im Raum. Das Zeichenfenster im Browser folgt
denselben Regeln (`web/js/cad_modell.js`), damit es nichts anlegt, was der
Kern anders saehe; der Kern haengt von ihm nicht ab.

## Inhalt

### nummer

```python
def nummer(kennung: str, vorsilbe: str) -> Optional[int]
```

Die Zahl hinter der Vorsilbe – `None`, wenn die Kennung anders gebaut ist.

### neue_kennung

```python
def neue_kennung(besitzer: Any, vorsilbe: str, vorhandene: Iterable[str]) -> str
```

Eine neue Kennung mit dieser Vorsilbe – ueber jeder, die `besitzer` je
vergeben hat, und ueber jeder der `vorhandene`n: eine Datei, die noch
keine Zaehlung kennt, hat nur sie. Der Besitzer merkt sich die neue.

### von_hand

```python
def von_hand(alt: Any, neu: Any, wo: str) -> None
```

Regel 1 fuer ein Bauteil, das jemand als Ganzes selbst schreibt, mit den
Kennungen seiner Elemente – ueber den MCP-Zugang ([[opencivil.mcp]]):
jede Kennung in `neu`, die `alt` nicht hat, liegt ueber jeder Nummer,
die `alt` je vergeben hat. Sonst traefe ein Diagramm, das noch auf
einen geloeschten Lastfall zeigt, einen neuen. `neu` merkt sich danach
je Vorsilbe die hoechste Nummer. Eine Kennung anderer Form als `LF3`
vergibt [[opencivil.projekt.netz#neue_kennung|neue_kennung]] nie; sie zaehlt hier nicht.

### _hoechste

```python
def _hoechste(vergeben: Mapping[str, int], kennungen: Iterable[str]) -> Dict[str, int]
```

`vergeben`, hochgezaehlt auf die Nummer jeder dieser Kennungen, wo sie darueber liegt.

### _kennungen

```python
def _kennungen(eintrag: Any) -> Iterator[str]
```

Die Kennungen der Elemente unter `eintrag`, auch tiefer – nicht seine eigene.

### Netz

```python
class Netz
```

Die Knoten einer Zeichnung – mit dem Zusammenfuehren gleicher Koordinaten.

`besitzer` ist das Bauteil: neue Knoten werden an seine Liste
`knoten` angehaengt, ihre Kennung zaehlt es ([[opencivil.projekt.netz#neue_kennung|neue_kennung]]).
Jeder Knoten hat `kennung` und seine Koordinaten – wie sie
heissen, sagt `achsen`: `y` und `z` im Querschnitt, `x` und `z`
im Balkensystem, `x`, `y` und `z` im 3D-Balkensystem. `neu` baut
einen aus Kennung und Lage – so bleibt der Baukasten bei der Klasse, die
die Beschreibung speichert, ohne sie zu kennen.

#### Netz.an

```python
def an(self, *koordinaten: float) -> str
```

Die Kennung des Knotens an diesen Koordinaten – angelegt, wenn es dort noch keinen gibt.

#### Netz.lage

```python
def lage(self, kennung: str) -> Optional[Tuple[float, ...]]
```

Wo der Knoten liegt – `None`, wenn es ihn nicht gibt.


## Konstanten

- `_GEBAUT = re.compile('(\\D+)(\\d+)')` – Wie eine Kennung gebaut ist, die [[opencivil.projekt.netz#neue_kennung|neue_kennung]] vergibt: Vorsilbe und Nummer, `LF3`.

## Braucht

- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.mcp.sitzung]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.projekt.faelle]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.staebe]]
