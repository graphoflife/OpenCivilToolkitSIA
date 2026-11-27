---
erzeugt: e3e8e020fd60
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.2.9, (19)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.2.9, (19)

*In der Herleitung: «Wirksamer Elastizitätsmodul von C30/37, mit dem Kriechen»*

$$
E_{c,eff} = \frac{E_{cm}}{1 + N_{G,Ed}/N_{Ed} \cdot \varphi}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $N_{G,Ed}/N_{Ed}$ | Ständiger Anteil der Normalkraft | – | Zwischenwert |
| $\varphi$ | Kriechzahl | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
E_{c,eff} = \frac{E_{cm}}{1 + N_{G,Ed}/N_{Ed} \cdot \varphi} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1 + 0.6 \cdot 2} = 15282\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Bemessungssteifigkeit einer Verbundstütze]]
- [[Biegesteifigkeit einer Verbundstütze für die Schlankheit]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._kriechen|_Fall._kriechen]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unter Dauerlast kriecht der Beton: er verformt sich mit der Zeit weiter,
und die Stütze wird weicher. (19) nimmt das in den Elastizitätsmodul des
Betons auf. Nur der ständige Teil der Normalkraft kriecht, mit der
Kriechzahl φ(t,t₀); ohne ständigen Anteil oder mit φ = 0 bleibt
[[Mittelwert des Elastizitätsmoduls|E_cm]]. Die Kriechzahl gilt für die
ganze Analyse, den ständigen Anteil gibt jeder Fall.

Der kleinere Modul geht in beide Steifigkeiten der Stütze ein:
[[Biegesteifigkeit einer Verbundstütze für die Schlankheit]] und
[[Bemessungssteifigkeit einer Verbundstütze]].
