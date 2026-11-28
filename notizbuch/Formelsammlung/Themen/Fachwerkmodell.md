---
erzeugt: 98b91a1ec388
art: thema
tags: [thema]
---
> [!abstract] Fachwerkmodelle
> 1 Formel, in der Folge, in der gerechnet wird.

## Formeln

1. [[Leichtestes Fachwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Fachwerkmodell zeigt, wie eine Scheibe ihre Lasten zu den Lagern
trägt: Druckstreben und Zugglieder, die sich an Knoten im Gleichgewicht
halten. In einer Wandscheibe aus Stahlbeton sind die Druckstreben der
Beton und die Zugglieder die Bewehrung. Jedes Fachwerk im Gleichgewicht
ist ein möglicher Weg der Kräfte: Nach dem unteren Grenzwertsatz der
Plastizitätstheorie trägt die Scheibe, wenn jede Strebe und jedes
Zugglied seine Kraft aufnimmt. Bemessen wird hier nichts – ohne Material
und Dicke hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten ab.

Das Werkzeug sucht das Fachwerk nach dem Verfahren Ground Structure. Über
die Scheibe legt es ein Raster aus Knoten; dazu kommen die Punkte der
Lager und Lasten und die Ecken der Umrisse. Je zwei Knoten sind ein
möglicher Stab, wenn er ganz im Material liegt – um eine Türe herum also,
nicht quer durch sie. Unter allen diesen Stäben wählt eine lineare
Optimierung die Kräfte im Gleichgewicht, die das Fachwerk am leichtesten
machen ([[Leichtestes Fachwerk]]).

Schon ein grobes Raster gibt tausende möglicher Stäbe. Darum beginnt die
Suche mit den kurzen und nimmt Runde um Runde die dazu, die das Fachwerk
noch leichter machten; fertig ist sie, wenn keiner mehr fehlt. Dann ist
es das Fachwerk, das die Optimierung über alle Stäbe fände. Jede Runde
gibt schon ein Fachwerk im Gleichgewicht: Wer anhält, hat ein brauchbares,
wenn auch womöglich nicht das leichteste.

Ein feineres Raster findet ein leichteres Fachwerk mit mehr und kürzeren
Stäben. Die Optimierung endet innen: Wo mehrere Fachwerke gleich leicht
sind, trägt jedes einen Teil. Darum fallen zuletzt die Stäbe unter der
kleinsten Stabkraft weg, und das Gleichgewicht wird ohne sie neu gesucht.
Wie fein das Raster ist und was als dünn gilt, ist eine Wahl: Das
leichteste Fachwerk ist ein guter Vorschlag für den Weg der Kräfte, weil
es am wenigsten Material braucht – nicht der einzige.

Beispiel: Die Wandscheibe 6 × 3 m mit Türe im Prüfprojekt hat im Raster
von 1 m 186 mögliche Stäbe; nach 8 Runden stehen 82 im Modell, und das
Fachwerk hat 22 Stäbe mit $V = 7110\,\mathrm{kNm}$. Im Raster von 0.5 m
sind es 1526 mögliche Stäbe und 58 im Fachwerk mit $V = 6819\,\mathrm{kNm}$,
4 % leichter. Unter der Türe liegt kein Stab: ihre Schwelle ist ein Rand
der Scheibe, und auf keiner Seite ist dort Material.
