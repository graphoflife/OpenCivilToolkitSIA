---
erzeugt: d6fabf8ff17b
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.2"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.2

*In der Herleitung: «Zwängung auf Biegung, je Stab»*

$$
\max_i \frac{\sigma_{s,i}(M_{s,adm})}{\sigma_{s,adm,i}} = 1\qquad M_{s,adm} \ge M_{Riss}
$$

## Im Code

- [[opencivil.nachweis.qa_gebrauch#ZwaengungBiegungQA|ZwaengungBiegungQA._protokoll_ansatz]]

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine aufgezwungene Krümmung reisst den Querschnitt auf der gezogenen Seite,
und der Beton gibt sein Rissmoment ab. Die Bewehrung muss es übernehmen,
ohne über ihre zulässige Spannung zu kommen. Gesucht ist darum das Moment,
bei dem im gerissenen Querschnitt der erste gezogene Stab seine Grenze
erreicht – elastisch, ohne Normalkraft, mit dem wirksamen Modul
$E_{cm}/(1+\varphi)$ und mit der gedrückten Bewehrung. Solange alles linear
bleibt, wachsen die Spannungen mit dem Moment, und es folgt aus einem
Dreisatz. Die Platte rechnet es von Hand, $\sigma_{s,adm} \cdot A_s \cdot
(d - x/3)$, ohne die gedrückte Bewehrung; an einem Rechteck mit Stäben nur
unten treffen sich beide.
