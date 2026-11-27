---
erzeugt: 0ce5ca3e4196
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.3.2, (22)"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.3.2, (22)

*In der Herleitung: «Bemessungssteifigkeit um y»*

$$
(EI)_{eff,d,y} = 0.9 \cdot \left(E_{a} \cdot I_{a,y} + 0.5 \cdot E_{c,eff} \cdot I_{c,y} + E_s \cdot I_{s,y}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{a}$ | Elastizitätsmodul des Baustahls | N/mm² | Vorgabe |
| $I_{a,y}$ | Trägheitsmoment von S355 um y | ·10⁶ mm⁴ | Zwischenwert |
| $E_{c,eff}$ | Wirksamer Elastizitätsmodul des Betons | N/mm² | [[Wirksamer Elastizitätsmodul des Betons einer Verbundstütze]] |
| $I_{c,y}$ | Trägheitsmoment von C30/37 um y | ·10⁶ mm⁴ | Zwischenwert |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $I_{s,y}$ | Trägheitsmoment von B500B um y | ·10⁶ mm⁴ | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  (EI)_{eff,d,y} &= 0.9 \cdot \left(E_{a,\text{S355}} \cdot I_{a,y} + 0.5 \cdot E_{c,eff} \cdot I_{c,y} + E_s \cdot I_{s,y}\right) \\
  &= 0.9 \cdot \left(210000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 251.8\,\cdot 10^{6}\,\mathrm{mm}^{4} + 0.5 \cdot 15282\,\mathrm{N}/\mathrm{mm}^{2} \cdot 4906.3\,\cdot 10^{6}\,\mathrm{mm}^{4} + 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 50.3\,\cdot 10^{6}\,\mathrm{mm}^{4}\right) \\
  &= 90.4\,\mathrm{MNm}^{2}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweite_ordnung|_Fall._zweite_ordnung]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Schnittgrössen nach Theorie 2. Ordnung zählt der Beton nur mit der
Hälfte seines wirksamen Moduls, und die Summe noch mit 0.9 (22). Sie ist
damit kleiner als die
[[Biegesteifigkeit einer Verbundstütze für die Schlankheit]], und das
Moment wächst mit ihr eher zu stark als zu schwach.

Daraus folgt die
[[Kritische Normalkraft einer Verbundstütze|kritische Normalkraft]] für
die Bemessung, N_cr,eff (23).
