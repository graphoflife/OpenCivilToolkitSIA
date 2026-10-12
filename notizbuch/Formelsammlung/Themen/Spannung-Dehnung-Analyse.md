---
erzeugt: 2656318104c9
art: thema
tags: [thema]
---
> [!abstract] Platte
> 17 Formeln, in der Folge, in der gerechnet wird.

## Was die Rechnung dazu sagt

Eine Spannung-Dehnung-Analyse hält nichts gegen etwas: sie zeigt, was der Querschnitt tut. Gerechnet wird mit dem Faserintegral der Nachweise und mit der Kriechzahl, dem Wertesatz und der Rechenart, die die Analyse wählt.

Ungerissen (Zustand I) trägt der Beton Druck und Zug, linear mit E\_c,eff und ohne Grenze: gebraucht wird hier die Steifigkeit, und wo der Querschnitt reisst, sagt die Rissbedingung am Bruttoquerschnitt. Gerissen (Zustand II) trägt er keinen Zug mehr, und im Druck gilt das Gesetz der gewählten Rechenart.

Unter 1 rechnet die Parabel k\_σ nicht: dort hätte ihr Nenner im ansteigenden Ast eine Nullstelle. So weit kommt es mit dem kriechweichen Modul und charakteristischen Werten; mit k\_σ = 1 ist der Beton bis f\_c bei ε\_c1d linear.

Am Bruttoquerschnitt reisst der Rand, wenn N/A + M/W = f\_ct,eff. Mit A = b·h und W = b·h²/6 hebt Druck das Rissmoment, Zug senkt es. Beim Rissmoment springt die Krümmung bei demselben Moment vom ungerissenen auf den gerissenen Wert.

Der Fliessbeginn ist der Punkt, an dem die am stärksten gezogene Lage die Fliessdehnung erreicht. Danach wächst die Kraft nur noch wenig: die Druckzone wird kleiner, der Hebelarm grösser, und der Beton füllt sein Gesetz, bis eine Grenzdehnung erreicht ist. Im Bild heisst die Kraft beim Fliessbeginn M\_Rd bzw. N\_Rd, am Ende M\_Rd,u bzw. N\_Rd,u; mit charakteristischen Werten Rk statt Rd.

Den gerissenen Teil rechnet die Linie über die Verformung, nicht über die Kraft: zu jeder Krümmung (bei der N-ε-Linie: zu jeder Dehnung) wird die Ebene gesucht, die die festgehaltene Grösse trägt. Sie endet bei der grössten Verformung, zu der es noch ein Gleichgewicht gibt – dort ist die erste Grenzdehnung erreicht. Es sind dieselben Grenzen wie im Dehnungsfächer der genauen M-N-Linie.

Der Spannungsblock ist ein Modell für den Bruch: unter (1 − 0.85)·ε\_c2d trägt der Beton darin nichts. Über dem Riss ist die Linie mit ihm darum weicher als der Querschnitt; ihr Ende ist der Widerstand mit dem Block.

Dieselbe Rissbedingung, nach der Normalkraft aufgelöst: beim Moment M reisst der Querschnitt, wenn die Zugkraft N\_Riss erreicht. Unter Zug reisst die ganze Dicke, darum gilt k\_t für t = h und nicht für h/3 wie beim Rissmoment. Bei N\_Riss springt die Dehnung bei derselben Kraft vom ungerissenen auf den gerissenen Wert.

Der äquivalente E-Modul ist der Modul, den ein reiner Betonquerschnitt bräuchte – ungerissen, ohne Stahl, elastisch –, um sich unter der laufenden Kraft gleich stark zu verformen wie der bewehrte Querschnitt. Gezählt wird ab dem Zustand ohne laufende Kraft: was die festgehaltene Kraft allein verformt, kann ein solcher Querschnitt nicht abbilden. Ist sie null, ist es genau M = E·I·χ bzw. N = E·A·ε.

## Formeln

1. [[Wirksamer Elastizitätsmodul]]
2. [[Beton ungerissen, in Druck und Zug]]
3. [[Beiwert der Parabel, mit dem wirksamen Modul]]
4. [[Parabel-Rechteck-Beziehung des Betons]]
5. [[Rissmoment bei der Normalkraft]]
6. [[Fliessdehnung]]
7. [[Grenzdehnungen am Ende der Linie]]
8. [[Grösste Krümmung]]
9. [[Spannungsblock des Betons]]
10. [[Beiwert für die Dicke]]
11. [[Wirksame Zugfestigkeit]]
12. [[Rissnormalkraft beim Moment]]
13. [[Grösste Dehnung auf halber Höhe]]
14. [[Reiner Betonquerschnitt – Flächenmoment]]
15. [[Äquivalenter E-Modul über dem Moment]]
16. [[Reiner Betonquerschnitt – Fläche]]
17. [[Äquivalenter E-Modul über der Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Kein Nachweis, sondern ein Blick in den Querschnitt: wie er sich unter
wachsender Last verhält, von ungerissen bis zum Bruch. Die Linien zeigen das
Moment über der Krümmung ($M$–$\chi$) bei fester Normalkraft, oder die
Normalkraft über der Dehnung ($N$–$\varepsilon$) bei festem Moment.

Die Linie hat drei Abschnitte:

1. **Ungerissen** ist der Querschnitt steif: der Beton trägt Druck und Zug,
   linear (siehe [[Beton ungerissen, in Druck und Zug]]).
2. **Beim Riss** springt die Verformung bei derselben Kraft auf den
   gerissenen Wert (siehe [[Rissmoment bei der Normalkraft]],
   [[Rissnormalkraft beim Moment]]).
3. **Gerissen** trägt der Beton keinen Zug mehr; die Linie steigt flacher,
   knickt beim Fliessbeginn der Bewehrung ab (siehe [[Fliessdehnung]]) und
   endet, wo die erste Grenzdehnung erreicht ist
   (siehe [[Grenzdehnungen am Ende der Linie]]).

Dazu zeigt der äquivalente E-Modul, wie steif der Querschnitt in jedem
Zustand ist -- gemessen an einem reinen Betonquerschnitt (siehe
[[Äquivalenter E-Modul über dem Moment]]).
