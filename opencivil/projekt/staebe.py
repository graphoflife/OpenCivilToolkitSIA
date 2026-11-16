"""
opencivil/projekt/staebe.py -- der Baukasten eines Stabwerks, eben und im Raum.

VERANTWORTUNG:
Was das 2D- und das 3D-Balkensystem gleich tun (:class:`MitStaeben`):
Knoten an gleichen Koordinaten zusammenfuehren; Linien, Lager, Materialien,
Querschnitte, Lasten und Diagramme ohne Oberflaeche anlegen; eine Linie
finden, messen, teilen und umkehren. Welche Klassen die Teile haben und wie
die Achsen heissen, sagt die Beschreibung, die ihn nimmt
(:class:`~opencivil.projekt.balkensystem.BalkensystemEintrag`,
:class:`~opencivil.projekt.balkensystem3d.Balkensystem3dEintrag`). Bis
2026-11-15 stand er im 2D-Balkensystem allein.

TEILEN UND UMKEHREN:
Die Lasten gehen mit ihrer Linie. Beim Teilen liegt eine verteilte Last
danach auf beiden Haelften, mit dem Wert an der Schnittstelle; eine
Einzellast bleibt, wo sie steht. Beim Umkehren bleiben die Lasten, wo sie
wirken: ihre Stellen gespiegelt, Anfangs- und Endwert getauscht, und eine
Richtung, die an der Linie haengt, mit umgekehrtem Vorzeichen -- welche,
sagt die Beschreibung (:meth:`MitStaeben._kehrt_um`).

QUERSCHNITTE:
Ein Querschnitt der Staebe ist in beiden Systemen nach Vorlage, ein
Stahlprofil aus der Tabelle oder mit Kennwerten von Hand
(:class:`StabquerschnittBasis`); welche Kennwerte, sagt das System. Aus
einer Platte oder Querschnittsanalyse nimmt ihn nur das 2D-Balkensystem.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field, replace
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from opencivil.core.wahl import Wahl
from opencivil.projekt.eintraege import Beschreibung
from opencivil.projekt.faelle import kennung_von
from opencivil.projekt.lesen import ProjektFehler, einer_von
from opencivil.projekt.netz import Netz, naechste_kennung
from opencivil.stabwerk import profiltabelle
from opencivil.stabwerk import querschnitte as qs
from opencivil.stabwerk.modell import Lastart

#: Ein Punkt in m -- oder die Kennung eines Knotens, der dort liegt.
Ort = Union[str, Sequence[float]]

#: Ein Punkt in m, mit so vielen Koordinaten, wie das System Achsen hat.
Punkt = Tuple[float, ...]


class Querschnittsart(Wahl):
    """
    Woher die Kennwerte eines Stabquerschnitts kommen. Aufgeloest wird die
    Art einmal, im Aufbau: je Art eine Klasse
    (:mod:`opencivil.stabwerk.stabquerschnitt`).
    """

    VORLAGE = "vorlage"
    PROFIL = "profil"
    KENNWERTE = "kennwerte"
    PLATTE = "platte"
    ANALYSE = "analyse"

    @property
    def beschriftung(self) -> str:
        return {
            Querschnittsart.VORLAGE: "nach Vorlage",
            Querschnittsart.PROFIL: "ein Stahlprofil aus der Tabelle",
            Querschnittsart.KENNWERTE: "Kennwerte von Hand",
            Querschnittsart.PLATTE: "aus einer Platte",
            Querschnittsart.ANALYSE: "aus einer Querschnittsanalyse",
        }[self]

    @property
    def kurz(self) -> str:
        """
        Fuer den Schalter und die Zeile des Querschnitts -- der lange Name
        steht im Titel des Schalters. «Aus QS Analyse», nicht «Analyse»: im
        Balkensystem heisst auch die Statik-Analyse so (Benutzer, 2026-11-16).
        """
        return {
            Querschnittsart.VORLAGE: "Vorlage",
            Querschnittsart.PROFIL: "Profil",
            Querschnittsart.KENNWERTE: "Kennwerte",
            Querschnittsart.PLATTE: "Platte",
            Querschnittsart.ANALYSE: "Aus QS Analyse",
        }[self]

    @property
    def aus_bauteil(self) -> bool:
        """
        Ob er ein Bauteil des Projekts nimmt, eine Platte oder eine
        Querschnittsanalyse. Nur dann bringt er ein Material mit, den Beton
        des Bauteils, und nur dann hat er ein E_eq -- eine
        Momenten-Kruemmungs-Linie mit ihrer Bewehrung, bei einer Platte immer
        in x-Richtung, Zug unten (Benutzer, 2026-10-24). Einer nach Vorlage
        oder von Hand ist nur eine Form.
        """
        return self in (Querschnittsart.PLATTE, Querschnittsart.ANALYSE)


def _aufgezaehlt(namen: Sequence[str]) -> str:
    """«A und I», «A, I_y, I_z und I_T»."""
    return " und ".join(filter(None, (", ".join(namen[:-1]), namen[-1])))


@dataclass
class StabquerschnittBasis(Beschreibung):
    """
    Ein Querschnitt der Staebe: nach Vorlage mit Massen in mm, ein
    Stahlprofil aus der Tabelle (``profil``) oder mit Kennwerten von Hand in
    ``masse`` -- ``A`` in mm², Traegheitsmomente in 10⁶ mm⁴; welche, sagt
    :attr:`KENNWERTE`. E und G kommen vom Material des Stabs.
    """

    KENNWERTE: ClassVar[Tuple[str, ...]]
    """Die Kennwerte von Hand, wie die Rechnung sie nimmt."""

    kennung: str = ""
    name: str = ""
    art: Querschnittsart = einer_von(tuple(Querschnittsart), Querschnittsart.VORLAGE)
    vorlage: str = einer_von((v.schluessel for v in qs.VORLAGEN), qs.RECHTECK.schluessel)
    masse: Dict[str, float] = field(default_factory=dict)
    profil: str = "IPE 300"
    """
    Der Name des Stahlprofils (:mod:`opencivil.stabwerk.profiltabelle`). Kein
    Wahlfeld, damit die Meldung nicht alle 666 Profile aufzaehlt: einen
    unbekannten Namen meldet der Aufbau, wie eine Platte, die es nicht gibt.
    """

    @classmethod
    def neu(cls) -> "StabquerschnittBasis":
        """Ein frischer Querschnitt, wie die Oberflaeche ihn anlegt: ein Rechteck mit seinen Vorgaben."""
        return cls(masse=qs.RECHTECK.vorgaben())

    def stabvorlage(self) -> qs.Stabvorlage:
        return qs.vorlage(self.vorlage)

    def masse_mit_vorgaben(self) -> Dict[str, float]:
        """Die Masse der Vorlage -- was fehlt, mit ihrer Vorgabe."""
        return {**self.stabvorlage().vorgaben(), **self.masse}

    def fehler(self) -> Optional[str]:
        """
        Was an Massen oder Kennwerten nicht geht -- ``None``, wenn alles geht.
        Ein Mass, das die Vorlage nicht kennt, ist ein Tippfehler: bis
        2026-10-16 stand ``B=500`` still da, und gerechnet wurde mit b = 300.
        """
        if self.art is Querschnittsart.VORLAGE:
            vorlage = self.stabvorlage()
            fremd = [k for k in self.masse if k not in vorlage.vorgaben()]
            if fremd:
                return (f"ein Mass «{fremd[0]}» gibt es bei «{vorlage.name}» nicht. "
                        f"Möglich sind: {', '.join(vorlage.vorgaben())}.")
            return vorlage.pruefen(self.masse_mit_vorgaben())
        if self.art is Querschnittsart.KENNWERTE:
            fremd = [k for k in self.masse if k not in self.KENNWERTE]
            if fremd:
                return (f"einen Kennwert «{fremd[0]}» gibt es nicht. "
                        f"Möglich sind: {', '.join(self.KENNWERTE)}.")
            if not all(self.masse.get(k, 0.0) > 0.0 for k in self.KENNWERTE):
                return f"{_aufgezaehlt(self.KENNWERTE)} müssen grösser als null sein."
        return None


class MitStaeben:
    """
    Der Baukasten eines Stabwerks -- fuer eine Beschreibung mit ``knoten``,
    ``linien``, ``lager``, ``knotenlasten``, ``stabmaterialien``,
    ``querschnitte`` und ``diagramme``. Die Klassen ihrer Teile, die Achsen
    und die Arten der Lager stehen in ihr als Klassenattribute.
    """

    BEZEICHNUNG: str
    ACHSEN: Tuple[str, ...]
    """Wie die Koordinaten eines Knotens heissen -- ``("x", "z")`` in der Ebene."""

    LAGERFELDER: Tuple[str, ...]
    """
    Die Richtungen eines Lagers, in der Folge der Vorwahlen in
    :attr:`LAGERARTEN` -- Felder des Lagers wie des Lagers im Rechenkern.
    """

    LAGERARTEN: Mapping[str, Tuple[str, ...]]
    """Die Vorwahlen eines Lagers -- je Richtung frei oder fest."""

    LINIENLAGER: Tuple[str, ...]
    """Die Richtungen eines Linienlagers -- Felder der Linie wie des Stabs im Rechenkern."""

    EINHEIT_DER_FEDER: Mapping[str, Any]
    """Die Einheit jeder Feder, nach ihrem Feld -- an Lager und Linie."""

    NEUE_DIAGRAMME: Tuple[str, ...]
    """Was ein frisches System von der GZT zeigt -- dazu die Verschiebung der GZG."""

    LAUFRICHTUNGEN: Tuple[Tuple[float, ...], ...]
    """
    Wohin eine neue Linie laeuft, wie herum sie auch gezeichnet ist: in die
    erste dieser Richtungen, auf der sie nicht senkrecht steht. Keine: wie
    gezeichnet. Die Oberflaeche legt danach Anfang und Ende.
    """

    KNOTEN: type
    LINIE: type
    LAGER: type
    STABLAST: type
    KNOTENLAST: type
    MATERIAL: type
    QUERSCHNITT: type
    DIAGRAMM: type

    name: str
    knoten: List[Any]
    linien: List[Any]
    lager: List[Any]
    knotenlasten: List[Any]
    stabmaterialien: List[Any]
    querschnitte: List[Any]
    diagramme: List[Any]

    @classmethod
    def neu(cls, kennung: str, name: str) -> Any:
        """
        Ein frisches System, wie der Benutzer es angelegt bekommt: ohne
        Knoten, Linie, Lager und Querschnitt (Benutzer, 2026-10-19), aber mit
        den Lastfaellen Eigengewicht -- es kommt von selbst --, Auflast und
        Nutzlast, die beiden ohne Last, und den Kombinationen GZT mit 1.35,
        1.35 und 1.5 und GZG mit je 1.0 (Benutzer, 2026-10-23). Dazu die
        Diagramme :attr:`NEUE_DIAGRAMME` der GZT und die Verschiebung der GZG.
        """
        s = cls(kennung=kennung, name=name)
        gzt = s.standardfaelle()
        gzg = s.gebrauchskombination()
        for groesse in cls.NEUE_DIAGRAMME:
            s.diagramm(gzt, groesse)
        s.diagramm(gzg, "verschiebung")
        return s

    # -- Zugriff -------------------------------------------------------------

    @property
    def wo(self) -> str:
        """Wie das System in einer Meldung heisst: «Balkensystem 'Rahmen'»."""
        return f"{self.BEZEICHNUNG} '{self.name}'"

    def materialien(self) -> List[str]:
        """
        Jedes Material des Projekts, auf das ein Material des Systems zeigt --
        auch eines, das gerade keinen Stab traegt: wer es loescht, liesse es
        ins Leere zeigen, und spaetestens die naechste Aenderung machte
        daraus einen Fehler beim Rechnen.
        """
        gesehen: List[str] = []
        for m in self.stabmaterialien:
            if m.art != "eigen" and m.stoff and m.stoff not in gesehen:
                gesehen.append(m.stoff)
        return gesehen

    def alle_lasten(self) -> List[Any]:
        """Jede Last des Systems, auf den Linien und an den Knoten -- ihre Kennungen zaehlen zusammen."""
        return [last for l in self.linien for last in l.lasten] + list(self.knotenlasten)

    def linie_von(self, kennung: str) -> Any:
        for l in self.linien:
            if l.kennung == kennung:
                return l
        raise ProjektFehler(f"{self.wo}: eine Linie «{kennung}» gibt es nicht.")

    def enden(self, linie: Any) -> Tuple[Punkt, Punkt]:
        """Anfang und Ende einer Linie, in m."""
        netz = self.netz()
        a, b = netz.lage(linie.von), netz.lage(linie.bis)
        if a is None or b is None:
            raise ProjektFehler(f"{self.wo}: {linie.kennung} verweist auf "
                                f"einen Knoten, den es nicht gibt.")
        return a, b

    def laenge(self, linie: Any) -> float:
        return math.dist(*self.enden(linie))

    def stelle_auf(self, kennung: str, punkt: Sequence[float]) -> float:
        """Wo ein Punkt auf einer Linie liegt, in m ab ihrem Anfang -- auf die Linie gelotet."""
        a, b = self.enden(self.linie_von(kennung))
        L = math.dist(a, b)
        return sum((p - pa) * (pb - pa) for p, pa, pb in zip(punkt, a, b)) / L if L else 0.0

    # -- Zeichnen ohne Oberflaeche --------------------------------------------

    def netz(self) -> Netz:
        return Netz(self.knoten, neu=self.KNOTEN, achsen=self.ACHSEN)

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        return ort if isinstance(ort, str) else netz.an(*ort)

    def _neue_kennung(self, liste: Sequence[Any], vorsilbe: str) -> str:
        return naechste_kennung((e.kennung for e in liste), vorsilbe)

    def linie(self, von: Ort, bis: Ort, *, querschnitt: Any = None, material: Any = None,
              **felder: Any) -> Any:
        """
        Eine Linie von ``von`` nach ``bis`` -- ein Stab, sobald ``querschnitt``
        und ``material`` dastehen: ein Material des Systems (:meth:`beton`,
        :meth:`baustahl`, :meth:`eigenes_material`). Weitere Felder wie die
        Klasse der Linien.
        """
        netz = self.netz()
        eintrag = self.LINIE.aus_dict({
            "kennung": self._neue_kennung(self.linien, "L"),
            "von": self._knoten(netz, von), "bis": self._knoten(netz, bis),
            "querschnitt": kennung_von(querschnitt) if querschnitt is not None else "",
            "material": kennung_von(material) if material is not None else "", **felder},
            f"{self.wo}, linien")
        self.linien.append(eintrag)
        return eintrag

    def lager_an(self, ort: Ort, art: str = "gelenkig", **felder: Any) -> Any:
        """Ein Lager -- eine der :attr:`LAGERARTEN`, einzelne Felder darueber."""
        if art not in self.LAGERARTEN:
            raise ProjektFehler(f"Eine Lagerart «{art}» gibt es nicht. Möglich sind: "
                                f"{', '.join(self.LAGERARTEN)}.")
        eintrag = self.LAGER.aus_dict({
            "kennung": self._neue_kennung(self.lager, "A"),
            "knoten": self._knoten(self.netz(), ort),
            **dict(zip(self.LAGERFELDER, self.LAGERARTEN[art])), **felder},
            f"{self.wo}, lager")
        self.lager.append(eintrag)
        return eintrag

    def beton(self, beton: Any) -> Any:
        """
        Das Material des Systems aus einem Beton des Projekts (Eintrag oder
        Kennung) -- das schon da ist, sonst ein neues.
        """
        return self._aus_projekt("beton", beton)

    def baustahl(self, stahl: Any) -> Any:
        """Das Material des Systems aus einem Baustahl des Projekts -- siehe :meth:`beton`."""
        return self._aus_projekt("baustahl", stahl)

    def _aus_projekt(self, art: str, stoff: Any) -> Any:
        kennung = kennung_von(stoff)
        for m in self.stabmaterialien:
            if m.art == art and m.stoff == kennung:
                return m
        eintrag = self.MATERIAL(kennung=self._neue_kennung(self.stabmaterialien, "M"),
                                art=art, stoff=kennung)
        self.stabmaterialien.append(eintrag)
        return eintrag

    def eigenes_material(self, name: str, **werte: float) -> Any:
        """Ein eigenes Material des Systems -- E in N/mm², die Dichte in kg/m³, Felder wie seine Klasse."""
        eintrag = self.MATERIAL.aus_dict({
            "kennung": self._neue_kennung(self.stabmaterialien, "M"), "art": "eigen",
            "name": name, **werte}, f"{self.wo}, stabmaterialien")
        self.stabmaterialien.append(eintrag)
        return eintrag

    def querschnitt(self, name: str, vorlage: str = qs.RECHTECK.schluessel,
                    **masse: float) -> Any:
        """Ein Querschnitt nach Vorlage -- Masse in mm, was fehlt nach ihrer Vorgabe."""
        try:
            qs.vorlage(vorlage)
        except KeyError as fehler:
            raise ProjektFehler(fehler.args[0]) from None
        eintrag = self.QUERSCHNITT(kennung=self._neue_kennung(self.querschnitte, "Q"),
                                   name=name, vorlage=vorlage, masse=dict(masse))
        self.querschnitte.append(eintrag)
        return eintrag

    def stahlprofil(self, name: str, profil: str, **felder: Any) -> Any:
        """Ein Stahlprofil aus der Tabelle, «HEB 300» -- Felder wie die Klasse der Querschnitte."""
        try:
            profiltabelle.profil(profil)
        except KeyError as fehler:
            raise ProjektFehler(fehler.args[0]) from None
        eintrag = self.QUERSCHNITT.aus_dict({
            "kennung": self._neue_kennung(self.querschnitte, "Q"), "name": name,
            "art": "profil", "profil": profil, **felder}, f"{self.wo}, querschnitte")
        self.querschnitte.append(eintrag)
        return eintrag

    def querschnitt_mit_kennwerten(self, name: str, **kennwerte: float) -> Any:
        """Ein Querschnitt mit Kennwerten von Hand -- A in mm², Traegheitsmomente in 10⁶ mm⁴."""
        eintrag = self.QUERSCHNITT(kennung=self._neue_kennung(self.querschnitte, "Q"),
                                   name=name, art="kennwerte", masse=dict(kennwerte))
        self.querschnitte.append(eintrag)
        return eintrag

    def diagramm(self, fall: Any, groesse: str) -> Any:
        """Ein Diagramm der Statik-Analyse -- ``fall`` ein Lastfall oder eine Kombination."""
        eintrag = self.DIAGRAMM.aus_dict({"fall": kennung_von(fall), "groesse": groesse},
                                         f"{self.wo}, diagramme")
        self.diagramme.append(eintrag)
        return eintrag

    def stablast(self, lastfall: Any, linie: Any, art: Lastart = Lastart.LINIENLAST,
                 wert: float = 10.0, **felder: Any) -> Any:
        """Eine Last auf einer Linie -- ``wert`` ist ``wert_a``; Felder wie die Klasse der Stablasten."""
        eintrag = self.STABLAST.aus_dict({"kennung": self._neue_kennung(self.alle_lasten(), "P"),
                                          "lastfall": kennung_von(lastfall), "art": art,
                                          "wert_a": wert, **felder},
                                         f"{self.wo}, lasten")
        self.linie_von(kennung_von(linie)).lasten.append(eintrag)
        return eintrag

    def knotenlast(self, lastfall: Any, ort: Ort, wert: float = 10.0, *, art: str = "kraft",
                   **felder: Any) -> Any:
        """Eine Last an einem Knoten -- eine Kraft oder ein Moment; Felder wie ihre Klasse."""
        eintrag = self.KNOTENLAST.aus_dict({
            "kennung": self._neue_kennung(self.alle_lasten(), "P"),
            "knoten": self._knoten(self.netz(), ort), "lastfall": kennung_von(lastfall),
            "art": art, "wert": wert, **felder},
            f"{self.wo}, knotenlasten")
        self.knotenlasten.append(eintrag)
        return eintrag

    # -- Teilen und Umkehren ----------------------------------------------------

    def teilen(self, kennung: str, stelle: float) -> Any:
        """
        Teilt eine Linie bei ``stelle`` m ab ihrem Anfang: sie endet dort, und
        eine neue laeuft weiter zum alten Ende -- mit ihren Eigenschaften. Die
        Lasten gehen mit: eine verteilte liegt danach auf beiden Haelften, mit
        dem Wert an der Schnittstelle, die auf der zweiten mit einer eigenen
        Kennung; eine Einzellast bleibt dort, wo sie steht, ihre Stelle in %
        der neuen Haelfte. Das Gelenk am Ende wandert mit ans neue Ende; an der
        Schnittstelle ist die Linie durchlaufend.
        """
        linie = self.linie_von(kennung)
        a, b = self.enden(linie)
        L = math.dist(a, b)
        if not 0.0 < stelle < L:
            raise ProjektFehler(f"{linie.kennung} ist {L:.3f} m lang -- geteilt werden kann nur "
                                f"dazwischen, nicht bei {stelle:g} m.")
        schnitt = self._knoten(self.netz(), tuple(pa + (pb - pa) * stelle / L
                                                  for pa, pb in zip(a, b)))
        zweite = copy.deepcopy(linie)
        zweite.kennung = self._neue_kennung(self.linien, "L")
        zweite.von, zweite.gelenk_anfang = schnitt, False
        linie.bis, linie.gelenk_ende = schnitt, False
        anteil = stelle / L
        vergeben = {last.kennung for last in self.alle_lasten()}
        erste_lasten, zweite_lasten = [], []
        for last in linie.lasten:
            if not last.verteilt:
                if last.stelle <= 100.0 * anteil:
                    erste_lasten.append(replace(last, stelle=last.stelle / anteil))
                else:
                    zweite_lasten.append(replace(
                        last, stelle=(last.stelle - 100.0 * anteil) / (1.0 - anteil)))
                continue
            mitte = None if last.wert_b is None else \
                last.wert_a + (last.wert_b - last.wert_a) * anteil
            neue = naechste_kennung(vergeben, "P")
            vergeben.add(neue)
            erste_lasten.append(replace(last, wert_b=mitte))
            zweite_lasten.append(replace(last, kennung=neue,
                                         wert_a=last.wert_a if mitte is None else mitte))
        linie.lasten, zweite.lasten = erste_lasten, zweite_lasten
        self.linien.insert(self.linien.index(linie) + 1, zweite)
        return zweite

    def umkehren(self, kennung: str) -> None:
        """
        Tauscht Anfang und Ende einer Linie, mit ihren Gelenken. Die Lasten
        bleiben, wo sie wirken: ihre Stellen gespiegelt, Anfangs- und Endwert
        getauscht, und mit umgekehrtem Vorzeichen, wo ihre Richtung an der
        Linie haengt (:meth:`_kehrt_um`).
        """
        linie = self.linie_von(kennung)
        linie.von, linie.bis = linie.bis, linie.von
        linie.gelenk_anfang, linie.gelenk_ende = linie.gelenk_ende, linie.gelenk_anfang
        neu = []
        for last in linie.lasten:
            vorzeichen = -1.0 if self._kehrt_um(last) else 1.0
            if not last.verteilt:
                neu.append(replace(last, stelle=100.0 - last.stelle,
                                   wert_a=vorzeichen * last.wert_a))
                continue
            wb = last.wert_a if last.wert_b is None else last.wert_b
            neu.append(replace(
                last, wert_a=vorzeichen * wb,
                wert_b=None if last.wert_b is None else vorzeichen * last.wert_a))
        linie.lasten = neu

    def _kehrt_um(self, last: Any) -> bool:
        """Ob eine Last ihr Vorzeichen wechselt, wenn ihre Linie umgekehrt wird."""
        raise NotImplementedError
