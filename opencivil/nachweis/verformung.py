"""
opencivil/nachweis/verformung.py -- die Durchbiegung der Platte.

VERANTWORTUNG:
Haelt je Verformungsfall die wirksame Durchbiegung gegen ihren Grenzwert::

    omega_w = (1 - 20 rho') / (10 rho^0.7) · (0.75 + 0.1 phi) · (h/d)^3
    w_eff   = omega_w · w
    w_max   = L / 350
    alpha   = w_max / w_eff

``w`` gibt der Benutzer an, ermittelt mit der Steifigkeit E_cm. Der
Vergroesserungsfaktor omega_w -- in der Norm w/w_c, SIA 262:2025, 4.4.3.2.5
-- fuehrt sie auf die Durchbiegung der gerissenen Platte unter Dauerlast.

EIN FAKTOR JE SEITE, NICHT JE FALL:
``rho = A_s/(b·d)`` gehoert zur gezogenen Seite, ``rho'`` zur Gegenseite, mit
``d'`` vom gezogenen Rand bis zur Gegenlage -- das ist deren statische Hoehe:
``rho'`` der einen Seite ist das ``rho`` der anderen. Der Faktor haengt also
nur an der Platte und an der Seite, die ein Fall zieht; er wird je Seite
einmal gerechnet und gilt fuer jeden Fall dieser Seite. Die x-Posten einer
Seite zaehlen zusammen, in ihrem Schwerpunkt. Fehlt die Gegenseite, ist
``rho' = 0``; fehlt die gezogene, gibt es keinen Faktor, und der Fall laesst
sich nicht nachweisen.

Bis 2026-10-16 stand der Faktor bei den Bewehrungslagen, mit einer
Kriechzahl der Platte. Der Benutzer hat ihn in diesen Nachweis gelegt, mit
dessen eigenem phi.

NACH VORGABE:
Der Grenzwert L/350 und dass ``w`` mit E_cm ermittelt ist, stehen so, wie
der Benutzer sie vorgegeben hat -- nicht nachgeschlagen
(``notizbuch/Notizen/TODO.md``). Die Formel des Faktors und ihre Normstelle
hat er geliefert.

EINHEITEN:
Alles in SI-Basis; ``w`` in mm und ``L`` in m kommen als Groessen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Eingabebezug, Eingaben, Nachweis, NachweisUrteil, grad_def, grad_formel,
)
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import als_text, angabe, bedingung
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.querschnitt.platte import Richtung

#: Vorgabe der Kriechzahl phi im Vergroesserungsfaktor -- Klima und
#: Belastungsalter, eine Annahme ueber das Bauwerk.
KRIECHZAHL = 2.0

#: ``w_max = L / GRENZE`` -- nach Vorgabe des Benutzers (2026-10-16), nicht
#: nachgeschlagen.
GRENZE = 350.0

#: Die Seiten, die ein Verformungsfall ziehen kann: unten im Feld, oben am
#: Kragarm oder ueber der Stuetze.
ZUGSEITEN = ("unten", "oben")


def gegenseite(seite: str) -> str:
    return "oben" if seite == "unten" else "unten"


@dataclass(frozen=True)
class Verformungsfall:
    """Eine Durchbiegung, mit E_cm ermittelt, zu ihrer Spannweite."""

    name: str
    w: Groesse
    """Die Durchbiegung mit der Steifigkeit E_cm -- ein Betrag."""

    laenge: Groesse
    """Die Spannweite L."""

    zugseite: str = "unten"
    """Welche Seite der Fall zieht -- danach richten sich rho und rho'."""

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


@dataclass
class Fallergebnis:
    """Was ein Fall ergibt -- fuer Urteil und Herleitung."""

    fall: Verformungsfall
    w_eff: Optional[Wert] = None
    w_max: Optional[Wert] = None
    erfuellungsgrad: float = 0.0
    erfuellt: bool = False
    begruendung: str = ""
    hinweis: str = ""


