---
erzeugt: 855a261679a5
art: formel
tags: [formel]
normstelle: "Kap. 9.2.18"
---
> [!info] Normstelle
> Kap. 9.2.18

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Ed}$ | Einwirkung normal zur Sohle | kN | Zwischenwert |
| $\delta^{*}$ | Reibungswinkel der Sohlfuge | ° | [[Reibungswinkel der Sohlfuge]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
T_{Rd} = N_{Ed} \cdot \tan \delta^{*} = 1500\,\mathrm{kN} \cdot \tan 27.51{}^{\circ} = 781.1\,\mathrm{kN}
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Gleiten.pruefe|Gleiten.pruefe]]

## Themen

- [[Gleiten]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kraft $T$ in der Sohle muss durch Reibung aufgenommen werden, höchstens
$N \tan\delta^{*}$. Ein Erdwiderstand vor dem Fundament wird nicht
angesetzt: das Kapitel erlaubt ihn nur, wenn er dauernd vorhanden ist und
die Verschiebung, die er braucht, zulässig ist.

Statt des Sicherheitsfaktors $F_{\alpha}$ des Kapitels steckt die Sicherheit
im Bemessungswert $\varphi_{eff}$. Mit $\varphi = 0$ gibt die Reibung keinen
Widerstand.
