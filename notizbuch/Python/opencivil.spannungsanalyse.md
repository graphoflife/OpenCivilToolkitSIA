---
erzeugt: 177da6fe6477
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/__init__.py
> den Querschnitt ansehen, ohne ihn nachzuweisen.
> Paket [[opencivil]] · [Quelltext](../../opencivil/spannungsanalyse/__init__.py)

## VERANTWORTUNG

Sechs Auswertungen am selben Faserintegral, das auch die Nachweise benutzen:

1. **Aus Schnittgroessen** -- `N` und `M` hinein, Dehnungsebene und
   Spannungsverteilung heraus.
2. **Aus Dehnungen** -- Randdehnungen hinein, Spannungen und Schnittgroessen
   heraus. Die Umkehrung von 1, und ohne Suche: die Ebene steht ja schon da.
3. **Momenten-Kruemmungs-Linie** -- eine Normalkraft hinein, der Verlauf
   `M(chi)` von null bis zum Bruch heraus.
4. **Normalkraft-Dehnungs-Linie** -- ein Moment hinein, der Verlauf
   `N(eps_m)` von null bis zum Bruch auf Zug heraus.
5. **Aequivalenter E-Modul ueber dem Moment** -- die Linie aus 3,
   umgerechnet in den Modul, den ein reiner, ungerissener, elastischer
   Betonquerschnitt braeuchte, um sich gleich stark zu kruemmen.
6. **Aequivalenter E-Modul ueber der Normalkraft** -- dasselbe aus der
   Linie in 4, fuer die Dehnung.


## KEIN NACHWEIS

