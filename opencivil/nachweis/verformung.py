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
nur an der Platte und an der gezogenen Seite: :class:`Vergroesserungsfaktor`
rechnet ihn je Seite mit x-Bewehrung, immer -- unten omega_w, oben omega_w'
--, denn die Zusammenfassung zeigt beide als Kennzahl (Benutzer,
2026-10-16). Der Nachweis liest ihn fuer jeden Fall seiner Seite. Die
x-Posten einer Seite zaehlen zusammen, in ihrem Schwerpunkt. Fehlt die
Gegenseite, ist ``rho' = 0``; fehlt die gezogene, gibt es keinen Faktor, und
der Fall laesst sich nicht nachweisen.

Das phi gehoert der Verformung der Platte, Vorgabe 2.

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
    NICHT_FUEHRBAR, Ausfuehrung, Ausgang, Eingabebezug, Eingaben, Fallausgang, Nachweis,
    NachweisUrteil, Prozedur, Vergleich, grad_def,
)
from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Kennzahl, Wert, WertDef, kennung_aus
from opencivil.querschnitt.lagenaufbau import Postenbezug, lage_aus_posten, protokoll_lage
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import UM_Y, Zugseite

#: Vorgabe der Kriechzahl phi im Vergroesserungsfaktor -- Klima und
#: Belastungsalter, eine Annahme ueber das Bauwerk.
KRIECHZAHL = 2.0

#: ``w_max = L / GRENZE`` -- nach Vorgabe des Benutzers (2026-10-16), nicht
#: nachgeschlagen.
GRENZE = 350.0

#: Wie der Faktor einer Seite heisst: omega_w fuer Zug unten, omega_w' fuer
#: Zug oben (Benutzer, 2026-10-16). Ziehen kann ein Fall die Seiten der
#: Platte, :data:`~opencivil.querschnitt.zugseite.UM_Y`: unten im Feld, oben
#: am Kragarm oder ueber der Stuetze.
SYMBOL = {Zugseite.UNTEN: r"\omega_w", Zugseite.OBEN: r"\omega_w'"}


@dataclass(frozen=True)
class Verformungsfall:
    """Eine Durchbiegung, mit E_cm ermittelt, zu ihrer Spannweite."""

    name: str
    w: Groesse
    """Die Durchbiegung mit der Steifigkeit E_cm -- ein Betrag."""

    laenge: Groesse
    """Die Spannweite L."""

    zugseite: Zugseite = Zugseite.UNTEN
    """Welche Seite der Fall zieht -- danach richten sich rho und rho'."""

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


@dataclass
class Fallergebnis(Fallausgang):
    """Was ein Fall ergibt -- fuer Urteil und Herleitung: w_eff gegen w_max."""

    fall: Verformungsfall
    ausgang: Ausgang = NICHT_FUEHRBAR
    begruendung: str = ""


