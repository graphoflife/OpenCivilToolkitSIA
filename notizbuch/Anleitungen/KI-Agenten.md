Eine KI kann mit dem Werkzeug arbeiten wie du an der Seite: Projekte öffnen,
Einträge anlegen und ändern, rechnen, die Herleitung lesen und den Bericht
schreiben. Ihr Programm startet dazu auf deinem Rechner einen kleinen Dienst
des Werkzeugs, den *MCP-Server*. MCP heisst Model Context Protocol – so reden
KI-Programme mit Werkzeugen. Gerechnet wird mit demselben Rechenkern wie hier;
die Ergebnisse sind dieselben.

Diese Seite führt Schritt für Schritt hin: für Claude Code, für die Claude-App
und für andere Programme. Einmal eingerichtet, genügt danach ein Satz an die
KI.

> [!info] Wie KI und Seite zusammenkommen
> Die KI arbeitet nicht in dieser Seite, sondern in einer Projektdatei auf
> deinem Rechner. Die beiden teilen keinen Speicher; die Datei trägt die
> Projekte hin und her:
>
> 1. Hier oben «Speichern»: der Browser legt alle Projekte als `.json`-Datei
>    ab, etwa `OCT Projekt.json` im Ordner «Downloads».
> 2. Die KI öffnet die Datei, ändert, rechnet und speichert.
> 3. Hier oben «Öffnen» und dieselbe Datei wählen, dann «Alles ersetzen» –
>    oder «Hinzufügen», dann kommen ihre Projekte zu denen hier dazu.
>
> Ohne Datei geht es auch: die KI legt eine neue an.

## Schritt 1 – Das Werkzeug und Python

**Das Werkzeug auf deinen Rechner holen.** Im Terminal:

```bash
git clone https://github.com/graphoflife/OpenCivilToolkitSIA.git
```

