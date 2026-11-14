---
erzeugt: 73e35a98d4aa
art: formel
tags: [formel]
normstelle: "Stahlbeton II, 7.2 Platten, Folie 14"
---
> [!info] Normstelle
> Stahlbeton II, 7.2 Platten, Folie 14

*In der Herleitung: «Vom Streifen zur Platte: je Meter, in den Achsen x und y»*

$$
\begin{aligned} & m = \frac{M}{b} \qquad m_x = m \cdot \cos^2\varphi \qquad m_y = m \cdot \sin^2\varphi \qquad m_{xy} = m \cdot \sin\varphi \cdot \cos\varphi \\ & v = \frac{V}{b} \qquad v_x = v \cdot \cos\varphi \qquad v_y = v \cdot \sin\varphi \qquad v_0 = \sqrt{v_x^2 + v_y^2} \end{aligned}
$$

## Im Code

- [[opencivil.decke.herleitung#_ansaetze|_ansaetze]]

## Themen

- [[Streifenmethode]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Streifen der Breite $b$ trägt in seiner Richtung wie ein Balken, mit
dem Moment $M$ und der Querkraft $V$; je Meter Breite sind das $m = M/b$
und $v = V/b$. Liegt der Streifen unter dem Winkel $\varphi$ gegen x, biegt
er die Platte nur um seine eigene Querachse. In die Achsen x und y gedreht,
wird daraus $m_x$, $m_y$ und ein Drillmoment $m_{xy}$; die Querkraft
zerfällt in $v_x$ und $v_y$. $v_0$ ist ihr Betrag: die Querkraft in der
Richtung, in der sie am grössten ist.

An einer Stelle zählen alle Streifen über ihr zusammen: je Richtung der
Feldstreifen, in dem sie liegt, und jeder Unterzug, in dessen Fläche sie
liegt. Streifen in x geben nur $m_x$ und $v_x$, Streifen in y nur $m_y$
und $v_y$; ein Drillmoment gibt es erst mit schiefen Streifen.

Beispiel: ein Streifen unter $\varphi = 30°$ mit $m = 20\,\mathrm{kNm/m}$
gibt $m_x = 15$, $m_y = 5$ und $m_{xy} = 8.7\,\mathrm{kNm/m}$.

Momente sind positiv, wenn sie unten ziehen. Der Bericht nennt je Fall jeden
Träger mit seinem kleinsten und grössten Moment je Meter, die Bilder zeigen
$m_x$ bis $v_0$ über der ganzen Decke.
