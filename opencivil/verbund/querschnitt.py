"""
opencivil/verbund/querschnitt.py -- ein gezeichneter Querschnitt aus Baustahl und Beton.

VERANTWORTUNG:
Was die Nachweise eines Verbundquerschnitts nach SIA 264:2014 aus der
Zeichnung brauchen, ohne Rechenwerk und ohne Herleitung, in mm und N/mm²:

* den Stahl fuer sich (:class:`~opencivil.stahlbau.querschnitt.Stahlquerschnitt`):
  seine Bleche, die Querkraft seiner Profile;
* je Beton und je Betonstahl eine Gruppe dazu (:attr:`Verbundquerschnitt.gruppen`);
* den Querschnitt starr-plastisch (:meth:`Verbundquerschnitt.starr`), je
  Gruppe mit der Festigkeit, die die Nachweise waehlen
  (:mod:`opencivil.querschnitt.plastisch`);
* was 5.1.2.2 fuer ``β`` misst: die Hoehe quer zur Nulllinie und wie weit der
  gedrueckte Beton von ihr reicht;
* die Klasse jedes Blechs an einer plastischen Nulllinie
  (:meth:`Verbundquerschnitt.zustaende`).

DER BETON, DIE STAEBE:
Ein Polygon aus Beton zaehlt wie eines aus Stahl: +1, wo es liegt, -1 im
Elternteil, den es dort ersetzt (:func:`~opencivil.querschnitt.plastisch.stuecke`)
-- ein Profil im Beton nimmt ihn dort weg. Ein Stab ist ein Quadrat seiner
Flaeche um seine Mitte, eine verschmierte Linie ein Rechteck ihrer Flaeche
ueber ihre Laenge; beide verdraengen den Beton, in dem sie liegen, wie im
Stahlbeton. Liegt die Nulllinie in einem Stab, verteilt sich seine Kraft so
ueber das Quadrat -- nach Vorgabe, nicht nachgeschlagen.

DIE KLASSEN (4.2.2.1, Tabellen 2 und 3):
Gefragt wird nur, ob jedes Blech die Klasse 1 oder 2 haelt: plastisch
rechnet der Verbund nur dann, und elastisch nach 5.1.2.4 und 5.1.2.5
rechnet ihn das Werkzeug nicht. Ein Blech darueber hat hier die Klasse 3 --
sie heisst «über 2». Gemessen wird wie im Stahl (:mod:`opencivil.stahlbau.klasse`),
mit ``α`` an der plastischen Nulllinie des Verbunds.

KAMMERBETONIERT (4.2.2.1, Tabelle 3; 5.2.1.3):
Ein Flansch eines I-Profils gilt als kammerbetoniert, wenn Beton seine
Innenseite von der Ausrundung bis 0.4 b von der Mitte des Stegs deckt: so
breit muss der Beton nach dem Bild der Tabelle 3 mindestens sein,
``0.8 ≤ b_c/b``. Der Steg, wenn Beton ihn auf beiden Seiten zwischen den
Ausrundungen deckt. Geprueft wird an fuenf Punkten einen Millimeter neben
dem Blech, von einem Millimeter nach der Ausrundung bis einen Millimeter
vor dem Ende (nach Vorgabe, nicht nachgeschlagen). Breiterer Beton zaehlt
mit: eingebettet beult ein Blech nicht frueher (nach Vorgabe, nicht
nachgeschlagen).

Dann gelten fuer den Flansch die Grenzen der Tabelle 3, wo sie weiter sind
als die der SIA 263 mit ``α``. Ein Steg der Klasse 3 darf nach 5.2.1.3 wie
einer der Klasse 2 rechnen; seine Grenze der Klasse 3 haengt aber an der
elastischen Spannung, und die rechnet das Werkzeug im Verbund nicht. Es
nimmt darum die kleinste fuer jedes ``ψ``, 42ε bei reinem Druck (SIA 263,
Tabelle 5a), als Grenze der Klasse 2 -- auf der sicheren Seite, nach
Vorgabe, nicht nachgeschlagen. Dass der Steg mit dem Kammerbeton verduebelt
ist (5.2.1.2), nimmt es an. Dass die Duebel einen Druckflansch nach 4.2.2.3
in die Klasse 1 heben, prueft es nicht.
"""

from __future__ import annotations

import dataclasses
import math
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.analyse import Flaechenteil
from opencivil.querschnitt.bewehrungselemente import Bewehrungselement
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.plastisch import Linie, Starrplastisch, Stueck, stuecke
from opencivil.stahlbau import klasse as kl
from opencivil.stahlbau.querschnitt import Blechzustand, Gruppe, Stahlquerschnitt, Teil
from opencivil.stahlprofile import tabelle
from opencivil.stahlprofile.bleche import Blech, Halterung
from opencivil.stahlprofile.formen import I_PROFIL

