---
erzeugt: b45190fd29df
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.4.6, (25)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.4.6, (25)

*In der Herleitung: «Widerstand um y nach (25)»*

$$
M_{y,Rd} = \alpha_M \cdot \mu_{d,y} \cdot M_{pl,y,Rd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\alpha_M$ | Grenze in (25) | – | Zwischenwert |
| $\mu_{d,y}$ | Beiwert der Interaktion | – | [[Beiwert μ_d einer Verbundstütze]] |
| $M_{pl,y,Rd}$ | Plastischer Biegewiderstand | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{y,Rd} = \alpha_M \cdot \mu_{d,y} \cdot M_{pl,y,Rd} = 0.9 \cdot 0.686 \cdot 863.9\,\mathrm{kNm} = 533.1\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._biegung|_Fall._biegung]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das [[Moment 2. Ordnung einer Verbundstütze|Moment nach Theorie 2. Ordnung]]
muss unter 0.9 μ_d M_pl,Rd bleiben (25), mit S420 und S460 unter 0.8. Der
Abschlag macht die einfache plastische Rechnung mit rechteckigen
Spannungsblöcken sicherer. Der Erfüllungsgrad ist dieser Widerstand durch
das Moment 2. Ordnung.
