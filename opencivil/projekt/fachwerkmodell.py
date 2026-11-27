"""
opencivil/projekt/fachwerkmodell.py -- ein Fachwerkmodell, wie die Oberfläche es beschreibt.

VERANTWORTUNG:
Der :class:`FachwerkmodellEintrag`: eine Scheibe aus Umrissen und Löchern,
Lager und Punktlasten, gezeichnet aus Knoten in der Ebene -- als
speicherbare Datenklasse wie die Decke (:mod:`opencivil.projekt.decke`).
Dazu der Baukasten, der ohne Oberfläche zeichnet. Gerechnet wird in
:mod:`opencivil.fachwerkmodell`.

ALLES HÄNGT AN KNOTEN:
Eine Scheibe und ein Loch sind Umrisse aus Knoten, ein Lager und eine
Last stehen an einem. Wo ein Lager an einer Ecke steht, teilt es ihren
Knoten: wer ihn verschiebt, verschiebt beide.

KEIN MATERIAL, KEINE LASTFÄLLE:
Ohne Bemessung hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten
ab. Ein Satz Lasten je Modell; für einen zweiten Lastfall kopiert man es
(Plan vom 2026-11-27, Entscheid 11).

KOORDINATEN UND EINHEITEN:
x nach rechts, y nach oben, in m. Eine Last in kN, ``F_h`` nach rechts,
``F_v`` nach unten positiv -- wie im Balkensystem. Umgerechnet wird beim
Bauen.

DAS GEFUNDENE FACHWERK:
Was die Suche zuletzt fand, steht im Eintrag (:class:`GefundenesFachwerk`):
die Seite fragt sie Runde um Runde an und legt hier ab, was die letzte
gab -- fertig oder angehalten. Geschrieben vom Kern, nicht von Hand; die
Rechnung glaubt ihm nur, was sie nicht nachrechnen kann, und erkennt am
Abdruck, ob es noch zu Modell und Verfahren gehört
(:mod:`opencivil.fachwerkmodell.suche`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence, Union

from opencivil.core.einheiten import KN, M, PROZENT
from opencivil.fachwerkmodell.modell import Halt
from opencivil.fachwerkmodell.suche import Fachwerk, Suchergebnis
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.lesen import ProjektFehler, bereich, lesen, teil
from opencivil.projekt.netz import Netz, neue_kennung

#: Ein Ort im Baukasten: die Kennung eines Knotens oder ``(x, y)`` in m.
Ort = Union[str, Sequence[float]]

#: Womit die Kennungen der Teile eines Fachwerkmodells beginnen -- «A» wie Auflager.
VORSILBEN = {"scheiben": "S", "loecher": "L", "lager": "A", "lasten": "F"}


@dataclass
class ScheibenknotenEintrag(Beschreibung):
    """Ein Punkt der Scheibe, in m."""

    kennung: str = ""
    x: float = bereich(0.0, heisst="x", einheit=M)
    y: float = bereich(0.0, heisst="y", einheit=M)


@dataclass
class ScheibeEintrag(Beschreibung):
    """Ein Umriss der Scheibe -- liegen mehrere da, ist Material, wo eine von ihnen ist."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)


