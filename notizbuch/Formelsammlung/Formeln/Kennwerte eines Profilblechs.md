---
erzeugt: f61c56e6ce0b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Das Blech je Rippe: Steg, Abwicklung, Dicke und Schwerpunkt»*

$$
L_w = \sqrt{h_p^2 + \left(\frac{b_o - b_u}{2}\right)^2} \qquad s = b_s - b_o + 2\, L_w + b_u \qquad t = \frac{A_p\, b_s}{s} \qquad e = \frac{h_p\, (L_w + b_s - b_o)}{s}
$$

## Im Code

- [[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA._form|KennzahlenBlechQA._form]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Datenblatt nennt die Fläche $A_p$ des Blechs je Meter Breite, nicht
seine Dicke und nicht, wo es liegt. Das Werkzeug denkt sich das Blech je
Rippe als gleich dicken Linienzug:

- unten der Boden der Rippe, $b_u$ breit;
- zwei schräge Stege, je $L_w$ lang, über die Höhe $h_p$;
- oben der Gurt zwischen zwei Rippen, $b_s - b_o$ breit.

Abgewickelt ist das die Länge $s$. Die Fläche je Rippe, $A_p \cdot b_s$,
gleichmässig über sie verteilt, gibt die Dicke $t$. Der Schwerpunkt liegt um
$e$ über der Unterkante des Blechs: der Gurt zählt mit der ganzen Höhe
$h_p$, die Stege mit der halben, der Boden mit null.

Sicken, Ausrundungen und Überlappungen des wirklichen Blechs zählen nicht
– eine Vorgabe, nicht aus der Norm. Aus $e$ folgt die
[[Statische Höhe einer Blechverbunddecke|statische Höhe]].
