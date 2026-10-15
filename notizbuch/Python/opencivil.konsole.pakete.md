---
erzeugt: 3140663d9025
art: modul
tags: [modul]
---
> [!abstract] opencivil/konsole/pakete.py
> welche Fremdpakete ein Skript einbinden kann.
> Paket [[opencivil.konsole]] · [Quelltext](../../opencivil/konsole/pakete.py)

## VERANTWORTUNG

Mitgeliefert ist, was unter `web/vendor/pyodide/` liegt: numpy und pandas
samt dem, was pandas braucht (Benutzer, 2026-10-15; geholt mit
`werkzeug/pyodide_holen.py`). Welche das sind, schreibt die Brücke aus den
Dateien, die dort liegen, nach `web/kern/dateien.json` (Eintrag
`pakete`: Importname -> Paketname). Hier wird nur gelesen -- eine zweite
Liste gäbe es nicht, die veralten könnte.


## WANN GELADEN WIRD

Erst wenn ein Skript ein Paket mit `import` einbindet: numpy kostet 2.9 MB,
und wer nur rechnet, soll sie nicht laden. Was ein Code einbindet, liest
[[opencivil.konsole.pakete#gebraucht|gebraucht]] aus seinem Syntaxbaum; geladen wird im Faden von Pyodide
([[opencivil.konsole.pakete#laden|laden]]). Unter CPython gibt es dort nichts zu laden.

## Inhalt

### mitgeliefert

```python
@lru_cache(maxsize=1)
def mitgeliefert() -> Dict[str, str]
```

Importname -> Paketname, für jedes Paket, das beiliegt.

### importe

```python
def importe(code: str) -> List[str]
```

Die Module, die `code` einbindet -- nur der erste Teil des Namens: `numpy` für `numpy.linalg`.

### gebraucht

```python
def gebraucht(code: str) -> List[str]
```

Die beiliegenden Pakete, die `code` einbindet -- ihre Abhängigkeiten lädt Pyodide selbst.

### laden

```python
async def laden(code: str) -> None
```

Lädt im Faden von Pyodide, was `code` braucht; unter CPython nichts.

### hinweis

```python
def hinweis(name: str) -> str
```

Was zu einem Modul gesagt wird, das sich nicht einbinden liess.


## Konstanten

- `VERZEICHNIS = Path(__file__).resolve().parents[2] / 'web' / 'kern' / 'dateien.json'` – Das Verzeichnis des Kerns -- im Faden liegt es an derselben Stelle neben `opencivil/` wie im Repo (`web/js/kern_arbeiter.js`).

## Gebraucht von

- [[opencivil.konsole.dienst]]
- [[opencivil.konsole.sitzung]]
