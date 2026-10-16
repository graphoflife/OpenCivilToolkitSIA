---
erzeugt: a1ec931c8e4f
art: formel
tags: [formel]
normstelle: "Kap. 9.2.6"
---
> [!info] Normstelle
> Kap. 9.2.6

*In der Herleitung: «Tragfähigkeitsfaktor der seitlichen Auflast»*

$$
N_q = e^{\pi \tan \varphi_{eff}} \cdot \tan^{2}\left(45^\circ + \frac{\varphi_{eff}}{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
N_q = e^{\pi \tan \varphi_{eff}} \cdot \tan^{2}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) = e^{\pi \tan 27.51{}^{\circ}} \cdot \tan^{2}\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right) = 13.95
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]
- [[Formfaktor s_c]]
- [[Lastneigungsfaktor i_c]]
- [[Tragfähigkeitsfaktor N_c]]
- [[Tragfähigkeitsfaktor N_γ]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark die Auflast neben dem Fundament den Bruch behindert. Der Faktor
kommt aus dem Bruchmechanismus nach Prandtl: unter der Sohle ein Keil,
daneben eine Zone, deren Gleitlinie eine logarithmische Spirale ist, aussen
ein zweiter Keil bis an die Oberfläche. Die Spirale vergrössert die Spannung
entlang ihres Weges um $e^{\pi \tan\varphi}$, die beiden Keile um
$\tan^2(45° + \varphi/2)$.

$N_q$ wächst darum sehr schnell mit $\varphi$: 6.4 bei 20°, 18.4 bei 30°,
33.3 bei 35°.
