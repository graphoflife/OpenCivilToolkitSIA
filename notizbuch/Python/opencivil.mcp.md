---
erzeugt: 63091ae0f072
art: modul
tags: [modul]
---
> [!abstract] opencivil/mcp/__init__.py
> das Werkzeug fuer eine KI, ueber das Model Context Protocol.
> Paket [[opencivil]] · [Quelltext](../../opencivil/mcp/__init__.py)

## WOZU

Eine KI -- Claude Code, ein anderes Programm, das MCP spricht -- arbeitet mit
dem Werkzeug wie jemand an der Seite: sie oeffnet eine Projektdatei, legt
Eintraege an und aendert sie, rechnet und holt den Bericht. Die Werkzeuge
dafuer stehen in [[opencivil.mcp.werkzeuge]], je eines mit Beschreibung
und Eingaben.


## START

`python3 -m opencivil.mcp` im Verzeichnis des Repos. Der Server spricht
JSON-RPC 2.0 ueber stdin und stdout, eine Nachricht je Zeile
([[opencivil.mcp.server]]), nur mit der Standardbibliothek. Claude Code
findet ihn ueber `.mcp.json`.


## EIN RECHENWEG

Gerechnet und geoeffnet wird ueber den Rechendienst
([[opencivil.web.dienst#bearbeite|opencivil.web.dienst.bearbeite]]), wie in der Seite; geaendert mit den
Methoden des Projekts, wie die Seite sie im Browser nachbaut. Eine zweite
Rechenlogik gibt es hier nicht. Jede Aenderung prueft der Kern sofort, und
seine Meldung geht unveraendert zurueck ([[opencivil.mcp.sitzung]]).


## BEWUSST NICHT

* Python-Skripte ausfuehren: die Konsole der Seite fuehrt beliebigen Code
  aus, und das soll eine KI nicht auf diesem Weg tun.
* Die ganze Antwort einer Rechnung zurueckgeben -- beim Beispiel rund
  870 kB. `rechnen` fasst sie je Bauteil zusammen
  ([[opencivil.mcp.ausgabe#rechnung|opencivil.mcp.ausgabe.rechnung]]); `herleitung` und `bericht`
  geben die Herleitung als Text.

## Module

- [[opencivil.mcp.__main__]] – startet den Server: `python3 -m opencivil.mcp`.
- [[opencivil.mcp.ausgabe]] – was die Werkzeuge als Text zurueckgeben.
- [[opencivil.mcp.server]] – das Protokoll: JSON-RPC 2.0 ueber stdin und stdout.
- [[opencivil.mcp.sitzung]] – die offene Projektdatei, und wie sie sich aendert.
- [[opencivil.mcp.werkzeuge]] – was eine KI mit dem Werkzeug tun kann, und mit welchen Angaben.
- [[opencivil.mcp.zeiger]] – einzelne Felder eines Eintrags aendern, ueber Pfade.
