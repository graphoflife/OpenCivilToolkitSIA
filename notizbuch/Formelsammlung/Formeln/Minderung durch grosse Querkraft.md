---
erzeugt: 5affbfbd69ef
art: formel
tags: [formel]
normstelle: ["SIA 263:2013, 5.1.5.1, (43); 5.1.7; 5.2.7; 5.3.6.1", "SIA 264:2014, 4.3.2.2; SIA 263:2013, 5.1.5.1, (43)"]
---
> [!info] Normstellen
> SIA 263:2013, 5.1.5.1, (43); 5.1.7; 5.2.7; 5.3.6.1 · SIA 264:2014, 4.3.2.2; SIA 263:2013, 5.1.5.1, (43)

*In der Herleitung: «Querkraft in z über der Hälfte von V\_Rd: was die Bleche, in denen sie steht, für Normalkraft und Biegung verlieren»*

$$
\rho_{z} = \left(\frac{V_{z,Ed}}{V_{z,Rd}}\right)^2
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_{z,Ed}$ | Querkraft, Betrag | kN | Zwischenwert |
| $V_{z,Rd}$ | Querkraftwiderstand | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\rho_{z} = \left(\frac{V_{z,Ed}}{V_{z,Rd}}\right)^2 = \left(\frac{900\,\mathrm{kN}}{1636.8\,\mathrm{kN}}\right)^2 = 0.302
$$

## Im Code

- [[opencivil.nachweis.qa_stahl#minderung|minderung]]

## Themen

- [[Stahlquerschnitt]]
- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Querkraft und Normalspannungen teilen sich die Fliessgrenze desselben
Blechs. Solange $V_{Ed}$ höchstens die Hälfte von $V_{Rd}$ ist, bleibt das
unberücksichtigt. Darüber zählen die Bleche, in denen die Querkraft steht –
beim I in Stegrichtung der Steg –, für Normalkraft und Biegung nur noch mit
$1 - \rho$; bei $V_{Ed} = V_{Rd}$ tragen sie dazu nichts mehr bei.

Das Werkzeug mindert so jedes Profil und jede Richtung, auch für die
Normalkraft und in den Klassen 3 und 4 (nach Vorgabe, nicht
nachgeschlagen). Plastisch liegt das auf der sicheren Seite: nach der
Vergleichsspannung bliebe dem Blech $\sqrt{1 - \rho}$ seiner Fliessgrenze,
mehr als $1 - \rho$.

Beispiel: ein IPE 600 aus S355 mit $V_{z,Ed} = 900\,\mathrm{kN}$ und
$V_{z,Rd} = 1636.8\,\mathrm{kN}$ gibt $\rho_z = 0.302$ – der Steg trägt für
Normalkraft und Biegung noch 70 %.
