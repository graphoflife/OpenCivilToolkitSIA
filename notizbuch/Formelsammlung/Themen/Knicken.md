---
erzeugt: 520a05b8012d
art: thema
tags: [thema]
---
> [!abstract] Platte
> 14 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Nachgewiesen wird am verformten System. Die Ausmitte zweiter Ordnung hängt von der Krümmung ab, die Krümmung vom Moment und das Moment wieder von der Ausmitte – also wird die Folge so lange durchlaufen, bis sie einläuft. Läuft sie nicht ein, gibt es keine Gleichgewichtslage: das System knickt.

Der Erfüllungsgrad ist ein Verhältnis von Normalkräften: N\_Rd ist die grösste Druckkraft, unter der der Stab noch steht. Über Momente zu vergleichen ginge nur, solange es ein Gleichgewicht gibt – beim Knicken ist gerade das der Fall, der fehlt.

Womit die Verformung gerechnet wird, wählt das Kapitel: Kriechzahl, Werte und Rechenart. Das Kriechen wirkt bei der Parabel und weicht den Beton auf: er verformt sich mehr, die Ausmitte zweiter Ordnung wächst, und der Stab knickt früher – φ = 0 läge dann auf der unsicheren Seite. Im Bereich der Gebrauchslasten unterscheidet sich die Parabel kaum vom linearen Gesetz, in der Nähe der Grenzlast erheblich, und genau dort entscheidet sich, ob es noch eine Gleichgewichtslage gibt.

Das Suchfenster bleibt dabei innerhalb der Grenzdehnungen (-3.5 ‰ bis 45.0 ‰). Jenseits davon geben die Werkstoffgesetze null zurück, die Kraft wäre nicht mehr monoton, und die Halbierung liefe auf eine beliebige Stelle zu. Passt zu einer Krümmung kein Fenster mehr, gibt es keine Gleichgewichtslage – dann sagt der Nachweis das und rät nicht.

Die Ausmitten-Iteration darüber steht dagegen vollständig da, Durchlauf für Durchlauf: sie ist das Verfahren selbst, und dass sie einläuft, ist die Aussage des Nachweises.

Der Querschnitt bleibt eben (Bernoulli). Zu jeder Dehnungsebene ergeben sich Normalkraft und Moment aus den Spannungen über die Höhe; Zug ist positiv, das Moment bezieht sich auf die halbe Querschnittshöhe. Die Resistenzlinie ist der Rand aller zulässigen Ebenen: an ihm erreicht der Stahl ε\_ud, der Beton am gedrückten Rand −ε\_c2d oder, wenn der ganze Querschnitt gedrückt ist, im Punkt C −ε\_c1d.

Der Beton ist in 200 Fasern über die Höhe geteilt, jede mit ihrer mittleren Spannung, die Bewehrung zählt Lage für Lage, und an ihrer Stelle zählt der Stahl statt des Betons – auch die gedrückte Bewehrung wirkt mit. Den Widerstand bei einer Einwirkung sucht die Rechnung auf dem Rand selbst, zwischen zwei benachbarten Ebenen; was dort gilt, zeigt bei jeder Kombination die Probe.

Zu jedem Moment wird die Dehnungsebene gesucht, die es im Gleichgewicht hält; aus deren Krümmung folgt die nächste Ausmitte. Begonnen wird mit e\_2d = 0, also ohne Verformung.

Gesucht wird die grösste Druckkraft mit Gleichgewichtslage. Die gewollte Ausmitte e\_1d bleibt dabei fest – sie gehört zum System und nicht zur Last, M\_Ed,1 wächst also mit. Bei N = 0 trägt der Stab immer; von dort aus wird das Fenster halbiert, bis getragene und nicht getragene Kraft zusammenfallen.

Am gezeichneten Querschnitt gilt jeder Knickfall in einer Richtung: der Zugseite, zu der sich der Stab biegt. Die Nulllinie bleibt dabei parallel zur Achse; das Moment um die andere Achse, das ein unsymmetrischer Querschnitt weckt, zählt nicht. d reicht vom gedrückten Rand bis zum entferntesten Stab in Zugrichtung.

Der Momentenwiderstand bei einer Druckkraft ist der Bruchzustand des Querschnitts in Biegerichtung, mit den Gesetzen des Widerstands – wie in der Tragsicherheit, mit der Nulllinie parallel zur Achse.

Die Dehnung wächst linear in Zugrichtung, ε = ε\_m + χ·v mit v ab dem Schwerpunkt. Zu jeder Druckkraft und jedem Moment finden zwei geschachtelte Suchen ε\_m und χ, wie bei der Platte. Die Ausmitten-Iteration darüber steht vollständig da, Durchlauf für Durchlauf: sie ist das Verfahren selbst, und dass sie einläuft, ist die Aussage des Nachweises.

## Formeln

1. [[Ungewollte Ausmitte – allgemein]]
2. [[Gewollte Ausmitte und Ausmitte 2. Ordnung – allgemein]]
3. [[Wirksamer Elastizitätsmodul]]
4. [[Beiwert der Parabel, mit dem wirksamen Modul]]
5. [[Parabel-Rechteck-Beziehung des Betons]]
6. [[Dehnungsebene und innere Kräfte]]
7. [[Spannungsblock des Betons]]
8. [[Bilineare Beziehung des Betonstahls]]
9. [[Schnittgrössen aus der Spannungsverteilung]]
10. [[Schiefstellung]]
11. [[Ungewollte Ausmitte]]
12. [[Gewollte Ausmitte]]
13. [[Iteration der Ausmitte 2. Ordnung]]
14. [[Erfüllungsgrad]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein schlanker, gedrückter Stab biegt sich unter seiner Last aus. Die
Ausbiegung vergrössert den Hebelarm der Normalkraft, das Moment wächst, der
Stab krümmt sich mehr -- und so fort. Ob diese Folge zur Ruhe kommt, ist die
Frage des Knicknachweises: kommt sie zur Ruhe, gibt es eine
Gleichgewichtslage, und der Stab steht; wächst sie ohne Ende, knickt er.

Das Moment am verformten System setzt sich aus drei Ausmitten zusammen:

- der [[Ungewollte Ausmitte|ungewollten]], aus der unvermeidlichen
  [[Schiefstellung]] und Massabweichung;
- der [[Gewollte Ausmitte|gewollten]], aus dem Moment erster Ordnung;
- der Ausmitte zweiter Ordnung, aus der Krümmung des Stabs.

Die Krümmung kommt aus dem Querschnitt: zu jedem Moment die Dehnungsebene,
die es hält, mit dem Werkstoffgesetz, das das Kapitel für die Verformung
wählt. Gesucht wird schliesslich die grösste Druckkraft, unter der die
[[Iteration der Ausmitte 2. Ordnung]] noch einläuft; der Erfüllungsgrad ist
das Verhältnis dieser Kraft zur wirkenden. Den Widerstand des Querschnitts
dabei gibt eine Resistenzlinie, die das Kapitel ebenfalls wählt.
