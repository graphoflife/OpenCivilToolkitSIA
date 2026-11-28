---
erzeugt: 7a096cc40a7a
art: formel
tags: [formel]
normstelle: ["SIA 266:2015, 4.3.1.3, Gl. (11)", "SIA 266:2015, 4.3.3.1, Gl. (17)"]
---
> [!info] Normstellen
> SIA 266:2015, 4.3.1.3, Gl. (11) · SIA 266:2015, 4.3.3.1, Gl. (17)

*In der Herleitung: «Normalkraftwiderstand des Pfeilers»*

$$
N_{xRd} = k_N \cdot l_w \cdot t_w \cdot f_{xd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_N$ | Beiwert der Normalkraft nach Theorie 2. Ordnung | – | Zwischenwert |
| $l_w$ | Breite des Pfeilers | mm | Zwischenwert |
| $t_w$ | Dicke der Wand | mm | Zwischenwert |
| $f_{xd}$ | Druckfestigkeit der Wand | N/mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{xRd} = k_N \cdot l_w \cdot t_w \cdot f_{xd} = 0.771 \cdot 800\,\mathrm{mm} \cdot 175\,\mathrm{mm} \cdot 2.98\,\mathrm{N}/\mathrm{mm}^{2} = 321.3\,\mathrm{kN}
$$

## Im Code

- [[opencivil.mauerwerk.nachweise#Normalkraft.stelle|Normalkraft.stelle]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Pfeiler trägt höchstens seine Fläche mal $f_{xd}$ – wenn die Last mittig
steht und er nicht knickt. Ausmitte und Schlankheit mindern das um den
Beiwert $k_N \le 1$: das Verhältnis der grössten Normalkraft, unter der die
verformte Wand noch im Gleichgewicht steht und ihre Ausmitte nirgends die
Grenze überschreitet, zu $l_w t_w f_{xd}$ (4.3.1.3, Gl. (11)).

Figur 5 zeigt $k_N$ als Kurven über der Schlankheit für einige Ausmitten.
Das Werkzeug rechnet ihn für die Ausmitten und Ränder jedes Pfeilers selbst,
nach Figur 3 und 4. Die Normalkraft steht dabei über die ganze Höhe mit
ihrem Wert am Fuss, das Eigengewicht des Pfeilers zählt also auch oben –
nach Vorgabe, nicht nachgeschlagen. Die Kurve für $e/t = 0.35$ der Figur 5
liegt fast doppelt so hoch, wie Figur 3 und 4 es zulassen; offen in
[[TODO]].

Zieht ein Pfeiler, lässt sich der Nachweis nicht führen: unbewehrtes
Mauerwerk trägt keinen Zug (4.1.2).

Trägt der Pfeiler auch Schub und steht die Normalkraft quer zur Wand
ausmittig, gilt Gl. (17) statt Gl. (11): dieselbe Formel mit der
gedrückten Länge $l_2$ statt $l_w$ (4.3.3.1) – nur sie trägt. $k_N$ bleibt
derselbe, er hängt von Schlankheit, Ausmitten und Steifigkeit ab, nicht
von der Länge. Steht die Normalkraft mittig, prüft die Druckstrebe nach
Gl. (13) die gedrückte Länge, und Gl. (11) bleibt mit $l_w$.
