"""
opencivil/nachweis/handrechnung.py -- Eckpunkte der Resistenzlinie von Hand.

VERANTWORTUNG:
Rechnet die wenigen Punkte der M-N-Interaktion, die sich mit Papier und
Taschenrechner nachvollziehen lassen, und schreibt dabei jeden Schritt
mit -- Formel, eingesetzte Zahlen, Ergebnis. Aus den Punkten entsteht ein
Polygon, und gegen dieses Polygon wird nachgewiesen.

WARUM NICHT GEGEN DIE GENAUE LINIE:
Die punktweise aus Dehnungsebenen aufgebaute Linie in
:mod:`opencivil.nachweis.biegung_normalkraft` ist genauer, aber sie entsteht aus
einer Faserintegration ueber hunderte Stuetzstellen. Wer das Ergebnis prueft,
kann es nicht nachrechnen -- er kann es nur glauben. Genau das soll dieses
Werkzeug nicht verlangen. Die genaue Linie bleibt darum als Vergleich im
Diagramm stehen, das Urteil faellt aber ueber die Handrechnung.

ANSATZ:
* Druckzone als Spannungsblock der Hoehe ``0.85 x`` mit durchgehend ``f_cd``.
* **Gedrueckter Stahl wird durchgehend vernachlaessigt.** Das liegt auf der
  sicheren Seite und erspart die Frage, ob er ueberhaupt fliesst.
* Bewehrung je Richtung zu zwei Lagen zusammengefasst -- eine je Seite.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite
Bezugsachse fuer M ist die halbe Querschnittshoehe, wie bei der genauen Linie.

DIE VIER PUNKTE (je Momentenvorzeichen, ausser wo vermerkt):

    1  M_Rd bei N = 0      x aus dem Kraeftegleichgewicht, dann M aus dem Hebelarm
    2  groesste Zugkraft   alles fliesst auf Zug; nur ein Punkt fuer beide Vorzeichen
    3  groesste Druckkraft reiner Beton, ohne Stahl; M = 0
    4  Punkt mit 0.85x = h/2   Druckzone bis zur halben Hoehe
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, MM, MM2, N_PRO_MM2, PROMILLE, Groesse,
)
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import Wert, WertDef

#: Anteil der Druckzonenhoehe, ueber den der Spannungsblock wirkt.
BLOCKANTEIL = 0.85


@dataclass(frozen=True)
class Lage:
    """Die zu einer Seite zusammengefasste Bewehrung."""

    a_s: float
    """Querschnittsflaeche in m^2, fuer die betrachtete Breite b."""

    z: float
    """Schwerpunkt in m, ab Oberkante."""

    f_yd: float
    """Bemessungswert der Fliessgrenze in Pa."""

    E_s: float
    """Elastizitaetsmodul in Pa."""

    text: str = ""


@dataclass(frozen=True)
class Eckpunkt:
    """Ein von Hand nachrechenbarer Punkt der Resistenzlinie."""

    kennung: str
    name: str
    N: float
    """Normalkraft in N (Zug positiv)."""

    M: float
    """Moment in Nm (Zug unten positiv)."""

    gueltig: bool = True
    hinweis: str = ""


class Handrechnung:
    """
    Die Eckpunkte einer Richtung, samt Mitschrift.

    Rechnet und schreibt in einem Zug -- wie jede Berechnung in diesem Werkzeug.
    Was in der Mitschrift steht, ist genau das, was gerechnet wurde.
    """

    def __init__(
        self, *,
        h: float, b: float, f_cd: float, eps_c2d: float,
        unten: Lage, oben: Lage, richtung: str, basis: str,
    ) -> None:
        self.h = h
        self.b = b
        self.f_cd = abs(f_cd)
        self.eps_c2d = abs(eps_c2d)
        self.unten = unten
        self.oben = oben
        self.richtung = richtung
        self.basis = basis

    # -- Hilfen fuer die Mitschrift -----------------------------------------

    def _w(self, name: str, symbol: str, groesse: Groesse,
           stellen: int = 1, beschreibung: str = "") -> Wert:
        """Ein benannter Zwischenwert, nur fuer die Darstellung."""
        return WertDef(
            id=f"{self.basis}.hand.{name}", symbol=symbol,
            einheit=groesse.anzeige, beschreibung=beschreibung, stellen=stellen,
        ).belegen(groesse)

    def _laenge(self, name: str, symbol: str, si: float, beschreibung: str = "") -> Wert:
        return self._w(name, symbol, Groesse.aus_si(si, MM), 1, beschreibung)

    def _flaeche(self, name: str, symbol: str, si: float, beschreibung: str = "") -> Wert:
        return self._w(name, symbol, Groesse.aus_si(si, MM2), 0, beschreibung)

    def _spannung(self, name: str, symbol: str, si: float, beschreibung: str = "") -> Wert:
        return self._w(name, symbol, Groesse.aus_si(si, N_PRO_MM2), 0, beschreibung)

    def _kraft(self, name: str, symbol: str, si: float, beschreibung: str = "") -> Wert:
        return self._w(name, symbol, Groesse.aus_si(si, KN), 1, beschreibung)

    def _moment(self, name: str, symbol: str, si: float, beschreibung: str = "") -> Wert:
        return self._w(name, symbol, Groesse.aus_si(si, KNM), 1, beschreibung)

    # -- Die Punkte ---------------------------------------------------------

    def rechnen(self, p: Protokoll) -> List[Eckpunkt]:
        """Rechnet alle Eckpunkte und schreibt die Herleitung."""
        self._ansatz(p)

        punkte: List[Eckpunkt] = []
        druck = self._groesste_druckkraft(p)
        zug = self._groesste_zugkraft(p)

        # Reihenfolge so, dass ein geschlossenes Polygon entsteht: vom reinen
        # Druck ueber die positive Seite zur Zugspitze und ueber die negative
        # Seite zurueck.
        rechts = self._seite(p, positiv=True)
        links = self._seite(p, positiv=False)

        punkte.append(druck)
        punkte.extend(reversed([q for q in rechts if q.gueltig]))
        punkte.append(zug)
        punkte.extend([q for q in links if q.gueltig])

        self._uebersicht(p, punkte)
        return punkte

    def _ansatz(self, p: Protokoll) -> None:
        p.titel(f"Resistenzlinie aus Handrechnung – {self.richtung}")
        p.text(
            "Die Druckzone wird als Spannungsblock der Höhe 0.85·x mit "
            "durchgehend f_cd angesetzt. Gedrückter Stahl bleibt durchgehend "
            "unberücksichtigt – das liegt auf der sicheren Seite und erspart "
            "die Frage, ob er fliesst. Die Bewehrung ist je Seite zu einer "
            "Lage zusammengefasst. Das Moment bezieht sich auf die halbe "
            "Querschnittshöhe."
        )
        p.tabelle(
            kopf=[r"\text{Seite}", r"A_s\ [\mathrm{mm}^2]",
                  r"z\ [\mathrm{mm}]", r"f_{yd}\ [\mathrm{N/mm^2}]"],
            zeilen=[
                [rf"\text{{{lage.text}}}", f"{lage.a_s * 1e6:.0f}",
                 f"{lage.z * 1e3:.1f}", f"{lage.f_yd / 1e6:.0f}"]
                for lage in (self.unten, self.oben)
            ],
            titel="Zusammengefasste Bewehrung",
            ausrichtung="lrrr",
        )

    def _groesste_druckkraft(self, p: Protokoll) -> Eckpunkt:
        """Reiner Beton ohne Stahl -- die einfachste aller Grenzen."""
        N = -self.b * self.h * self.f_cd
        p.titel("Grösste Druckkraft", ebene=3)
        p.formel(
            self._kraft("N_Rd_druck", "N_{Rd}^{-}", N,
                        "Grösste aufnehmbare Druckkraft"),
            r"-@b \cdot @h \cdot @f_cd",
            {
                "b": self._laenge("b", "b", self.b),
                "h": self._laenge("h", "h", self.h),
                "f_cd": self._spannung("f_cd", "f_{cd}", self.f_cd),
            },
            titel="Gleichmässiger Druck, ohne Bewehrung",
        )
        p.text("Zum zugehörigen Moment: M_Rd = 0, da die Spannung gleichmässig ist.")
        return Eckpunkt("druck", "grösste Druckkraft", N, 0.0)

    def _groesste_zugkraft(self, p: Protokoll) -> Eckpunkt:
        """
        Beide Lagen fliessen auf Zug.

        Es gibt hier nur *einen* Punkt, nicht je Momentenvorzeichen einen: der
        Dehnungszustand ist eindeutig, also auch das zugehoerige Moment.
        """
        u, o = self.unten, self.oben
        N = u.a_s * u.f_yd + o.a_s * o.f_yd
        # Jede Kraft mal ihrem Hebelarm um die halbe Hoehe. Beide sind Zug, also
        # positiv; die Hebelarme haben verschiedene Vorzeichen.
        M = u.a_s * u.f_yd * (u.z - self.h / 2) + o.a_s * o.f_yd * (o.z - self.h / 2)

        p.titel("Grösste Zugkraft", ebene=3)
        eingaben = {
            "A_s": self._flaeche("As_u", "A_s", u.a_s),
            "A_s2": self._flaeche("As_o", "A_s'", o.a_s),
            "f_yd": self._spannung("fyd_u", "f_{yd}", u.f_yd),
            "f_yd2": self._spannung("fyd_o", "f_{yd}'", o.f_yd),
        }
        p.formel(
            self._kraft("N_Rd_zug", "N_{Rd}^{+}", N, "Grösste aufnehmbare Zugkraft"),
            r"@A_s \cdot @f_yd + @A_s2 \cdot @f_yd2",
            eingaben,
            titel="Beide Lagen fliessen auf Zug",
        )
        p.formel(
            self._moment("M_Rd_zug", "M_{Rd}(N_{Rd}^{+})", M,
                         "Moment bei grösster Zugkraft"),
            r"@A_s \cdot @f_yd \cdot \left(@d - \tfrac{@h}{2}\right) "
            r"+ @A_s2 \cdot @f_yd2 \cdot \left(@d2 - \tfrac{@h}{2}\right)",
            {
                **eingaben,
                "d": self._laenge("z_u", "d", u.z),
                "d2": self._laenge("z_o", "d'", o.z),
                "h": self._laenge("h", "h", self.h),
            },
            titel="Kräfte mal Hebelarm um die halbe Höhe",
        )
        p.text(
            "Beide Lagen stehen unter Zug, ihre Hebelarme haben aber "
            "entgegengesetzte Vorzeichen. Bei symmetrischer Bewehrung hebt sich "
            "das Moment deshalb auf – die Zugspitze liegt dann auf der Achse "
            "M = 0. Für beide Momentenvorzeichen gilt derselbe Punkt."
        )
        return Eckpunkt("zug", "grösste Zugkraft", N, M)

    def _seite(self, p: Protokoll, *, positiv: bool) -> List[Eckpunkt]:
        """Die beiden Punkte eines Momentenvorzeichens."""
        zug, gegen = (self.unten, self.oben) if positiv else (self.oben, self.unten)
        # d wird ab der gedrueckten Randfaser gemessen -- die wechselt mit dem
        # Vorzeichen des Moments die Seite.
        d = zug.z if positiv else self.h - zug.z
        vz = 1.0 if positiv else -1.0
        marke = "pos" if positiv else "neg"

        p.titel(
            "Positives Moment (Zug unten)" if positiv
            else "Negatives Moment (Zug oben)", ebene=3)

        punkte = [self._bei_n_null(p, zug, d, vz, marke)]
        halb = self._halbe_hoehe(p, zug, d, vz, marke)
        if halb is not None:
            punkte.append(halb)
        return punkte

    def _bei_n_null(self, p: Protokoll, zug: Lage, d: float,
                    vz: float, marke: str) -> Eckpunkt:
        """Reine Biegung: die Druckkraft im Beton haelt der Zugkraft die Waage."""
        x = zug.a_s * zug.f_yd / (BLOCKANTEIL * self.b * self.f_cd)
        M = zug.a_s * zug.f_yd * (d - BLOCKANTEIL * x / 2.0)

        w_x = self._laenge(f"x_{marke}", "x", x, "Höhe der Druckzone")
        eingaben = {
            "A_s": self._flaeche(f"As_{marke}", "A_s", zug.a_s),
            "f_yd": self._spannung(f"fyd_{marke}", "f_{yd}", zug.f_yd),
            "b": self._laenge("b", "b", self.b),
            "f_cd": self._spannung("f_cd", "f_{cd}", self.f_cd),
        }
        p.formel(
            w_x,
            rf"\frac{{@A_s \cdot @f_yd}}{{{BLOCKANTEIL} \cdot @b \cdot @f_cd}}",
            eingaben,
            titel="Druckzonenhöhe aus dem Kräftegleichgewicht",
        )
        p.formel(
            self._moment(f"M_Rd_N0_{marke}", "M_{Rd}(N=0)", vz * M,
                         "Momentenwiderstand bei N = 0"),
            rf"@A_s \cdot @f_yd \cdot \left(@d - \frac{{{BLOCKANTEIL} \cdot @x}}{{2}}\right)",
            {**eingaben, "d": self._laenge(f"d_{marke}", "d", d), "x": w_x},
            titel="Momentenwiderstand bei reiner Biegung",
        )
        return Eckpunkt(f"n0_{marke}", f"M_Rd(N=0) {'+' if vz > 0 else '−'}",
                        0.0, vz * M)

    def _halbe_hoehe(self, p: Protokoll, zug: Lage, d: float,
                     vz: float, marke: str) -> Optional[Eckpunkt]:
        """
        Der Punkt, bei dem der Spannungsblock bis zur halben Hoehe reicht.

        Gilt nur, solange die Zugbewehrung dabei noch fliesst. Tut sie es nicht,
        waere ``f_sd = f_yd`` zu guenstig angesetzt, und der Punkt faellt weg --
        das Polygon laeuft dann geradlinig vom reinen Druck zum Punkt bei N = 0.
        """
        x = self.h / (2.0 * BLOCKANTEIL)
        block = BLOCKANTEIL * x                      # = h/2
        D = self.f_cd * self.b * block               # Betondruckkraft, Betrag
        N = -D + zug.a_s * zug.f_yd
        M = D * (self.h / 2 - block / 2) + zug.a_s * zug.f_yd * (d - self.h / 2)

        # Fliesskriterium: die Dehnung der Zugbewehrung bei Kruemmung
        # chi = eps_c2d / x muss die Fliessdehnung erreichen.
        chi = self.eps_c2d / x
        eps_s = (d - x) * chi
        eps_yd = zug.f_yd / zug.E_s

        w_x = self._laenge(f"xh_{marke}", "x", x, "Druckzonenhöhe")
        p.formel(
            w_x,
            rf"\frac{{@h}}{{2 \cdot {BLOCKANTEIL}}}",
            {"h": self._laenge("h", "h", self.h)},
            titel=f"Druckzone bis zur halben Höhe: {BLOCKANTEIL}·x = h/2",
        )
        p.formel(
            self._w(f"eps_s_{marke}", r"\varepsilon_s",
                    Groesse.aus_si(eps_s, PROMILLE), 2,
                    "Dehnung der Zugbewehrung"),
            r"\left(@d - @x\right) \cdot \frac{@eps_c2d}{@x}",
            {
                "d": self._laenge(f"d_{marke}", "d", d),
                "x": w_x,
                "eps_c2d": self._w("eps_c2d", r"\varepsilon_{c2d}",
                                   Groesse.aus_si(self.eps_c2d, PROMILLE), 2),
            },
            titel="Fliesskriterium – Dehnung der Zugbewehrung",
        )

        if eps_s < eps_yd:
            p.hinweis(
                f"Die Zugbewehrung erreicht die Fliessdehnung nicht "
                f"(ε_s = {eps_s * 1e3:.2f} ‰ < ε_yd = {eps_yd * 1e3:.2f} ‰). "
                f"Dieser Eckpunkt entfällt; das Polygon verläuft geradlinig vom "
                f"reinen Druck zum Punkt bei N = 0."
            )
            return Eckpunkt(
                f"halb_{marke}", "0.85x = h/2", N, vz * M,
                gueltig=False,
                hinweis=f"ε_s = {eps_s * 1e3:.2f} ‰ < ε_yd = {eps_yd * 1e3:.2f} ‰")

        p.text(
            f"ε_s = {eps_s * 1e3:.2f} ‰ ≥ ε_yd = {eps_yd * 1e3:.2f} ‰ – "
            f"die Zugbewehrung fliesst, f_sd = f_yd gilt."
        )

        eingaben = {
            "f_cd": self._spannung("f_cd", "f_{cd}", self.f_cd),
            "b": self._laenge("b", "b", self.b),
            "x": w_x,
            "A_s": self._flaeche(f"As_{marke}", "A_s", zug.a_s),
            "f_sd": self._spannung(f"fsd_{marke}", "f_{sd}", zug.f_yd),
        }
        p.formel(
            self._kraft(f"N_halb_{marke}", "N_{Rd}", N, "Normalkraft in diesem Punkt"),
            rf"-@f_cd \cdot @b \cdot {BLOCKANTEIL} \cdot @x + @A_s \cdot @f_sd",
            eingaben,
            titel="Kräftegleichgewicht",
        )
        p.formel(
            self._moment(f"M_halb_{marke}", "M_{Rd}", vz * M,
                         "Moment in diesem Punkt"),
            rf"@f_cd \cdot @b \cdot {BLOCKANTEIL} \cdot @x \cdot "
            rf"\left(\tfrac{{@h}}{{2}} - \tfrac{{{BLOCKANTEIL} \cdot @x}}{{2}}\right) "
            rf"+ @A_s \cdot @f_sd \cdot \left(@d - \tfrac{{@h}}{{2}}\right)",
            {
                **eingaben,
                "h": self._laenge("h", "h", self.h),
                "d": self._laenge(f"d_{marke}", "d", d),
            },
            titel="Momentengleichgewicht um die halbe Höhe",
        )
        return Eckpunkt(f"halb_{marke}", "0.85x = h/2", N, vz * M)

    def _uebersicht(self, p: Protokoll, punkte: List[Eckpunkt]) -> None:
        p.tabelle(
            kopf=[r"\text{Eckpunkt}", r"N\ [\mathrm{kN}]", r"M\ [\mathrm{kNm}]"],
            zeilen=[
                [rf"\text{{{q.name}}}", f"{q.N / 1e3:.1f}", f"{q.M / 1e3:.1f}"]
                for q in punkte
            ],
            titel="Eckpunkte der Resistenzlinie aus Handrechnung",
            ausrichtung="lrr",
        )
        p.text(
            "Zwischen diesen Punkten wird geradlinig verbunden. Alle weiteren "
            "Widerstände folgen durch lineare Interpolation auf diesem Polygon."
        )


def lagen_zusammenfassen(posten) -> Dict[str, Lage]:
    """
    Fasst die Bewehrungsposten einer Richtung zu zwei Lagen zusammen.

    Je Richtung liegen genau zwei Bewehrungslagen, jede davon aus Grund-
    bewehrung und Zulage. Fuer die Handrechnung zaehlt je Seite nur die Summe
    der Flaechen und ihr gemeinsamer Schwerpunkt.

    ``posten`` ist eine Folge von ``(a_s, z, f_yd, E_s, text, von_unten)``.

    Gruppiert wird nach ``von_unten``, also nach der Zugehoerigkeit zur unteren
    oder oberen Lage -- **nicht** nach der Hoehenlage. Grundbewehrung und Zulage
    derselben Lage liegen naemlich auf leicht verschiedenen Hoehen, weil ihre
    Durchmesser verschieden sind. Wer nach z gruppiert, bekommt drei Gruppen
    statt zwei und verliert stillschweigend eine davon.
    """
    if not posten:
        raise ValueError("Ohne Bewehrung lässt sich nichts von Hand rechnen.")

    gruppen: Dict[bool, List] = {}
    for eintrag in posten:
        gruppen.setdefault(eintrag[5], []).append(eintrag)

    def buendeln(gruppe) -> Lage:
        flaeche = sum(a for a, _, _, _, _, _ in gruppe)
        if flaeche <= 0.0:
            # Ohne Flaeche gibt es keinen Schwerpunkt -- die Hoehenlage genuegt.
            a_s, z, f_yd, E_s, text, _ = gruppe[0]
            return Lage(0.0, z, f_yd, E_s, text)
        schwerpunkt = sum(a * z for a, z, _, _, _, _ in gruppe) / flaeche
        # Bei verschiedenen Stahlsorten in einer Lage zaehlt die schwaechere --
        # sonst rechnete man mit einer Festigkeit, die ein Teil nicht hat.
        f_yd = min(f for _, _, f, _, _, _ in gruppe)
        E_s = min(e for _, _, _, e, _, _ in gruppe)
        beteiligt = [t for a, _, _, _, t, _ in gruppe if a > 0.0]
        return Lage(flaeche, schwerpunkt, f_yd, E_s, " + ".join(beteiligt))

    if True not in gruppen or False not in gruppen:
        # Nur eine Seite bewehrt -- die andere zaehlt mit null Flaeche, damit
        # die Formeln unveraendert gelten.
        vorhanden = buendeln(next(iter(gruppen.values())))
        leer = Lage(0.0, 0.0 if vorhanden.z > 0 else 0.0,
                    vorhanden.f_yd, vorhanden.E_s, "keine")
        return ({"unten": vorhanden, "oben": leer} if True in gruppen
                else {"unten": leer, "oben": vorhanden})

    return {"unten": buendeln(gruppen[True]), "oben": buendeln(gruppen[False])}
