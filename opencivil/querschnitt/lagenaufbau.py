"""
opencivil/querschnitt/lagenaufbau.py -- wo die Bewehrung einer Platte liegt.

VERANTWORTUNG:
Der Lagenaufbau (:class:`Lagenaufbau`) rechnet je Bewehrungsposten seine
Tiefe ab Oberkante und seinen Querschnitt, dazu Bewehrungsmass und
Distanzhalter. Die Nachweise fassen die Posten einer Lage mit den Helfern
hier zusammen: Querschnitt, gemeinsamer Schwerpunkt und statische Hoehe
(:func:`lage_aus_posten`, :func:`protokoll_lage`).

EIN POSTEN, EINE GESTALT:
Ein Posten reist als :class:`Postenbezug` -- Lage, Art, Posten und seine
Werte. Bis 2026-10-25 reiste er als Tupel ``(Lage, Art, Posten, ID von A_s,
ID von z)``, wurde rund zwanzigmal nach Stelle zerlegt, und seine Marke
``1g`` entstand an neun Stellen neu. Bis dahin stand all das auch in
:mod:`opencivil.querschnitt.platte`, die damit ueber 1000 Zeilen kam.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import KG_PRO_M3, MM, MM2, Groesse
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Abschnitt, Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.material.betonstahl import STAHLDICHTE
from opencivil.querschnitt.zugseite import Zugseite

if TYPE_CHECKING:
    from opencivil.querschnitt.platte import Bewehrungslage, Bewehrungsposten, Postenart


@dataclass(frozen=True)
class Postenbezug:
    """
    Ein Bewehrungsposten einer Platte samt den Werten, die ihn beschreiben --
    siehe Dateikopf. Angelegt nur von der Platte
    (:class:`~opencivil.querschnitt.platte.Plattenquerschnitt`), die auch
    Marke, Index und Bezeichnung bildet.

    Ein Nachweis liest die Werte eines Postens unter Namen mit dessen
    :attr:`marke` (:meth:`name`): ``a_s_1g``, ``z_1g``, ``phi_1g``. So lesen
    sie auch die Helfer hier.
    """

    lage: Bewehrungslage
    art: Postenart
    posten: Bewehrungsposten
    marke: str
    """Kurzform fuer die Namen der Werte, z.B. ``1g``."""

    index: str
    """
    Der Symbolindex, z.B. ``1,x,g``: Lage, Richtung, Art -- in dieser
    Reihenfolge, und immer alle drei. Damit ist jedes Symbol eindeutig, auch
    wenn zwei Lagen dieselbe Richtung tragen. Die Handrechnung braucht
    denselben Index fuer ihre zusammengefassten Lagen.
    """

    bezeichnung: str
    """``1. Lage Grundbewehrung``."""

    phi_def: WertDef
    """Der Stabdurchmesser."""

    as_def: WertDef
    """Der Bewehrungsquerschnitt, aus dem Lagenaufbau."""

    z_def: WertDef
    """Die Tiefe ab Oberkante, aus dem Lagenaufbau -- nicht die statische Hoehe."""

    def name(self, groesse: str) -> str:
        """Der Name, unter dem ein Nachweis eine Groesse des Postens liest: ``a_s_1g``."""
        return f"{groesse}_{self.marke}"

    def bezuege(self, *groessen: str) -> List[Eingabebezug]:
        """Diese Groessen des Postens -- ``a_s``, ``z``, ``phi`` -- als Eingaben, je unter :meth:`name`."""
        definitionen = {"a_s": self.as_def, "z": self.z_def, "phi": self.phi_def}
        return [Eingabebezug(self.name(g), definitionen[g].id) for g in groessen]


def lagenindex(posten: Sequence[Postenbezug]) -> str:
    """
    Der Symbolindex einer Lage aus ihren Posten -- ``1,x`` statt ``1,x,g``.

    Gerechnet wird mit der ganzen Lage, nicht mit einem Posten; ein
    Postenindex am Symbol behauptete etwas anderes. Hat die Lage nur einen
    Posten, ist dessen Index auch ihrer -- dann heisst ``A_s`` so wie in der
    Tabelle der Platte.
    """
    if not posten:
        return ""
    if len(posten) == 1:
        return posten[0].index
    return posten[0].lage.index


def statische_hoehe(z: float, h: float, seite: Zugseite) -> float:
    """
    Die statische Hoehe einer Lage in der Tiefe ``z`` unter der Oberkante,
    gemessen ab dem gedrueckten Rand: unten ``d = z``, oben ``d = h - z`` --
    die Zahl zur Zeile von :func:`protokoll_statische_hoehe`. Wer ``z``
    stehen liesse, bekaeme bei den oberen Lagen eine Zahl, die keine
    statische Hoehe ist.
    """
    return z if seite is Zugseite.UNTEN else h - z


def lage_aus_posten(
    e: Eingaben, posten: Sequence[Postenbezug],
) -> Tuple[float, Optional[float], Optional[float]]:
    """
    Querschnitt, gemeinsamer Schwerpunkt und statische Hoehe einer Lage aus
    ihren Posten -- die Zahlen, die :func:`protokoll_lage` herleitet. Der
    Nachweis liest dafuer je Posten ``a_s`` und ``z``
    (:meth:`Postenbezug.bezuege`), dazu die Dicke ``h``.

    Grundbewehrung und Zulage liegen auf leicht verschiedenen Hoehen, gehoeren
    aber zur selben Lage: es zaehlt ihr gemeinsamer Schwerpunkt. Ohne Stahl
    gibt es weder Schwerpunkt noch Hoehe, beide ``None``. Bis 2026-10-18
    rechneten drei Nachweise das je fuer sich.
    """
    flaechen = [(e.g(q.name("a_s")).si, e.g(q.name("z")).si) for q in posten]
    a_s = sum(a for a, _ in flaechen)
    if a_s <= 0.0:
        return a_s, None, None
    z = sum(a * t for a, t in flaechen) / a_s
    return a_s, z, statische_hoehe(z, e.g("h").si, posten[0].lage.seite)


def protokoll_lage(
    p: Protokoll, e: Eingaben, werte: Zwischenwerte, posten: Sequence[Postenbezug],
    *, a_s: float, z: Optional[float] = None, d: float = 0.0,
) -> Tuple[Wert, Optional[Wert]]:
    """
    Querschnitt und statische Hoehe einer Lage, aus ihren Posten hergeleitet
    -- gelesen wie bei :func:`lage_aus_posten`.

    Liegen Grundbewehrung und Zulage in der Lage, stehen Summe und gemeinsamer
    Schwerpunkt da -- sonst fiele der Schwerpunkt vom Himmel. Ohne ``z`` nur
    der Querschnitt. Zurueck kommen ``A_s`` und ``d`` fuer die Formeln danach.
    """
    index = lagenindex(posten)
    eingaben = {f"a{i}": e[q.name("a_s")] for i, q in enumerate(posten)}
    summe = " + ".join(f"@{name}" for name in eingaben)
    flaeche = werte.flaeche("A_s", f"A_{{s,{index}}}", a_s)
    if len(posten) > 1:
        p.formel(flaeche, summe, eingaben, titel="Bewehrung der Lage")
    if z is None:
        return flaeche, None

    if len(posten) > 1:
        tiefe = werte.laenge("z", f"z_{{{index}}}", z)
        eingaben.update({f"z{i}": e[q.name("z")] for i, q in enumerate(posten)})
        momente = " + ".join(rf"@a{i} \cdot @z{i}" for i in range(len(posten)))
        p.formel(tiefe, rf"\frac{{{momente}}}{{{summe}}}", eingaben,
                 titel="Gemeinsamer Schwerpunkt der Lage",
                 name="Schwerpunkt der zusammengefassten Lage")
    else:
        tiefe = e[posten[0].name("z")]
    hoehe = werte.laenge("d", f"d_{{{index}}}", d)
    protokoll_statische_hoehe(p, hoehe, h=e["h"], z=tiefe, seite=posten[0].lage.seite)
    return flaeche, hoehe


def protokoll_statische_hoehe(
    p: Protokoll, d: Wert, *, h: Wert, z: Wert, seite: Zugseite,
) -> None:
    """
    Die statische Hoehe einer gezogenen Lage, gemessen ab dem gedrueckten Rand.

    Eine untere Lage misst ab der Oberkante, ``d = z``; eine obere ab der
    Unterkante, ``d = h - z``. Mehrere Nachweise brauchen diese Zeile -- steht
    sie an einer Stelle, sagt «unten» in allen dasselbe.
    """
    rand, gezogen = seite.raender
    vorlage, eingaben = (("@z", {"z": z}) if seite is Zugseite.UNTEN
                         else ("@h - @z", {"h": h, "z": z}))
    p.formel(d, vorlage, eingaben,
             titel=f"Statische Höhe der Lage {gezogen}, ab dem gedrückten Rand {rand}",
             name="Statische Höhe")


class Lagenaufbau(Prozedur):
    """
    Bestimmt statische Hoehe und Bewehrungsquerschnitt aller Posten.

    Beides in einem Zug und in einer Tabelle. Frueher stand fuer jeden Posten
    eine eigene Flaechenformel in der Herleitung -- fuenf Lagen ergaben fuenf
    gleich aussehende Bloecke, in denen sich nur die Zahlen unterschieden. Die
    Formel steht jetzt einmal da, die Ergebnisse stehen in der Tabelle.

    STAPELUNG:
    Die Lagen werden je Seite von aussen nach innen gestapelt. Die Huelle einer
    Lage beginnt bei der Ueberdeckung und waechst um den groessten Durchmesser
    der davorliegenden Lage. ``d`` wird von der gezogenen Randfaser aus
    gemessen -- bei den unteren Lagen von der Unterkante, bei den oberen von
    der Oberkante.

    Wie Grundbewehrung und Zulage innerhalb einer Lage zueinander liegen, sagt
    :attr:`~opencivil.querschnitt.platte.Bewehrungslage.unguenstig`.
    """

    def __init__(
        self,
        id: str,
        *,
        ausgaben: Sequence[WertDef],
        bezuege: Sequence[Eingabebezug],
        posten: Sequence[Postenbezug],
        d_bewehrungsmass: WertDef,
        d_distanzhalter: WertDef,
        titel: str = "Bewehrungslagen",
        abschnitt: Optional[Abschnitt] = None,
    ) -> None:
        super().__init__(id, ausgaben=ausgaben, bezuege=bezuege, titel=titel,
                         referenz="SIA 262:2025, 5.2.2", abschnitt=abschnitt)
        self.posten = list(posten)
        self.d_bewehrungsmass = d_bewehrungsmass
        self.d_distanzhalter = d_distanzhalter

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        h = e.g("h")
        b = e.g("b")
        # Die Teilung einer y-Lage ist auf den Laufmeter bezogen, die einer
        # x-Lage auf die eingegebene Breite. Wer hier eine einzige Breite
        # nimmt, rechnet bei b != 1000 mm die halbe oder doppelte y-Bewehrung.
        breite_von = lambda r: e.g(r.breite)
        breiten: Dict[str, Groesse] = {}
        # Ohne erklaerende Vorrede: die Lagentabelle zeigt Randabstand und Tiefe
        # je Posten, und wie beides zustande kommt, steht in der Klassendoku.
        ueber_abstand = any(q.posten.ueber_abstand for q in self.posten)
        ueber_anzahl = any(not q.posten.ueber_abstand for q in self.posten)
        # Nur wenn alle Posten dieselbe Art der Mengenangabe verwenden, darf die
        # Grösse in die Kopfzeile. Sonst muss sie in jeder Zelle stehen.
        einheitlich = not (ueber_abstand and ueber_anzahl)
        if ueber_abstand:
            p.ansatz(
                r"A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}",
                titel="Bewehrungsquerschnitt über die Breite b",
                referenz="SIA 262:2025, 5.5.2")
        if ueber_anzahl:
            p.ansatz(
                r"A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot n",
                titel="Bewehrungsquerschnitt aus der Stabzahl",
                referenz="SIA 262:2025, 5.5.2")

        # Huellen je Seite, von aussen nach innen. Jede Lage kommt nur einmal
        # vor, auch wenn sie zwei Posten traegt -- nach Nummer entdoppelt, weil
        # Bewehrungslage als veraenderliche Datenklasse nicht hashbar ist.
        huelle = {True: e.g("c_nom_unten"), False: e.g("c_nom_oben")}
        lagen_nach_nummer = {q.lage.nummer: q.lage for q in self.posten}
        raender: Dict[Tuple[bool, int], Groesse] = {}
        for lage in sorted(lagen_nach_nummer.values(),
                           key=lambda l: (not l.von_unten, l.stapelrang)):
            schluessel = (lage.von_unten, lage.stapelrang)
            raender[schluessel] = huelle[lage.von_unten]
            huelle[lage.von_unten] = huelle[lage.von_unten] + lage.groesster_durchmesser

        # Der dickste Stab je Lage bestimmt, wo die innere Kante liegt.
        dickster: Dict[int, Groesse] = {}
        for q in self.posten:
            phi = e.g(q.name("phi"))
            vorher = dickster.get(q.lage.nummer)
            if vorher is None or phi.si > vorher.si:
                dickster[q.lage.nummer] = phi

        # Die Breite je Zeile nur, wo sie sich unterscheidet: x gilt je b, y
        # je Laufmeter. Bei b = 1000 mm stuende in jeder Zeile dieselbe Zahl.
        mit_breite = len({breite_von(q.lage.richtung).si for q in self.posten}) > 1

        ergebnis: Dict[str, Groesse] = {}
        zeilen: List[List[str]] = []
        #: Je Lagennummer die Ober- und Unterkante des Stahls, in m ab Oberkante.
        kanten: Dict[int, Tuple[float, float]] = {}
        for q in self.posten:
            phi = e.g(q.name("phi"))
            huellebene = raender[(q.lage.von_unten, q.lage.stapelrang)]
            if q.lage.unguenstig:
                # Innere Kanten fluchten: der dünnere Stab rückt zur Mitte.
                rand = huellebene + dickster[q.lage.nummer] - phi / 2.0
            else:
                # Äussere Kanten fluchten, jeder um seinen eigenen Halbmesser.
                rand = huellebene + phi / 2.0
            z = h - rand if q.lage.von_unten else rand

            oben, unten = z.si - phi.si / 2.0, z.si + phi.si / 2.0
            vorher = kanten.get(q.lage.nummer)
            kanten[q.lage.nummer] = (
                (min(oben, vorher[0]), max(unten, vorher[1])) if vorher
                else (oben, unten))

            b_q = breite_von(q.lage.richtung)
            breiten[q.as_def.id] = b_q
            if q.posten.ueber_abstand:
                s = e.g(q.name("s"))
                a_s = Groesse.aus_si(
                    math.pi * phi.si * phi.si / 4.0 * (b_q.si / s.si), MM2)
                # Bei gemischter Angabe muss in jeder Zelle stehen, um welche
                # Grösse es geht -- sonst liest man 150 und 7 in derselben
                # Spalte und weiss nicht, was gemeint ist.
                menge = Mathe(s.formatiert(0, MM) if einheitlich
                              else rf"s = {s.als_latex(0, MM)}")
            else:
                anzahl = float(q.posten.anzahl)
                a_s = Groesse.aus_si(math.pi * phi.si * phi.si / 4.0 * anzahl, MM2)
                menge = Mathe(f"{anzahl:g}" if einheitlich else f"n = {anzahl:g}")

            ergebnis[q.z_def.id] = z
            ergebnis[q.as_def.id] = a_s
            zeilen.append([
                q.bezeichnung,
                q.lage.richtung.value,
                q.lage.stahl.name if q.lage.stahl else "–",
                Mathe(phi.formatiert(0, MM)),
                menge,
                *([Mathe(b_q.formatiert(0, MM))] if mit_breite else []),
                Mathe(rand.formatiert(1, MM)),
                Mathe(z.formatiert(1, MM)),
                Mathe(a_s.formatiert(0, MM2)),
            ])

        ergebnis.update(self._kennzahlen(p, e, h, b, ergebnis, kanten, breiten))

        if not einheitlich:
            mengenkopf = "Menge"
        elif ueber_abstand:
            mengenkopf = Mathe(r"s\ [\mathrm{mm}]")
        else:
            mengenkopf = Mathe("n")

        kopf = ["Bewehrung", "Richtung", "Stahl",
                Mathe(r"\varnothing\ [\mathrm{mm}]"), mengenkopf,
                *([Mathe(r"b\ [\mathrm{mm}]")] if mit_breite else []),
                "Randabstand [mm]",
                Mathe(r"z\ [\mathrm{mm}]"), Mathe(r"A_s\ [\mathrm{mm}^2]")]
        p.tabelle(
            kopf=kopf,
            zeilen=zeilen,
            titel="Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte",
            ausrichtung="lll" + "r" * (len(kopf) - 3),
        )
        return ergebnis

    def _kennzahlen(
        self, p: Protokoll, e: Eingaben, h: Groesse, b: Groesse,
        flaechen: Mapping[str, Groesse], kanten: Mapping[int, Tuple[float, float]],
        breiten: Mapping[str, Groesse],
    ) -> Dict[str, Groesse]:
        """
        Bewehrungsmass und Hoehe der Distanzhalter.

        Beides sind Angaben fuer die Ausfuehrung, keine Nachweisgroessen -- sie
        gehoeren aber in den Kern und nicht in die Oberflaeche, damit sie in der
        Herleitung stehen und sich zurueckverfolgen lassen.
        """
        ergebnis: Dict[str, Groesse] = {}
        werte = Zwischenwerte(self.id)

        # Auf b bezogen: eine y-Lage steht je Laufmeter da, eine x-Lage je b.
        # Das Verhaeltnis b/b_q rechnet sie auf denselben Streifen um; sind alle
        # Breiten gleich, ist es die schlichte Summe.
        a_s_gesamt = sum(
            (flaechen[q.as_def.id].si * (b.si / breiten[q.as_def.id].si)
             for q in self.posten), 0.0)
        # Stahlvolumen je Betonvolumen: A_s * L * rho / (b * L * h) -- die Laenge
        # kuerzt sich heraus.
        mass = a_s_gesamt * STAHLDICHTE / (b.si * h.si)
        ergebnis[self.d_bewehrungsmass.id] = Groesse(mass, KG_PRO_M3)
        p.formel(
            self.d_bewehrungsmass.belegen(Groesse(mass, KG_PRO_M3)),
            rf"\frac{{@A_s \cdot {STAHLDICHTE:g}\,\mathrm{{kg}}/\mathrm{{m}}^{{3}}}}"
            rf"{{@b \cdot @h}}",
            {"A_s": werte.flaeche("A_s_gesamt", "A_{s,tot}", a_s_gesamt),
             "b": e["b"], "h": e["h"]},
            titel="Bewehrungsmass je Kubikmeter Beton",
        )

        # Die Distanzhalter stehen zwischen der innersten unteren und der
        # innersten oberen Lage. Fehlt die innere, gilt die aeussere.
        unten = kanten.get(2) or kanten.get(1)
        oben = kanten.get(3) or kanten.get(4)
        if unten is None or oben is None:
            # Eine deklarierte Ausgabe muss immer entstehen, sonst bricht der
            # Loeser ab. Ohne Bewehrung auf beiden Seiten gibt es nichts
            # abzustuetzen -- null ist hier die richtige Antwort, nicht "fehlt".
            ergebnis[self.d_distanzhalter.id] = Groesse(0, MM)
            p.text("Bewehrung nur auf einer Seite → keine Distanzhalter.")
            return ergebnis

        hoehe = unten[0] - oben[1]
        ergebnis[self.d_distanzhalter.id] = Groesse.aus_si(hoehe, MM)
        p.formel(
            self.d_distanzhalter.belegen(Groesse.aus_si(hoehe, MM)), "@OK - @UK",
            {"OK": werte.laenge("OK", r"\text{OK innere untere Lage}", unten[0]),
             "UK": werte.laenge("UK", r"\text{UK innere obere Lage}", oben[1])},
            titel="Höhe der Distanzhalter")
        return ergebnis
