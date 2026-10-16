---
erzeugt: 8866a91fa391
art: formel
tags: [formel]
normstelle: "Kap. 9.2.6"
---
> [!info] Normstelle
> Kap. 9.2.6

*In der Herleitung: «Tragfähigkeitsfaktor des Gleitkörpergewichts»*

$$
N_{\gamma} = 1.8 \cdot \left(N_q - 1\right) \cdot \tan \varphi_{eff}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_q$ | Tragfähigkeitsfaktor der seitlichen Auflast | – | [[Tragfähigkeitsfaktor N_q]] |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
N_{\gamma} = 1.8 \cdot \left(N_q - 1\right) \cdot \tan \varphi_{eff} = 1.8 \cdot \left(13.95 - 1\right) \cdot \tan 27.51{}^{\circ} = 12.14
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Anteil aus dem Gewicht des Gleitkörpers hat keine geschlossene Lösung;
die Formel ist eine Näherung an genauere Rechnungen, wie das Kapitel sie
angibt.

Bei kleinem $\varphi$ ist der Faktor klein, er wächst aber am schnellsten von
allen: bei grossen Reibungswinkeln und breiten Fundamenten trägt der
Gleitkörper den grössten Teil.
