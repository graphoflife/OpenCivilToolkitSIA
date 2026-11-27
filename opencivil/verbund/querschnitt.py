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
  (:mod:`opencivil.querschnitt.plastisch`) -- und in den zwei Teilen, die
  nur die Duebel verbinden (:meth:`Verbundquerschnitt.getrennt`, siehe
  unten);
* ob der Baustahl ein doppelsymmetrisches Profil ist -- fuer (29)
  (:attr:`Verbundquerschnitt.doppelsymmetrisch`) --, und auf welcher Seite
  des Baustahls der Beton liegt: zieht ein Moment diese Seite, liegt es im
  Bereich negativer Momente (:attr:`Verbundquerschnitt.zum_beton`);
* was 5.1.2.2 fuer ``β`` misst: die Hoehe quer zur Nulllinie und wie weit der
  gedrueckte Beton von ihr reicht;
* die Klasse jedes Blechs an einer plastischen Nulllinie
  (:meth:`Verbundquerschnitt.zustaende`).

DER BETON, DIE STAEBE:
Ein Polygon aus Beton zaehlt wie eines aus Stahl: +1, wo es liegt, -1 im
Elternteil, den es dort ersetzt (:func:`~opencivil.querschnitt.plastisch.stuecke`)
-- ein Profil im Beton nimmt ihn dort weg. Ein Stab ist ein Quadrat seiner
Flaeche um seine Mitte, eine verschmierte Linie ein Rechteck ihrer Flaeche
ueber ihre Laenge
(:meth:`~opencivil.querschnitt.bewehrungselemente.Bewehrungselement.stahlflaechen`);
beide verdraengen den Beton, in dem sie liegen, wie im Stahlbeton. Liegt
die Nulllinie in einem Stab, verteilt sich seine Kraft so ueber das Quadrat
-- nach Vorgabe, nicht nachgeschlagen. Das Profilblech einer
Blechverbunddecke liegt am Rand ihres Betons und verdraengt keinen.

WAS DIE DUEBEL VERBINDEN:
Die Kopfbolzenduebel sitzen in der Fuge zwischen dem Beton und dem Profil.
Auf der einen Seite liegen Beton und Betonstahl ausserhalb der Profile --
die Platte --, auf der anderen der Baustahl mit dem Beton und den Staeben in
seiner konvexen Huelle: Kammerbeton zaehlt zum Stahl, denn er ist mit dem
Steg verbunden (5.2.1.2), nicht ueber die Duebel der Fuge (nach Vorgabe,
nicht nachgeschlagen). Was in der Huelle liegt, schneidet das Werkzeug aus
jedem Stueck aus (:func:`~opencivil.querschnitt.geometrie.in_huelle`): mit
umgekehrtem Gewicht auf der Seite des Betons, mit seinem eigenen auf der
des Stahls, dort mit dem Zusatz «in der Kammer» (:attr:`Verbundquerschnitt.fuge`).

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
from functools import cached_property
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
from opencivil.stahlprofile.formen import I_PROFIL, RECHTECKROHR_GERUNDET, RUNDROHR

#: Was der Kammerbeton je Blech erlaubt: die Grenzen ``c/t`` der Klassen 1 und 2, durch
#: ``ε``, und woher sie kommen -- siehe Dateikopf.
KAMMER = {Halterung.EINSEITIG: ((9.0, 14.0), "SIA 264, Tabelle 3"),
          Halterung.BEIDSEITIG: ((0.0, 42.0), "SIA 264, 5.2.1.3")}

#: Wie breit der Beton nach dem Bild der Tabelle 3 mindestens ist: ``b_c/b``.
BREITE_BETON = 0.8

#: Wie weit neben dem Flansch und an wie vielen Stellen geprueft wird, ob Beton ihn deckt.
NEBEN = 1.0
STELLEN = 5

#: Die Formen, deren Profile zwei Symmetrieachsen haben.
DOPPELSYMMETRISCH = (I_PROFIL, RECHTECKROHR_GERUNDET, RUNDROHR)

#: Wie ein Stueck heisst, das in der Huelle eines Profils liegt -- siehe Dateikopf.
IN_DER_KAMMER = "in der Kammer"