@dataclass
class LochEintrag(Beschreibung):
    """Ein Loch: in seinem Innern ist kein Material, auf seinem Rand schon."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)


@dataclass
class ScheibenlagerEintrag(Beschreibung):
    """Ein Lager an einem Knoten, fest in x, in y oder in beiden."""

    kennung: str = ""
    knoten: str = ""
    halt: Halt = Halt.XY


@dataclass
class ScheibenlastEintrag(Beschreibung):
    """Eine Punktlast an einem Knoten, in jeder Richtung."""

    kennung: str = ""
    knoten: str = ""
    F_h: float = bereich(0.0, heisst="F_h", einheit=KN)
    """Waagrecht, nach rechts positiv."""

    F_v: float = bereich(100.0, heisst="F_v", einheit=KN)
    """Senkrecht, nach unten positiv."""


@dataclass
class FachwerkpunktEintrag(Beschreibung):
    """Ein Knoten des gefundenen Fachwerks, in m."""

    IM_ORT = "Knoten des Fachwerks"

    x: float = bereich(0.0, heisst="x", einheit=M)
    y: float = bereich(0.0, heisst="y", einheit=M)


@dataclass
class FachwerkstabEintrag(Beschreibung):
    """Ein Stab des gefundenen Fachwerks: von Knoten zu Knoten, gezählt ab null, mit seiner Kraft."""

    IM_ORT = "Stab des Fachwerks"

    von: int = bereich(0, heisst="von", ab=0)
    bis: int = bereich(0, heisst="bis", ab=0)
    N: float = bereich(0.0, heisst="N", einheit=KN)
    """Zug positiv."""


@dataclass
class GefundenesFachwerk(Beschreibung):
    """Was die Suche zuletzt fand -- siehe Dateikopf."""

    abdruck: str = ""
    """Woran es Modell und Verfahren erkennt, zu denen es gehört."""

    runden: int = bereich(0, heisst="Runden", ab=0)
    fertig: bool = False
    """Ob die Suche zu Ende kam -- sonst wurde sie angehalten."""

    moeglich: int = bereich(0, heisst="Mögliche Stäbe", ab=0)
    """Wie viele Stäbe die Grundstruktur hatte."""

    im_modell: int = bereich(0, heisst="Stäbe im Modell", ab=0)
    """Wie viele davon in der letzten Runde im Modell waren."""

    knoten: List[FachwerkpunktEintrag] = field(default_factory=list)
    staebe: List[FachwerkstabEintrag] = field(default_factory=list)

    @classmethod
    def aus(cls, ergebnis: Suchergebnis) -> "GefundenesFachwerk":
        """Das Ergebnis einer Runde, wie es im Projekt steht: Kräfte in kN."""
        fw = ergebnis.fachwerk
        return cls(abdruck=ergebnis.abdruck, runden=ergebnis.runden, fertig=ergebnis.fertig,
                   moeglich=ergebnis.moeglich, im_modell=ergebnis.im_modell,
                   knoten=[FachwerkpunktEintrag(x, y) for x, y in fw.knoten],
                   staebe=[FachwerkstabEintrag(a, b, N / 1e3) for a, b, N in fw.staebe])

    def ergebnis(self) -> Optional[Suchergebnis]:
        """
        Zurück in SI -- ``None``, wenn ein Stab auf einen Knoten zeigt, den es
        nicht gibt: dann ist es keines, das die Suche schrieb.
        """
        n = len(self.knoten)
        if any(not (0 <= s.von < n and 0 <= s.bis < n) or s.von == s.bis for s in self.staebe):
            return None
        fw = Fachwerk(knoten=tuple((k.x, k.y) for k in self.knoten),
                      staebe=tuple((s.von, s.bis, s.N * 1e3) for s in self.staebe))
        return Suchergebnis(fachwerk=fw, abdruck=self.abdruck, runden=self.runden,
                            fertig=self.fertig, moeglich=self.moeglich, im_modell=self.im_modell)


@dataclass
class FachwerkmodellEintrag(BauteilEintrag):
    """
    Ein Fachwerkmodell: eine Scheibe aus Umrissen und Löchern an Lagern,
    mit Punktlasten. Ohne Regeln, die das ganze Projekt aufhielten: was
    ihm fehlt, steht in seinen Meldungen, und die anderen Bauteile rechnen
    weiter.
    """

    BEZEICHNUNG = "Fachwerkmodell"
    STAMM = "Fachwerkmodell"

    kennung: str
    name: str
    knoten: List[ScheibenknotenEintrag] = field(default_factory=list)
    scheiben: List[ScheibeEintrag] = field(default_factory=list)
    loecher: List[LochEintrag] = field(default_factory=list)
    lager: List[ScheibenlagerEintrag] = field(default_factory=list)
    lasten: List[ScheibenlastEintrag] = field(default_factory=list)
    rasterweite: float = bereich(0.5, heisst="Rasterweite", einheit=M, ueber=0.0)
    """Wie weit die Knoten der Grundstruktur auseinander liegen."""

    w_Z: float = bereich(1.0, heisst="w_Z", ab=0.1, bis=10.0)
    """Wie schwer Zug gegenüber Druck zählt -- 1: gleich (Plan vom 2026-11-27, Entscheid 11)."""

    N_min: float = bereich(1.0, heisst="N_min", einheit=PROZENT, ab=0.0, bis=50.0)
    """Die kleinste Stabkraft, die stehen bleibt, bezogen auf die grösste."""

    fachwerk: Optional[GefundenesFachwerk] = teil(lambda: None, heisst="Gefundenes Fachwerk")
    """Was die Suche zuletzt fand -- siehe Dateikopf."""

    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    def lagen(self) -> dict:
        """Kennung -> ``(x, y)`` jedes Knotens, in m."""
        return {k.kennung: (k.x, k.y) for k in self.knoten}

    # -- Zeichnen ohne Oberfläche -------------------------------------------

    def netz(self) -> Netz:
        return Netz(self, neu=lambda kennung, x, y: ScheibenknotenEintrag(kennung, x, y),
                    achsen=("x", "y"))

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        return ort if isinstance(ort, str) else netz.an(float(ort[0]), float(ort[1]))

    def _anlegen(self, liste: str, cls: type, felder: dict, wo: str) -> Any:
        eintrag = lesen(cls, felder, f"Fachwerkmodell '{self.name}': {wo}",
                        cls(kennung=neue_kennung(self, VORSILBEN[liste],
                                                 (e.kennung for e in getattr(self, liste)))))
        getattr(self, liste).append(eintrag)
        return eintrag

    def scheibe(self, ecken: Sequence[Ort]) -> ScheibeEintrag:
        """Ein Umriss der Scheibe mit diesen Ecken."""
        netz = self.netz()
        return self._anlegen("scheiben", ScheibeEintrag,
                             {"knoten": [self._knoten(netz, e) for e in ecken]}, "Scheibe")

    def loch(self, ecken: Sequence[Ort]) -> LochEintrag:
        netz = self.netz()
        return self._anlegen("loecher", LochEintrag,
                             {"knoten": [self._knoten(netz, e) for e in ecken]}, "Loch")

    def lager_setzen(self, ort: Ort, halt: str = "xy") -> ScheibenlagerEintrag:
        """Ein Lager bei ``ort`` -- heisst nicht ``lager``, weil die Liste so heisst."""
        return self._anlegen("lager", ScheibenlagerEintrag,
                             {"knoten": self._knoten(self.netz(), ort), "halt": halt}, "Lager")

    def last(self, ort: Ort, **felder: Any) -> ScheibenlastEintrag:
        """Eine Punktlast bei ``ort`` -- ``F_h`` nach rechts, ``F_v`` nach unten, in kN."""
        return self._anlegen("lasten", ScheibenlastEintrag,
                             {"knoten": self._knoten(self.netz(), ort), **felder}, "Last")

    def suchen(self) -> GefundenesFachwerk:
        """
        Sucht das Fachwerk bis zum Ende, wie «Fachwerk suchen» auf der Seite,
        und legt es ab. Fehlt dem Modell etwas, sagt ein :class:`ProjektFehler`,
        was; ein zu feines Raster meldet
        :class:`~opencivil.fachwerkmodell.grundstruktur.ZuVieleKnoten`.
        """
        # Erst hier: der Aufbau liest diesen Eintrag.
        from opencivil.fachwerkmodell.pruefen import pruefen
        from opencivil.fachwerkmodell.suche import ganz_suchen
        from opencivil.projekt.aufbau.fachwerkmodell import einstellung_von, modell_von
        modell, meldungen = modell_von(self)
        halt = [m.text for m in meldungen + pruefen(modell) if m.haelt_an]
        if halt:
            raise ProjektFehler(f"Fachwerkmodell '{self.name}': {' '.join(halt)}")
        self.fachwerk = GefundenesFachwerk.aus(ganz_suchen(modell, einstellung_von(self)))
        return self.fachwerk
