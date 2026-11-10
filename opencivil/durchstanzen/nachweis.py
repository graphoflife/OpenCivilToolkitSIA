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

DIE PLATTENROTATION (4.3.6.4.2):
In Näherungsstufe 1 ist ``m_sd/m_Rd = 1``; in Stufe 2 kommen die Momente im
Stützstreifen aus den Gleichungen (62) bis (65), in Stufe 3 gibt sie der
Benutzer an, mit 1.2 statt 1.5 vor der Klammer. ``r_s = 0.22 · l`` in den
Stufen 1 und 2 (4.3.6.4.4). Massgebend ist die grössere Rotation der beiden
Richtungen. Für Wandende und Wandecke nennt 4.3.6.4.7 keine Momente; dort
rechnet Stufe 2 wie Stufe 1, und die Herleitung sagt es.

DIE BREITE DER STÜTZSTREIFEN (Figur 25), gelesen (nicht nachgeschlagen):
``b_s = 1.5 · √(r_sx · r_sy) ≤ l_min``. Ein Streifen senkrecht zum Rand einer
Randstütze und die Randstreifen einer Eckstütze sind auf ``b_sr`` begrenzt:
die Breite, die zwei Linien unter 45° von den inneren Ecken der Stütze am
Plattenrand einschliessen, ``b_sr = b_x + 2 · (b_y + a_y)`` für den Streifen
in y, entsprechend in x, höchstens ``b_s``.

EINHEITEN:
SI-Basis; wo die Norm in mm rechnet (59), sagt es die Herleitung.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.nachweis import NICHT_FUEHRBAR, Nachweis, NachweisUrteil, Vergleich, grad_def
from opencivil.core.einheiten import EINHEITSLOS, KNM_PRO_M, M2, MM, MM2_PRO_M, Groesse
from opencivil.core.latex import Mathe, als_text, angabe
from opencivil.core.protokoll import GleichungBlock, Protokoll, TabellenBlock, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.durchstanzen import herleitung, mit_bewehrung
from opencivil.durchstanzen.herleitung import STUETZE
from opencivil.durchstanzen.flaeche import Randbreite
from opencivil.durchstanzen.mit_bewehrung import Grundlage
from opencivil.durchstanzen.pruefung import Leistenpruefung, Pilzbefund, Schnittpruefung
from opencivil.durchstanzen.schnitt import Auswertung, Punkt, nachweisschnitt
from opencivil.durchstanzen.stelle import (
    Durchstanzstelle, KeArt, Naeherungsstufe, wirksame_stufe,
)
from opencivil.nachweis.querkraft_ohne_buegel import beiwert_k_g
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL

#: Obere Grenze von k_r (SIA 262:2025, Gleichung (59)).
K_R_GRENZE = 2.0

#: ``r_s = R_S · l`` in den Näherungsstufen 1 und 2 (SIA 262:2025, 4.3.6.4.4).
R_S = 0.22

#: Unter dieser Plattenrotation fehlt Verformungsvermögen, wenn keine
#: Durchstanzbewehrung nach (67) liegt (SIA 262:2025, 4.3.6.1.2).
ROTATION_MINDEST = 0.020


@dataclass(frozen=True)
class Rotation:
    """Die Plattenrotation in einer Richtung: r_s, m_sd/m_Rd und ψ."""

    richtung: Richtung
    r_s: float
    m_sd: Optional[float]
    m_Rd: Optional[float]
    psi: float


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

    leisten: Optional[Leistenpruefung] = None
    """Die vorgeschlagene Durchstanzbewehrung mit ihren vier Nachweisen."""

    pilz: Optional[Pilzbefund] = None
    """Der gewählte Stahlpilz; mit ``leisten`` stehen die Leisten um ihn."""


