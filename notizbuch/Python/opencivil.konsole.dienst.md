---
erzeugt: d1756685e1d1
art: modul
tags: [modul]
---
> [!abstract] opencivil/konsole/dienst.py
> die Konsole als Dienst für ihren Faden.
> Paket [[opencivil.konsole]] · [Quelltext](../../opencivil/konsole/dienst.py)

## VERANTWORTUNG

Nimmt die Anfragen der App «Python» an, wie [[opencivil.web.dienst]] die
des Rechenkerns: Name und Rumpf als JSON hinein, `{"status", "daten"}` als
JSON heraus. Derselbe Faden (`web/js/kern_arbeiter.js`) trägt beide; die
Konsole bekommt einen eigenen, damit eine Endlosschleife im Skript weder die
Seite noch den Rechenkern anhält -- und damit «Abbrechen» ihn einfach
beenden kann.


## ANFRAGEN

`ausfuehren` {code, name, eingabe}
Lädt die Pakete, die der Code einbindet, und führt ihn aus. Zurück
kommen die Ereignisse des Laufs und die Variablen danach.
`zuruecksetzen` {}
Leert den Namensraum.

Asynchron, weil das Laden der Pakete im Browser wartet; der Faden wartet auf
jede Antwort, beim Rechenkern auf eine fertige Zeichenkette. Verpackt wird
wie beim Rechenkern ([[opencivil.web.umschlag]]).

## Inhalt

### bearbeite_json

```python
async def bearbeite_json(name: str, rumpf: str) -> str
```

Eine Anfrage, als JSON hinein und hinaus -- Fehler kommen als Antwort, nie als Absturz.


## Konstanten

- `SITZUNG = Sitzung()`

## Braucht

- [[opencivil.konsole.pakete]]
- [[opencivil.konsole.sitzung]]
- [[opencivil.web.umschlag]]
