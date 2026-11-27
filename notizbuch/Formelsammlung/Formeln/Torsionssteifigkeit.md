---
erzeugt: 942345daf0e4
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Torsionssteifigkeit, «Balken 300×500» aus C30/37»*

$$
GI_{T} = G_{cm} \cdot I_{T}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $G_{cm}$ | Mittelwert des Schubmoduls | N/mm² | [[Mittelwert des Schubmoduls]] |
| $I_{T}$ | Torsionsträgheitsmoment, Balken 300×500 | ·10⁶ mm⁴ | [[Torsionsträgheitsmoment eines Rechtecks]], [[Torsionsträgheitsmoment eines I-Profils]], Eingabe, Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
GI_{T,\text{Q1,C30/37}} = G_{cm} \cdot I_{T,\text{Q1}} = 14008\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2817.37\,\cdot 10^{6}\,\mathrm{mm}^{4} = 39466\,\mathrm{kNm}^{2}
$$

## Im Code

- [[opencivil.stabwerk.rechnung#_modul_mal_kennwert|_modul_mal_kennwert]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich ein Stab gegen Verdrillen wehrt: $T = GI_T \cdot \theta_x'$,
mit der Verdrillung $\theta_x'$ je Länge. In der Steifigkeitsmatrix
verhält sie sich wie die [[Dehnsteifigkeit]], mit $GI_T/L$ statt $EA/L$.

Der Schubmodul ist der des Materials, beim Beton der
[[Mittelwert des Schubmoduls]]. Beim Stahlbeton gilt die Steifigkeit für den
ungerissenen Querschnitt; reisst er unter Torsion, fällt sie stark ab. In
einem unbestimmten System trägt dann die Biegung der Nachbarstäbe mehr –
wie viel, hängt an diesem Verhältnis. Offen in [[TODO]].
