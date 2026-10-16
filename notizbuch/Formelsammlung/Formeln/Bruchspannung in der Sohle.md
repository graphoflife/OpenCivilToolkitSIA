---
erzeugt: 6f0f100e0d46
art: formel
tags: [formel]
normstelle: ["Kap. 9.2.10", "Kap. 9.2.17"]
---
> [!info] Normstellen
> Kap. 9.2.10 · Kap. 9.2.17

*In der Herleitung: «Bruchspannung in der Sohle»*

$$
\sigma_f = c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma}
$$

*In der Herleitung: «Bruchspannung in der Sohle, undrainiert»*

$$
\sigma_f = 5.1 \cdot c_{eff} \cdot \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \sigma_{v,0}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $c_{eff}$ | Kohäsion, Bemessungswert | kPa | [[Bemessungswert der Kohäsion]] |
| $N_c$ | Tragfähigkeitsfaktor der Kohäsion | – | [[Tragfähigkeitsfaktor N_c]] |
| $s_c$ | Formfaktor der Kohäsion | – | [[Formfaktor s_c]] |
| $d_c$ | Tiefenfaktor der Kohäsion | – | [[Tiefenfaktor d_c]] |
| $i_c$ | Lastneigungsfaktor der Kohäsion | – | [[Lastneigungsfaktor i_c]] |
| $g_c$ | Geländeneigungsfaktor der Kohäsion | – | [[Geländeneigungsfaktor g_c]] |
| $b_c$ | Sohlneigungsfaktor der Kohäsion | – | [[Sohlneigungsfaktor b_c]] |
| $\sigma_{v,0}$ | Überlagerung auf Höhe der Sohle | kPa | [[Überlagerung auf Höhe der Sohle]] |
| $N_q$ | Tragfähigkeitsfaktor der seitlichen Auflast | – | [[Tragfähigkeitsfaktor N_q]] |
| $s_q$ | Formfaktor der seitlichen Auflast | – | [[Formfaktor s_q]] |
| $d_q$ | Tiefenfaktor der seitlichen Auflast | – | [[Tiefenfaktor d_q]] |
| $i_q$ | Lastneigungsfaktor der seitlichen Auflast | – | [[Lastneigungsfaktor i_q]] |
| $g_q$ | Geländeneigungsfaktor der Auflast und des Gleitkörpers | – | [[Geländeneigungsfaktor g_q]] |
| $b_q$ | Sohlneigungsfaktor der seitlichen Auflast | – | [[Sohlneigungsfaktor b_q]] |
| $\gamma_G$ | Raumlast im Gleitkörper | kN/m³ | [[Raumlast im Gleitkörper]] |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $N_{\gamma}$ | Tragfähigkeitsfaktor des Gleitkörpergewichts | – | [[Tragfähigkeitsfaktor N_γ]] |
| $s_{\gamma}$ | Formfaktor des Gleitkörpergewichts | – | [[Formfaktor s_γ]] |
| $i_{\gamma}$ | Lastneigungsfaktor des Gleitkörpergewichts | – | [[Lastneigungsfaktor i_γ]] |
| $b_{\gamma}$ | Sohlneigungsfaktor des Gleitkörpergewichts | – | [[Sohlneigungsfaktor b_γ]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  \sigma_f &= c_{eff} \cdot N_c \cdot s_c \cdot d_c \cdot i_c \cdot g_c \cdot b_c + \sigma_{v,0} \cdot N_q \cdot s_q \cdot d_q \cdot i_q \cdot g_q \cdot b_q + \tfrac{1}{2} \cdot \gamma_G \cdot b \cdot N_{\gamma} \cdot s_{\gamma} \cdot 1 \cdot i_{\gamma} \cdot g_q \cdot b_{\gamma} \\
  &= 0\,\mathrm{kPa} \cdot 24.86 \cdot 1.45 \cdot 1.22 \cdot 0.76 \cdot 1 \cdot 1 + 25.2\,\mathrm{kPa} \cdot 13.95 \cdot 1.42 \cdot 1.16 \cdot 0.77 \cdot 1 \cdot 1 + \tfrac{1}{2} \cdot 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 2\,\mathrm{m} \cdot 12.14 \cdot 0.68 \cdot 1 \cdot 0.7 \cdot 1 \cdot 1 \\
  &= 568.8\,\mathrm{kPa}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sigma_f &= 5.1 \cdot c_{eff} \cdot \left(1 + s_c + d_c - i_c - b_c - g_c\right) + \sigma_{v,0} \\
  &= 5.1 \cdot 26.7\,\mathrm{kPa} \cdot \left(1 + 0.15 + 0.21 - 0.15 - 0.03 - 0.07\right) + 16.8\,\mathrm{kPa} \\
  &= 169.3\,\mathrm{kPa}
\end{aligned}
$$

## Gebraucht von

- [[Grundbruchwiderstand]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainierter_fall]]
- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._undrainierter_fall]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die mittlere Spannung in der Sohle, bei der der Boden bricht: die Summe der
drei Anteile der [[Erweiterte Tragfähigkeitsformel|Tragfähigkeitsformel]],
jeder mit seinen Beiwerten. Undrainiert ist es $5.1\,s_u$ mal die Klammer
der Korrekturen, dazu die totale Überlagerung.

Die Spannung gilt gleichmässig über die ganze Sohle $b \cdot L$; die Last
steht mittig, eine Ausmitte kennt die Eingabe nicht.