#: Was der Kammerbeton je Blech erlaubt: die Grenzen ``c/t`` der Klassen 1 und 2, durch
#: ``ε``, und woher sie kommen -- siehe Dateikopf.
KAMMER = {Halterung.EINSEITIG: ((9.0, 14.0), "SIA 264, Tabelle 3"),
          Halterung.BEIDSEITIG: ((0.0, 42.0), "SIA 264, 5.2.1.3")}

#: Wie breit der Beton nach dem Bild der Tabelle 3 mindestens ist: ``b_c/b``.
BREITE_BETON = 0.8

#: Wie weit neben dem Flansch und an wie vielen Stellen geprueft wird, ob Beton ihn deckt.
NEBEN = 1.0
STELLEN = 5


def _quadrat(mitte: Punkt, seite: float) -> Tuple[Punkt, ...]:
    h = seite / 2.0
    y, z = mitte
    return ((y - h, z - h), (y + h, z - h), (y + h, z + h), (y - h, z + h))


def stahlflaechen(element: Bewehrungselement) -> List[Tuple[Tuple[Punkt, ...], Punkt]]:
    """
    Die Flaechen eines Bewehrungselements als Polygone, je mit dem Punkt, an
    dem es den Beton verdraengt -- siehe Dateikopf.
    """
    if element.verschmiert:
        (y_1, z_1), (y_2, z_2) = element.von, element.bis
        laenge = math.dist(element.von, element.bis)
        halb = element.flaeche / laenge / 2.0
        n = (-(z_2 - z_1) / laenge * halb, (y_2 - y_1) / laenge * halb)
        ecken = ((y_1 - n[0], z_1 - n[1]), (y_2 - n[0], z_2 - n[1]),
                 (y_2 + n[0], z_2 + n[1]), (y_1 + n[0], z_1 + n[1]))
        return [(ecken, ((y_1 + y_2) / 2.0, (z_1 + z_2) / 2.0))]
    seite = math.sqrt(math.pi) * element.durchmesser / 2.0
    return [(_quadrat(p, seite), p) for p in element.punkte]


