---
erzeugt: bfc24e8c7944
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
E_{eq} = \frac{M}{I_c \cdot \left(\chi - \chi_0\right)}
$$

## Im Code

- [[opencivil.spannungsanalyse.herleitung#_herleitung_modul|_herleitung_modul]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wer eine Platte mit einem Stabwerk- oder Plattenprogramm rechnet, gibt ihr
einen Querschnitt und einen Elastizitätsmodul. Der wirkliche Querschnitt aber
ist bewehrt, reisst und kriecht. Der äquivalente Modul ist der Wert, den ein
reiner, ungerissener, elastischer Betonquerschnitt bräuchte, um sich gleich
stark zu krümmen wie der wirkliche: $M = E_{eq} \cdot I_c \cdot (\chi -
\chi_0)$.

Gezählt wird ab dem Zustand ohne laufende Kraft: $\chi_0$ ist die Krümmung,
die die feste Normalkraft allein schon erzeugt. Ungerissen liegt $E_{eq}$
etwas über dem Modul des Betons, weil der Stahl mitträgt; nach dem Riss
fällt er stark.
