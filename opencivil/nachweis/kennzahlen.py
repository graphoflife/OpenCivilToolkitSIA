"""
opencivil/nachweis/kennzahlen.py -- was eine Platte aufnimmt, ohne Einwirkung.

VERANTWORTUNG:
Die Kennzahlen der Platte in x, gerechnet immer -- ob es Lastfaelle gibt oder
nicht (Benutzer, 2026-10-16). Die Zusammenfassung zeigt sie unter jeder
Platte:

* aus der Handrechnung mit Bemessungswerten: ``M_Rd+`` und ``M_Rd-`` bei
  ``N_Ed = 0``, ``N_Rd+`` und ``N_Rd-`` bei ``M_Ed = 0``, dazu ``x/d`` bei
  ``N_Ed = 0`` je gezogene Seite;
* der Querkraftwiderstand bei ``N_Ed = 0``. Ohne Buegel ``V_Rd,max``, das
  Kleinere beider Seiten bei ``M_Ed = 0``, und ``V_Rd,min``, das Kleinere
  bei ``M_Ed = M_Rd``. Mit Buegeln der Widerstand bei der guenstigsten
  Neigung, ``V_Rd(alpha_opt)`` -- auch er das Kleinere beider Seiten.

x/d je Seite, das Kleinere beider Seiten auch mit Buegeln und die
Handrechnung mit Bemessungswerten hat der Benutzer am 2026-10-16 bestaetigt.

Die Vergroesserungsfaktoren omega_w und omega_w' rechnet
:class:`~opencivil.nachweis.verformung.Vergroesserungsfaktor`; die
Zusammenfassung stellt sie dazu.

WAS FEHLT, FEHLT:
Jede Kennzahl steht mit ihrer Beschriftung hier (:attr:`Plattenkennzahlen.kennzahlen`),
und nur, was die Platte hat: ein x/d gibt es nur fuer eine Seite mit
Zugbewehrung. Bis 2026-10-18 stand fuer die andere 0, und ein Widerstand, den
die Linie nicht traf, ebenfalls -- so hatte eine Platte nur mit oberer
Bewehrung den Druckwiderstand 0 statt -5000 kN.

NICHTS ZWEIMAL:
Rechnet die Tragsicherheit von Hand mit Bemessungswerten -- die Vorgabe --,
lesen die Kennzahlen deren Linie aus ihrem Befund und leiten nichts ein
zweites Mal her; sonst rechnen sie eine eigene, mit Herleitung -- das
entscheidet, wie beim Knicken, die
:class:`~opencivil.nachweis.biegung_normalkraft.Linienquelle`. Die
Querkraft rechnet ihr Nachweis: er liest die
Eingaenge (:attr:`~opencivil.nachweis.querkraft.Querkraft.bezuege_ohne_faelle`),
loest sie (:meth:`~opencivil.nachweis.querkraft_ohne_buegel.QuerkraftOhneBuegel.kurvenbeiwerte`,
:meth:`~opencivil.nachweis.querkraft_buegel.QuerkraftMitBuegeln.buegelwerte`)
und rechnet je Zugseite
(:meth:`~opencivil.nachweis.querkraft_ohne_buegel.Kurvenbeiwerte.widerstand`,
:meth:`~opencivil.nachweis.querkraft_buegel.Buegelwerte.suche`) -- fuer seine
Faelle wie fuer die Kennzahlen. Geschrieben wird mit den Funktionen seiner
Herleitung: :func:`~opencivil.nachweis.querkraft_ohne_buegel.beiwert_k_g`,
:func:`~opencivil.nachweis.querkraft.protokoll_hoehen`,
:func:`~opencivil.nachweis.querkraft_ohne_buegel.protokoll_ohne_buegel` und
:func:`~opencivil.nachweis.querkraft_buegel.protokoll_mit_buegeln`. Bis
2026-10-18 standen ihre Zeilen hier ein zweites Mal, bis 2026-11-20 ihre
Rechnung: Beiwerte, Stahl und Eingaenge eigens zusammengestellt, fuer die
Hoehen ein ``Kurvenbeiwerte`` voller Nullen. Eine neue Buegelgroesse nur im
Nachweis haette den Widerstand unter der Platte still abweichen lassen.

WAS DIE GRENZEN BEDEUTEN:
Ohne Buegel ist bei ``M_Ed = 0`` die Dehnung null und ``k_d = 1``; bei
``M_Ed = M_Rd`` ist sie ``f_yd/E_s``, gleich wie gross ``M_Rd`` ist
(SIA 262:2025, 4.3.3.2.2, Gl. (38)). Dazwischen liegt jeder Widerstand ohne
Normalkraft, solange die Bewehrung elastisch bleibt. Sind plastische
Verformungen nicht auszuschliessen, gilt ``1.5 * f_yd/E_s`` (Gl. (41)), und
der Widerstand liegt unter ``V_Rd,min``.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from opencivil.core.berechnung import BerechnungsFehler, Eingaben, Kennzahlprozedur
from opencivil.core.einheiten import EINHEITSLOS, KN, KN_PRO_M, KNM, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.nachweis import linie as geo
from opencivil.nachweis.biegung_normalkraft import Linienquelle
from opencivil.nachweis.querkraft import protokoll_hoehen, statische_hoehen, zugposten
from opencivil.nachweis.querkraft_buegel import (
    REFERENZ as REFERENZ_MIT_BUEGELN, protokoll_mit_buegeln,
)
from opencivil.nachweis.querkraft_ohne_buegel import (
    REFERENZ as REFERENZ_OHNE_BUEGEL, beiwert_k_g, protokoll_ohne_buegel, tau_cd_wert,
)
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import UM_Y, Zugseite

#: Womit die Kennzahlen rechnen: die Handrechnung mit Bemessungswerten.
WAHL = Rechenwahl()

#: Woher die Eckwerte stammen -- ihre Erklaerung unter der Platte.
HAND = "Handrechnung mit Bemessungswerten"


class Plattenkennzahlen(Kennzahlprozedur):
    """Die Kennzahlen einer Platte in x -- siehe Dateikopf."""

    THEMA = "Kennzahlen"

    def __init__(self, querschnitt, mn, querkraft) -> None:
        self.querschnitt = querschnitt
        self.posten = querschnitt.posten_in_richtung(Richtung.X)
        self.mn = mn
        self.querkraft = querkraft
        """Der Querkraftnachweis in x -- mit seiner Rechnung je Zugseite rechnen die Kennzahlen."""
        self.linienquelle = Linienquelle(WAHL, mn, querschnitt, self.posten, Richtung.X)
        """Woher die Kennzahlen die Linie ihrer Eckwerte nehmen."""

        basis = f"{querschnitt.id}.kennzahlen"
        dazu = self.anlegen(basis)
        dazu("M_Rd_pos", r"M_{Rd}^{+}(N_{Ed} = 0)", KNM,
             "Momentenwiderstand bei N_Ed = 0, Zug unten", "Momentenwiderstand, Zug unten", HAND)
        dazu("M_Rd_neg", r"M_{Rd}^{-}(N_{Ed} = 0)", KNM,
             "Momentenwiderstand bei N_Ed = 0, Zug oben", "Momentenwiderstand, Zug oben", HAND)
        dazu("N_Rd_zug", r"N_{Rd}^{+}(M_{Ed} = 0)", KN,
             "Zugwiderstand bei M_Ed = 0", "Zugwiderstand", HAND)
        dazu("N_Rd_druck", r"N_{Rd}^{-}(M_{Ed} = 0)", KN,
             "Druckwiderstand bei M_Ed = 0", "Druckwiderstand", HAND)
        # Ein x/d nur, wo Zug auf Bewehrung trifft: ohne sie gibt es kein d.
        gezogen = {q.lage.seite for q in self.posten}
        for seite in UM_Y:
            if seite in gezogen:
                dazu(f"x_d_{seite.marke}", rf"\left(x/d\right)^{{{seite.zeichen}}}",
                     EINHEITSLOS, f"Bezogene Druckzonenhöhe bei N_Ed = 0, Zug {seite}",
                     f"Bezogene Druckzonenhöhe, Zug {seite}", HAND, stellen=3)
        # Welcher Ansatz gilt, entscheidet sich hier, einmal: er bestimmt die
        # Kennzahlen der Querkraft und ihre Rechnung.
        if querkraft.buegel is None:
            dazu("V_Rd_max", r"V_{Rd,max}", KN_PRO_M,
                 "Querkraftwiderstand ohne Bügel bei M_Ed = 0 und N_Ed = 0",
                 "Querkraftwiderstand ohne Bügel, grösster",
                 "N_Ed = 0, M_Ed = 0 – das Kleinere beider Seiten",
                 referenz=f"{REFERENZ_OHNE_BUEGEL}, (36)")
            # Der kleinste bei elastischer Bewehrung: ist plastisches Fliessen
            # nicht auszuschliessen, gilt (41), und der Widerstand liegt tiefer.
            dazu("V_Rd_min", r"V_{Rd,min}", KN_PRO_M,
                 "Querkraftwiderstand ohne Bügel bei M_Ed = M_Rd und N_Ed = 0",
                 "Querkraftwiderstand ohne Bügel, kleinster bei elastischer Bewehrung",
                 "N_Ed = 0, M_Ed = M_Rd – das Kleinere beider Seiten",
                 referenz=f"{REFERENZ_OHNE_BUEGEL}, (36); 4.3.3.2.2, (38)")
            self._querkraftteil = self._ohne_buegel
        else:
            dazu("V_Rd_buegel", r"V_{Rd}(\alpha_{opt})", KN_PRO_M,
                 "Querkraftwiderstand mit Bügeln bei der günstigsten Neigung, N_Ed = 0",
                 "Querkraftwiderstand mit Bügeln",
                 "N_Ed = 0, günstigste Neigung – das Kleinere beider Seiten",
                 referenz=REFERENZ_MIT_BUEGELN)
            self._querkraftteil = self._mit_buegeln

        super().__init__(
            basis,
            # Was die Querkraft ohne Fall liest, unter den Namen ihres
            # Nachweises -- und was eine eigene Linie liest, wo es eine gibt.
            bezuege=self.linienquelle.bezuege(querkraft.bezuege_ohne_faelle),
            befunde=self.linienquelle.befunde,
            titel="Kennzahlen",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Kennzahlen")
        p.erklaerung(
            "Was die Platte in x aufnimmt, ohne Bezug auf eine Einwirkung: die "
            "Eckwerte der Handrechnung mit Bemessungswerten und der "
            "Querkraftwiderstand ohne Normalkraft. Wo eine Seite massgebend ist, "
            "gilt das Kleinere beider Seiten."
        )
        werte = Zwischenwerte(self.id)
        ergebnis: Dict[str, Groesse] = {}

        momente = self._handrechnung(e, p, werte, ergebnis)
        self._querkraftteil(e, p, werte, ergebnis, momente)
        return ergebnis

    def _handrechnung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                      ergebnis: Dict[str, Groesse]) -> Dict[Zugseite, float]:
        """M_Rd und x/d bei N = 0, N_Rd bei M = 0 -- aus der Linie der Handrechnung."""
        linie = self.linienquelle.linie(
            e, p, basis=f"{self.id}.hand", vorsatz="Kennzahlen: ",
            wahltitel="Rechenwahl – Kennzahlen",
            wenn_geteilt=lambda p: p.text(
                "Die Eckpunkte stammen aus der Handrechnung der Tragsicherheit – "
                "sie rechnet ebenso, von Hand mit Bemessungswerten."))

        p.titel("Biegung und Normalkraft", ebene=3)
        eckpunkt = {q.kennung: q for q in linie.punkte}
        momente: Dict[Zugseite, float] = {}
        for seite in UM_Y:
            kurz = seite.marke
            m = self._auf_der_linie(p, linie, ergebnis, geo.MOMENT, seite.positiv,
                                    f"M_Rd_{kurz}", f"Momentenwiderstand bei N_Ed = 0, Zug {seite}")
            momente[seite] = abs(m)
            if f"x_d_{kurz}" not in self.d:
                p.text(f"Zug {seite} ohne x-Bewehrung → kein d, kein x/d dieser Seite.")
                continue
            punkt = eckpunkt[f"n0_{kurz}"]
            p.formel(self._belegen(ergebnis, f"x_d_{kurz}",
                                   punkt.x.groesse.si / punkt.d.groesse.si),
                     r"\frac{@x}{@d}", {"x": punkt.x, "d": punkt.d},
                     titel=f"Bezogene Druckzonenhöhe bei N_Ed = 0, Zug {seite}",
                     name="Bezogene Druckzonenhöhe")

        for positiv, kurz, wie in ((True, "zug", "Zugwiderstand"),
                                   (False, "druck", "Druckwiderstand")):
            self._auf_der_linie(p, linie, ergebnis, geo.NORMALKRAFT, positiv,
                                f"N_Rd_{kurz}", f"{wie} bei M_Ed = 0")
        return momente

    def _auf_der_linie(self, p: Protokoll, linie, ergebnis: Dict[str, Groesse],
                       achse: geo.Achse, positiv: bool, kurz: str, titel: str) -> float:
        """
        Ein Widerstand auf der Linie, die Gegengroesse null -- hergeleitet, wie
        die Linie ihn findet: als Eckpunkt oder zwischen zweien.

        Getroffen wird sie immer: sie umschliesst den Querschnitt ohne
        Dehnung, N = M = 0, oder geht durch ihn, und jede Gerade durch ihn
        trifft sie (bei einseitiger Bewehrung als Eckpunkt,
        :func:`~opencivil.nachweis.linie.kante`).
        """
        treffer = linie.kante(achse, 0.0, positiv=positiv)
        if treffer is None:
            raise BerechnungsFehler(
                self.id, f"{titel}: die Linie trifft {achse.gegen.name} = 0 nicht.")
        wert = self._belegen(ergebnis, kurz, treffer.wert)
        linie.protokoll_treffer(p, treffer, achse=achse, fest=0.0,
                                basis=f"{self.id}.{kurz}", titel=titel, ergebnis=wert)
        return wert.groesse.si

    def _hoehen(self, e: Eingaben, werte: Zwischenwerte, p: Protokoll, seite: Zugseite,
                d: float, d_v: Optional[float] = None) -> Tuple[Wert, Optional[Wert]]:
        """``d`` der gezogenen Seite und, ohne Buegel, ``d_v`` -- hergeleitet wie im Querkraftnachweis."""
        return protokoll_hoehen(p, werte, e, zugposten(self.posten, seite), d, d_v,
                                seite=seite, zeichen=seite.zeichen)

    def _ohne_buegel(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                     ergebnis: Dict[str, Groesse], momente: Dict[Zugseite, float]) -> None:
        p.titel("Querkraftwiderstand ohne Bügel bei N_Ed = 0", ebene=3)
        p.erklaerung(
            "Ohne Bügel hängt der Widerstand am Moment: am grössten bei M_Ed = 0, "
            "wo die Dehnung null ist. Solange die Bewehrung elastisch bleibt, ist er "
            "am kleinsten bei M_Ed = M_Rd, wo sie zu fliessen beginnt und die "
            "Dehnung f_yd/E_s erreicht; darf sie plastisch werden, gilt "
            "1.5·f_yd/E_s, und er liegt tiefer. Je Seite gilt ihre statische Höhe."
        )
        k_g = beiwert_k_g(p, self.id, e["D_max"], e["f_ck"])
        tau_cd = tau_cd_wert(werte, e)
        w = self.querkraft.kurvenbeiwerte(e, k_g.groesse.si)

        bei_null: List[Wert] = []
        beim_widerstand: List[Wert] = []
        for seite in UM_Y:
            hoch = seite.zeichen
            hoehen = w.hoehen(seite)
            if hoehen is None:
                p.text(f"Zug {seite} ohne x-Bewehrung → kein d, kein Widerstand dieser Seite.")
                continue
            d, d_v = self._hoehen(e, werte, p, seite, *hoehen)
            m_Rd = momente[seite]
            null, voll = (w.widerstand(seite, M_Ed=m_Ed, N_Ed=0.0, m_Rd=m_Rd)
                          for m_Ed in (0.0, m_Rd))
            v_null = werte.wert(f"V_null_{hoch}", rf"V_{{Rd}}^{{{hoch}}}(M_{{Ed}} = 0)",
                                Groesse.aus_si(null.v_Rd, KN_PRO_M), 1)
            v_voll = werte.wert(f"V_voll_{hoch}",
                                rf"V_{{Rd}}^{{{hoch}}}(M_{{Ed}} = M_{{Rd}}^{{{hoch}}})",
                                Groesse.aus_si(voll.v_Rd, KN_PRO_M), 1)
            bei_null.append(v_null)
            beim_widerstand.append(v_voll)
            # Reicht die Einlage ueber d, bleibt dieser Seite nichts -- und
            # das Kleinere beider Seiten ist null.
            if null.grund:
                p.text(f"Zug {seite}: {null.grund}")
                continue

            p.formel(v_null, r"@tau_cd \cdot @d_v", {"tau_cd": tau_cd, "d_v": d_v},
                     titel=f"Zug {seite}, M_Ed = 0: ε_v = 0, k_d = 1",
                     referenz=f"{REFERENZ_OHNE_BUEGEL}, (36)",
                     name="Querkraftwiderstand ohne Bügel bei M_Ed = 0")
            f_yd, E_s = self.querkraft.zugstahl(e, seite)
            eps_v = werte.dehnung(f"eps_v_{hoch}", rf"\varepsilon_v^{{{hoch}}}", voll.eps_v,
                                  stellen=3)
            p.formel(eps_v, r"\frac{@f_yd}{@E_s}", {"f_yd": f_yd, "E_s": E_s},
                     titel=f"Zug {seite}, M_Ed = M_Rd: Dehnung beim Fliessbeginn",
                     referenz="SIA 262:2025, 4.3.3.2.2, (38)", name=FLIESSDEHNUNG)
            protokoll_ohne_buegel(p, werte, v_voll, k_d=voll.k_d, eps_v=eps_v, d=d, d_v=d_v,
                                  k_g=k_g, tau_cd=tau_cd, titel=f"Zug {seite}, M_Ed = M_Rd",
                                  zeichen=hoch)

        for kurz, teile, titel in (("V_Rd_max", bei_null, "bei M_Ed = 0"),
                                   ("V_Rd_min", beim_widerstand, "bei M_Ed = M_Rd")):
            self._kleinstes(p, ergebnis, kurz, teile,
                            f"Querkraftwiderstand ohne Bügel {titel}, das Kleinere beider Seiten")

    def _mit_buegeln(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                     ergebnis: Dict[str, Groesse], _momente: Dict[Zugseite, float]) -> None:
        """Mit Buegeln haengt der Widerstand nicht am Moment, nur an der gezogenen Seite."""
        p.titel("Querkraftwiderstand mit Bügeln bei N_Ed = 0", ebene=3)
        p.erklaerung(
            "Mit Bügeln trägt das Fachwerk; gesucht wird ganzgradig zwischen "
            "α_min und α_max die Neigung mit dem grössten Widerstand. Ohne "
            "Normalkraft bleiben die Grenzen, wie sie eingegeben sind."
        )
        w = self.querkraft.buegelwerte(e)
        s_y = self.querkraft.teilung_y(werte, e, w.s_y)
        self.querkraft.protokoll_teilung_y(p, e, s_y)
        hoehen = statische_hoehen(e, self.posten)

        teile: List[Wert] = []
        for seite in UM_Y:
            hoch = seite.zeichen
            if seite not in hoehen:
                p.text(f"Zug {seite} ohne x-Bewehrung → kein d, kein Widerstand dieser Seite.")
                continue
            d, _ = self._hoehen(e, werte, p, seite, hoehen[seite])
            suche = w.suche(hoehen[seite], zugkraft=False)
            seite_wert = werte.wert(f"V_{hoch}", rf"V_{{Rd}}^{{{hoch}}}(\alpha_{{opt}})",
                                    Groesse.aus_si(suche.massgebend.V_Rd, KN_PRO_M), 1)
            protokoll_mit_buegeln(p, werte, seite_wert, suche.massgebend, e=e, s_y=s_y, d=d,
                                  alpha_min=suche.alpha_min, alpha_max=suche.alpha_max,
                                  seite=seite, zeichen=hoch)
            teile.append(seite_wert)
        self._kleinstes(p, ergebnis, "V_Rd_buegel", teile,
                        "Querkraftwiderstand mit Bügeln, das Kleinere beider Seiten")

    def _kleinstes(self, p: Protokoll, ergebnis: Dict[str, Groesse], kurz: str,
                   teile: List[Wert], titel: str) -> None:
        """
        Das Kleinere der Seiten mit Zugbewehrung -- bei nur einer sie selbst.
        Eine hat die Platte immer: ohne x-Bewehrung gibt es keine Kennzahlen.
        """
        wert = self._belegen(ergebnis, kurz, min(t.groesse.si for t in teile))
        if len(teile) == 2:
            p.formel(wert, r"\min\left[@a;\ @b\right]", {"a": teile[0], "b": teile[1]},
                     titel=titel, name="Kleinerer Widerstand beider Seiten")
        else:
            p.formel(wert, "@a", {"a": teile[0]}, titel=titel,
                     name="Kleinerer Widerstand beider Seiten")

