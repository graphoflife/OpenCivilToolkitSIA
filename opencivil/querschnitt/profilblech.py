"""
opencivil/querschnitt/profilblech.py -- das Profilblech einer Blechverbunddecke.

VERANTWORTUNG:
Die Form eines Profilblechs aus den Massen seines Datenblatts
(:class:`Blechform`): seine Linie, der Beton darueber, wie dick es ist und
wo sein Schwerpunkt liegt. Dazu das Blech als Bewehrungselement der
Querschnittsanalyse (:class:`Profilblech`). Die Nachweise der Decke stehen
in :mod:`opencivil.nachweis.qa_blechverbund`, ihr Eintrag in
:mod:`opencivil.projekt.blechdecken`.

DIE FORM (SIA 264:2014, Figur 18):
``n`` Rippen im Abstand ``b_s``. Eine Rippe -- der Beton zwischen zwei
Stegen des Blechs -- ist oben ``b_o`` breit, unten ``b_u`` und ``h_p``
hoch; ist sie oben schmaler als unten, ist das Blech hinterschnitten. Ueber
den Rippen liegt der Beton ``h_c = h − h_p``. Die Decke liegt mit ihrer
Ecke links unten -- der Unterkante der Rippen, dem linken Rand -- auf ihrem
Punkt.

``b_0``, die Breite einer Rippe fuer die Querkraft, ist bei einem offenen
Blech die mittlere, ``(b_o + b_u)/2``, bei einem hinterschnittenen die
Oeffnung oben, ``b_o``.

DIE DICKE (nach Vorgabe, nicht nachgeschlagen):
Das Datenblatt nennt die Flaeche ``A_p`` je Meter Breite. Das Werkzeug
verteilt sie gleichmaessig ueber die Abwicklung einer Rippe, ``s = b_s −
b_o + 2·L_w + b_u`` mit der Laenge ``L_w`` eines Stegs: ``t = A_p·b_s/s``.
Sicken und Ausrundungen laesst es weg. Damit liegt der Schwerpunkt des
Blechs ``e`` ueber der Unterkante, und die statische Hoehe ist ``d_p = h −
e`` (Figur 18).

IM QUERSCHNITT:
Das Blech liegt am Rand des Betons, nicht in ihm: es verdraengt keinen.
Jede gerade Strecke geht wie eine verschmierte Linie in den Querschnitt ein
(:func:`~opencivil.querschnitt.interaktion.linie_als_bewehrung`), mit ihrem
Teil der Flaeche.

IM FENSTER DER VORLAGEN:
Die Decke kommt wie ein Stahlprofil als ein Element in die Zeichnung, nicht
als Flaechen (:data:`VORLAGE`). Ihre Skizze zeigt die ganze Decke mit ihren
Massen von aussen (:func:`skizze`), dazu eine Rippe mit ihren eigenen
(:func:`rippenskizze`): bei tausend Millimetern Breite waeren ``b_o``,
``b_u`` und ``h_p`` in der ganzen Decke nicht zu lesen.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import List, Tuple

from opencivil.core.latex import Mathe, Zelle
from opencivil.material.basis import Baustoff
from opencivil.querschnitt.bewehrungselemente import (
    MM, Bewehrungselement, Flaechen, Verdraengt, baender,
)
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.interaktion import Bewehrung, linie_als_bewehrung
from opencivil.querschnitt.vorlagen import Teile, masslinie

#: Unter welchem Schluessel das Fenster der Vorlagen die Decke fuehrt -- neben
#: den Flaechen (:mod:`opencivil.querschnitt.vorlagen`) und dem Stahlprofil.
VORLAGE = "blechdecke"

#: Wie nah zwei Punkte der Linie liegen duerfen, in mm, ehe sie einer sind: bei
#: ``b_o = b_s`` stossen die Rippen oben aneinander.
GLEICH = 1e-9

Strecke = Tuple[Punkt, Punkt]


@dataclass(frozen=True)
class Blechform:
    """Die Masse eines Profilblechs nach seinem Datenblatt, in mm -- siehe Dateikopf."""

    ursprung: Punkt
    """Die Ecke links unten: die Unterkante der Rippen, der linke Rand."""

    rippen: int
    h: float
    """Die Dicke der ganzen Decke."""

    h_p: float
    b_s: float
    b_o: float
    b_u: float
    A_p: float
    """Die Flaeche des Blechs je Meter Breite, in mm²/m."""

    @property
    def breite(self) -> float:
        return self.rippen * self.b_s

    @property
    def h_c(self) -> float:
        """Der Beton ueber den Rippen."""
        return self.h - self.h_p

    @property
    def hinterschnitten(self) -> bool:
        return self.b_o < self.b_u

    @property
    def b_0(self) -> float:
        """Die Breite einer Rippe fuer die Querkraft (Figur 18)."""
        return self.b_o if self.hinterschnitten else (self.b_o + self.b_u) / 2.0

    @property
    def L_w(self) -> float:
        """Die Laenge eines Stegs."""
        return math.hypot(self.h_p, (self.b_o - self.b_u) / 2.0)

    @property
    def s(self) -> float:
        """Die Abwicklung des Blechs je Rippe."""
        return self.b_s - self.b_o + 2.0 * self.L_w + self.b_u

    @property
    def t(self) -> float:
        """Die Dicke des Blechs, gleich ueber die Abwicklung -- siehe Dateikopf."""
        return self.A_p * self.b_s / 1000.0 / self.s

    @property
    def e(self) -> float:
        """Wie hoch der Schwerpunkt des Blechs ueber der Unterkante liegt."""
        return self.h_p * (self.L_w + self.b_s - self.b_o) / self.s

    @property
    def d_p(self) -> float:
        """Die statische Hoehe: von der Oberkante zum Schwerpunkt des Blechs (Figur 18)."""
        return self.h - self.e

    @property
    def flaeche(self) -> float:
        """Die Flaeche des Blechs ueber die ganze Breite, in mm²."""
        return self.A_p * self.breite / 1000.0

    @property
    def linie(self) -> Tuple[Punkt, ...]:
        """Das Blech von links nach rechts: oben, in jede Rippe hinunter und wieder hinauf."""
        y_0, z_0 = self.ursprung
        oben = z_0 + self.h_p
        punkte: List[Punkt] = [(y_0, oben)]
        for i in range(self.rippen):
            c = y_0 + (i + 0.5) * self.b_s
            punkte += [(c - self.b_o / 2.0, oben), (c - self.b_u / 2.0, z_0),
                       (c + self.b_u / 2.0, z_0), (c + self.b_o / 2.0, oben)]
        punkte.append((y_0 + self.breite, oben))
        linie: List[Punkt] = []
        for p in punkte:
            if not linie or math.dist(p, linie[-1]) > GLEICH:
                linie.append(p)
        return tuple(linie)

    @property
    def strecken(self) -> Tuple[Strecke, ...]:
        linie = self.linie
        return tuple(zip(linie[:-1], linie[1:]))

    @property
    def beton(self) -> Tuple[Punkt, ...]:
        """Der Beton ueber dem Blech, gegen den Uhrzeigersinn."""
        y_0, z_0 = self.ursprung
        return (*self.linie, (y_0 + self.breite, z_0 + self.h), (y_0, z_0 + self.h))


@dataclass(frozen=True)
class Profilblech(Bewehrungselement):
    """
    Das Blech einer Blechverbunddecke -- ``von`` und ``bis`` sind die Enden
    seiner Linie, ``flaeche`` die des Blechs ueber die ganze Breite.
    """

    form: Blechform

    verschmiert = True

    @property
    def strecken(self) -> Tuple[Strecke, ...]:
        return self.form.strecken

    @property
    def menge(self) -> Zelle:
        f = self.form
        return Mathe(rf"{f.rippen} \times {f.b_s:g}\,\mathrm{{mm}},\ h_p = {f.h_p:g}\,"
                     rf"\mathrm{{mm}},\ t = {f.t:.2f}\,\mathrm{{mm}}")

    @property
    def kurzmenge(self) -> Zelle:
        return Mathe(rf"{self.flaeche:.0f}\,\mathrm{{mm}}^2")

    @property
    def rissdurchmesser(self) -> float:
        raise NotImplementedError("Die Rissbreite prueft das Werkzeug nur im Stahlbeton.")

    def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]:
        """Je Strecke ihr Teil der Flaeche, ohne den Beton zu verdraengen -- siehe Dateikopf."""
        je_mm = self.flaeche / sum(math.dist(a, b) for a, b in self.strecken)
        return [b for von, bis in self.strecken
                for b in linie_als_bewehrung((von[0] * MM, von[1] * MM), (bis[0] * MM, bis[1] * MM),
                                             je_mm * math.dist(von, bis) * MM * MM, stahl, None)]

    def stahlflaechen(self) -> Flaechen:
        return baender(self.strecken, self.flaeche, verdraengt=False)


def skizze(form: Blechform) -> Teile:
    """
    Die Decke fuer das Fenster der Vorlagen: ihr Beton, die Linie ihres
    Blechs und ihre zwei Masse von aussen -- die Breite unten, «5 × 200 =
    1000», die Dicke links. Die Ecke links unten liegt im Ursprung der Form:
    sie kommt an den Einsetzpunkt, wie bei den Flaechen.
    """
    y_0, z_0 = form.ursprung
    breite = {**masslinie((y_0, z_0), (y_0 + form.breite, z_0), "b", form.breite, "unten"),
              "text": f"{form.rippen} × {form.b_s:g} = {form.breite:g}"}
    return Teile(polygone=[{"punkte": list(form.beton), "aussparung": False}],
                 bleche=[{"punkte": list(form.linie)}],
                 masslinien=[breite, masslinie((y_0, z_0), (y_0, z_0 + form.h), "h", form.h,
                                               "links")])


def rippenskizze(form: Blechform) -> Teile:
    """
    Eine Rippe der Decke mit ihren Massen, fuer das Fenster der Vorlagen:
    der Abstand ``b_s`` ueber der Decke, ``b_o`` ueber der Oeffnung der
    Rippe, ``b_u`` unter ihr, ``h_p`` rechts und ``h`` links.
    """
    f = replace(form, ursprung=(0.0, 0.0), rippen=1)
    c, oben = f.b_s / 2.0, f.h_p
    masse = [
        masslinie((0.0, f.h), (f.b_s, f.h), "b_s", f.b_s, "oben"),
        masslinie((c - f.b_o / 2.0, oben), (c + f.b_o / 2.0, oben), "b_o", f.b_o, "oben"),
        masslinie((c - f.b_u / 2.0, 0.0), (c + f.b_u / 2.0, 0.0), "b_u", f.b_u, "unten"),
        masslinie((f.b_s, 0.0), (f.b_s, oben), "h_p", f.h_p, "rechts"),
        masslinie((0.0, 0.0), (0.0, f.h), "h", f.h, "links"),
    ]
    return replace(skizze(f), masslinien=masse)


def aus_form(name: str, kennung: str, stahl: Baustoff, form: Blechform) -> Profilblech:
    """Das Blech einer Decke mit dieser Form, aus dem Baustoff ``stahl``."""
    linie = form.linie
    return Profilblech(name=name, kennung=kennung, stahl=stahl, von=linie[0], bis=linie[-1],
                       flaeche=form.flaeche, form=form)
