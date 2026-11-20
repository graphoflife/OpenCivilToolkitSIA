"""
opencivil/mcp -- das Werkzeug fuer eine KI, ueber das Model Context Protocol.

WOZU:
Eine KI -- Claude Code, ein anderes Programm, das MCP spricht -- arbeitet mit
dem Werkzeug wie jemand an der Seite: sie oeffnet eine Projektdatei, legt
Eintraege an und aendert sie, rechnet und holt den Bericht. Die Werkzeuge
dafuer stehen in :mod:`opencivil.mcp.werkzeuge`, je eines mit Beschreibung
und Eingaben.

START:
``python3 -m opencivil.mcp`` im Verzeichnis des Repos. Der Server spricht
JSON-RPC 2.0 ueber stdin und stdout, eine Nachricht je Zeile
(:mod:`opencivil.mcp.server`), nur mit der Standardbibliothek. Claude Code
findet ihn ueber ``.mcp.json``.

EIN RECHENWEG:
Gerechnet und geoeffnet wird ueber den Rechendienst
(:func:`opencivil.web.dienst.bearbeite`), wie in der Seite; geaendert mit den
Methoden des Projekts, wie die Seite sie im Browser nachbaut. Eine zweite
Rechenlogik gibt es hier nicht. Jede Aenderung prueft der Kern sofort, und
seine Meldung geht unveraendert zurueck (:mod:`opencivil.mcp.sitzung`).

BEWUSST NICHT:
* Python-Skripte ausfuehren: die Konsole der Seite fuehrt beliebigen Code
  aus, und das soll eine KI nicht auf diesem Weg tun.
* Die ganze Antwort einer Rechnung zurueckgeben -- beim Beispiel rund
  870 kB. ``rechnen`` fasst sie je Bauteil zusammen
  (:func:`opencivil.mcp.ausgabe.rechnung`); ``herleitung`` und ``bericht``
  geben die Herleitung als Text.
"""
