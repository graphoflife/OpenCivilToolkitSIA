---
erzeugt: 07f9214debf6
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.4.2, Figur 11"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.4.2, Figur 11

*In der Herleitung: «Widerstand des waagrechten Gewölbes: ein Bogen mit drei Gelenken, an jedem über t\_w/2 mit f\_yd gedrückt»*

$$
p_{Rd,h} = 2 \cdot f_{yd} \cdot \frac{t_w^{2}}{L^{2}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yd}$ | Druckfestigkeit der Wand parallel zu den Lagerfugen | N/mm² | Zwischenwert |
| $t_w$ | Dicke der Wand | mm | Zwischenwert |
| $L$ | Spannweite des waagrechten Gewölbes | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
p_{Rd,h} = 2 \cdot f_{yd} \cdot \frac{t_w^{2}}{L^{2}} = 2 \cdot 1.36\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\left(175\,\mathrm{mm}\right)^{2}}{\left(2.4\,\mathrm{m}\right)^{2}} = 14.46\,\mathrm{kN}/\mathrm{m}^{2}
$$

## Gebraucht von

- [[Querlastwiderstand einer Wand aus Mauerwerk]]

## Im Code

- [[opencivil.mauerwerk.querlast#Querlastnachweis._waagrecht|Querlastnachweis._waagrecht]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Zwischen zwei gehaltenen Rändern kann die Wand Querlast als waagrechter
Bogen tragen (SIA 266:2015, 4.3.4.2, Figur 11): Er drückt an den Rändern
nahe der einen Seite der Wand und in der Mitte nahe der anderen. Seine
Druckkraft $H$ hält der Querlast das Gleichgewicht, weil sie auf dem Weg
vom Rand zur Mitte die Wand quer durchläuft.

Das Werkzeug nimmt einen Bogen mit drei Gelenken an, an beiden Rändern und
in der Mitte, und an jedem eine Druckzone der halben Dicke mit $f_{yd}$:
$H = f_{yd}\, t_w/2$ je Meter Höhe. Die Mitten der Druckzonen liegen
$t_w/4$ unter der Oberfläche, der Hebelarm zwischen Rand und Mitte ist
also $t_w/2$. Das Gleichgewicht in der Mitte,
$p\, L^2/8 = H \cdot t_w/2 = f_{yd}\, t_w^2/4$, gibt
$p_{Rd,h} = 2\, f_{yd}\, t_w^2/L^2$ – nach Vorgabe, nicht nachgeschlagen.

Der Bogen drückt parallel zu den Lagerfugen, darum $f_{yd}$ (4.2.1.1,
Tabelle 7), und er läuft durch die Stossfugen: Sie müssen vollfugig
vermörtelt sein (4.3.4.3), sonst zählt er nicht. Öffnungen unterbrechen
ihn; mit ihnen zählt er nicht – nach Vorgabe. Die Effekte 2. Ordnung –
der Bogen flacht sich unter der Last ab, sein Hebelarm schrumpft – lässt
er weg. Das darf er nur, wo Gl. (19) und (20) mit $L$ gelten, siehe
[[Durchbiegung einer Wand als waagrechter Streifen]]. Dass die Ränder $H$
aufnehmen und weiterleiten (4.3.4.5), prüft das Werkzeug nicht.

Beispiel: Kalksandstein MK im Verband, vollfugig vermauert:
$f_{yd}$ = 0.85 · 1.6 = 1.36 N/mm². Mit $t_w$ = 175 mm und $L$ = 2.4 m
trägt der Bogen 2 · 1.36 · 175²/2400² N/mm² = 14.46 kN/m².
