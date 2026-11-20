---
erzeugt: 54a48741d5f9
art: modul
tags: [modul]
---
> [!abstract] opencivil/mcp/zeiger.py
> einzelne Felder eines Eintrags aendern, ueber Pfade.
> Paket [[opencivil.mcp]] · [Quelltext](../../opencivil/mcp/zeiger.py)

Ein Pfad zeigt in einen Eintrag, wie er in der Datei steht und wie
`eintrag_lesen` ihn zeigt: `/lastfaelle/0/M_Ed` ist `M_Ed` im ersten
Lastfall, nach RFC 6901 -- `~1` steht fuer «/» in einem Namen, `~0` fuer
«~». `-` am Ende einer Liste haengt an; der leere Pfad meint den ganzen
Eintrag. Ob das Geaenderte gilt, entscheidet danach der Leser des Kerns
([[opencivil.projekt.lesen]]): ein Feld, das es nicht gibt, meldet er mit
dem aehnlichsten, das es gibt.

## Inhalt

### anwenden

```python
def anwenden(roh: Any, aenderungen: Iterable[Mapping[str, Any]]) -> Any
```

Die `aenderungen` an `roh`, der Reihe nach: je eine mit `pfad` und
`wert` -- setzen, bei `-` anhaengen -- oder mit `pfad` und
`entfernen` -- aus einer Liste nehmen, ein Feld auf seine Vorgabe
zuruecksetzen. Gibt das Ganze zurueck.

### _teile

```python
def _teile(pfad: str) -> List[str]
```

Die Namen eines Pfads, RFC 6901 -- keiner beim leeren.

### _hinein

```python
def _hinein(ziel: Any, teil: str, pfad: str) -> Any
```

Einen Schritt tiefer -- in ein Feld oder an eine Stelle einer Liste.

### _stelle

```python
def _stelle(liste: List[Any], teil: str, pfad: str) -> int
```

Die Stelle in einer Liste, ab 0 gezaehlt -- eine, die es gibt.


## Braucht

- [[opencivil.mcp.sitzung]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.mcp.werkzeuge]]
