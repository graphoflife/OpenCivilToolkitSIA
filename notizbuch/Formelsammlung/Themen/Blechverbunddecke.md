---
erzeugt: e875cbc78727
art: thema
tags: [thema]
---
> [!abstract] Querschnittsanalyse
> 12 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Je Lastfall der plastische Zustand bei N\_Ed, dessen Moment die Seite von M\_y,Ed zieht – wie im Verbundträger: Blech und Betonstahl ganz gezogen, der Beton nur gedrückt, mit 0.85 f\_cd über die ganze Druckzone. Bei negativem Moment zählt das Blech nicht. Die Normalkraft bleibt, das Moment wächst, bis der Widerstand erreicht ist.

Was die Blechverbunddecke aufnimmt, ohne Bezug auf einen Lastfall: die Widerstände gegen Zug, Druck und Biegung, plastisch wie im Verbundträger, gegen Querkraft und gegen den Längsschub zwischen Blech und Beton nach der m-k-Methode – alle über die ganze gezeichnete Breite b. Dazu die Schlankheit L/d\_p: bis 26 muss die Durchbiegung nicht gerechnet werden.

Je Lastfall die Querkraft V\_z,Ed über die ganze Breite der Decke, gegen ihren Querkraftwiderstand und gegen den Längsschubwiderstand zwischen Blech und Beton – beide aus den Kennzahlen.

## Formeln

1. [[Erfüllungsgrad bei fester Normalkraft – einachsig um y]]
2. [[Probe – Normalkraft]]
3. [[Probe – Moment um y]]
4. [[Erfüllungsgrad]]
5. [[Festigkeiten im Verbundquerschnitt]]
6. [[Kennwerte eines Profilblechs]]
7. [[Statische Höhe einer Blechverbunddecke]]
8. [[Rippenbreite einer Blechverbunddecke]]
9. [[Querkraftwiderstand einer Blechverbunddecke]]
10. [[Schublänge einer Blechverbunddecke]]
11. [[Längsschubwiderstand nach der m-k-Methode]]
12. [[Schlankheit einer Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Blechverbunddecke ist eine Betonplatte auf einem Profilblech: das
Blech ist beim Betonieren die Schalung und trägt danach als Zugbewehrung
mit. Im Werkzeug ist sie ein Element der Querschnittsanalyse mit ihrem
Beton und ihrem Blech: $n$ Rippen im Abstand $b_s$, die Rippe $h_p$ hoch,
oben $b_o$ und unten $b_u$ breit, die Fläche $A_p$ des Blechs je Meter aus
dem Datenblatt. Sie trägt in Richtung ihrer Rippen; gerechnet wird ein
Streifen der ganzen gezeichneten Breite $b = n \cdot b_s$.

Die Analyse weist nach:

- **Biegung und Normalkraft** plastisch wie der Verbundträger
  ([[Festigkeiten im Verbundquerschnitt]]): der Beton nur gedrückt, Blech
  und Betonstahl gezogen. Unter negativem Moment zählt das Blech nicht –
  über einer Stütze trägt nur Betonstahl in der Decke.
- **Querkraft** nach Gleichung (26), bis $d_p = 150$ mm.
- **Längsschub** zwischen Blech und Beton nach der m-k-Methode,
  Gleichung (28), mit $m$ und $k$ aus dem Datenblatt.
- **Schlankheit** $L/d_p$: bis 26 braucht es keine Rechnung der
  Durchbiegung.

Was das Werkzeug an der Decke nicht rechnet, nennt die Herleitung der
Kennzahlen: das Durchstanzen unter Einzellasten, die Endverankerung, den
Bauzustand, die Mindestbewehrung über den Stützen, die Schwingungen und
die Durchbiegung selbst.
