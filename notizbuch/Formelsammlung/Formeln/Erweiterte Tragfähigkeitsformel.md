---
erzeugt: 3ab712ede5ea
art: formel
tags: [formel]
normstelle: "Kap. 9.2.10"
---
> [!info] Normstelle
> Kap. 9.2.10

$$
\sigma_f = c \, N_c s_c d_c i_c g_c b_c + \sigma_{v,0} \, N_q s_q d_q i_q g_q b_q + \tfrac{1}{2} \gamma_G \, b \, N_{\gamma} s_{\gamma} d_{\gamma} i_{\gamma} g_{\gamma} b_{\gamma} \qquad N_{Rd} = \sigma_f \cdot b \cdot L
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Bruchlast eines Flachfundaments setzt sich aus drei Anteilen zusammen:
der Kohäsion entlang der Gleitfläche ($c\,N_c$), der seitlichen Auflast
neben dem Fundament, die den Gleitkörper niederhält ($\sigma_{v,0}\,N_q$),
und dem Eigengewicht des Gleitkörpers ($\tfrac{1}{2}\gamma_G\,b\,N_{\gamma}$).

Die Tragfähigkeitsfaktoren $N$ gelten für einen langen Streifen mit
lotrechter, mittiger Last auf waagrechtem Gelände. Die Beiwerte passen jeden
Anteil an das wirkliche Fundament an: $s$ an die Form, $d$ an die Tiefe, $i$
an die Lastneigung, $g$ an die Geländeneigung und $b$ an die Sohlneigung.

Die drei Anteile haben nicht genau dieselbe Gleitfläche. Sie einzeln zu
rechnen und zu addieren, liegt auf der sicheren Seite: die Summe der
kleinsten Anteile ist nie grösser als der kleinste Wert der Summe.