class Vergroesserungsfaktor(Prozedur):
    """
    Der Vergroesserungsfaktor der Durchbiegung in x, je gezogene Seite mit
    x-Bewehrung: unten omega_w, oben omega_w'. Er gehoert der Platte und
    rechnet immer -- als Kennzahl und fuer den Verformungsnachweis.
    """

    THEMA = "Verformung"

    def __init__(self, querschnitt, *, kriechzahl: float = KRIECHZAHL) -> None:
        self.kriechzahl = kriechzahl
        posten = querschnitt.posten_in_richtung(Richtung.X)
        #: Je Seite ihre x-Posten: eine Lage, mit Grundbewehrung und Zulage --
        #: die x-Lage unten ist die 1. oder 2., die oben die 3. oder 4.
        self.posten_je_seite: Dict[Zugseite, List[Postenbezug]] = {
            seite: [q for q in posten if q.lage.seite is seite] for seite in UM_Y}
        basis = f"{querschnitt.id}.vergroesserung"
        self.d_omega: Dict[Zugseite, WertDef] = {
            seite: WertDef(
                id=f"{basis}.omega_w_{seite}", symbol=SYMBOL[seite], einheit=EINHEITSLOS,
                beschreibung=f"Vergrösserungsfaktor der Durchbiegung, Zug {seite}",
                referenz="SIA 262:2025, 4.4.3.2.5", stellen=2)
            for seite in UM_Y if self.posten_je_seite[seite]}
        #: Je Seite mit x-Bewehrung ihr Faktor, mit allen Stellen.
        self.kennzahlen: List[Kennzahl] = [
            Kennzahl(definition, f"Vergrösserungsfaktor, Zug {seite}", definition.referenz,
                     feste_stellen=True)
            for seite, definition in self.d_omega.items()]

        bezuege = [
            Eingabebezug("h", querschnitt.id_von("h")),
            Eingabebezug("b", querschnitt.id_breite(Richtung.X)),
        ]
        for q in posten:
            bezuege += q.bezuege("a_s", "z")
        super().__init__(
            basis, ausgaben=list(self.d_omega.values()), bezuege=bezuege,
            titel="Vergrösserungsfaktor der Durchbiegung",
            referenz="SIA 262:2025, 4.4.3.2.5", abschnitt=querschnitt.abschnitt)

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Vergrösserungsfaktor der Durchbiegung")
        werte = Zwischenwerte(self.id)
        phi = werte.zahl("phi", r"\varphi", self.kriechzahl, "Kriechzahl", stellen=2)
        p.erklaerung(
            "Eine Durchbiegung, mit der Steifigkeit E_cm ermittelt, gilt für die "
            "ungerissene Platte. Die gerissene ist weicher, und unter Dauerlast "
            "kriecht der Beton; um wie viel beides die Durchbiegung vergrössert, "
            "schätzt der Faktor ω_w. Er hängt nur an der Platte und an der Seite, "
            "die gezogen wird: ω_w für Zug unten, ω_w′ für Zug oben."
        )
        p.ansatz(
            r"\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot "
            r"\left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3}"
            r" \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}",
            titel="Vergrösserungsfaktor der Durchbiegung – allgemein",
            referenz="SIA 262:2025, 4.4.3.2.5", name="Vergrösserungsfaktor der Durchbiegung")
        p.erklaerung(
            "Gerechnet in x, je Seite mit x-Bewehrung – einmal je Platte, nicht je "
            "Fall. ρ gehört zur gezogenen Seite, ρ′ zur Gegenseite; d′ reicht vom "
            "gezogenen Rand bis zur Gegenlage und ist damit deren statische Höhe – "
            "ρ′ der einen Seite ist das ρ der anderen. Die x-Bewehrung einer Seite "
            "zählt zusammen, in ihrem Schwerpunkt."
        )
        p.wert(phi, titel="Kriechzahl")
        gehalte = self._bewehrungsgehalte(p, e, werte)
        h = e["h"]
        ergebnis: Dict[str, Groesse] = {}
        for seite, definition in self.d_omega.items():
            rho, d = gehalte[seite]
            gegen = gehalte.get(seite.gegen)
            k = seite.gegen.value[0]
            rho_s = gegen[0] if gegen else werte.zahl(f"rho_{k}", rf"\rho_{{{k}}}", 0.0,
                                                      stellen=5)
            zahl = ((1.0 - 20.0 * rho_s.groesse.si) / (10.0 * rho.groesse.si ** 0.7)
                    * (0.75 + 0.1 * phi.groesse.si)
                    * (h.groesse.si / d.groesse.si) ** 3)
            omega = definition.belegen(Groesse(zahl, EINHEITSLOS))
            ergebnis[definition.id] = omega.groesse
            p.formel(
                omega,
                r"\frac{1 - 20 \cdot @rho_s}{10 \cdot @rho^{0.7}} \cdot "
                r"\left(0.75 + 0.1 \cdot @phi\right) \cdot \left(\frac{@h}{@d}\right)^{3}",
                {"rho_s": rho_s, "rho": rho, "phi": phi, "h": h, "d": d},
                titel=f"Vergrösserungsfaktor, Zug {seite}",
                name="Vergrösserungsfaktor der Durchbiegung")
        return ergebnis

    def _bewehrungsgehalte(self, p: Protokoll, e: Eingaben,
                           werte: Zwischenwerte) -> Dict[Zugseite, Tuple[Wert, Wert]]:
        """
        Je Seite mit x-Bewehrung der Bewehrungsgehalt und seine statische
        Hoehe -- die gezogene Seite braucht beide, die Gegenseite ihren
        Gehalt als rho'. Querschnitt, Schwerpunkt und Hoehe der Lage schreibt
        :func:`~opencivil.querschnitt.lagenaufbau.protokoll_lage`, wie in den
        Nachweisen der Lagen: dieselbe Hoehe heisst ueberall gleich, etwa
        d_{2,x}. Bis 2026-10-18 hiess sie hier d_u.
        """
        b = e["b"]
        gehalte: Dict[Zugseite, Tuple[Wert, Wert]] = {}
        for seite, eintraege in self.posten_je_seite.items():
            if not eintraege:
                continue
            a_s, z, d = lage_aus_posten(e, eintraege)
            A, d = protokoll_lage(p, e, Zwischenwerte(f"{self.id}.{seite}"), eintraege,
                                  a_s=a_s, z=z, d=d)
            k = seite.value[0]
            r = werte.zahl(f"rho_{k}", rf"\rho_{{{k}}}", a_s / (b.groesse.si * d.groesse.si),
                           stellen=5)
            p.formel(r, r"\frac{@A}{@b \cdot @d}", {"A": A, "b": b, "d": d},
                     titel=f"Bewehrungsgehalt {seite}", name="Bewehrungsgehalt")
            gehalte[seite] = (r, d)
        return gehalte


