---
erzeugt: 5c165dfb350a
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/umschlag.py
> wie eine Antwort an die Oberfläche verpackt wird.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/umschlag.py)

## VERANTWORTUNG

Der Umschlag jeder Antwort: `{"status": …, "daten": …}` als JSON, ohne
`NaN` und `Infinity`, und im Fehlerfall `{"fehler", "spur"}` als Daten.
Der Rechenkern ([[opencivil.web.dienst]], auch hinter dem Server) und die
Konsole der App «Python» ([[opencivil.konsole.dienst]]) packen beide hier.
Bis 2026-10-17 baute die Konsole ihren Umschlag selbst, ohne den Riegel
gegen `NaN` -- eine Linie mit `lw=float("nan")` kam als Antwort an, die
`JSON.parse` ablehnte, und die Konsole blieb bei «Läuft …» stehen.


## LEICHT

Nur `json`, `math` und `traceback`. Der Faden der Konsole lädt dieses
Modul und nicht den Rechenkern; ein Test hält das fest.

## Inhalt

### endlich

```python
def endlich(daten: Any) -> Any
```

Ersetzt unendliche und undefinierte Zahlen durch `None`.

`json.dumps` schreibt dafuer sonst `Infinity` bzw. `NaN` -- eine
Erweiterung, die Python selbst wieder liest, `JSON.parse` im Browser aber
ablehnt. Die Antwort kaeme mit Status 200 an und waere dennoch unbrauchbar.

Solche Werte entstehen ganz regulaer: ein Erfuellungsgrad ist unendlich,
wenn die Einwirkung null ist. In JSON wird daraus `null`, und die
Oberflaeche zeigt dafuer das Unendlichkeitszeichen.

### nach_json

```python
def nach_json(daten: Any) -> str
```

Wandelt eine Antwort in JSON.

`allow_nan=False` ist Absicht: `json.dumps` schriebe sonst `Infinity`
und `NaN`. Python liest das wieder, `JSON.parse` im Browser lehnt es ab
-- die Antwort kaeme heil an und waere trotzdem unbrauchbar. Lieber hier
laut scheitern als dort stumm. [[opencivil.web.umschlag#endlich|endlich]] raeumt die Faelle vorher weg,
sodass der Riegel nur zuschlaegt, wenn wirklich etwas Neues auftaucht.

### fehlerdaten

```python
def fehlerdaten(meldung: str, spur: str='') -> Dict[str, str]
```

Was eine Anfrage zurueckgibt, die nicht gelang -- an jedem Dienst dieselbe Form.

### umschlag

```python
def umschlag(status: int, daten: Any) -> str
```

Der Umschlag als JSON, wie `web/js/kern.js` ihn liest. Laesst sich
`daten` nicht schreiben, wird daraus eine Antwort 500 mit dem Grund --
eine Anfrage soll nie ohne lesbare Antwort bleiben.


## Gebraucht von

- [[opencivil.konsole.dienst]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.server]]