Hier wird nichts gegen etwas gehalten. Es gibt keinen Erfuellungsgrad und kein
Urteil -- das ist der Unterschied zu allem anderen in diesem Werkzeug und der
Grund, warum die Auswertungen nicht im [[opencivil.core.rechenwerk#Rechenwerk|Rechenwerk]] stehen. Sie
beantworten eine Frage, die man beim Entwerfen stellt: *was passiert
eigentlich im Querschnitt?*


## JE ANALYSE GEWAEHLT

Jede Analyse ([[opencivil.projekt.eintraege#SpannungsfallEintrag|SpannungsfallEintrag]]) waehlt als
[[opencivil.querschnitt.gesetzwahl#Rechenwahl|Rechenwahl]]

* die Kriechzahl;
* der Wertesatz -- Bemessung (`f_cd`, `f_yd`) oder charakteristisch
  (`f_ck`, `f_yk`), siehe [[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]];
* die Rechenart -- die 0.85·x-Vereinfachung oder praezise ohne Vereinfachung,
  die Parabel mit `E_c,eff`. Die Handrechnung gibt es hier nicht
  ([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]): eine Linie rechnet die
  Normalkraft Ebene fuer Ebene genau, ein Polygon aus Eckpunkten haette dort
  nichts zu suchen.

Moduln und Grenzdehnungen sind in beiden Wertesaetzen dieselben, wie ueberall
im Werkzeug.


## DIE BEIDEN LINIEN

Unter dem Riss ist der Querschnitt ungerissen (Zustand I) und deutlich
steifer, als die Nachweise ihn rechnen -- dort wird der Beton auf Zug
grundsaetzlich nicht angesetzt. Beim Riss springt die Verformung bei
derselben Kraft vom ungerissenen auf den gerissenen Wert (Zustand II), im
Bild ein waagrechtes Stueck. Darueber gilt Zustand II bis zum Bruch. Beide
Zustaende rechnet derselbe Loeser, nur mit verschiedenem Betongesetz.

Die Zugfestigkeit des Betons zaehlt nur bis zum Riss: der ungerissene
Zustand steht zum Vergleich darum nur bis `M_Riss` bzw. `N_Riss` da,
nicht darueber hinaus -- dort haette der Beton Zug ohne Grenze (Benutzer,
2026-10-12). Der gerissene Zustand steht zum Vergleich auf der ganzen Linie.


## DIE NAMEN AN DER LINIE

Ihr Ende heisst `M_Rd` bzw. `N_Rd` (`R_k` mit charakteristischen
Werten), wie der Widerstand der Tragsicherheit: bei derselben Rechenwahl ist
es dieselbe Zahl, bis auf die Schranke der Suche. Der Fliessbeginn heisst
`M_y` bzw. `N_y`, wie seine Kruemmung `chi_y`. Bis 2026-10-12 hiess er
`M_Rd` und das Ende `M_Rd,u` -- und wer im Bild nach dem Widerstand
suchte, fand den Fliessbeginn.

Den gerissenen Teil rechnet die Linie ueber die Verformung -- die Kruemmung
bzw. die Dehnung --, nicht ueber die Kraft. Nach dem Fliessen waechst die
Kraft kaum noch, die Verformung aber stark; ueber die Kraft gerechnet laegen
dort kaum Punkte, und die Suche nach einer Ebene zu einer Kraft nahe am
Widerstand ist die heikelste ueberhaupt.


## DAS ENDE

Die Linie endet bei der groessten Verformung, zu der es noch ein
Gleichgewicht gibt. Dort ist die erste Grenzdehnung erreicht: der Beton am
gedrueckten Rand bei `-eps_c2d`, der Stahl einer Lage bei `eps_ud`, der
ganz gedrueckte Querschnitt im Punkt C bei `-eps_c1d`. Dieselben Grenzen
wie im Dehnungsfaecher der genauen M-N-Linie
([[opencivil.nachweis.dehnungsfaecher]]). Bis 2026-10-09 endete die M-chi-
Linie stattdessen dort, wo die Suche des Loesers aufgab -- an der Platte des
Beispiels bei chi = 0.040 1/m statt 0.057 1/m, und `eps_ud` galt am
Betonrand statt am Stahl.

Gezeigt wird der Querschnitt, nicht das Bauteil: die Mitwirkung des Betons
zwischen den Rissen (Zugversteifung) steckt nicht darin. Mit welcher Regel
eine Linie des Bauteils zu rechnen waere, ist offen
(`notizbuch/Notizen/TODO.md`).


## PLATTE UND GEZEICHNETER QUERSCHNITT

Die Fragen selbst -- Bild, Linie, Modul -- kennen nur einen
[[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]] und ein Paar
daraus: gerissen und ungerissen, dazu Riss, Bezugsflaeche des Moduls und
Rechenwahl ([[opencivil.spannungsanalyse.linie#Paar|Paar]]). Die Platte
bietet es je Tragrichtung, der gezeichnete Querschnitt je Zugseite, und
eine Schleife stellt die Fragen beiden.


## DIE TEILE

* [[opencivil.spannungsanalyse.art|art]] -- welche Frage gestellt wird;
* [[opencivil.spannungsanalyse.bild|bild]] -- das Bild aus Schnittgroessen
  oder Dehnungen;
* [[opencivil.spannungsanalyse.linie|linie]] -- die beiden Linien und das
  Paar, an dem sie laufen;
* [[opencivil.spannungsanalyse.modul|modul]] -- der aequivalente Modul;
* [[opencivil.spannungsanalyse.herleitung|herleitung]] -- wie eine Linie entstand;
* [[opencivil.spannungsanalyse.platte|platte]] und
  [[opencivil.spannungsanalyse.schnitt|schnitt]] -- die Paare;
* [[opencivil.spannungsanalyse.analysen|analysen]] -- alles zusammen, je Bauteil.

Bis 2026-10-17 war das ein Modul von 1300 Zeilen, und das Paar des
gezeichneten Querschnitts stand im Querschnitt, auf diesem Modul gebaut.

## Module

- [[opencivil.spannungsanalyse.analysen]] – die Analysen eines Projekts.
- [[opencivil.spannungsanalyse.art]] – welche der sechs Fragen eine Analyse stellt.
- [[opencivil.spannungsanalyse.bild]] – das Bild eines Querschnitts.
- [[opencivil.spannungsanalyse.herleitung]] – wie eine Linie entstand.
- [[opencivil.spannungsanalyse.linie]] – die Linien eines Querschnitts.
- [[opencivil.spannungsanalyse.modul]] – der aequivalente E-Modul.
- [[opencivil.spannungsanalyse.platte]] – das Paar einer Platte.
- [[opencivil.spannungsanalyse.schnitt]] – das Paar eines gezeichneten Querschnitts.

## Braucht

- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.art]]
- [[opencivil.spannungsanalyse.bild]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]

## Gebraucht von

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.ergebnis]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.web.api]]
- [[opencivil.web.diagrammdaten]]