Ohne Git: auf [GitHub](https://github.com/graphoflife/OpenCivilToolkitSIA)
«Code» → «Download ZIP» wählen und die Datei entpacken. Den Ordner, der dabei
entsteht, nennt diese Seite den *Ordner des Werkzeugs*. Merke dir seinen
vollen Pfad, etwa `/home/benutzer/OpenCivilToolkitSIA` oder
`C:\Users\benutzer\OpenCivilToolkitSIA`.

**Python prüfen.** Es braucht Python 3.11 oder neuer, sonst nichts – kein
weiteres Paket. Im Terminal:

```bash
python3 --version
```

Unter Windows heisst der Befehl `python` statt `python3`, hier und in allen
folgenden Schritten. Steht dort 3.10 oder weniger, braucht es ein neueres
Python.

## Schritt 2 – Probieren, ob der Server startet

Im Terminal, im Ordner des Werkzeugs – unter Windows in der PowerShell:

```bash
cd /home/benutzer/OpenCivilToolkitSIA
echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | python3 -m opencivil.mcp
```

Kommt diese Zeile zurück, läuft der Server:

```
{"jsonrpc": "2.0", "id": 1, "result": {}}
```

Die Zeile mit `echo` schickt dem Server eine einzige Nachricht, «ping»; er
antwortet und hört auf. Startest du ihn ohne sie, wartet er still auf
Nachrichten – so muss es sein, denn sein Gegenüber ist ein Programm, kein
Mensch. `Ctrl+C` beendet ihn. Kommt eine Fehlermeldung, hilft der letzte
Abschnitt: [[#Wenn es nicht geht|Wenn es nicht geht]].

Nun Schritt 3a, 3b oder 3c – je nach Programm.

## Schritt 3a – Claude Code

Claude Code findet den Server von selbst: im Ordner des Werkzeugs liegt die
Datei `.mcp.json`, die ihn nennt.

1. Claude Code im Ordner des Werkzeugs starten: im Terminal mit `cd` dorthin
   und `claude`. In der Claude-App im Tab «Code» denselben Ordner wählen.
2. Beim ersten Mal fragt Claude Code, ob es den Server «opencivil» aus
   `.mcp.json` verwenden darf. Zustimmen.
3. Prüfen: im Terminal zeigt `/mcp` in Claude Code den Server «opencivil» als
   verbunden. In jedem Programm geht auch die Frage an die KI: «Welche
   Werkzeuge von opencivil kennst du?»

Hast du beim ersten Mal abgelehnt: im Terminal
`claude mcp reset-project-choices`, dann Claude Code neu starten – es fragt
wieder. Eine laufende Sitzung liest `.mcp.json` nicht neu; nach einer
Änderung braucht es eine neue Sitzung.

Soll Claude Code den Server auch in anderen Ordnern kennen, trägst du ihn mit
`claude mcp add` für dich ein, mit denselben drei Angaben wie in Schritt 3c.

## Schritt 3b – Claude-App (Chat)

Im Chat der Claude-App, ohne den Tab «Code», trägst du den Server einmal von
Hand ein.

1. **Den vollen Pfad von Python suchen.** Im Terminal `which python3`, unter
   Windows `where python`. Die App startet den Server nicht aus deinem
   Terminal und fände darum nicht unbedingt dasselbe Python; mit dem vollen
   Pfad nimmt sie das richtige.
2. **Die Einstellungen der App öffnen:** «Einstellungen» → «Entwickler» →
   «Konfiguration bearbeiten» (englisch: Settings → Developer → Edit Config).
   Das zeigt die Datei `claude_desktop_config.json`. Sie liegt
   - unter macOS in `~/Library/Application Support/Claude/`,
   - unter Windows in `%APPDATA%\Claude\`,
   - unter Linux in `~/.config/Claude/`.

   Je nach Fassung der App heissen die Menüs etwas anders.
3. **Den Server eintragen**, mit deinen beiden Pfaden:

   ```json
   {
     "mcpServers": {
       "opencivil": {
         "command": "/usr/bin/python3",
         "args": ["-m", "opencivil.mcp"],
         "env": { "PYTHONPATH": "/home/benutzer/OpenCivilToolkitSIA" }
       }
     }
   }
   ```

   `command` ist der Pfad von Python aus Punkt 1, `PYTHONPATH` der Ordner des
   Werkzeugs: so findet Python das Werkzeug, gleich in welchem Ordner die App
   den Server startet. Stehen unter `mcpServers` schon andere Server, kommt
   «opencivil» als weiterer Eintrag dazu, mit einem Komma getrennt. Unter
   Windows steht in dieser Datei jeder `\` doppelt:
   `"C:\\Users\\benutzer\\OpenCivilToolkitSIA"`.
4. **Die App ganz beenden** – nicht nur das Fenster schliessen – und wieder
   starten.
5. **Prüfen:** im Eingabefeld unter «+» → «Connectors» steht «opencivil» mit
   seinen Werkzeugen.

## Schritt 3c – Andere Programme

Jedes Programm, das MCP-Server über «stdio» startet, geht – etwa Cursor,
VS Code oder ein eigenes Skript. Es braucht drei Angaben:

| Angabe | heisst meist | Wert |
|---|---|---|
| Befehl | `command` | `python3`, besser sein voller Pfad aus `which python3` |
| Argumente | `args` | `-m` und `opencivil.mcp`, zwei Einträge |
| Umgebung | `env` | `PYTHONPATH`, der volle Pfad des Ordners des Werkzeugs |

Statt `PYTHONPATH` geht auch der Ordner des Werkzeugs als Arbeitsordner
(`cwd`), wo das Programm einen kennt. Viele Programme nehmen denselben Eintrag
wie die Claude-App, `mcpServers` mit `command`, `args` und `env`; wo ihr
Format anders ist, gehören dieselben drei Angaben hinein.

Wer selbst ein Programm schreibt: der Server spricht JSON-RPC 2.0 über stdin
und stdout, eine Nachricht je Zeile, in den Fassungen 2025-06-18, 2025-03-26
und 2024-11-05 des Protokolls. Er bietet nur Werkzeuge an (`tools/list`,
`tools/call`), keine Ressourcen und keine Vorlagen. Wie er gebaut ist und
was jedes Werkzeug erwartet, sagt die Python-Doku: [[opencivil.mcp]] und
[[opencivil.mcp.werkzeuge]].

## Schritt 4 – Loslegen

Sag der KI in gewöhnlichen Worten, was sie tun soll. Zum Beispiel:

- «Öffne `~/Downloads/OCT Projekt.json` und sag mir, welche Nachweise nicht
  erfüllt sind und warum.»
- «Lege eine neue Platte an, 250 mm dick, aus C30/37. Rechne sie und zeig mir
  die Tragsicherheit.»
- «Probier in der Sandbox der Querschnittsanalyse aus, wie viel Bewehrung es
  für M_Ed = 120 kNm braucht.»
- «Zeig mir die Herleitung des Grundbruchs.»
- «Speichere unter `~/Projekte/Halle.json`.»
- «Schreib den Bericht als LaTeX nach `~/Projekte/Halle.tex`.»

Danach hier oben «Öffnen», die Datei wählen und «Alles ersetzen»: die Seite
zeigt, was die KI gemacht hat.

> [!tip] Pfade ganz nennen
> Ein Pfad wie `~/Projekte/Halle.json` oder
> `C:\Users\benutzer\Projekte\Halle.json` ist eindeutig. Ein kurzer wie
> `Halle.json` gälte vom Ordner aus, in dem das Programm den Server gestartet
> hat: bei Claude Code der Ordner des Werkzeugs, bei der Claude-App ein
> Ordner, den du nicht kennst.

## Was die KI kann – und was nicht

- **Sie rechnet nicht selbst.** Jede Zahl kommt aus dem Rechenkern, wie hier,
  und zu jedem Nachweis gibt es die Herleitung.
- **Jede Änderung prüft der Kern sofort.** Was er nicht lesen kann – ein Feld,
  das es nicht gibt, eine Zahl ausserhalb ihrer Grenzen –, ändert nichts.
  Seine Meldung geht an die KI, etwa «Gemeint ist vielleicht …», und sie
  versucht es richtig.
- **Nichts geht still verloren.** In die Datei, die sie geöffnet hat,
  speichert sie ohne Rückfrage; eine andere Datei, die es schon gibt,
  überschreibt sie nur, wenn sie es ausdrücklich verlangt. Was sie noch nicht
  gespeichert hat, verwirft sie beim Öffnen einer anderen Datei ebenso nur
  ausdrücklich. Sag ihr, ob sie überschreiben darf.
- **Die Sandbox** jeder App kann sie zurücksetzen, nicht löschen. Wie hier
  kommt die Sandbox nicht in den Bericht – der richtige Ort zum Ausprobieren.
- **Python-Skripte** der App «Python» führt der Zugang nicht aus.
- **Sie fragt zuerst.** Claude Code und die Claude-App fragen dich, bevor die
  KI ein Werkzeug zum ersten Mal braucht.

## Wenn es nicht geht

| Was du siehst | Woran es liegt | Was hilft |
|---|---|---|
| `No module named 'opencivil'` | Python findet das Werkzeug nicht | im Ordner des Werkzeugs starten oder `PYTHONPATH` auf ihn setzen, voll ausgeschrieben |
| `cannot import name 'StrEnum'` | Python ist älter als 3.11 | ein neueres Python, mit seinem vollen Pfad unter `command` |
| `python3` wird nicht gefunden | das Programm sucht Python anderswo als dein Terminal | den vollen Pfad aus Schritt 3b eintragen |
| Claude Code kennt «opencivil» nicht | nicht im Ordner des Werkzeugs gestartet, oder beim ersten Mal abgelehnt | dort starten; nach einer Ablehnung `claude mcp reset-project-choices` und neu starten |
| Die Claude-App zeigt «opencivil» nicht | ein Fehler in der Datei, oder die App lief noch | Kommas und doppelte `\` prüfen, die App ganz beenden; das Protokoll `mcp-server-opencivil.log` lesen – unter macOS in `~/Library/Logs/Claude/`, unter Windows in `%APPDATA%\Claude\logs\`, unter Linux in `~/.config/Claude/logs/` |
| Die Seite zeigt nicht, was die KI geändert hat | die Seite liest die Datei nicht von selbst | «Öffnen» und dieselbe Datei wählen |
| Die KI kennt nicht, was du hier angelegt hast | es ist noch nicht in der Datei | «Speichern» und der KI den Pfad der Datei nennen |
