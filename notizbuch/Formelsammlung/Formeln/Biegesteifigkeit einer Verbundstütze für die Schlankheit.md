---
erzeugt: f03125921e4c
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.2.8, (17)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.2.8, (17)

*In der Herleitung: «Biegesteifigkeit um z, für die Schlankheit»*

$$
(EI)_{eff,\lambda,z} = E_{a} \cdot I_{a,z} + 0.6 \cdot E_{c,eff} \cdot I_{c,z} + E_s \cdot I_{s,z}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{a}$ | Elastizitätsmodul des Baustahls | N/mm² | Vorgabe |
| $I_{a,z}$ | Trägheitsmoment von S355 um z | ·10⁶ mm⁴ | Zwischenwert |
| $E_{c,eff}$ | Wirksamer Elastizitätsmodul des Betons | N/mm² | [[Wirksamer Elastizitätsmodul des Betons einer Verbundstütze]] |
| $I_{c,z}$ | Trägheitsmoment von C30/37 um z | ·10⁶ mm⁴ | Zwischenwert |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $I_{s,z}$ | Trägheitsmoment von B500B um z | ·10⁶ mm⁴ | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  (EI)_{eff,\lambda,z} &= E_{a,\text{S355}} \cdot I_{a,z} + 0.6 \cdot E_{c,eff} \cdot I_{c,z} + E_s \cdot I_{s,z} \\
  &= 210000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 85.6\,\cdot 10^{6}\,\mathrm{mm}^{4} + 0.6 \cdot 15282\,\mathrm{N}/\mathrm{mm}^{2} \cdot 5072.4\,\cdot 10^{6}\,\mathrm{mm}^{4} + 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 50.3\,\cdot 10^{6}\,\mathrm{mm}^{4} \\
  &= 74.6\,\mathrm{MNm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Kritische Normalkraft einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall|_Fall._knicken]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Schlankheit zählen Profil und Betonstahl mit ihrer ganzen
Steifigkeit, der Beton nur mit 0.6 seines wirksamen Moduls (17). Sein
Trägheitsmoment gilt für den ganzen, ungerissenen Beton; der Faktor nimmt
die Risse vorweg. Die Trägheitsmomente gelten je Werkstoff um die Mitte des
Profils, bei einer doppelsymmetrischen Stütze ihr Schwerpunkt; der Beton
ohne die Fläche, die Profil und Stäbe einnehmen. Liegt der Betonstahl über
6 % der Betonfläche, zählt er auch hier nur mit seinem Anteil – 5.3.2.2
sagt das für den Widerstand, für die Steifigkeit ist es nach Vorgabe, im
[[TODO]].

Daraus folgt [[Kritische Normalkraft einer Verbundstütze]].