#: Wie weit die Schwerpunkte von Baustahl und Beton mindestens auseinander liegen, in mm,
#: damit der Beton eine Seite hat.
SEITE_AB = 1.0


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
            for ecken, mitte in element.stahlflaechen():
                weitere.append(Stueck(g, 1.0, ecken, teil))
                beton = None if mitte is None else geo.innerstes(mitte, polygone)
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

    @cached_property
    def fuge(self) -> Tuple[Tuple[Stueck, ...], Tuple[Stueck, ...]]:
        """
        Beton und Betonstahl je auf ihrer Seite der Fuge (siehe Dateikopf):
        ausserhalb der Profile -- mit dem, was in ihrer Huelle liegt,
        abgezogen --, und in der Huelle eines Profils.
        """
        huellen = [geo.konvexe_huelle(t.flaeche.punkte) for t in self.stahl.teile]
        aussen: List[Stueck] = []
        kammer: List[Stueck] = []
        for s in self.weitere:
            aussen.append(s)
            for huelle in huellen:
                innen = tuple(geo.in_huelle(s.punkte, huelle))
                # Eine Platte, die nur auf dem Profil aufliegt, beruehrt die
                # Huelle: was bleibt, hat keine Flaeche.
                if abs(geo.flaeche(innen)) > geo.TOLERANZ:
                    aussen.append(dataclasses.replace(s, gewicht=-s.gewicht, punkte=innen))
                    kammer.append(dataclasses.replace(s, punkte=innen, was=IN_DER_KAMMER))
        return tuple(aussen), tuple(kammer)

    def getrennt(self, zug: Sequence[float], druck: Sequence[float],
                 stahl: Optional[Stahlquerschnitt] = None) -> Tuple[Starrplastisch,
                                                                    Starrplastisch]:
        """
        Der Querschnitt starr-plastisch in den zwei Teilen, die nur die Duebel
        verbinden (:attr:`fuge`): Beton und Betonstahl ausserhalb der Profile,
        und der Baustahl -- mit ``stahl``, wo die Querkraft ihm einen Teil
        genommen hat -- mit dem Kammerbeton. Je Gruppe mit ``zug`` und
        ``druck``.
        """
        aussen, kammer = self.fuge
        return (Starrplastisch(aussen, tuple(zug), tuple(druck)),
                Starrplastisch((*(stahl or self.stahl).stuecke, *kammer), tuple(zug),
                               tuple(druck)))

    @property
    def doppelsymmetrisch(self) -> bool:
        """
        Ob der Baustahl ein einziges Profil mit zwei Symmetrieachsen ist: ein
        I-Profil oder ein Rohr. Ein frei gezeichneter Baustahl zaehlt nicht,
        auch wo er symmetrisch ist -- das Werkzeug prueft es nicht.
        """
        teile = self.stahl.teile
        return (len(teile) == 1 and teile[0].flaeche.profil is not None
                and tabelle.profil(teile[0].flaeche.profil.name).form in DOPPELSYMMETRISCH)

    @cached_property
    def zum_beton(self) -> Optional[Tuple[float, float]]:
        """
        Ueber die Fuge (:attr:`fuge`): vom Schwerpunkt des Stahls mit dem
        Kammerbeton zu dem von Beton und Betonstahl ausserhalb der Profile,
        in mm, je nach Flaeche. ``None``, wo ausserhalb nichts liegt oder die
        Schwerpunkte keinen Millimeter auseinander -- dort hat der Beton keine
        Seite.
        """
        aussen, kammer = self.fuge

        def schwerpunkt(stuecke: Sequence[Stueck]) -> Optional[Punkt]:
            A = sum(s.gewicht * s.werte.A for s in stuecke)
            if A <= 0.0:
                return None
            return (sum(s.gewicht * s.werte.A * s.werte.y_S for s in stuecke) / A,
                    sum(s.gewicht * s.werte.A * s.werte.z_S for s in stuecke) / A)

        beton, stahl = schwerpunkt(aussen), schwerpunkt((*self.stahl.stuecke, *kammer))
        if beton is None or stahl is None:
            return None
        weg = (beton[0] - stahl[0], beton[1] - stahl[1])
        return weg if math.hypot(*weg) > SEITE_AB else None

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
