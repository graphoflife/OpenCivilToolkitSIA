---
erzeugt: 83edf99df788
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.2.4, (14)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.2.4, (14)

*In der Herleitung: «Plastischer Normalkraftwiderstand, Teil für Teil»*

$$
N_{pl,Rd} = A_a\, f_{yd} + A_c\, 0.85\, f_{cd} + A_s\, f_{sd}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_kennzahlen#KennzahlenVerbundQA|KennzahlenVerbundQA._normalkraft]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ganz gedrückt trägt jeder Teil mit seiner Festigkeit: das Profil mit
$f_{yd}$, der Beton mit $0.85\, f_{cd}$, der Betonstahl mit $f_{sd}$ –
siehe [[Festigkeiten im Verbundquerschnitt]]. Die Summe ist der Widerstand
des Querschnitts nach (14). Er gilt nur, wenn jedes gedrückte Blech in
Klasse 1 oder 2 liegt; sonst steht er auf null, und ein Hinweis nennt das
Blech.

Ein ganz mit Beton gefülltes Rohr dürfte seinen Beton nach 5.3.2.5 mit 1.0
statt 0.85 rechnen; das gehört zu den Verbundstützen und rechnet das
Werkzeug noch nicht. Knicken gehört dem Stab und steht nicht hier.

Gezogen trägt der Beton nichts: der Zugwiderstand ist die Summe aus
Baustahl und Betonstahl allein.
