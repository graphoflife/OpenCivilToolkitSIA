---
erzeugt: af30b9679cd4
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.4.1, (13); Figur 8"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.4.1, (13); Figur 8

$$
V_{Rd} = \frac{0.9 \sqrt{\tau_{cr}\, \tau_y}\, b\, t}{\gamma_{M1}} \le \frac{\tau_y\, b\, t}{\gamma_{M1}} \qquad \tau_{cr} = k_\tau\, 0.9\, E \left(\frac{t}{b}\right)^2 \qquad k_\tau = 5.34
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_kennzahlen#querkraft|querkraft]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein schlanker Steg beult unter Schub schräg aus. $\tau_{cr}$ ist die
Schubspannung, bei der ein ideales Blech beult; sie wächst mit $(t/b)^2$.
Der Beulwert $k_\tau = 5.34$ gilt für ein langes Feld, also ohne
Quersteifen – wo welche stehen, weiss das Werkzeug nicht (nach Vorgabe,
nicht nachgeschlagen).

Der Widerstand liegt zwischen Beulen und Fliessen:
$0.9 \sqrt{\tau_{cr}\, \tau_y}$, höchstens $\tau_y$. Bei einem sehr
schlanken Steg ist das mehr als $\tau_{cr}$ – das Blech trägt nach dem
Beulen weiter.

Das Werkzeug wendet es an:

- beim I und U, wenn der Steg [[Steg ohne Schubbeulen]] nicht einhält, mit
  $b\, t = (h - t_f)\, t_w$;
- beim Rechteckrohr immer, je Wand.

Flansche und Rundrohre beulen hier nicht: gewalzte sind dafür zu gedrungen
(nach Vorgabe, nicht nachgeschlagen).