class Verformung(Nachweis):
    """
    Die Durchbiegung je Verformungsfall, in x -- mit dem
    Vergroesserungsfaktor der Seite, die der Fall zieht
    (:class:`Vergroesserungsfaktor`).
    """

    THEMA = "Verformung"
    ART = "w"

    def __init__(self, querschnitt, faelle: Sequence[Verformungsfall], *,
                 faktor: Vergroesserungsfaktor) -> None:
        if not faelle:
            raise ValueError("Der Verformungsnachweis braucht mindestens einen Fall.")
        self.querschnitt = querschnitt
        self.richtung = Richtung.X
        self.faelle = list(faelle)
        #: Die Faktoren der Seiten, die ein Fall zieht -- soweit es sie gibt.
        self.seiten = [seite for seite in UM_Y if seite in faktor.d_omega
                       and any(f.zugseite == seite for f in self.faelle)]

        basis = f"{querschnitt.id}.nachweis.verformung"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,w,{als_text(f.name)}}}",
                f"Erfüllungsgrad Verformung – {f.name}")
            for f in self.faelle}
        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=[Eingabebezug(f"omega_{seite}", faktor.d_omega[seite].id)
                     for seite in self.seiten],
            titel=f"Verformung – {querschnitt.name}",
            abschnitt=querschnitt.abschnitt,
        )

    # -- Rechnen ------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        self._protokoll_ansatz(p)
        omega = {seite: e[f"omega_{seite}"] for seite in self.seiten}
        urteile: List[NachweisUrteil] = []
        for fall in self.faelle:
            erg = self._einen_fall(p, fall, omega.get(fall.zugseite))
            urteile.append(self.urteil(self.d_ausnutzung[fall.name], fall.name, erg.ausgang,
                                       erg.begruendung))
        return Ausfuehrung({}, urteile)

    def _einen_fall(self, p: Protokoll, fall: Verformungsfall,
                    omega: Optional[Wert]) -> Fallergebnis:
        erg = Fallergebnis(fall=fall)
        p.titel(f"Verformung – {fall.name}", ebene=3)
        if omega is None:
            erg.begruendung = (
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

        erg.ausgang = v = Vergleich(w_eff, w_max)
        erg.begruendung = (
            f"w_eff = ω_w · w = {omega.groesse.si:.2f} · {w.formatiert()} mm = "
            f"{w_eff.formatiert()} mm {'≤' if v.erfuellt else '>'} "
            f"w_max = L/{GRENZE:g} = {w_max.formatiert()} mm.")
        v.bedingung(p, "Durchbiegung gegen Grenzwert")
        v.zeile(p, self.d_ausnutzung[fall.name], mit_urteil=True)
        return erg

    # -- Mitschrift ---------------------------------------------------------

    def _protokoll_ansatz(self, p: Protokoll) -> None:
        p.titel("Verformung")
        p.erklaerung(
            "Die Durchbiegung w ist mit der Steifigkeit E_cm ermittelt: elastisch, "
            "am ungerissenen Querschnitt. Der Faktor ω_w der gezogenen Seite führt "
            "sie auf die gerissene Platte unter Dauerlast; die so vergrösserte "
            "Durchbiegung hält der Nachweis gegen L/350."
        )
        p.annahme(f"w ist mit der Steifigkeit E_cm ermittelt. Grenzwert w_max = "
                  f"L/{GRENZE:g} nach Vorgabe, nicht nachgeschlagen.")
