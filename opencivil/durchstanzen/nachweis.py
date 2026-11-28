"""
opencivil/durchstanzen/nachweis.py -- der Durchstanznachweis nach SIA 262:2025, 4.3.6.

VERANTWORTUNG:
Der Nachweis :class:`Durchstanzen` an einer Durchstanzstelle: der
Durchstanzwiderstand ohne Durchstanzbewehrung (4.3.6.3) gegen den
Bemessungswert der Querkraft, mit allem, was er braucht -- der statischen
Höhe (4.3.6.2.1), dem Nachweisschnitt (4.3.6.2.2 und 4.3.6.2.3,
:mod:`.schnitt`), k_e (4.3.6.2.4 und 4.3.6.2.5), den Lasten im Schnitt
(4.3.6.2.6) und der Plattenrotation (4.3.6.4).

DIE RECHNUNG::

    V_Rd,c = k_r · τ_cd · d_v · u                              (58)
    k_r    = 1 / (0.45 + 0.18 · ψ · d · k_g)  ≤ 2              (59), d in mm
    ψ      = 1.5 · r_s / d · f_yd / E_s · (m_sd / m_Rd)^(3/2)   (60)
    u      = k_e · u_red

``u_red`` ist der Nachweisschnitt ohne das, was nach Figur 23 nicht zählt;
``d`` die mittlere statische Höhe der beiden Lagen der Zugbewehrung und
``d_v`` die wirksame -- gleich ``d``, solange die gestützte Fläche nicht in die
Platte reicht (Figur 21).

PLATTENBEREICHE (4.3.6.2.7):
Steht die Stütze in Bereichen mit eigener Dicke, gilt an ihr deren d, ψ
rechnet mit dem kleinsten d um sie, und an jeder Stufe, wo der Bereich
dicker ist als die Platte darum, liegt ein weiterer Schnitt mit eigenem
Urteil (:mod:`.stufen`). Liegt ein Bereich neben der Stütze, kommt der
schwächste Schnitt durch verschiedene Dicken dazu, auch mit eigenem Urteil
(:mod:`.weg`); weiter draussen geht ein Bereich nicht ein. Bereiche an
Wänden rechnet das Werkzeug noch nicht; die Herleitung sagt es. Leisten
schlägt es an der Stütze vor, im innersten Bereich um sie und ausserhalb der
übrigen (:class:`.mit_bewehrung.Platz`); an den Schnitten der Stufen und
durch verschiedene Dicken zählen sie nicht, und dort schlägt es noch keine
eigenen vor.

DIE PLATTENROTATION (4.3.6.4.2):
In Näherungsstufe 1 ist ``m_sd/m_Rd = 1``; in Stufe 2 kommen die Momente im
Stützstreifen aus den Gleichungen (62) bis (65), in Stufe 3 gibt sie der
Benutzer an, und in (60) steht 1.2 statt 1.5 als erster Faktor; an Rand- und
Eckstützen gilt dann r_s ≥ 2/3 · b_sr (4.3.6.4.8). ``r_s = 0.22 · l`` in den
Stufen 1 und 2 (4.3.6.4.4). Massgebend ist die grössere Rotation der beiden
Richtungen. Für Wandende und Wandecke nennt 4.3.6.4.7 keine Momente; dort
rechnet Stufe 2 wie Stufe 1, und die Herleitung sagt es.

DIE BREITE DER STÜTZSTREIFEN (4.3.6.4.6, Figur 25):
``b_s = 1.5 · √(r_sx · r_sy) ≤ l_min``. Ein Streifen senkrecht zum Rand einer
Randstütze und die Randstreifen einer Eckstütze sind auf ``b_sr`` begrenzt:
die Breite, die zwei Linien unter 45° von den inneren Ecken der Stütze am
Plattenrand einschliessen, ``b_sr = b_x + 2 · (b_y + a_y)`` für den Streifen
in y, entsprechend in x. An der Randstütze ist der Streifen
``min[b_s; b_sr]`` breit. An der Eckstütze schneidet ihn quer der zweite
Rand ab: die halbe Breite ``min[b_s; b_sr]/2`` innen, zum zweiten Rand hin
nur bis zu ihm, ``b_x/2 + a_x`` für den Streifen in y, höchstens ebenso viel.
Bis 2026-11-14 lag er an der Ecke symmetrisch um die Achse, bis zu 50 %
breiter, als Figur 25 ihn zeigt.

DIE KRAFT IN m_sd (Benutzer, 2026-11-26):
Die Gleichungen (62) bis (65) rechnen mit der ganzen Auflagerkraft ``V_d``,
ohne die Last innerhalb des Nachweisschnitts abzuziehen. Die Norm sagt nicht
ausdruecklich, welches V_d dort gilt; der Abzug nach 4.3.6.2.6 ist erlaubt,
nicht verlangt. Das Skript «Stahlbeton II, 7.4 Platten» (Kaufmann, FS 2026,
Folie 28) verknuepft m_sd mit der Stuetzenreaktion: die Momente im
Stuetzstreifen entstehen aus der ganzen Stuetzenkraft. Das liegt auf der
sicheren Seite. Den Abzug behaelt die Querkraft im Nachweis, in (66) und
(67) und am aeusseren Schnitt. Bis 2026-11-25 kam m_sd aus V_d,red -- bei
einer Bodenplatte mit 150 kN/m² Bodenpressung bis 7 % zu viel Widerstand,
bei einer Decke unter 1 %.

EINHEITEN:
SI-Basis; wo die Norm in mm rechnet (59), sagt es die Herleitung.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich, grad_def,
)
from opencivil.core.einheiten import EINHEITSLOS, KNM_PRO_M, MM2_PRO_M, Groesse
from opencivil.core.latex import Mathe, als_text, angabe
from opencivil.core.protokoll import GleichungBlock, Protokoll, TabellenBlock, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.core.sprache import aufgezaehlt
from opencivil.durchstanzen import herleitung, mit_bewehrung, stufen, weg
from opencivil.durchstanzen.bereiche import Dicken, Plattenbereich
from opencivil.durchstanzen.herleitung import STUETZE
from opencivil.durchstanzen.flaeche import Mass, Masse, Randbreite
from opencivil.durchstanzen.mit_bewehrung import Grundlage
from opencivil.durchstanzen.pruefung import (
    KeExzentrizitaet, Leistenpruefung, Pilzbefund, Schnittpruefung, exzentrizitaet,
)
from opencivil.durchstanzen.schnitt import (
    Auswertung, Punkt, nachweisschnitt, schatten_am_schnitt,
)
from opencivil.durchstanzen.stelle import (
    Durchstanzstelle, KeArt, Naeherungsstufe, wirksame_stufe,
)
from opencivil.durchstanzen.stufen import Bereichswerte, Stufe, Stuetzenhoehe
from opencivil.nachweis.querkraft_ohne_buegel import beiwert_k_g
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL

#: ``r_s = R_S · l`` in den Näherungsstufen 1 und 2 (SIA 262:2025, 4.3.6.4.4).
R_S = 0.22

#: Unter dieser Plattenrotation fehlt Verformungsvermögen, wenn keine
#: Durchstanzbewehrung nach (67) liegt (SIA 262:2025, 4.3.6.1.2).
ROTATION_MINDEST = 0.020

#: Was der Nachweis nicht prueft, weil er die Lasten um die Stuetze nicht
#: kennt (SIA 262:2025, 4.3.6.2.3, vierter Fall).
EINZELLASTEN = ("Nicht geprüft: Einzellasten über 0.2·V_d, die näher als 3·d_v am "
                "Nachweisschnitt angreifen, verteilen die Querkraft im Schnitt "
                "ungleichmässig; das Werkzeug kennt solche Lasten nicht (4.3.6.2.3).")


@dataclass(frozen=True)
class Rotation:
    """Die Plattenrotation in einer Richtung: r_s, m_sd/m_Rd und ψ."""

    richtung: Richtung
    r_s: float
    m_sd: Optional[float]
    m_Rd: Optional[float]
    psi: float


@dataclass(frozen=True)
class Biegelage:
    """Eine Lage der Zugbewehrung über der Stütze, wie gerechnet -- fürs Bild der Leiste."""

    richtung: Richtung
    tiefe: float
    """Wie weit ihre Mitte unter der Oberfläche der Zugseite liegt: h − d in ihrer Richtung."""

    durchmesser: float
    abstand: float


@dataclass(frozen=True)
class Stufenbefund:
    """
    Eine Stufe mit ihrem Schnitt und seinem Widerstand -- der fehlt ohne
    Einwirkung und wo die Stufe keinen eigenen Schnitt hat.
    """

    stufe: Stufe
    V_Rd_c: Optional[float] = None


@dataclass(frozen=True)
class Wegbefund:
    """Der Schnitt durch verschiedene Dicken und sein Widerstand (:mod:`.weg`)."""

    schnitt: weg.Wegschnitt
    V_Rd_c: float


@dataclass(frozen=True)
class Durchstanzbefund:
    """
    Was der Nachweis gefunden hat -- für die Zusammenfassung und das Bild.
    Längen in m, Kräfte in N. Leisten und Stahlpilz stehen nur da, wo es sie
    braucht; jedes mit seinen eigenen Zahlen.
    """

    d: float
    innen: Schnittpruefung
    """Der Schnitt um die gestützte Fläche."""

    rotationen: Tuple[Rotation, ...]
    psi: float
    k_r: float
    V_Rd_c: float
    umriss: Tuple[Punkt, ...]
    aussparungen: Tuple[Tuple[Punkt, ...], ...]
    raender: Tuple[Tuple[Punkt, float], ...]
    """Je Plattenrand ein Punkt auf ihm und die Richtung, in die die Platte liegt (rad)."""

    lagen: Tuple[Biegelage, ...] = ()
    """Die beiden Lagen der Zugbewehrung, die äussere zuerst."""

    leisten: Optional[Leistenpruefung] = None
    """Die vorgeschlagene Durchstanzbewehrung mit ihren Nachweisen (4.3.6.5.1)."""

    pilz: Optional[Pilzbefund] = None
    """Der gewählte Stahlpilz; mit ``leisten`` stehen die Leisten um ihn."""

    stufen: Tuple[Stufenbefund, ...] = ()
    """Die Schnitte an den Stufen der Bereiche um die Stütze (:mod:`.stufen`)."""

    weg: Optional[Wegbefund] = None
    """Der Schnitt durch verschiedene Dicken -- wo ein Bereich neben der Stütze liegt."""

    platz: Optional[mit_bewehrung.Platz] = None
    """Wo die Leisten an der Stütze liegen dürfen -- mit ``leisten`` gesetzt."""

    @property
    def ohne_einwirkung(self) -> bool:
        """
        Ob die Stütze nichts trägt -- dann ist nichts durchzustanzen. Die eine
        Stelle für Nachweis und Grundriss: dort stand bis 2026-11-27
        «V_d = 0 ≤ V_Rd,c – erfüllt, α = ∞».
        """
        return self.innen.V_d == 0.0


@dataclass(frozen=True)
class Stuetzenschnitt:
    """
    Der Schnitt um die gestützte Fläche mit allem, was nicht von der
    Stützenkraft abhängt -- für Nachweis und Kennzahl derselbe. Ohne
    Plattenbereiche sind ``d`` und ``d_platte`` derselbe Wert, und ψ rechnet
    mit ihm und ``hoehen``.
    """

    masse: Dict[str, float]
    d: Wert
    """Die statische Höhe an der Stütze -- k_r und d_v rechnen mit ihr."""

    d_v: Wert
    hoehen: Dict[Richtung, Wert]
    """Die statischen Höhen der beiden Lagen in der Platte."""

    innen: Schnittpruefung
    k_e: Wert
    u: Wert
    e_u: Tuple[float, float]
    """Die Exzentrizität der Resultierenden zum Schwerpunkt des Schnitts, je Richtung."""

    d_platte: Wert
    """d der Platte, ausserhalb aller Bereiche."""

    hoehe: Optional[Stuetzenhoehe] = None
    bereiche: Optional[Bereichswerte] = None
    stufen: Tuple[Stufe, ...] = ()
    """Die Stufen um die Stütze, je mit ihrem Schnitt -- ohne Plattenbereiche keine."""

    netz: Optional[weg.Netz] = None
    """Wo die Schnitte durch verschiedene Dicken gesucht werden -- nur mit Bereichen neben ihr."""

    dicken: Optional[Dicken] = None
    """Die Platte und ihre Bereiche -- ohne Bereiche, und an Wänden, keine."""

    @property
    def rotation(self) -> Tuple[Wert, Dict[Richtung, Wert]]:
        """d und die beiden Lagen, mit denen ψ rechnet: die kleinsten um die Stütze."""
        b = self.bereiche
        if b is None or b.d_psi is None:
            return self.d_platte, self.hoehen
        return b.d_psi, b.lagen_psi


@dataclass(frozen=True)
class Widerstand:
    """Was an der Stütze von der Stützenkraft abhängt: ψ, k_r und V_Rd,c."""

    rotationen: Tuple[Rotation, ...]
    psi: Wert
    k_g: Wert
    k_r: Wert
    tau_cd: Wert
    V_Rd_c: Wert


class Stuetzenrechnung:
    """
    Was der Nachweis (:class:`Durchstanzen`) und die Kennzahl
    (:class:`~opencivil.durchstanzen.kennzahl.Durchstanzkennzahl`) an der
    Stütze gleich rechnen, je mit seiner Herleitung: den Schnitt um sie
    (:meth:`_schnitt`) und ihren Widerstand ohne Durchstanzbewehrung bei einer
    Stützenkraft (:meth:`_widerstand`). Beide sind Berechnungen einer
    ``stelle``; die Kennzahl rechnet den Widerstand still bei vielen Kräften
    und schreibt nur den letzten.
    """

    stelle: Durchstanzstelle
    id: str

    def _schnitt(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, V_d: float) -> Stuetzenschnitt:
        """
        Statische Höhe, Nachweisschnitt, k_e und wirksamer Umfang -- und die
        Schnitte an den Stufen der Plattenbereiche. ``V_d`` in N.
        """
        s, f = self.stelle, self.stelle.flaeche
        masse = {k: e.g(k).si for k in f.masse}
        d, hoehen = self._statische_hoehe(e, p, w)
        dicken, hoehe, bereiche, nah = self._bereiche(e, p, w, masse, d, hoehen)
        d_S = d if bereiche is None else bereiche.d_S
        d_v = w.laenge("d_v", "d_v", d_S.groesse.si)
        p.formel(d_v, "@d", {"d": d_S},
                 titel="Wirksame statische Höhe: die gestützte Fläche reicht nicht in die Platte",
                 referenz="SIA 262:2025, 4.3.6.2.1, Figur 21", name="Wirksame Höhe ohne Abzug")
        dv = d_v.groesse.si
        schnitt = nachweisschnitt(f.kandidaten(masse, dv / 2.0, dv), d_v=dv,
                                  achse=f.achse(masse), aussparungen=s.aussparungen)
        a = schnitt.massgebend
        u_red = self._nachweisschnitt(e, p, w, a, d_v)
        resultierende = self._resultierende(e, masse)
        regel = (f.k_e_naeherung(a) if s.ke is KeArt.NAEHERUNG
                 else KeExzentrizitaet(resultierende))
        innen = Schnittpruefung(schnitt, regel, V_d, e.g("q_d").si, d_v=dv)
        p.titel("Momentenübertragung", ebene=3)
        k_e = herleitung.k_e(p, w, innen, ix=STUETZE)
        u = herleitung.wirksam(p, w, k_e, u_red, ix=STUETZE,
                               titel="Wirksamer Umfang des Nachweisschnitts")
        um_stufen: Tuple[Stufe, ...] = ()
        netz: Optional[weg.Netz] = None
        if hoehe is not None:
            stuetze, achse, q_d = f.form.flaeche(masse), f.achse(masse), e.g("q_d").si
            um_stufen = stufen.stufen(dicken, hoehe, stuetze, raender=f.raender(masse),
                                      achse=achse, aussparungen=s.aussparungen, regel=regel,
                                      V_d=V_d, q_d=q_d)
            if nah:
                schatten = schatten_am_schnitt(s.aussparungen, a.kandidat.stuecke, d_v=dv,
                                               achse=achse)
                netz = weg.Netz(dicken, hoehe.um, stuetze, raender=f.raender(masse),
                                aussparungen=s.aussparungen, schatten=schatten, d_v=dv,
                                k_e=k_e.groesse.si, regel=regel, V_d=V_d, q_d=q_d)
        return Stuetzenschnitt(masse, d_S, d_v, hoehen, innen, k_e, u,
                               exzentrizitaet(resultierende, a), d, hoehe, bereiche, um_stufen,
                               netz, dicken if hoehe is not None else None)

    def _bereiche(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, masse: Masse, d: Wert,
                  hoehen: Dict[Richtung, Wert]
                  ) -> Tuple[Optional[Dicken], Optional[Stuetzenhoehe], Optional[Bereichswerte],
                             Tuple[Plattenbereich, ...]]:
        """
        Die Plattenbereiche um die Stütze und die neben ihr, durch die ein
        Schnitt laufen kann -- nichts ohne Bereiche und an Wänden (Dateikopf).
        """
        s, f = self.stelle, self.stelle.flaeche
        if not s.bereiche:
            return None, None, None, ()
        if not f.hat_form:
            p.titel("Plattenbereiche", ebene=3)
            p.hinweis(f"An {f.lage.mehrzahl} rechnet das Werkzeug Plattenbereiche noch nicht: "
                      f"{aufgezaehlt([b.titel for b in s.bereiche])} gehen nicht ein.")
            return None, None, None, ()
        dicken = Dicken(e.g("h").si, d.groesse.si, tuple(s.bereiche))
        stuetze = f.form.flaeche(masse)
        hoehe = stufen.an_der_stuetze(dicken, stuetze)
        nah, fern = weg.neben(dicken, hoehe.um, stuetze)
        werte = stufen.bereiche_schreiben(p, w, e, dicken, hoehe, d, hoehen, nah)
        if fern:
            einer = len(fern) == 1
            p.hinweis(f"{aufgezaehlt([b.titel for b in fern])} lieg{'t' if einer else 'en'} mehr "
                      f"als {weg.REICHWEITE:g}·d neben der Stütze"
                      f"{' und den Bereichen um sie' if hoehe.um else ''}: so weit draussen wird "
                      f"kein Schnitt um sie massgebend, {'er geht' if einer else 'sie gehen'} "
                      f"nicht ein – nach Vorgabe, nicht nachgeschlagen.")
        return dicken, hoehe, werte, nah

    def _widerstand(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Stuetzenschnitt,
                    V_d: Wert, ergebnis: Optional[WertDef] = None) -> Widerstand:
        """
        ψ, k_r und V_Rd,c bei der Stützenkraft ``V_d``: in Näherungsstufe 2
        wachsen die Momente im Stützstreifen mit ihr. ``ergebnis`` ist die
        Definition, die V_Rd,c belegt -- sonst ein Zwischenwert.
        """
        rotationen, psi = self._rotation(e, p, w, g, V_d)
        p.titel("Durchstanzwiderstand", ebene=3)
        k_g = beiwert_k_g(p, self.id, e["D_max"], e[self.stelle.beton.eingabename("f_ck")])
        k_r = herleitung.k_r(p, w, psi, g.d, k_g, ix=STUETZE,
                             titel="Beiwert für Bauteilgrösse, Plattenrotation und Grösstkorn")
        tau = e[self.stelle.beton.eingabename("tau_cd")]
        tau_cd = w.wert("tau_cd", tau.symbol, tau.groesse, 4)
        V_Rd_c = herleitung.widerstand(p, w, g.innen, ix=STUETZE, k_r=k_r, tau_cd=tau_cd,
                                       d_v=g.d_v, u=g.u,
                                       titel="Durchstanzwiderstand ohne Durchstanzbewehrung",
                                       referenz="SIA 262:2025, 4.3.6.3.1", ergebnis=ergebnis)
        return Widerstand(rotationen, psi, k_g, k_r, tau_cd, V_Rd_c)

    def _stufe_schreiben(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Stuetzenschnitt,
                         r: Widerstand, st: Stufe,
                         V_d: Optional[Wert] = None) -> Optional[Tuple[Wert, Wert]]:
        """Der Schnitt an einer Stufe (:func:`.stufen.stufe_schreiben`) mit ψ und k_g der Stütze."""
        return stufen.stufe_schreiben(p, w, e, st, d=g.d_platte, werte=g.bereiche, psi=r.psi,
                                      k_g=r.k_g, tau_cd=r.tau_cd, k_e_stuetze=g.k_e,
                                      last=self.stelle.plattenart.last, V_d=V_d)

    def _weg_schreiben(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Stuetzenschnitt,
                       r: Widerstand, ws: weg.Wegschnitt,
                       V_d: Optional[Wert] = None) -> Tuple[Wert, Wert]:
        """Der Schnitt durch verschiedene Dicken (:func:`.weg.schreiben`), ψ und k_g der Stütze."""
        return weg.schreiben(p, w, e, ws, d=g.d_platte, h_B=g.bereiche.dicken, psi=r.psi,
                             k_g=r.k_g, tau_cd=r.tau_cd, k_e_stuetze=g.k_e,
                             last=self.stelle.plattenart.last, V_d=V_d)

    # -- Statische Höhe -----------------------------------------------------

    def _statische_hoehe(self, e: Eingaben, p: Protokoll,
                         w: Zwischenwerte) -> Tuple[Wert, Dict[Richtung, Wert]]:
        """Die statischen Höhen der beiden Lagen in der Platte und ihr Mittel d (4.3.6.2.1)."""
        s = self.stelle
        h, c = e.g("h").si, e.g("c").si
        phi = {Richtung.X: e.g("phi_x").si, Richtung.Y: e.g("phi_y").si}
        aussen, innen = s.aussen, s.aussen.gegenrichtung
        hoehen: Dict[Richtung, Wert] = {}
        for r in (Richtung.X, Richtung.Y):
            k = r.value
            if r is aussen:
                si = h - c - phi[r] / 2.0
                vorlage = rf"@h - @c - \frac{{@phi_{k}}}{{2}}"
            else:
                si = h - c - phi[aussen] - phi[r] / 2.0
                vorlage = rf"@h - @c - @phi_{aussen.value} - \frac{{@phi_{k}}}{{2}}"
            hoehen[r] = w.laenge(f"d_{k}", f"d_{k}", si)
            lage = "äusseren" if r is aussen else "inneren"
            p.formel(hoehen[r], vorlage, {"h": e["h"], "c": e["c"], "phi_x": e["phi_x"],
                                          "phi_y": e["phi_y"]},
                     titel=f"Statische Höhe der Lage in {k} ({'aussen' if r is aussen else 'innen'})",
                     name=f"Statische Höhe der {lage} Lage")
        d = w.laenge("d", "d", (hoehen[Richtung.X].groesse.si + hoehen[Richtung.Y].groesse.si) / 2.0)
        p.formel(d, r"\frac{@d_x + @d_y}{2}", {"d_x": hoehen[Richtung.X], "d_y": hoehen[Richtung.Y]},
                 titel="Mittlere statische Höhe der beiden Lagen der Zugbewehrung",
                 referenz="SIA 262:2025, 4.3.6.2.1")
        return d, hoehen

    # -- Nachweisschnitt ----------------------------------------------------

    def _nachweisschnitt(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, a: Auswertung,
                         d_v: Wert) -> Wert:
        """
        Der Nachweisschnitt und was von ihm nicht zählt: ``u_red``, noch ohne
        k_e. Wo die gestützte Fläche eine Formel für u_0 kennt, steht sie da,
        sonst die Länge in der Platte; die Abzüge schreibt :mod:`.herleitung`,
        wie an jedem Schnitt.
        """
        f = self.stelle.flaeche
        p.titel("Nachweisschnitt", ebene=3)
        formel = f.umfang(e, d_v, a)
        if formel is not None:
            u_0 = w.laenge("u_0", "u_0", formel.wert, stellen=0)
            p.formel(u_0, formel.vorlage, formel.eingaben, titel=formel.titel,
                     referenz=formel.referenz, name=formel.name)
        else:
            if a.kandidat.raender:
                p.erklaerung(
                    "Der Schnitt endet am Plattenrand: so ist er kürzer als der geschlossene "
                    "(Figur 22d). Was jenseits des Rands läge, zählt nicht.")
            u_0 = herleitung.rand(p, w, a, ix=STUETZE,
                                  titel="Nachweisschnitt im Abstand d_v/2, soweit er in der Platte liegt",
                                  referenz="SIA 262:2025, 4.3.6.2.2, Figur 22")
        return herleitung.abzuege(
            p, w, a, u_0, ix=STUETZE, ecken=f.ecken_abziehen,
            ecken_text="An den Ecken grosser gestützter Flächen ballt sich die Querkraft: von "
                       "einer geraden Strecke des Schnitts zählt nur, was höchstens 1.5·d_v von "
                       "einer Ecke entfernt liegt.",
            ecken_referenz="SIA 262:2025, 4.3.6.2.3, Figur 23a")

    def _resultierende(self, e: Eingaben, masse: Masse) -> Punkt:
        """
        Wo die Auflagerkraft angreift: in der Stützenachse, verschoben um die
        Exzentrizität e_x, e_y, wo k_e nach (57) sie liest. Von hier misst e_u
        an jedem Schnitt -- um die Stütze, um die äussersten Anker und um den Pilz.
        """
        ax, ay = self.stelle.flaeche.achse(masse)
        return (ax + (e.g("e_x").si if e.hat("e_x") else 0.0),
                ay + (e.g("e_y").si if e.hat("e_y") else 0.0))

    # -- Plattenrotation ----------------------------------------------------

    def _rotation(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Stuetzenschnitt,
                  V_d: Wert) -> Tuple[Tuple[Rotation, ...], Wert]:
        """ψ je Richtung und die massgebende, die grössere (4.3.6.4.1) -- bei der Kraft ``V_d``."""
        s = self.stelle
        (d, hoehen), e_u, masse = g.rotation, g.e_u, g.masse
        p.titel("Plattenrotation", ebene=3)
        if g.hoehe is not None:
            stufen.rotation_schreiben(p, g.hoehe)
        stufe = wirksame_stufe(s.flaeche, s.stufe)
        if stufe is not s.stufe:
            p.hinweis(f"Für {s.flaeche.lage.mehrzahl} nennt 4.3.6.4.7 keine Momente im "
                      f"Stützstreifen: gerechnet wie in {stufe.beschriftung}, mit m_sd/m_Rd = 1.")
        p.erklaerung(
            f"{stufe.beschriftung}: "
            + {Naeherungsstufe.EINS: "für regelmässig gestützte Flachdecken mit "
                                     "0.5 ≤ l_x/l_y ≤ 2 ohne grosse Umlagerung: m_sd/m_Rd = 1.",
               Naeherungsstufe.ZWEI: "die mittleren Momente im Stützstreifen nach den "
                                     "Gleichungen (62) bis (65).",
               Naeherungsstufe.DREI: "r_s und die mittleren Momente im Stützstreifen aus einer "
                                     "Berechnung nach der Elastizitätstheorie; in (60) steht "
                                     "1.2 statt 1.5 als erster Faktor."}[stufe])
        f_yd, E_s = e[s.stahl.eingabename("f_yd")], e[s.stahl.eingabename("E_s")]
        r_s: Dict[Richtung, Wert] = {}
        for r in (Richtung.X, Richtung.Y):
            k = r.value
            if stufe is Naeherungsstufe.DREI:
                rand = s.flaeche.randbreite(r, masse)
                r_s[r] = e[f"r_s{k}"] if rand is None else self._r_s_am_rand(e, p, w, r, rand)
            else:
                r_s[r] = w.laenge(f"r_s{k}", f"r_{{s{k}}}", R_S * e.g(f"l_{k}").si, stellen=0)
                p.formel(r_s[r], rf"{R_S} \cdot @l", {"l": e[f"l_{k}"]},
                         titel=f"Abstand zum Momentennullpunkt in {k}",
                         referenz="SIA 262:2025, 4.3.6.4.4", name="Abstand zum Momentennullpunkt")
        m_sd: Dict[Richtung, Optional[Wert]] = {Richtung.X: None, Richtung.Y: None}
        m_Rd: Dict[Richtung, Optional[Wert]] = {Richtung.X: None, Richtung.Y: None}
        if stufe is not Naeherungsstufe.EINS:
            for r in (Richtung.X, Richtung.Y):
                m_Rd[r] = self._m_Rd(e, p, w, r, hoehen[r])
            if stufe is Naeherungsstufe.ZWEI:
                m_sd = self._m_sd(e, p, w, r_s, e_u, masse, V_d)
            else:
                m_sd = {Richtung.X: e["m_sdx"], Richtung.Y: e["m_sdy"]}
        faktor = stufe.faktor
        rotationen: List[Rotation] = []
        psis: Dict[Richtung, Wert] = {}
        for r in (Richtung.X, Richtung.Y):
            k = r.value
            eingaben = {"r_s": r_s[r], "d": d, "f_yd": f_yd, "E_s": E_s}
            if m_sd[r] is None:
                verhaeltnis = 1.0
                vorlage = rf"{faktor} \cdot \frac{{@r_s}}{{@d}} \cdot \frac{{@f_yd}}{{@E_s}}"
            else:
                verhaeltnis = max(0.0, m_sd[r].groesse.si) / m_Rd[r].groesse.si
                vorlage = (rf"{faktor} \cdot \frac{{@r_s}}{{@d}} \cdot \frac{{@f_yd}}{{@E_s}} "
                           r"\cdot \left(\frac{@m_sd}{@m_Rd}\right)^{3/2}")
                eingaben.update({"m_sd": m_sd[r], "m_Rd": m_Rd[r]})
            psi_si = (faktor * r_s[r].groesse.si / d.groesse.si * f_yd.groesse.si / E_s.groesse.si
                      * verhaeltnis ** 1.5)
            psis[r] = w.zahl(f"psi_{k}", rf"\psi_{k}", psi_si, stellen=4)
            p.formel(psis[r], vorlage, eingaben, titel=f"Plattenrotation in {k}",
                     referenz="SIA 262:2025, 4.3.6.4.1, (60)", name="Plattenrotation")
            if m_sd[r] is not None and verhaeltnis > 1.0:
                p.hinweis(f"m_sd > m_Rd in {k}: die Biegebewehrung im Stützstreifen genügt "
                          f"nicht – der Biegenachweis gehört dazu.")
            rotationen.append(Rotation(r, r_s[r].groesse.si,
                                       None if m_sd[r] is None else m_sd[r].groesse.si,
                                       None if m_Rd[r] is None else m_Rd[r].groesse.si, psi_si))
        psi = w.zahl("psi", r"\psi", max(x.groesse.si for x in psis.values()), stellen=4)
        p.formel(psi, r"\max\left[@psi_x;\ @psi_y\right]",
                 {"psi_x": psis[Richtung.X], "psi_y": psis[Richtung.Y]},
                 titel="Massgebende Plattenrotation: die grössere",
                 referenz="SIA 262:2025, 4.3.6.4.1")
        return tuple(rotationen), psi

    def _m_Rd(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r: Richtung, d_r: Wert) -> Wert:
        """Der Biegewiderstand je Meter im Stützstreifen, aus dem Kräftegleichgewicht (Spannungsblock)."""
        s = self.stelle
        k = r.value
        phi, teilung = e.g(f"phi_{k}").si, e.g(f"s_{k}").si
        a_s_si = math.pi * phi ** 2 / 4.0 / teilung
        a_s = w.wert(f"a_s{k}", f"a_{{s,{k}}}", Groesse.aus_si(a_s_si, MM2_PRO_M), 0,
                     f"Bewehrung in {k} je Meter")
        p.formel(a_s, rf"\frac{{\pi \cdot @phi^{{2}}}}{{4 \cdot @s}}",
                 {"phi": e[f"phi_{k}"], "s": e[f"s_{k}"]}, titel=f"Bewehrung in {k} je Meter",
                 name="Biegebewehrung im Stützstreifen je Meter")
        f_yd, f_cd = e[s.stahl.eingabename("f_yd")], e[s.beton.eingabename("f_cd")]
        x_si = a_s_si * f_yd.groesse.si / (BLOCKANTEIL * f_cd.groesse.si)
        x = w.laenge(f"x_{k}", f"x_{k}", x_si)
        p.formel(x, rf"\frac{{@a_s \cdot @f_yd}}{{{BLOCKANTEIL} \cdot @f_cd}}",
                 {"a_s": a_s, "f_yd": f_yd, "f_cd": f_cd},
                 titel=f"Druckzonenhöhe in {k}, je Meter",
                 referenz="SIA 262:2025, 4.2.1.5, Figur 12",
                 name="Druckzonenhöhe im Stützstreifen")
        m_si = a_s_si * f_yd.groesse.si * (d_r.groesse.si - BLOCKANTEIL * x_si / 2.0)
        m = w.wert(f"m_Rd{k}", f"m_{{Rd,{k}}}", Groesse.aus_si(m_si, KNM_PRO_M), 1)
        p.formel(m, rf"@a_s \cdot @f_yd \cdot \left(@d - \frac{{{BLOCKANTEIL} \cdot @x}}{{2}}\right)",
                 {"a_s": a_s, "f_yd": f_yd, "d": d_r, "x": x},
                 titel=f"Biegewiderstand im Stützstreifen in {k}",
                 referenz="SIA 262:2025, 4.3.6.4.5; 4.2.1.5, Figur 12",
                 name="Biegewiderstand im Stützstreifen")
        return m

    def _m_sd(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r_s: Dict[Richtung, Wert],
              e_u: Tuple[float, float], masse: Dict[str, float],
              V_d: Wert) -> Dict[Richtung, Optional[Wert]]:
        """
        Die mittleren Momente im Stützstreifen in Näherungsstufe 2 (4.3.6.4.7),
        aus der ganzen Auflagerkraft ``V_d`` -- siehe Dateikopf.
        """
        s = self.stelle
        l_min = min(e.g("l_x").si, e.g("l_y").si)
        frei = 1.5 * math.sqrt(r_s[Richtung.X].groesse.si * r_s[Richtung.Y].groesse.si)
        b_s = w.laenge("b_s", "b_s", min(frei, l_min), "Breite des Stützstreifens", stellen=0)
        p.formel(b_s, r"\min\left[1.5 \cdot \sqrt{@r_sx \cdot @r_sy};\ @l_min\right]",
                 {"r_sx": r_s[Richtung.X], "r_sy": r_s[Richtung.Y],
                  "l_min": w.laenge("l_min", "l_{min}", l_min, "Die kleinere Spannweite",
                                    stellen=0)},
                 titel="Breite des Stützstreifens", referenz="SIA 262:2025, 4.3.6.4.6, (61)")
        if l_min < frei:
            p.text("l_min ist hier die kleinere der beiden eingegebenen Spannweiten, je die "
                   "grössere der angrenzenden. Ist ein angrenzendes Feld kürzer, gilt seine "
                   "Spannweite, und b_s wird kleiner (4.3.6.4.6).")
        if e.g("q_d").si > 0.0:
            p.erklaerung("m_sd kommt aus der ganzen Auflagerkraft V_d: Die Momente im "
                         "Stützstreifen entstehen aus der ganzen Stützenkraft, wie im Modell "
                         "des Skripts «Stahlbeton II, 7.4 Platten» (Folie 28). Die Last "
                         "innerhalb des Nachweisschnitts zieht nur die Querkraft im Nachweis "
                         "ab (4.3.6.2.6).")
        V = V_d.groesse.si
        ergebnis: Dict[Richtung, Optional[Wert]] = {}
        for r, e_i in ((Richtung.X, e_u[0]), (Richtung.Y, e_u[1])):
            k = r.value
            e_w = w.laenge(f"e_u{k}", f"e_{{u,{k}}}", abs(e_i), stellen=0)
            g = s.flaeche.momentengleichung(r, masse)
            rand = s.flaeche.randbreite(r, masse)
            breite = b_s if rand is None else self._breite_am_rand(p, w, r, b_s, rand)
            m_si = max(V * (1.0 / 8.0 + abs(e_i) / (g.teiler * breite.groesse.si)), g.mindest * V)
            m = w.wert(f"m_sd{k}", f"m_{{sd,{k}}}", Groesse.aus_si(m_si, KNM_PRO_M), 1)
            nenner = r"2 \cdot @b" if g.teiler == 2.0 else "@b"
            vorlage = rf"@V_d \cdot \left(\frac{{1}}{{8}} + \frac{{@e}}{{{nenner}}}\right)"
            if g.mindest:
                vorlage = rf"\max\left[{vorlage};\ {g.mindest:g} \cdot @V_d\right]"
            p.formel(m, vorlage, {"V_d": V_d, "e": e_w, "b": breite},
                     titel=f"Mittleres Moment im Stützstreifen in {k}",
                     referenz=f"SIA 262:2025, 4.3.6.4.7, {g.nummer}",
                     name="Mittleres Moment im Stützstreifen")
            ergebnis[r] = m
        return ergebnis

    @staticmethod
    def _mass(w: Zwischenwerte, mass: Mass) -> Wert:
        was = ("Abstand der Stütze vom Plattenrand" if mass.name.startswith("a_")
               else "Abmessung der Stütze")
        return w.laenge(mass.name, mass.zeichen, mass.wert, was, stellen=0)

    def _b_sr(self, p: Protokoll, w: Zwischenwerte, r: Richtung, rand: Randbreite) -> Wert:
        """b_sr des Streifens in ``r``: zwischen den Linien unter 45° (Figur 25) -- siehe Kopf."""
        quer, laengs, a = rand.quer, rand.laengs, rand.abstand
        b_sr = w.laenge(f"b_sr{r.value}", f"b_{{sr,{r.value}}}",
                        quer.wert + 2.0 * (laengs.wert + a.wert),
                        "Grenze der Breite des Stützstreifens am Plattenrand", stellen=0)
        p.formel(b_sr, r"@quer + 2 \cdot \left(@laengs + @a\right)",
                 {"quer": self._mass(w, quer), "laengs": self._mass(w, laengs),
                  "a": self._mass(w, a)},
                 titel=f"Grenze der Breite des Stützstreifens in {r.value} am Plattenrand: "
                       f"zwischen den Linien unter 45° von den inneren Ecken der Stütze",
                 referenz="SIA 262:2025, 4.3.6.4.6, Figur 25",
                 name="Breite des Stützstreifens am Plattenrand")
        return b_sr

    def _breite_am_rand(self, p: Protokoll, w: Zwischenwerte, r: Richtung, b_s: Wert,
                        rand: Randbreite) -> Wert:
        """
        Die Breite eines Streifens, den der Plattenrand begrenzt: höchstens
        b_sr, an der Ecke vom zweiten Rand abgeschnitten -- siehe Dateikopf.
        """
        k = r.value
        b_sr = self._b_sr(p, w, r, rand)
        halb = min(b_s.groesse.si, b_sr.groesse.si) / 2.0
        if rand.zweiter is None:
            breite = w.laenge(f"b_s{k}", f"b_{{s,{k}}}", 2.0 * halb,
                              f"Breite des Stützstreifens in {k}", stellen=0)
            p.formel(breite, r"\min\left[@b_s;\ @b_sr\right]", {"b_s": b_s, "b_sr": b_sr},
                     titel=f"Breite des Stützstreifens in {k}, senkrecht zum Rand",
                     referenz="SIA 262:2025, 4.3.6.4.6, Figur 25",
                     name="Breite des Stützstreifens senkrecht zum Rand")
            return breite
        quer, zweiter = rand.quer, rand.zweiter
        breite = w.laenge(f"b_s{k}", f"b_{{s,{k}}}",
                          halb + min(halb, quer.wert / 2.0 + zweiter.wert),
                          f"Breite des Stützstreifens in {k}", stellen=0)
        haelfte = r"\frac{\min\left[@b_s;\ @b_sr\right]}{2}"
        p.formel(breite, rf"{haelfte} + \min\left[{haelfte};\ \frac{{@quer}}{{2}} + @a\right]",
                 {"b_s": b_s, "b_sr": b_sr, "quer": self._mass(w, quer),
                  "a": self._mass(w, zweiter)},
                 titel=f"Breite des Randstreifens in {k}: innen die halbe, aussen bis zum "
                       f"zweiten Plattenrand",
                 referenz="SIA 262:2025, 4.3.6.4.6, Figur 25",
                 name="Breite des Randstreifens an der Eckstütze")
        return breite

    def _r_s_am_rand(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r: Richtung,
                     rand: Randbreite) -> Wert:
        """In Stufe 3 an Rand- und Eckstützen: r_s mindestens 2/3 · b_sr (4.3.6.4.8)."""
        k = r.value
        eingabe = e[f"r_s{k}"]
        b_sr = self._b_sr(p, w, r, rand)
        r_s = w.laenge(f"r_s{k}", f"r_{{s{k}}}",
                       max(eingabe.groesse.si, 2.0 / 3.0 * b_sr.groesse.si),
                       f"Abstand zum Momentennullpunkt in {k}", stellen=0)
        p.formel(r_s, r"\max\left[@r_s;\ \frac{2}{3} \cdot @b_sr\right]",
                 {"r_s": eingabe, "b_sr": b_sr},
                 titel=f"Abstand zum Momentennullpunkt in {k}: am Plattenrand mindestens "
                       f"2/3 · b_sr", referenz="SIA 262:2025, 4.3.6.4.8",
                 name="Abstand zum Momentennullpunkt am Plattenrand")
        return r_s


class Durchstanzen(Stuetzenrechnung, Nachweis):
    """Der Durchstanznachweis an einer Durchstanzstelle -- siehe Dateikopf."""

    THEMA = "Durchstanzen"
    ART = "DS"
    LANGNAME = "Durchstanzen"

    def __init__(self, stelle: Durchstanzstelle) -> None:
        self.stelle = stelle
        basis = f"{stelle.id}.nachweis.durchstanzen"
        self.d_ohne: WertDef = grad_def(
            f"{basis}.ohne.erfuellungsgrad", r"\alpha_{eff,DS}",
            "Erfüllungsgrad Durchstanzen ohne Durchstanzbewehrung", "SIA 262:2025, 4.3.6.3")
        # Die Grade mit Durchstanzbewehrung (4.3.6.5.1). Braucht es keine, oder
        # schlägt das Werkzeug keine vor, fällt kein Urteil, und der Kern setzt
        # sie unbeschränkt.
        self.d_mit: WertDef = grad_def(
            f"{basis}.mit.erfuellungsgrad", r"\alpha_{eff,DS,s}",
            "Erfüllungsgrad der Durchstanzbewehrung", "SIA 262:2025, 4.3.6.5.2")
        self.d_verformung: WertDef = grad_def(
            f"{basis}.verformung.erfuellungsgrad", r"\alpha_{eff,DS,v}",
            "Erfüllungsgrad Verformungsvermögen", "SIA 262:2025, 4.3.6.5.3")
        self.d_diagonale: WertDef = grad_def(
            f"{basis}.diagonale.erfuellungsgrad", r"\alpha_{eff,DS,max}",
            "Erfüllungsgrad erste Betondruckdiagonale", "SIA 262:2025, 4.3.6.5.8")
        self.d_aussen: WertDef = grad_def(
            f"{basis}.aussen.erfuellungsgrad", r"\alpha_{eff,DS,out}",
            "Erfüllungsgrad ausserhalb der Durchstanzbewehrung oder des Stahlpilzes",
            "SIA 262:2025, 4.3.6.5.10; 4.3.6.6.2")
        # Je Plattenbereich der Grad an seiner Stufe; wo sie keinen Schnitt
        # hat, fällt kein Urteil.
        self.d_stufen: Dict[str, WertDef] = {b.name: grad_def(
            f"{basis}.stufe.{b.name}.erfuellungsgrad", rf"\alpha_{{eff,DS,{b.name}}}",
            f"Erfüllungsgrad an der Stufe von {b.titel}", stufen.REFERENZ)
            for b in stelle.bereiche}
        # Am Schnitt durch verschiedene Dicken; ohne Bereich neben der Stütze kein Urteil.
        self.d_weg: WertDef = grad_def(
            f"{basis}.weg.erfuellungsgrad", r"\alpha_{eff,DS,W}",
            f"Erfüllungsgrad am Schnitt {weg.NAME}", weg.REFERENZ)
        bezuege = [Eingabebezug(n, stelle.id_von(n)) for n in stelle.eingaben()]
        bezuege += [stelle.beton.bezug(k) for k in ("f_ck", "f_ctm", "f_cd", "tau_cd")]
        bezuege += [stelle.stahl.bezug(k) for k in ("f_yd", "E_s")]
        bezuege += [stelle.anker.bezug(k) for k in ("f_yd", "E_s")]
        super().__init__(basis, ausgaben=[self.d_ohne, *self.mit_graden, *self.d_stufen.values(),
                                          *([self.d_weg] if stelle.bereiche else [])],
                         bezuege=bezuege,
                         titel=f"Durchstanzen – {stelle.name}", referenz="SIA 262:2025, 4.3.6",
                         abschnitt=stelle.abschnitt)

    @property
    def mit_graden(self) -> Tuple[WertDef, ...]:
        """
        Die vier Grade mit Durchstanzbewehrung: die drei Nachweise nach
        4.3.6.5.1, der erste geteilt in den Beitrag der Bewehrung (66), (68)
        und das Verformungsvermögen (67).
        """
        return (self.d_mit, self.d_verformung, self.d_diagonale, self.d_aussen)

    def _stufen_pruefen(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Stuetzenschnitt,
                        r: Widerstand) -> Tuple[List[NachweisUrteil], Tuple[Stufenbefund, ...]]:
        """Die Schnitte an den Stufen, je mit eigenem Urteil (4.3.6.2.7)."""
        urteile: List[NachweisUrteil] = []
        befunde: List[Stufenbefund] = []
        for st in g.stufen:
            werte = self._stufe_schreiben(e, p, w, g, r, st)
            if werte is None:
                befunde.append(Stufenbefund(st))
                continue
            V, V_Rd_c = werte
            v = stufen.vergleich_schreiben(p, st, V, V_Rd_c)
            ziel = self.d_stufen[st.bereich.name]
            v.zeile(p, ziel)
            urteile.append(self.urteil(
                ziel, f"an der Stufe von {st.bereich.titel}", v,
                f"V_d = {V.formatiert()} kN {'≤' if v.erfuellt else '>'} "
                f"V_Rd,c = {V_Rd_c.formatiert()} kN an der Stufe."))
            befunde.append(Stufenbefund(st, V_Rd_c.groesse.si))
        return urteile, tuple(befunde)

    def _weg_pruefen(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Stuetzenschnitt,
                     r: Widerstand) -> Tuple[List[NachweisUrteil], Optional[Wegbefund]]:
        """Der Schnitt durch verschiedene Dicken, mit eigenem Urteil (:mod:`.weg`)."""
        if g.netz is None:
            return [], None
        ws = g.netz.schnitt(r.psi.groesse.si, r.k_g.groesse.si, r.tau_cd.groesse.si)
        if ws is None:
            p.titel(f"Schnitt {weg.NAME}", ebene=3)
            p.text(g.netz.warum_keiner)
            return [], None
        V, V_Rd_c = self._weg_schreiben(e, p, w, g, r, ws)
        v = Vergleich(V, V_Rd_c)
        v.bedingung(p, f"Querkraft gegen den Widerstand am Schnitt {weg.NAME}")
        v.zeile(p, self.d_weg)
        urteil = self.urteil(self.d_weg, f"am Schnitt {weg.NAME}", v,
                             f"V_d = {V.formatiert()} kN {'≤' if v.erfuellt else '>'} "
                             f"V_Rd,c = {V_Rd_c.formatiert()} kN am Schnitt {weg.NAME}.")
        return [urteil], Wegbefund(ws, V_Rd_c.groesse.si)

    def _platz(self, e: Eingaben, g: Stuetzenschnitt) -> mit_bewehrung.Platz:
        """
        Wo die Leisten an der Stütze liegen dürfen: im innersten Bereich um sie,
        so hoch, wie er dick ist, und ausserhalb aller Bereiche, die sie nicht
        umschliessen. Ohne Bereiche, und an Wänden, in der ganzen Platte.
        """
        if g.hoehe is None or g.bereiche is None or g.dicken is None:
            return mit_bewehrung.Platz(e["h"])
        um = g.hoehe.um[:1]
        return mit_bewehrung.Platz(
            g.bereiche.dicken[um[0].name] if um else e["h"], um,
            tuple(b for b in self.stelle.bereiche if b not in g.hoehe.um),
            g.dicken.aussen(um[0]) if um else None)

    def _ohne_eigene(self, p: Protokoll, weitere: List[NachweisUrteil], *,
                     an_der_stuetze: bool) -> None:
        """
        Ein Hinweis, wo ein Schnitt an einer Stufe oder durch verschiedene
        Dicken nicht hält: dort schlägt das Werkzeug noch keine Bewehrung vor,
        und die Leisten an der Stütze, wo es welche gibt, zählen nicht.
        """
        offen = [u.fall for u in weitere if not u.erfuellt]
        if not offen:
            return
        wo = aufgezaehlt(offen)
        wo = wo[0].upper() + wo[1:]
        system = self.stelle.system.regeln
        p.hinweis(f"{wo} zählen die {system.LEISTEN} an der Stütze nicht, und eigene schlägt das "
                  f"Werkzeug dort noch nicht vor." if an_der_stuetze else
                  f"{wo} schlägt das Werkzeug noch keine Durchstanzbewehrung vor.")

    def nicht_fuehrbar(self, grund: str) -> List[NachweisUrteil]:
        """Die vier Urteile mit Durchstanzbewehrung, wo sich keine finden liess."""
        return [self.urteil(d, fall, NICHT_FUEHRBAR, grund) for d, fall in zip(
            self.mit_graden, ("mit Durchstanzbewehrung", "Verformungsvermögen",
                              "Betondruckdiagonale", "ausserhalb der Durchstanzbewehrung"))]

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        s, f = self.stelle, self.stelle.flaeche
        w = Zwischenwerte(self.id)
        p.titel("Durchstanzen")
        p.erklaerung(
            f"{f.lage.beschriftung} einer {s.plattenart.beschriftung}. Die Querkraft "
            f"fliesst im Bereich der gestützten Fläche auf einen Kegel zu; ohne "
            f"Durchstanzbewehrung trägt ihn der Beton allein. Wie viel, hängt davon ab, "
            f"wie stark sich die Platte über der Stütze verdreht: je grösser die "
            f"Rotation ψ, desto breiter der kritische Schubriss und desto kleiner k_r.")
        g = self._schnitt(e, p, w, e.g("V_d").si)
        p.titel("Bemessungswert der Querkraft", ebene=3)
        V_d = herleitung.querkraft(p, w, e, g.innen, ix=STUETZE,
                                   titel_last=f"{s.plattenart.last} innerhalb des Nachweisschnitts",
                                   titel="Bemessungswert der Querkraft im Nachweisschnitt")
        r = self._widerstand(e, p, w, g, e["V_d"])
        psi, V_Rd_c = r.psi, r.V_Rd_c
        umriss = tuple(f.umriss(g.masse, g.d_v.groesse.si))
        befund = Durchstanzbefund(
            d=g.d.groesse.si, innen=g.innen, rotationen=r.rotationen, psi=psi.groesse.si,
            k_r=r.k_r.groesse.si, V_Rd_c=V_Rd_c.groesse.si, umriss=umriss,
            aussparungen=tuple(s.aussparungen),
            raender=tuple(((h.c * h.n[0], h.c * h.n[1]), math.atan2(-h.n[1], -h.n[0]))
                          for h in f.raender(g.masse)),
            lagen=tuple(Biegelage(lage, e.g("h").si - g.hoehen[lage].groesse.si,
                                  e.g(f"phi_{lage.value}").si, e.g(f"s_{lage.value}").si)
                        for lage in (s.aussen, s.aussen.gegenrichtung)),
            stufen=tuple(Stufenbefund(st) for st in g.stufen))
        if befund.ohne_einwirkung:
            # Ohne Stützenkraft ist nichts durchzustanzen -- bis 2026-11-19 stand
            # eine frische Stelle als «erfüllt, ∞» in der Zusammenfassung.
            p.text(OHNE_EINWIRKUNG)
            return Ausfuehrung({}, [self.urteil(self.d_ohne, "ohne Durchstanzbewehrung",
                                                UNBESCHRAENKT, OHNE_EINWIRKUNG)], befund)
        p.hinweis(EINZELLASTEN)
        v = Vergleich(V_d, V_Rd_c)
        v.bedingung(p, "Querkraft gegen Durchstanzwiderstand")
        v.zeile(p, self.d_ohne)
        an_stufen, stufenbefunde = self._stufen_pruefen(e, p, w, g, r)
        an_weg, wegbefund = self._weg_pruefen(e, p, w, g, r)
        weitere = [*an_stufen, *an_weg]
        befund = replace(befund, stufen=stufenbefunde, weg=wegbefund)
        if not v.erfuellt and f.vorschlag:
            platz = self._platz(e, g)
            urteile, leisten, pilz = mit_bewehrung.nachweisen(self, e, p, w, Grundlage(
                innen=g.innen, d=g.d, d_v=g.d_v, k_e=g.k_e, k_r=r.k_r, tau_cd=r.tau_cd, u=g.u,
                psi=psi, V_d=V_d, V_Rd_c=V_Rd_c, masse=g.masse, umriss=umriss), platz)
            self._ohne_eigene(p, weitere, an_der_stuetze=leisten is not None)
            # Der Grad ohne Bewehrung bleibt ein Wert der Herleitung, ohne Urteil.
            return Ausfuehrung({self.d_ohne.id: Groesse(v.grad, EINHEITSLOS)},
                               [*urteile, *weitere],
                               replace(befund, leisten=leisten, pilz=pilz, platz=platz))
        alle = v.erfuellt and all(u.erfuellt for u in weitere)
        if not alle and not f.vorschlag:
            p.hinweis(f"Für {f.lage.mehrzahl} schlägt das Werkzeug noch keine "
                      f"Durchstanzbewehrung vor.")
        elif not alle:
            self._ohne_eigene(p, weitere, an_der_stuetze=False)
        elif psi.groesse.si <= ROTATION_MINDEST:
            p.hinweis(
                f"ψ = {psi.formatiert()} ≤ {ROTATION_MINDEST:.3f}: das Verformungsvermögen ist "
                f"ohne Durchstanzbewehrung nach Gleichung (67) nicht nachgewiesen – sonst "
                f"sind die aufgezwungenen Verformungen nach 4.1.2 zu berücksichtigen "
                f"(4.3.6.1.2).")
        if alle:
            p.hinweis("Ohne Durchstanzbewehrung, die Bedingung (67) erfüllt, braucht es eine "
                      "Sicherung gegen Totaleinsturz nach 4.3.6.7 (4.3.6.1.3).")
        urteil = self.urteil(
            self.d_ohne, "ohne Durchstanzbewehrung", v,
            f"V_d = {V_d.formatiert()} kN {'≤' if v.erfuellt else '>'} "
            f"V_Rd,c = {V_Rd_c.formatiert()} kN.")
        return Ausfuehrung({}, [urteil, *weitere], befund)


# ===========================================================================
# Für die Zusammenfassung
# ===========================================================================


def angaben(stelle: Durchstanzstelle, werte: Dict[str, Wert]) -> GleichungBlock:
    """Was über der Tabelle steht: Lage, Platte, Beton und die Masse, wie gerechnet."""
    teile = [als_text(f"{stelle.flaeche.lage.beschriftung}, {stelle.plattenart.beschriftung}, "
                      f"Beton {stelle.beton.name}")]
    teile += [angabe(werte[stelle.id_von(n)]) for n in ("h", *stelle.flaeche.masse)
              if stelle.id_von(n) in werte]
    return GleichungBlock(latex=r" \qquad ".join(teile), titel="Angaben zur Durchstanzstelle")


def kennwerttabelle(befund: Durchstanzbefund) -> TabellenBlock:
    """
    Die Grössen, aus denen der Widerstand entsteht -- eine Zeile je Grösse. Mit
    Stahlpilz und Durchstanzbewehrung dazu, was sie sind und was sie tragen.
    Ohne Einwirkung nur der Schnitt: ψ = 0 und k_r = 2 gälten nur ohne Last;
    was die Stelle trägt, sagt die Kennzahl (:mod:`.kennzahl`). Bis 2026-11-27
    stand dort V_Rd,c = 866.7 kN, wo die Kennzahl 503.6 kN sagt.
    """
    def zeile(text: str, zeichen: str, wert: str, einheit: str) -> list:
        return [text, Mathe(zeichen), Mathe(wert), einheit]

    def kraft(x: float) -> str:
        return f"{x / 1e3:.1f}"

    innen = befund.innen
    zeilen = [
        zeile("Wirksame statische Höhe", "d_v", f"{innen.d_v * 1e3:.0f}", "mm"),
        zeile("Nachweisschnitt, wirksam", "u", f"{innen.u * 1e3:.0f}", "mm"),
        zeile("Momentenübertragung", "k_e", f"{innen.k_e:.3f}", "–"),
    ]
    if not befund.ohne_einwirkung:
        zeilen += [
            zeile("Plattenrotation", r"\psi", f"{befund.psi:.4f}", "–"),
            zeile("Beiwert", "k_r", f"{befund.k_r:.3f}", "–"),
            zeile("Querkraft im Schnitt", "V_d", kraft(innen.V_d_red), "kN"),
            zeile("Widerstand ohne Durchstanzbewehrung", "V_{Rd,c}", kraft(befund.V_Rd_c), "kN"),
        ]
        for x in befund.stufen:
            if x.V_Rd_c is None:
                continue
            b = x.stufe.bereich
            zeilen += [
                zeile(f"Querkraft an der Stufe von {b.titel}", f"V_{{d,{b.name}}}",
                      kraft(x.stufe.pruefung.V_d_red), "kN"),
                zeile(f"Widerstand an der Stufe von {b.titel}", f"V_{{Rd,c,{b.name}}}",
                      kraft(x.V_Rd_c), "kN"),
            ]
        if befund.weg is not None:
            zeilen += [
                zeile(f"Querkraft im Schnitt {weg.NAME}", "V_{d,W}",
                      kraft(befund.weg.schnitt.last.V_d_red), "kN"),
                zeile(f"Widerstand am Schnitt {weg.NAME}", "V_{Rd,c,W}",
                      kraft(befund.weg.V_Rd_c), "kN"),
            ]
    pilz, leisten = befund.pilz, befund.leisten
    if pilz is not None:
        zeilen += [
            ["Stahlpilz", "", pilz.pilz.name, ""],
            zeile("Querkraft um den Stahlpilz", "V_{d,P}", kraft(pilz.pruefung.V_d_red), "kN"),
            zeile("Widerstand um den Stahlpilz", "V_{Rd,c,P}", kraft(pilz.V_Rd_c), "kN"),
        ]
    if leisten is not None:
        v = leisten.vorschlag
        zeilen += [
            ["Durchstanzbewehrung", "", v.name, ""],
            zeile("Abstände ab Stütze" if pilz is None else "Abstände ab Pilz", "s",
                  " / ".join(f"{a * 1e3:.0f}" for a in v.abstaende), "mm"),
            zeile("Beitrag der Bewehrung", "V_{Rd,s}", kraft(leisten.V_Rd_s), "kN"),
            zeile("Erste Betondruckdiagonale", "V_{Rd,max}", kraft(leisten.V_Rd_max), "kN"),
            zeile("Querkraft ausserhalb", "V_{d,out}", kraft(leisten.aussen.V_d_red), "kN"),
            zeile("Widerstand ausserhalb", "V_{Rd,c,out}", kraft(leisten.V_Rd_c_aussen), "kN"),
        ]
    return TabellenBlock(kopf=["Grösse", "Zeichen", "Wert", "Einheit"], zeilen=zeilen,
                         titel="Durchstanzen", ausrichtung="llrl")
