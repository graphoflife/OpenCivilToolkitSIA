---
erzeugt: 656b8c1e8ebe
art: thema
tags: [thema]
---
> [!abstract] Baustoffe
> 3 Formeln, in der Folge, in der gerechnet wird.

## Formeln

1. [[Dehnung beim Zugbruch in Faserrichtung]]
2. [[Stauchung an der Druckgrenze in Faserrichtung]]
3. [[Grenzstauchung des Holzes, elastisch-plastisch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Holz nach SIA 265:2012: Vollholz C16, C24 und C30 aus Nadelholz und D30
aus Buche oder Eiche (Tabelle 6), Brettschichtholz aus Nadelholz GL24k bis
GL36h (Tabelle 7). Die Norm nennt die Bemessungswerte selbst, für
Feuchteklasse 1 und ohne stossartige Einwirkung; der Beiwert
$\gamma_M/\eta_M$ – 1.7 für Vollholz, 1.5 für Brettschichtholz
(Tabelle 1) – steckt schon darin. Aus $f_{m,k}$ gerechnet kämen sie nicht
genau heraus, denn die Tabellen runden: bei D30 gäbe 30/1.7 = 17.6 statt
17 N/mm².

Für das Eigengewicht gilt die mittlere Raumlast nach SIA 261:2020,
Tabelle 28: Nadelholz, auch verleimtes, 5 kN/m³, Laubholz 7.5 kN/m³. Mit
g = 10 m/s² sind das 500 und 750 kg/m³. Die Rohdichte $\rho_k$ der
Tabellen ist eine andere Zahl: das 5%-Fraktil, für die Verbindungen.

Holz rechnet linear bis zum Bruch, auf Zug bis $f_{t,0,d}$, auf Druck bis
$f_{c,0,d}$, beides in Faserrichtung und mit $E_{0,mean}$. Kann ein
Bauteil plastisch stauchen, darf der Druck elastisch-plastisch gehen: die
Spannung bleibt dann bei $f_{c,0,d}$ stehen, bis zur
[[Grenzstauchung des Holzes, elastisch-plastisch]].
