---
erzeugt: 5679b265beea
art: formel
tags: [formel]
normstelle: "Kap. 9.2.6"
---
> [!info] Normstelle
> Kap. 9.2.6

*In der Herleitung: «Tragfähigkeitsfaktor der Kohäsion»*

$$
N_c = \frac{N_q - 1}{\tan \varphi_{eff}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_q$ | Tragfähigkeitsfaktor der seitlichen Auflast | – | [[Tragfähigkeitsfaktor N_q]] |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
N_c = \frac{N_q - 1}{\tan \varphi_{eff}} = \frac{13.95 - 1}{\tan 27.51{}^{\circ}} = 24.86
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]
- [[Formfaktor s_c]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Faktor der Kohäsion folgt aus [[Tragfähigkeitsfaktor N_q|N_q]]: ein Boden
mit Kohäsion $c$ verhält sich wie ein kohäsionsloser unter einem allseitigen
Druck $c \cot\varphi$ (Satz von Caquot). Daraus wird
$N_c = (N_q - 1)\cot\varphi$.

Für $\varphi \to 0$ strebt er gegen $\pi + 2 = 5.14$ -- daher der Beiwert
5.1 der [[Tragfähigkeitsformel undrainiert|undrainierten Formel]].