class Durchstanzen(Nachweis):
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
            "Erfüllungsgrad ausserhalb der Durchstanzbewehrung", "SIA 262:2025, 4.3.6.5.10")
        bezuege = [Eingabebezug(n, stelle.id_von(n)) for n in stelle.eingaben()]
        bezuege += [stelle.beton.bezug(k) for k in ("f_ck", "f_ctm", "f_cd", "tau_cd")]
        bezuege += [stelle.stahl.bezug(k) for k in ("f_yd", "E_s")]
        super().__init__(basis, ausgaben=[self.d_ohne, *self.mit_graden], bezuege=bezuege,
                         titel=f"Durchstanzen – {stelle.name}", referenz="SIA 262:2025, 4.3.6",
                         abschnitt=stelle.abschnitt)

    @property
    def mit_graden(self) -> Tuple[WertDef, ...]:
        """Die Grade der vier Nachweise mit Durchstanzbewehrung (4.3.6.5.1)."""
        return (self.d_mit, self.d_verformung, self.d_diagonale, self.d_aussen)

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
        masse = {k: e.g(k).si for k in f.masse}
        d, d_v, hoehen = self._statische_hoehe(e, p, w)
        dv = d_v.groesse.si
        schnitt = nachweisschnitt(f.kandidaten(masse, dv / 2.0, dv), d_v=dv,
                                  achse=f.achse(masse), aussparungen=s.aussparungen)
        a = schnitt.massgebend
        u_red = self._nachweisschnitt(e, p, w, a, d_v)
        e_u = self._exzentrizitaet(e, a, masse)
        k_e = self._k_e(e, p, w, a, e_u)
        innen = Schnittpruefung(schnitt, dv, k_e.groesse.si, e.g("V_d").si, e.g("q_d").si)
        u = herleitung.wirksam(p, w, k_e, u_red, ix=STUETZE,
                               titel="Wirksamer Umfang des Nachweisschnitts")
        p.titel("Bemessungswert der Querkraft", ebene=3)
        V_d = herleitung.querkraft(p, w, e, innen, ix=STUETZE,
                                   titel_last=f"{s.plattenart.last} innerhalb des Nachweisschnitts",
                                   titel="Bemessungswert der Querkraft im Nachweisschnitt")
        rotationen, psi = self._rotation(e, p, w, d, hoehen, V_d, e_u, masse)
        k_r = self._k_r(e, p, w, psi, d)
        tau = e[s.beton.eingabename("tau_cd")]
        tau_cd = w.wert("tau_cd", tau.symbol, tau.groesse, 4)
        V_Rd_c = herleitung.widerstand(p, w, innen, ix=STUETZE, k_r=k_r, tau_cd=tau_cd, d_v=d_v,
                                       u=u, titel="Durchstanzwiderstand ohne Durchstanzbewehrung",
                                       referenz="SIA 262:2025, 4.3.6.3.1")
        v = Vergleich(V_d, V_Rd_c)
        v.bedingung(p, "Querkraft gegen Durchstanzwiderstand")
        v.zeile(p, self.d_ohne, mit_urteil=True)
        umriss = tuple(f.umriss(masse, dv))
        befund = Durchstanzbefund(
            d=d.groesse.si, innen=innen, rotationen=rotationen, psi=psi.groesse.si,
            k_r=k_r.groesse.si, V_Rd_c=V_Rd_c.groesse.si, umriss=umriss,
            aussparungen=tuple(s.aussparungen),
            raender=tuple(((h.c * h.n[0], h.c * h.n[1]), math.atan2(-h.n[1], -h.n[0]))
                          for h in f.raender(masse)))
        if not v.erfuellt and f.vorschlag:
            urteile, leisten, pilz = mit_bewehrung.nachweisen(self, e, p, w, Grundlage(
                innen=innen, d=d, d_v=d_v, k_e=k_e, k_r=k_r, tau_cd=tau_cd, u=u, psi=psi,
                V_d=V_d, V_Rd_c=V_Rd_c, masse=masse, umriss=umriss))
            # Der Grad ohne Bewehrung bleibt ein Wert der Herleitung, ohne Urteil.
            return Ausfuehrung({self.d_ohne.id: Groesse(v.grad, EINHEITSLOS)}, urteile,
                               replace(befund, leisten=leisten, pilz=pilz))
        if not v.erfuellt:
            p.hinweis(f"Für {f.lage.mehrzahl} schlägt das Werkzeug noch keine "
                      f"Durchstanzbewehrung vor.")
        elif psi.groesse.si <= ROTATION_MINDEST:
            p.hinweis(
                f"ψ = {psi.formatiert()} ≤ {ROTATION_MINDEST:.3f}: das Verformungsvermögen ist "
                f"ohne Durchstanzbewehrung nach Gleichung (67) nicht nachgewiesen -- sonst "
                f"sind die aufgezwungenen Verformungen nach 4.1.2 zu berücksichtigen "
                f"(4.3.6.1.2).")
        if v.erfuellt:
            p.hinweis("Ohne Durchstanzbewehrung, die Bedingung (67) erfüllt, braucht es eine "
                      "Sicherung gegen Totaleinsturz nach 4.3.6.7 (4.3.6.1.3).")
        urteil = self.urteil(
            self.d_ohne, "ohne Durchstanzbewehrung", v,
            f"V_d = {V_d.formatiert()} kN {'≤' if v.erfuellt else '>'} "
            f"V_Rd,c = {V_Rd_c.formatiert()} kN.")
        return Ausfuehrung({}, [urteil], befund)

    # -- Statische Höhe -----------------------------------------------------

    def _statische_hoehe(self, e: Eingaben, p: Protokoll,
                         w: Zwischenwerte) -> Tuple[Wert, Wert, Dict[Richtung, Wert]]:
        """Die statischen Höhen der beiden Lagen, ihr Mittel d und die wirksame d_v (4.3.6.2.1)."""
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
        d_v = w.laenge("d_v", "d_v", d.groesse.si)
        p.formel(d_v, "@d", {"d": d},
                 titel="Wirksame statische Höhe: die gestützte Fläche reicht nicht in die Platte",
                 referenz="SIA 262:2025, 4.3.6.2.1, Figur 21", name="Wirksame Höhe ohne Abzug")
        return d, d_v, hoehen

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

    def _exzentrizitaet(self, e: Eingaben, a: Auswertung,
                        masse: Dict[str, float]) -> Tuple[float, float]:
        """
        e_u: von dem Schwerpunkt der zählenden Teile des Schnitts zur Resultierenden
        der Auflagerkraft -- je Komponente, in m.
        """
        ax, ay = self.stelle.flaeche.achse(masse)
        ex = e.g("e_x").si if e.hat("e_x") else 0.0
        ey = e.g("e_y").si if e.hat("e_y") else 0.0
        return (ax + ex - a.schwerpunkt[0], ay + ey - a.schwerpunkt[1])

    def _k_e(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, a: Auswertung,
             e_u: Tuple[float, float]) -> Wert:
        """Der Beiwert k_e: aus der Näherung (4.3.6.2.5) oder aus der Exzentrizität (57)."""
        s = self.stelle
        p.titel("Momentenübertragung", ebene=3)
        if s.ke is KeArt.NAEHERUNG:
            k, titel = s.flaeche.k_e_naeherung(a)
            k_e = w.zahl("k_e", "k_e", k, stellen=2)
            p.erklaerung(
                "Bei regelmässig gestützten Flachdecken mit gleichmässigen angrenzenden "
                "Spannweiten und biegesteif angeschlossenen Stützen, die nicht für die "
                "Aufnahme horizontaler Einwirkungen ausgelegt sind, darf k_e näherungsweise "
                "angenommen werden.")
            p.wert(k_e, titel=titel, referenz="SIA 262:2025, 4.3.6.2.5")
            return k_e
        A = w.wert("A_u", "A_u", Groesse.aus_si(a.flaeche, M2), 3,
                   "Fläche innerhalb des Nachweisschnitts")
        p.wert(A, titel="Fläche innerhalb des Nachweisschnitts", referenz="SIA 262:2025, Figur 22")
        b = w.laenge("b", "b", math.sqrt(4.0 * a.flaeche / math.pi), stellen=0)
        p.formel(b, r"\sqrt{\frac{4 \cdot @A_u}{\pi}}", {"A_u": A},
                 titel="Durchmesser des flächengleichen Kreises", referenz="SIA 262:2025, 4.3.6.2.4")
        e_u_si = math.hypot(*e_u)
        e_u_w = w.laenge("e_u", "e_u", e_u_si, stellen=0)
        p.erklaerung(
            "e_u ist der Abstand zwischen der Resultierenden der Auflagerkraft -- in der "
            "Stützenachse, verschoben um die Exzentrizität e_x, e_y -- und dem Schwerpunkt der "
            "zählenden Teile des Nachweisschnitts.")
        p.wert(e_u_w, titel="Exzentrizität zum Schwerpunkt des Nachweisschnitts",
               referenz="SIA 262:2025, 4.3.6.2.4")
        k_e = w.zahl("k_e", "k_e", 1.0 / (1.0 + e_u_si / b.groesse.si), stellen=3)
        p.formel(k_e, r"\frac{1}{1 + \frac{@e_u}{@b}}", {"e_u": e_u_w, "b": b},
                 titel="Beiwert der Momentenübertragung", referenz="SIA 262:2025, 4.3.6.2.4, (57)")
        return k_e

    # -- Plattenrotation ----------------------------------------------------

    def _rotation(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, d: Wert,
                  hoehen: Dict[Richtung, Wert], V_d: Wert, e_u: Tuple[float, float],
                  masse: Dict[str, float]) -> Tuple[Tuple[Rotation, ...], Wert]:
        """ψ je Richtung und die massgebende -- die grössere (4.3.6.4.1)."""
        s = self.stelle
        p.titel("Plattenrotation", ebene=3)
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
                                     "Berechnung nach der Elastizitätstheorie; 1.2 statt 1.5 "
                                     "vor der Klammer."}[stufe])
        f_yd, E_s = e[s.stahl.eingabename("f_yd")], e[s.stahl.eingabename("E_s")]
        r_s: Dict[Richtung, Wert] = {}
        for r in (Richtung.X, Richtung.Y):
            k = r.value
            if stufe is Naeherungsstufe.DREI:
                r_s[r] = e[f"r_s{k}"]
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
                m_sd = self._m_sd(e, p, w, r_s, V_d, e_u, masse)
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
                          f"nicht -- der Biegenachweis gehört dazu.")
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
                 titel=f"Druckzonenhöhe in {k}, je Meter", name="Druckzonenhöhe im Stützstreifen")
        m_si = a_s_si * f_yd.groesse.si * (d_r.groesse.si - BLOCKANTEIL * x_si / 2.0)
        m = w.wert(f"m_Rd{k}", f"m_{{Rd,{k}}}", Groesse.aus_si(m_si, KNM_PRO_M), 1)
        p.formel(m, rf"@a_s \cdot @f_yd \cdot \left(@d - \frac{{{BLOCKANTEIL} \cdot @x}}{{2}}\right)",
                 {"a_s": a_s, "f_yd": f_yd, "d": d_r, "x": x},
                 titel=f"Biegewiderstand im Stützstreifen in {k}", referenz="SIA 262:2025, 4.3.6.4.5",
                 name="Biegewiderstand im Stützstreifen")
        return m

    def _m_sd(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r_s: Dict[Richtung, Wert],
              V_d: Wert, e_u: Tuple[float, float],
              masse: Dict[str, float]) -> Dict[Richtung, Optional[Wert]]:
        """Die mittleren Momente im Stützstreifen in Näherungsstufe 2 (4.3.6.4.7)."""
        s = self.stelle
        l_min = min(e.g("l_x").si, e.g("l_y").si)
        b_s_si = min(1.5 * math.sqrt(r_s[Richtung.X].groesse.si * r_s[Richtung.Y].groesse.si), l_min)
        b_s = w.laenge("b_s", "b_s", b_s_si, stellen=0)
        p.formel(b_s, r"\min\left[1.5 \cdot \sqrt{@r_sx \cdot @r_sy};\ @l_min\right]",
                 {"r_sx": r_s[Richtung.X], "r_sy": r_s[Richtung.Y],
                  "l_min": w.laenge("l_min", "l_{min}", l_min, stellen=0)},
                 titel="Breite des Stützstreifens", referenz="SIA 262:2025, 4.3.6.4.6, (61)")
        V = V_d.groesse.si
        ergebnis: Dict[Richtung, Optional[Wert]] = {}
        for r, e_i in ((Richtung.X, e_u[0]), (Richtung.Y, e_u[1])):
            k = r.value
            e_w = w.laenge(f"e_u{k}", f"e_{{u,{k}}}", abs(e_i), stellen=0)
            g = s.flaeche.momentengleichung(r, masse)
            breite = b_s if g.rand is None else self._b_sr(p, w, r, b_s, g.rand)
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

    def _b_sr(self, p: Protokoll, w: Zwischenwerte, r: Richtung, b_s: Wert,
              rand: Randbreite) -> Wert:
        """
        Die Breite eines Streifens senkrecht zum Rand oder eines Randstreifens an
        der Ecke (Figur 25) -- siehe Dateikopf.
        """
        quer, laengs, a = rand.quer, rand.laengs, rand.abstand
        breite_si = quer.wert + 2.0 * (laengs.wert + a.wert)
        b_sr = w.laenge(f"b_sr{r.value}", f"b_{{sr,{r.value}}}", min(b_s.groesse.si, breite_si),
                        stellen=0)
        p.formel(b_sr, r"\min\left[@b_s;\ @quer + 2 \cdot \left(@laengs + @a\right)\right]",
                 {"b_s": b_s,
                  "quer": w.laenge(quer.name, quer.zeichen, quer.wert, stellen=0),
                  "laengs": w.laenge(laengs.name, laengs.zeichen, laengs.wert, stellen=0),
                  "a": w.laenge(a.name, a.zeichen, a.wert, stellen=0)},
                 titel=f"Breite des Stützstreifens in {r.value}, durch den Plattenrand begrenzt",
                 referenz="SIA 262:2025, 4.3.6.4.6, Figur 25",
                 name="Breite des Stützstreifens am Plattenrand")
        return b_sr

    # -- k_r ----------------------------------------------------------------

    def _k_r(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, psi: Wert, d: Wert) -> Wert:
        """Der Beiwert k_r (59), mit k_g nach 4.3.3.2.1."""
        p.titel("Durchstanzwiderstand", ebene=3)
        k_g = beiwert_k_g(p, self.id, e["D_max"], e[self.stelle.beton.eingabename("f_ck")])
        k_r_si = min(K_R_GRENZE, 1.0 / (0.45 + 0.18 * psi.groesse.si * d.groesse.si * 1e3
                                         * k_g.groesse.si))
        k_r = w.zahl("k_r", "k_r", k_r_si, stellen=3)
        p.formel(k_r, rf"\min\left[{K_R_GRENZE:g};\ \frac{{1}}{{0.45 + 0.18 \cdot @psi \cdot @d "
                      r"\cdot @k_g}\right]",
                 {"psi": psi, "d": d, "k_g": k_g}, empirisch={"d": MM},
                 titel="Beiwert für Bauteilgrösse, Plattenrotation und Grösstkorn",
                 referenz="SIA 262:2025, 4.3.6.3.2, (59)", name="Beiwert k_r")
        return k_r


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
        zeile("Plattenrotation", r"\psi", f"{befund.psi:.4f}", "–"),
        zeile("Beiwert", "k_r", f"{befund.k_r:.3f}", "–"),
        zeile("Querkraft im Schnitt", "V_d", kraft(innen.V_d_red), "kN"),
        zeile("Widerstand ohne Durchstanzbewehrung", "V_{Rd,c}", kraft(befund.V_Rd_c), "kN"),
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
