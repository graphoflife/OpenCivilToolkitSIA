"""
opencivil/nachweis/knicken.py -- Nachweis am verformten System.

VERANTWORTUNG:
Prueft je Knickfall, ob sich unter der Druckkraft ueberhaupt eine
Gleichgewichtslage einstellt -- und wenn ja, ob der Querschnitt das dabei
entstehende Moment aufnimmt.

DAS VERFAHREN::

    alpha_i = min[ max(0.01/sqrt(l); 1/300) ; 1/200 ]      Schiefstellung
    e_0d    = max( d/30 ; alpha_i * l_cr/2 )               ungewollte Ausmitte
    e_1d    = |M_Ed,1 / N_Ed|                              gewollte Ausmitte
    e_2d    = |chi| * l_cr^2 / pi^2                        Ausmitte 2. Ordnung

    wiederhole:
        M_ziel = |N_Ed| * (e_0d + e_1d + e_2d)
        (eps_m, chi) = Gleichgewicht zu (N_Ed, M_ziel)
        e_2d neu aus chi
    bis M_ziel sich nicht mehr aendert

Konvergiert die Folge, gibt es eine Gleichgewichtslage: das System ist stabil.
Waechst sie, kippt es -- dann ist der Nachweis nicht erfuellt, und zwar nicht
wegen einer ueberschrittenen Spannung, sondern weil es gar kein Gleichgewicht
gibt. Genau das ist Knicken.

NUR IN X-RICHTUNG:
Ein Knicknachweis braucht eine Knicklaenge, und die gehoert zu einer
Tragrichtung. Gerechnet wird darum nur mit der Bewehrung in x -- in y waere
die Breite der Platte die Laenge, und die ist keine Stuetze.

WAS IN DIE MITSCHRIFT GEHOERT:
Das Verfahren, die letzte Ausmitte und die **Probe**: mit der gefundenen Ebene
entstehen genau ``N_Ed`` und das Moment zweiter Ordnung. Die Iteration selbst
steht nicht da.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import (
    Eingabebezug, Eingaben, Nachweis, NachweisUrteil,
)
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, MM, Groesse
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.material.basis import mit_index
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, beton_nichtlinear, stahl_bilinear,
)
from opencivil.querschnitt.platte import Richtung

#: Groesste Zahl an Durchlaeufen der Ausmitten-Iteration.
DURCHLAEUFE = 40

#: Wann die Iteration als eingelaufen gilt -- Aenderung des Moments.
SCHRANKE = 1e-4

#: Riegel der Schiefstellung, SIA 262:2025, 4.3.7.
ALPHA_UNTEN = 1.0 / 300.0
ALPHA_OBEN = 1.0 / 200.0


@dataclass(frozen=True)
class Knickfall:
    """Eine zu pruefende Kombination aus Druckkraft und Moment 1. Ordnung."""

    name: str
    N_Ed: Groesse
    """Druck negativ -- wie ueberall in diesem Werkzeug."""

    M_Ed_1: Groesse
    laenge: Groesse
    knicklaenge: Groesse

    @property
    def kennung(self) -> str:
        return "".join(z if z.isalnum() else "_" for z in self.name)


@dataclass
class Knickergebnis:
    """Alle Zwischenwerte eines Knickfalls."""

    fall: Knickfall
    alpha_i: float = 0.0
    e_0d: float = 0.0
    e_1d: float = 0.0
    e_2d: float = 0.0
    M_ges: float = 0.0
    """Moment am verformten System, in Nm."""

    eps_m: float = 0.0
    chi: float = 0.0
    N_int: float = 0.0
    M_int: float = 0.0
    durchlaeufe: int = 0
    stabil: bool = False
    M_Rd: float = 0.0
    """Momentenwiderstand bei dieser Normalkraft, in Nm."""

    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""


def schiefstellung(laenge: float) -> float:
    """``alpha_i = min[ max(0.01/sqrt(l); 1/300) ; 1/200 ]``, ``l`` in m."""
    if laenge <= 0.0:
        return ALPHA_OBEN
    return min(max(0.01 / math.sqrt(laenge), ALPHA_UNTEN), ALPHA_OBEN)


class Knicken(Nachweis):
    """
    Nachweis am verformten System, je Knickfall -- nur in x-Richtung.

    Der Nachweis ist erfüllt, wenn die Ausmitten-Iteration einläuft **und**
    der Querschnitt das Moment zweiter Ordnung aufnimmt.
    """

    def __init__(
        self,
        querschnitt,
        faelle: Sequence[Knickfall],
        mn_nachweis,
    ) -> None:
        if not faelle:
            raise ValueError("Der Knicknachweis braucht mindestens einen Fall.")
        self.posten = querschnitt.posten_in_richtung(Richtung.X)
        if not self.posten:
            raise ValueError(
                f"Querschnitt '{querschnitt.name}': ohne Bewehrung in "
                f"x-Richtung ist kein Knicknachweis möglich.")

        self.querschnitt = querschnitt
        self.richtung = Richtung.X
        self.faelle = list(faelle)
        self.mn = mn_nachweis
        self.ergebnisse: List[Knickergebnis] = []

        basis = f"{querschnitt.id}.nachweis.knicken"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: WertDef(
                id=f"{basis}.{f.kennung}.erfuellungsgrad",
                symbol=rf"\alpha_{{eff,K,{f.kennung}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Erfüllungsgrad Knicken – {f.name}",
                referenz="SIA 262:2025, 4.3.7",
                stellen=2,
            )
            for f in self.faelle
        }

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(self.richtung)),
            Eingabebezug("f_cd", querschnitt.beton.id_von("f_cd")),
            Eingabebezug("E_cm", querschnitt.beton.id_von("E_cm")),
            Eingabebezug("eps_c1d", querschnitt.beton.id_von("eps_c1d")),
            Eingabebezug("eps_c2d", querschnitt.beton.id_von("eps_c2d")),
            Eingabebezug("phi", querschnitt.id_von("kriechzahl")),
        ]
        for lage, art, _, as_id, z_id in self.posten:
            marke = f"{lage.nummer}{art.kuerzel}"
            bezuege += [
                Eingabebezug(f"a_s_{marke}", as_id),
                Eingabebezug(f"z_{marke}", z_id),
            ]
        stahl = self.posten[0][0].stahl
        bezuege += [
            Eingabebezug("E_s", stahl.id_von("E_s")),
            Eingabebezug("f_yd", stahl.id_von("f_yd")),
            Eingabebezug("eps_ud", stahl.id_von("eps_ud")),
        ]
        self.s_f_cd = mit_index("f_{cd}", querschnitt.beton.symbol_index)

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=bezuege,
            titel=f"Knicknachweis – {querschnitt.name}",
            referenz="SIA 262:2025, 4.3.7",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        h = e.g("h").si
        b = e.g("b").si
        f_cd = e.g("f_cd").si
        E_cm = e.g("E_cm").si
        phi = e.g("phi").si
        E_s = e.g("E_s").si
        f_yd = e.g("f_yd").si
        eps_ud = e.g("eps_ud").si
        eps_c1d = e.g("eps_c1d").si
        eps_c2d = e.g("eps_c2d").si

        lagen = [Stahllage(a_s=e.g(f"a_s_{l.nummer}{a.kuerzel}").si,
                           z=e.g(f"z_{l.nummer}{a.kuerzel}").si,
                           nummer=l.nummer)
                 for l, a, _, _, _ in self.posten]
        # Kriechen weicht den Beton auf; das Gesetz rechnet mit dem wirksamen
        # Modul. eps_c1d und eps_c2d bleiben, wie die Norm sie angibt.
        loeser = Querschnittsloeser(
            h=h, b=b, lagen=lagen,
            beton=beton_nichtlinear(f_cd=f_cd, E_c=E_cm / (1.0 + phi),
                                    eps_c1d=eps_c1d, eps_c2d=eps_c2d),
            stahl=stahl_bilinear(E_s=E_s, f_sd=f_yd, eps_ud=eps_ud),
            eps_druck=eps_c2d, eps_zug=eps_ud)

        self._protokoll_ansatz(p, phi, E_cm, f_cd)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        self.ergebnisse = []

        for fall in self.faelle:
            erg = self._einen_fall(loeser, fall, h)
            self.ergebnisse.append(erg)
            self._protokoll_fall(p, erg)
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
                min(erg.erfuellungsgrad, 1e9), EINHEITSLOS)
            urteile.append(self._urteil(erg))

        return ergebnis, urteile

    def _einen_fall(self, loeser: Querschnittsloeser, fall: Knickfall,
                    h: float) -> Knickergebnis:
        erg = Knickergebnis(fall=fall)
        N_Ed = fall.N_Ed.si
        l_cr = fall.knicklaenge.si

        if N_Ed >= 0.0:
            erg.begruendung = erg.hinweis = (
                "Knicken setzt eine Druckkraft voraus; hier ist N_Ed nicht "
                "negativ. Der Nachweis entfällt.")
            erg.erfuellungsgrad = float("inf")
            erg.erfuellt = True
            return erg

        # Statische Hoehe der untersten x-Lage -- daraus die Mindestausmitte.
        d = max(l.z for l in loeser.lagen)
        erg.alpha_i = schiefstellung(fall.laenge.si)
        erg.e_0d = max(d / 30.0, erg.alpha_i * l_cr / 2.0)
        erg.e_1d = abs(fall.M_Ed_1.si / N_Ed)

        e_2d = 0.0
        vorher: Optional[float] = None
        for durchlauf in range(1, DURCHLAEUFE + 1):
            erg.durchlaeufe = durchlauf
            M_ziel = abs(N_Ed) * (erg.e_0d + erg.e_1d + e_2d)
            ebene = loeser.loese(N_Ed=N_Ed, M_Ed=M_ziel)
            if not ebene.konvergiert:
                erg.begruendung = erg.hinweis = (
                    f"Bei N_Ed = {fall.N_Ed.formatiert(1, KN)} kN stellt sich "
                    f"keine Gleichgewichtslage mehr ein: das Moment zweiter "
                    f"Ordnung wächst über das, was der Querschnitt aufnimmt. "
                    f"Das System knickt.")
                return erg
            e_2d = abs(ebene.chi) * l_cr * l_cr / (math.pi ** 2)
            if vorher is not None and abs(M_ziel - vorher) <= SCHRANKE * max(
                    abs(M_ziel), 1.0):
                erg.stabil = True
                erg.e_2d = e_2d
                erg.M_ges = M_ziel
                erg.eps_m, erg.chi = ebene.eps_m, ebene.chi
                erg.N_int, erg.M_int = ebene.N_int, ebene.M_int
                break
            vorher = M_ziel
        else:
            erg.begruendung = erg.hinweis = (
                f"Die Ausmitte zweiter Ordnung läuft nach {DURCHLAEUFE} "
                f"Durchläufen nicht ein. Das System ist nicht stabil.")
            return erg

        # Der Querschnitt muss das Moment am verformten System aufnehmen.
        widerstand = self.mn.moment_bei(N_Ed, positiv=erg.M_ges >= 0)
        erg.M_Rd = widerstand or 0.0
        erg.erfuellungsgrad = (float("inf") if erg.M_ges == 0
                               else erg.M_Rd / abs(erg.M_ges))
        erg.erfuellt = erg.M_Rd >= abs(erg.M_ges)
        erg.begruendung = (
            f"Stabil nach {erg.durchlaeufe} Durchläufen: "
            f"e_0d = {erg.e_0d * 1e3:.1f} mm, e_1d = {erg.e_1d * 1e3:.1f} mm, "
            f"e_2d = {erg.e_2d * 1e3:.1f} mm. "
            f"M_ges = {erg.M_ges / 1e3:.1f} kNm gegen "
            f"M_Rd = {erg.M_Rd / 1e3:.1f} kNm.")
        return erg

    def _urteil(self, erg: Knickergebnis) -> NachweisUrteil:
        machbar = erg.stabil
        einwirkung = WertDef(
            id=f"{self.id}.{erg.fall.kennung}.M_ges",
            symbol=r"M_{Ed,II}",
            einheit=KNM, beschreibung="Einwirkung", stellen=1,
        ).belegen(Groesse.aus_si(abs(erg.M_ges), KNM))
        widerstand = WertDef(
            id=f"{self.id}.{erg.fall.kennung}.M_Rd",
            symbol=r"M_{Rd,x}(N_{Ed})",
            einheit=KNM, beschreibung="Widerstand", stellen=1,
        ).belegen(Groesse.aus_si(erg.M_Rd, KNM))
        return NachweisUrteil(
            name=f"Knicken – {erg.fall.name}",
            art="K",
            langname=f"Knicken ({self.richtung.value})",
            fall=erg.fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=einwirkung if machbar else None,
            widerstand=widerstand if machbar else None,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, phi: float, E_cm: float,
                          f_cd: float) -> None:
        p.titel("Knicken")
        p.text(
            "Nachgewiesen wird am verformten System. Die Ausmitte zweiter "
            "Ordnung hängt von der Krümmung ab, die Krümmung vom Moment und "
            "das Moment wieder von der Ausmitte – also wird die Folge so "
            "lange durchlaufen, bis sie einläuft. Läuft sie nicht ein, gibt es "
            "keine Gleichgewichtslage: das System knickt."
        )
        p.gleichung(
            r"\alpha_i = \min\left[\max\left(\frac{0.01}{\sqrt{l}};\ "
            rf"\frac{{1}}{{300}}\right);\ \frac{{1}}{{200}}\right] \qquad "
            r"e_{0d} = \max\left(\frac{d}{30};\ "
            r"\frac{\alpha_i \cdot l_{cr}}{2}\right)",
            titel="Ungewollte Ausmitte", referenz="SIA 262:2025, 4.3.7")
        p.gleichung(
            r"e_{1d} = \left|\frac{M_{Ed,1}}{N_{Ed}}\right| \qquad "
            r"e_{2d} = \left|\chi\right| \cdot \frac{l_{cr}^{2}}{\pi^{2}} "
            r"\qquad M_{Ed,II} = \left|N_{Ed}\right| \cdot "
            r"\left(e_{0d} + e_{1d} + e_{2d}\right)",
            titel="Gewollte Ausmitte und Ausmitte 2. Ordnung")
        p.gleichung(
            rf"E_{{c,eff}} = \frac{{E_{{cm}}}}{{1 + \varphi}} = "
            rf"\frac{{{E_cm / 1e6:.0f}}}{{1 + {phi:.2f}}} = "
            rf"{E_cm / (1.0 + phi) / 1e6:.0f}\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}"
            rf" \qquad {self.s_f_cd} = {f_cd / 1e6:.1f}"
            rf"\,\mathrm{{N}}/\mathrm{{mm}}^{{2}}",
            titel="Steifigkeit des Betons")
        p.text(
            "Gerechnet wird mit dem nichtlinearen Werkstoffgesetz und den "
            "Bemessungswerten. Die Krümmung zu einer Schnittgrössenkombination "
            "wird gesucht, nicht hergeleitet; nachgewiesen wird deshalb die "
            "Probe – dass die gefundene Dehnungsebene genau diese Kräfte "
            "erzeugt."
        )

    def _protokoll_fall(self, p: Protokoll, erg: Knickergebnis) -> None:
        fall = erg.fall
        p.titel(f"Knicken – {fall.name}", ebene=3)
        p.gleichung(
            rf"N_{{Ed}} = {fall.N_Ed.als_latex(1, KN)} \qquad "
            rf"M_{{Ed,1}} = {fall.M_Ed_1.als_latex(1, KNM)} \qquad "
            rf"l = {fall.laenge.als_latex(2)} \qquad "
            rf"l_{{cr}} = {fall.knicklaenge.als_latex(2)}",
            titel="Einwirkung und System")

        if not erg.stabil:
            p.text(erg.begruendung)
            return

        p.gleichung(
            rf"\alpha_i = {erg.alpha_i:.5f} \qquad "
            rf"e_{{0d}} = {erg.e_0d * 1e3:.1f}\,\mathrm{{mm}} \qquad "
            rf"e_{{1d}} = {erg.e_1d * 1e3:.1f}\,\mathrm{{mm}} \qquad "
            rf"e_{{2d}} = {erg.e_2d * 1e3:.1f}\,\mathrm{{mm}}",
            titel=f"Ausmitten nach {erg.durchlaeufe} Durchläufen")
        p.gleichung(
            rf"M_{{Ed,II}} = \left|N_{{Ed}}\right| \cdot "
            rf"\left(e_{{0d}} + e_{{1d}} + e_{{2d}}\right)"
            rf" = {abs(fall.N_Ed.si) / 1e3:.1f} \cdot "
            rf"\left({erg.e_0d * 1e3:.1f} + {erg.e_1d * 1e3:.1f} + "
            rf"{erg.e_2d * 1e3:.1f}\right) \cdot 10^{{-3}}"
            rf" = {erg.M_ges / 1e3:.1f}\,\mathrm{{kNm}}",
            titel="Moment am verformten System")
        p.gleichung(
            rf"\varepsilon_m = {erg.eps_m * 1e3:.4f}\,\text{{‰}} \qquad "
            rf"\chi = {erg.chi:.5f}\,\mathrm{{m}}^{{-1}}",
            titel="Gefundene Dehnungsebene")
        p.gleichung(
            rf"N_{{int}} = {erg.N_int / 1e3:.1f}\,\mathrm{{kN}} \;\checkmark"
            rf" \qquad M_{{int}} = {erg.M_int / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \;\checkmark",
            titel="Probe: die Ebene erzeugt die Schnittgrössen")

        zustand = r"\text{erfüllt}" if erg.erfuellt else r"\text{NICHT erfüllt}"
        vergleich = r"\ge" if erg.erfuellt else "<"
        p.gleichung(
            rf"M_{{Rd,x}}(N_{{Ed}}) = {erg.M_Rd / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \quad {vergleich} \quad M_{{Ed,II}} = "
            rf"{abs(erg.M_ges) / 1e3:.1f}\,\mathrm{{kNm}}"
            rf" \quad \Rightarrow \quad {zustand}",
            titel="Momentenwiderstand am verformten System")