class Verformung(Nachweis):
    """
    Die Durchbiegung je Verformungsfall, in x -- mit dem
    Vergroesserungsfaktor der Seite, die der Fall zieht.
    """

    THEMA = "Verformung"

    def __init__(self, querschnitt, faelle: Sequence[Verformungsfall], *,
                 kriechzahl: float = KRIECHZAHL) -> None:
        if not faelle:
            raise ValueError("Der Verformungsnachweis braucht mindestens einen Fall.")
        self.querschnitt = querschnitt
        self.richtung = Richtung.X
        self.faelle = list(faelle)
        self.kriechzahl = kriechzahl

        posten = querschnitt.posten_in_richtung(Richtung.X)
        #: Je Seite die Marken ihrer x-Posten, etwa «2g» und «2z».
        self.marken: Dict[str, List[str]] = {
            seite: [f"{lage.nummer}{art.kuerzel}" for lage, art, _, _, _ in posten
                    if lage.von_unten is (seite == "unten")]
            for seite in ZUGSEITEN}

        basis = f"{querschnitt.id}.nachweis.verformung"
        # Ein Faktor je gezogene Seite, die ein Fall verlangt -- und nur, wo
        # sie x-Bewehrung hat: ohne sie gibt es keinen.
        self.d_omega: Dict[str, WertDef] = {
            seite: WertDef(
                id=f"{basis}.omega_w_{seite}", symbol=rf"\omega_{{w,{seite[0]}}}",
                einheit=EINHEITSLOS,
                beschreibung=f"Vergrösserungsfaktor der Durchbiegung, Zug {seite}",
                referenz="SIA 262:2025, 4.4.3.2.5", stellen=2)
            for seite in ZUGSEITEN
            if self.marken[seite] and any(f.zugseite == seite for f in self.faelle)}
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,w,{als_text(f.name)}}}",
                f"Erfüllungsgrad Verformung – {f.name}")
            for f in self.faelle}

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(Richtung.X)),
        ]
        for lage, art, _, as_id, z_id in posten:
            marke = f"{lage.nummer}{art.kuerzel}"
            bezuege += [Eingabebezug(f"a_s_{marke}", as_id),
                        Eingabebezug(f"z_{marke}", z_id)]

        super().__init__(
            basis,
            ausgaben=[*self.d_omega.values(), *self.d_ausnutzung.values()],
            bezuege=bezuege,
            titel=f"Verformung – {querschnitt.name}",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        werte = Zwischenwerte(self.id)
        phi = werte.zahl("phi", r"\varphi", self.kriechzahl, "Kriechzahl", stellen=2)
        self._protokoll_ansatz(p, phi)

        omega = self._vergroesserung(p, e, werte, phi)
        ergebnis: Dict[str, Groesse] = {self.d_omega[s].id: o.groesse
                                        for s, o in omega.items()}
        urteile: List[NachweisUrteil] = []
        for fall in self.faelle:
            erg = self._einen_fall(p, fall, omega.get(fall.zugseite))
            ergebnis[self.d_ausnutzung[fall.name].id] = Groesse(
                erg.erfuellungsgrad, EINHEITSLOS)
            urteile.append(self._urteil(erg))
        return Ausfuehrung(ergebnis, urteile)

    def _vergroesserung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
                        phi: Wert) -> Dict[str, Wert]:
        """Je gezogene Seite, die ein Fall verlangt, der Faktor omega_w."""
        if not self.d_omega:
            return {}
        gehalte = self._bewehrungsgehalte(p, e, werte)
        h = e["h"]
        ergebnis: Dict[str, Wert] = {}
        for seite, definition in self.d_omega.items():
            rho, d = gehalte[seite]
            gegen = gehalte.get(gegenseite(seite))
            k = gegenseite(seite)[0]
            rho_s = gegen[0] if gegen else werte.zahl(f"rho_{k}", rf"\rho_{{{k}}}", 0.0,
                                                      stellen=5)
            zahl = ((1.0 - 20.0 * rho_s.groesse.si) / (10.0 * rho.groesse.si ** 0.7)
                    * (0.75 + 0.1 * phi.groesse.si)
                    * (h.groesse.si / d.groesse.si) ** 3)
            ergebnis[seite] = definition.belegen(Groesse(zahl, EINHEITSLOS))
            p.formel(
                ergebnis[seite],
                r"\frac{1 - 20 \cdot @rho_s}{10 \cdot @rho^{0.7}} \cdot "
                r"\left(0.75 + 0.1 \cdot @phi\right) \cdot \left(\frac{@h}{@d}\right)^{3}",
                {"rho_s": rho_s, "rho": rho, "phi": phi, "h": h, "d": d},
                titel=f"Vergrösserungsfaktor, Zug {seite}",
                name="Vergrösserungsfaktor der Durchbiegung")
        return ergebnis

    def _bewehrungsgehalte(self, p: Protokoll, e: Eingaben,
                           werte: Zwischenwerte) -> Dict[str, Tuple[Wert, Wert]]:
        """
        Je Seite mit x-Bewehrung der Bewehrungsgehalt und seine statische
        Hoehe -- die gezogene Seite eines Falls braucht beide, die Gegenseite
        ihren Gehalt als rho'.
        """
        h, b = e["h"], e["b"]
        gehalte: Dict[str, Tuple[Wert, Wert]] = {}
        for seite in ZUGSEITEN:
            marken = self.marken[seite]
            if not marken:
                continue
            unten = seite == "unten"
            k = seite[0]
            flaechen = [e[f"a_s_{m}"] for m in marken]
            tiefen = [e[f"z_{m}"] for m in marken]
            a_s = sum(a.groesse.si for a in flaechen)
            if len(marken) == 1:
                A, z = flaechen[0], tiefen[0]
            else:
                A = werte.flaeche(f"A_s_{k}", f"A_{{s,{k}}}", a_s)
                p.formel(A, " + ".join(f"@A{i}" for i in range(len(marken))),
                         {f"A{i}": a for i, a in enumerate(flaechen)},
                         titel=f"x-Bewehrung {seite}, zusammen",
                         name="Bewehrungsquerschnitt der zusammengefassten Lage")
                z = werte.laenge(f"z_{k}", f"z_{{{k}}}",
                                 sum(a.groesse.si * t.groesse.si
                                     for a, t in zip(flaechen, tiefen)) / a_s)
                p.formel(z, rf"\frac{{{' + '.join(f'@A{i} \\cdot @z{i}' for i in range(len(marken)))}}}"
                            rf"{{@A}}",
                         {"A": A, **{f"A{i}": a for i, a in enumerate(flaechen)},
                          **{f"z{i}": t for i, t in enumerate(tiefen)}},
                         titel=f"Schwerpunkt der x-Bewehrung {seite}",
                         name="Schwerpunkt der zusammengefassten Lage")
            d = werte.laenge(f"d_{k}", f"d_{{{k}}}",
                             z.groesse.si if unten else h.groesse.si - z.groesse.si)
            p.formel(d, "@z" if unten else "@h - @z", {"z": z, "h": h},
                     titel=f"Statische Höhe der x-Bewehrung {seite}", name="Statische Höhe")
            r = werte.zahl(f"rho_{k}", rf"\rho_{{{k}}}", a_s / (b.groesse.si * d.groesse.si),
                           stellen=5)
            p.formel(r, r"\frac{@A}{@b \cdot @d}", {"A": A, "b": b, "d": d},
                     titel=f"Bewehrungsgehalt {seite}", name="Bewehrungsgehalt")
            gehalte[seite] = (r, d)
        return gehalte

    def _einen_fall(self, p: Protokoll, fall: Verformungsfall,
                    omega: Optional[Wert]) -> Fallergebnis:
        erg = Fallergebnis(fall=fall)
        p.titel(f"Verformung – {fall.name}", ebene=3)
        if omega is None:
            erg.begruendung = erg.hinweis = (
                f"Zug {fall.zugseite} ohne x-Bewehrung → kein Vergrösserungsfaktor, "
                f"kein Nachweis.")
            p.text(erg.begruendung)
            return erg

        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        w = werte.laenge("w", "w", fall.w.si, "Durchbiegung mit E_cm")
        L = werte.wert("L", "L", fall.laenge, 2, "Spannweite")
        w_eff = werte.laenge("w_eff", "w_{eff}", omega.groesse.si * fall.w.si,
                             "Einwirkung")
        w_max = werte.laenge("w_max", "w_{max}", fall.laenge.si / GRENZE, "Widerstand")
        p.formel(w_eff, r"@omega \cdot @w", {"omega": omega, "w": w},
                 titel=f"Wirksame Durchbiegung, Zug {fall.zugseite}",
                 name="Wirksame Durchbiegung")
        p.formel(w_max, rf"\frac{{@L}}{{{GRENZE:g}}}", {"L": L},
                 titel="Grenzwert der Durchbiegung, nach Vorgabe",
                 name="Grenzwert der Durchbiegung")

        erg.w_eff, erg.w_max = w_eff, w_max
        erg.erfuellt = w_eff.groesse.si <= w_max.groesse.si
        erg.erfuellungsgrad = (float("inf") if w_eff.groesse.si == 0.0
                               else w_max.groesse.si / w_eff.groesse.si)
        erg.begruendung = (
            f"w_eff = ω_w · w = {omega.groesse.si:.2f} · {w.formatiert()} mm = "
            f"{w_eff.formatiert()} mm {'≤' if erg.erfuellt else '>'} "
            f"w_max = L/{GRENZE:g} = {w_max.formatiert()} mm.")
        p.gleichung(bedingung(angabe(w_eff), r"\le", angabe(w_max), erg.erfuellt,
                              mit_urteil=False),
                    titel="Durchbiegung gegen Grenzwert")
        grad_formel(p, self.d_ausnutzung[fall.name], erg.erfuellungsgrad, w_max, w_eff,
                    erg.erfuellt, mit_urteil=True)
        return erg

    def _urteil(self, erg: Fallergebnis) -> NachweisUrteil:
        return NachweisUrteil(
            art="w",
            ziel=self.d_ausnutzung[erg.fall.name].id,
            fall=erg.fall.name,
            erfuellt=erg.erfuellt,
            erfuellungsgrad=Groesse(erg.erfuellungsgrad, EINHEITSLOS),
            begruendung=erg.begruendung,
            hinweis=erg.hinweis,
            einwirkung=erg.w_eff,
            widerstand=erg.w_max,
        )

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll, phi: Wert) -> None:
        p.titel("Verformung")
        p.erklaerung(
            "Die Durchbiegung w ist mit der Steifigkeit E_cm ermittelt: elastisch, "
            "am ungerissenen Querschnitt. Die gerissene Platte ist weicher, und unter "
            "Dauerlast kriecht der Beton; um wie viel beides die Durchbiegung "
            "vergrössert, schätzt der Faktor ω_w. Die so vergrösserte Durchbiegung "
            "hält der Nachweis gegen L/350."
        )
        p.annahme(f"w ist mit der Steifigkeit E_cm ermittelt. Grenzwert w_max = "
                  f"L/{GRENZE:g} nach Vorgabe, nicht nachgeschlagen.")
        if not self.d_omega:
            return
        p.ansatz(
            r"\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot "
            r"\left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3}"
            r" \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}",
            titel="Vergrösserungsfaktor der Durchbiegung – allgemein",
            referenz="SIA 262:2025, 4.4.3.2.5", name="Vergrösserungsfaktor der Durchbiegung")
        p.erklaerung(
            "Gerechnet in x, je Seite, die ein Verformungsfall zieht – einmal je "
            "Platte, nicht je Fall. ρ gehört zur gezogenen Seite, ρ′ zur Gegenseite; "
            "d′ reicht vom gezogenen Rand bis zur Gegenlage und ist damit deren "
            "statische Höhe – ρ′ der einen Seite ist das ρ der anderen. Die "
            "x-Bewehrung einer Seite zählt zusammen, in ihrem Schwerpunkt."
        )
        p.wert(phi, titel="Kriechzahl")