class Verbundquerschnitt:
    """Die Polygone und Staebe eines Verbundquerschnitts -- siehe Dateikopf."""

    def __init__(self, flaechen: Sequence[Flaechenteil], eltern: Sequence[Optional[int]],
                 bewehrung: Sequence[Bewehrungselement] = ()) -> None:
        self.flaechen = tuple(flaechen)
        self.stahl = Stahlquerschnitt(flaechen, eltern)
        self.gruppen: List[Gruppe] = list(self.stahl.gruppen)
        """Erst die Gruppen des Stahls, dann je Beton und je Betonstahl eine."""

        self.namen: List[str] = [t.name for t in self.stahl.teile]
        """Je Teil sein Name: erst die des Stahls, dann die Polygone aus Beton, dann die Staebe."""

        gruppe_von: Dict[int, int] = {}
        teil_von: Dict[int, int] = {}
        for i, f in enumerate(flaechen):
            if f.stoff is not None and f.stoff.art is Baustoffart.BETON:
                gruppe_von[i] = self._gruppe(f.stoff)
                teil_von[i] = len(self.namen)
                self.namen.append(f.name)
        weitere = stuecke([f.punkte for f in flaechen], eltern, gruppe_von, teil_von)
        polygone = [f.punkte for f in flaechen]
        for element in bewehrung:
            g = self._gruppe(element.stahl)
            teil = len(self.namen)
            self.namen.append(element.name)
            for ecken, mitte in stahlflaechen(element):
                weitere.append(Stueck(g, 1.0, ecken, teil))
                beton = geo.innerstes(mitte, polygone)
                if beton in gruppe_von:
                    weitere.append(Stueck(gruppe_von[beton], -1.0, ecken, teil_von[beton]))
        self.weitere: Tuple[Stueck, ...] = tuple(weitere)
        """Was zum Stahl dazukommt: der Beton und die Bewehrung, die ihn verdraengt."""

    def _gruppe(self, stoff: Baustoff) -> int:
        gruppe = Gruppe(stoff, False)
        if gruppe not in self.gruppen:
            self.gruppen.append(gruppe)
        return self.gruppen.index(gruppe)

    def art(self, g: int) -> Baustoffart:
        return self.gruppen[g].stoff.art

    def gruppen_der(self, art: Baustoffart) -> List[int]:
        return [g for g in range(len(self.gruppen)) if self.art(g) is art]

    # -- Plastisch ---------------------------------------------------------------

    def stuecke(self, stahl: Optional[Stahlquerschnitt] = None) -> Tuple[Stueck, ...]:
        """Alle Stuecke -- mit ``stahl``, wo die Querkraft einen Teil des Stahls genommen hat."""
        return (*(stahl or self.stahl).stuecke, *self.weitere)

    def starr(self, zug: Sequence[float], druck: Sequence[float],
              stahl: Optional[Stahlquerschnitt] = None) -> Starrplastisch:
        """Der Querschnitt starr-plastisch, je Gruppe mit ``zug`` und ``druck``."""
        return Starrplastisch(self.stuecke(stahl), tuple(zug), tuple(druck))

    def flaechen_je_gruppe(self) -> List[float]:
        """Je Gruppe ihre Flaeche in mm² -- beim Beton ohne, was Stahl und Staebe verdraengen."""
        summe = [0.0] * len(self.gruppen)
        for s in self.stuecke():
            summe[s.gruppe] += s.gewicht * s.werte.A
        return summe

    # -- Was 5.1.2.2 misst ---------------------------------------------------------

    def hoehe(self, n: Tuple[float, float]) -> float:
        """Die Hoehe des Querschnitts quer zur Nulllinie mit der Einheitsnormalen ``n``, in mm."""
        werte = [n[0] * p[0] + n[1] * p[1] for f in self.flaechen if f.stoff is not None
                 for p in f.punkte]
        return max(werte) - min(werte)

    def druckzone_beton(self, linie: Linie) -> float:
        """
        Wie weit der gedrueckte Beton von der Nulllinie reicht, in mm --
        ``x_p`` in 5.1.2.2; null, wo kein Beton gedrueckt ist.
        """
        return max([0.0] + [-linie.d(p) for f in self.flaechen
                            if f.stoff is not None and f.stoff.art is Baustoffart.BETON
                            for p in f.punkte])

    # -- Klassen -------------------------------------------------------------------

    def zustaende(self, linie: Linie, eps: Sequence[float],
                  stahl: Optional[Stahlquerschnitt] = None) -> List[Blechzustand]:
        """
        Jedes Blech jedes Profils an der plastischen Nulllinie, mit ``ε`` je
        Gruppe des Stahls -- Klasse 1, 2 oder 3 fuer «über 2»; ein
        kammerbetoniertes Blech mit den Grenzen der SIA 264, wo sie weiter
        sind, und dann mit ihrer Stelle (siehe Dateikopf).
        """
        zustaende = []
        for z in (stahl or self.stahl).zustaende(linie, None, eps):
            if z.alpha > 0.0 and self.kammerbetoniert(z.teil, z.blech):
                (g_1, g_2), woher = KAMMER[z.blech.halterung]
                e = eps[z.teil.gruppe]
                g = z.grenzen.werte
                if g_1 * e > g[0] or g_2 * e > g[1]:
                    grenzen = kl.Grenzen((max(g[0], g_1 * e), max(g[1], g_2 * e), g[2]))
                    z = dataclasses.replace(z, grenzen=grenzen, tabelle=woher,
                                            klasse=grenzen.klasse(z.schlankheit))
            zustaende.append(z)
        return zustaende

    def freie_gedrueckt(self, linie: Linie) -> List[Teil]:
        """Die frei gezeichneten Flaechen aus Baustahl, die an der Nulllinie gedrueckt sind."""
        return self.stahl.freie_gedrueckt(linie, None)

    def kammerbetoniert(self, teil: Teil, blech: Blech) -> bool:
        """Ob Beton im I-Profil den Flansch innen, den Steg beidseits deckt -- siehe Dateikopf."""
        profil = teil.flaeche.profil
        if blech.halterung not in KAMMER or profil is None \
                or tabelle.profil(profil.name).form is not I_PROFIL:
            return False
        u = ((blech.bis[0] - blech.von[0]) / blech.b, (blech.bis[1] - blech.von[1]) / blech.b)
        n = (-u[1], u[0])
        von = blech.vor + NEBEN
        if blech.halterung is Halterung.BEIDSEITIG:
            seiten: Tuple[float, ...] = (1.0, -1.0)
            bis = blech.vor + blech.c - NEBEN
        else:
            # Die Innenseite zeigt zur Mitte des Profils; der Beton reicht bis kurz vor
            # 0.4 b von der Mitte des Stegs -- b des Blechs ist b/2.
            w = geo.flaechenwerte(teil.flaeche.punkte)
            innen = n[0] * (w.y_S - blech.von[0]) + n[1] * (w.z_S - blech.von[1]) > 0.0
            seiten = (1.0 if innen else -1.0,)
            bis = BREITE_BETON * blech.b - NEBEN
        bis = max(bis, von)
        polygone = [f.punkte for f in self.flaechen]
        for seite in seiten:
            abstand = seite * (blech.t / 2.0 + NEBEN)
            for k in range(STELLEN):
                p = blech.punkt(von + (bis - von) * k / (STELLEN - 1))
                i = geo.innerstes((p[0] + abstand * n[0], p[1] + abstand * n[1]), polygone)
                stoff = self.flaechen[i].stoff if i is not None else None
                if stoff is None or stoff.art is not Baustoffart.BETON:
                    return False
        return True
