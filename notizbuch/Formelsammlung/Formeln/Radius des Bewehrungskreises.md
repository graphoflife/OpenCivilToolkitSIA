---
erzeugt: 5ba359109daa
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Radius des Kreises, auf dem die Längsstäbe liegen»*

$$
r_s = \frac{D}{2} - c - \varnothing_w - \frac{\varnothing_l}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |
| $c$ | Überdeckung der Wendel | mm | Vorgabe |
| $\varnothing_w$ | Durchmesser der Wendel | mm | Vorgabe |
| $\varnothing_l$ | Durchmesser der Längsstäbe | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
r_s = \frac{D}{2} - c - \varnothing_w - \frac{\varnothing_l}{2} = \frac{900\,\mathrm{mm}}{2} - 75\,\mathrm{mm} - 10\,\mathrm{mm} - \frac{20\,\mathrm{mm}}{2} = 355\,\mathrm{mm}
$$

## Im Code

- [[opencivil.pfahl.innen#InnererWiderstand|InnererWiderstand._bohrpfahl]]

## Themen

- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wo die Längsstäbe im Querschnitt liegen: von aussen die Überdeckung c bis zur
Wendel, die Wendel selbst, dann der halbe Stab bis zu seiner Mitte. Bei
D = 900, c = 75, ⌀_w = 10 und ⌀_l = 20 liegen die Mitten auf
r_s = 450 − 75 − 10 − 10 = 355 mm.

Für die Normalkraft allein spielt der Radius keine Rolle. Er zeigt, ob die
Stäbe Platz haben: auf dem Kreis darf keiner den nächsten berühren.
