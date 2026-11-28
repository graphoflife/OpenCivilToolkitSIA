"""
opencivil/mauerwerk/werk.py -- eine Mauerwerkswand im Rechenwerk.

VERANTWORTUNG:
Was eine Wand im Rechenwerk anmeldet: ihre Vorgaben (:data:`VORGABEN`) --
in der Maske die Kacheln «Mauerwerk» und «Ränder», in der Herleitung ein
Kasten -- und eine Prozedur, die ihre Zeichnung prüft
(:mod:`~opencivil.mauerwerk.pruefen`), die Werte ihres Mauerwerks liest, an
den Mindestwerten misst und nach ihrer Wahl umrechnet
(:mod:`~opencivil.mauerwerk.kennwerte`), die Pfeiler bestimmt
(:func:`~opencivil.mauerwerk.modell.pfeiler`), ihre Lasten je Lastfall und
Kombination auf Pfeiler und Stürze verteilt -- die lotrechten nach
:mod:`~opencivil.mauerwerk.lasten`, die waagrechten nach
:mod:`~opencivil.mauerwerk.scheibe`, die Querlasten je m² Wand, die des
Erdbebens nach :mod:`~opencivil.mauerwerk.querlast` -- und die Herleitung
schreibt (:mod:`~opencivil.mauerwerk.herleitung`).

DAS ERGEBNIS:
kommt als Befund in die Lösung (:class:`Wandbefund`); Zeichnung,
Zusammenfassung und Nachweise (:mod:`~opencivil.mauerwerk.nachweise`) lesen
es dort. Eine Wand, der etwas fehlt, ist ein Befund mit Meldung und keine
Ausnahme: der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Prozedur, Vorgabe
from opencivil.core.einheiten import M_PRO_S2, MM, Groesse
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.vorgaben import Feld, Gruppe
from opencivil.core.wert import WertDef
from opencivil.material.basis import ERDBESCHLEUNIGUNG, Baustoff
from opencivil.mauerwerk import herleitung, querlast, scheibe
from opencivil.mauerwerk.kennwerte import GELESEN, Wandwerte, unter_mindestwerten, wandwerte
from opencivil.mauerwerk.lasten import Abtrag, abtragen, kombinieren
from opencivil.mauerwerk.modell import Halterung, Pfeiler, Wand, pfeiler
from opencivil.mauerwerk.pruefen import dickenhinweis, lasten_pruefen, pruefen
from opencivil.stabwerk.system import Meldung

#: Unter welchem Thema ihre Herleitung in der Formelsammlung steht.
THEMA = "Mauerwerk"

#: Was die Wand aus ihrer Beschreibung liest (:mod:`opencivil.core.vorgaben`) --
#: die Ausmitte am Fuss nur, wo er sich drehen kann.
VORGABEN = (
    Gruppe("Mauerwerk", lambda: (
        Feld("t", "t_w", MM, "Dicke der Wand", stellen=0, schritt=5,
             hinweis="Meist so dick, wie die Steine der Sorte sind – eine andere Dicke geht "
                     "auch."),)),
    Gruppe("Ränder", lambda fuss: (
        Feld("e_u", "e_u", MM, "Ausmitte der Normalkraft am Fuss", stellen=0, schritt=5,
             beschriftung="Ausmitte am Fuss",
             hinweis="Quer zur Wand, positiv zur Seite, von der aus man die Ansicht sieht – "
                     "etwa wenn die Wand nicht mittig auf der Decke darunter steht."),)
           if fuss is Halterung.GELENKIG else (), nach=("fuss",)),
)


@dataclass
class Wandbefund:
    """Was die Rechnung fand: die Wand, ihr Mauerwerk, ihre Meldungen, Werte und Pfeiler."""

    wand: Wand
    mauerwerk: str
    """Der Name ihres Mauerwerks."""

    material: Dict[str, float]
    """Je Kurzname, was die Wand von ihrem Mauerwerk liest (:data:`.kennwerte.GELESEN`)."""

    werte: Wandwerte
    t: float
    """Ihre Dicke, in m."""

    meldungen: List[Meldung]
    """Was an der Zeichnung falsch ist oder fehlt -- die der Beschreibung zuerst."""

    zum_mauerwerk: List[Meldung] = field(default_factory=list)
    """
    Was zu Mauerwerk und Dicke zu sagen ist: Werte unter den Mindestwerten
    deklarierten Mauerwerks, eine unübliche Dicke -- in der Maske bei ihren
    Feldern.
    """

    zum_erdbeben: List[Meldung] = field(default_factory=list)
    """
    Was zum Erdbeben am Mauerwerk zu sagen ist (:func:`.querlast.erdbebenhinweise`)
    -- in der Maske bei den Querlasten, wo man es einstellt.
    """

    gezeichnet: bool = False
    """Ob ihre Zeichnung rechnet: keine Meldung zu Umriss, Öffnungen oder Stürzen hält sie auf."""

    pfeiler: List[Pfeiler] = field(default_factory=list)
    """Leer, solange sie nicht :attr:`gezeichnet` ist."""

    g_k: float = 0.0
    """Ihr Eigengewicht je m² Ansicht, in N/m²."""

    e_u: Optional[float] = None
    """Die Ausmitte am Fuss in m -- ``None``, wo er eingespannt ist."""

    querlasten: Dict[str, float] = field(default_factory=dict)
    """Je Querlast, nach ihrem Namen, ihre Zahl in N/m² -- die des Erdbebens nach Gl. (49)."""

    faelle: Dict[str, Abtrag] = field(default_factory=dict)
    """Je Lastfall, nach seinem Namen, was er Pfeilern und Stürzen gibt; leer, wo nichts rechnet."""

    kombinationen: Dict[str, Abtrag] = field(default_factory=dict)
    """Dasselbe je Kombination: die Summe der Lastfälle mit ihren Beiwerten."""

    @property
    def alle_meldungen(self) -> List[Meldung]:
        """Was zur Zeichnung zu sagen ist, dann was zu Mauerwerk und Dicke, dann zum Erdbeben."""
        return self.meldungen + self.zum_mauerwerk + self.zum_erdbeben

    @property
    def bereit(self) -> bool:
        """Ob die Wand rechnet: keine Meldung hält sie auf."""
        return not any(m.haelt_an for m in self.alle_meldungen)


class WandProzedur(Prozedur):
    """Die ganze Wand, geprüft, umgerechnet und aufgeschrieben."""

    def __init__(self, wand: "Mauerwerkswand", **kwargs) -> None:
        super().__init__(**kwargs)
        self.wand = wand

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        return self.wand.rechnen_und_schreiben(e, p)


class Mauerwerkswand(Rechenobjekt):
    """Eine Wand aus Mauerwerk, fertig für das Rechenwerk."""

    WAS = "Mauerwerk"

    def __init__(self, *, name: str, kennung: str, praefix: str, wand: Wand, mauerwerk: Baustoff,
                 vorgaben: Mapping[str, Groesse], meldungen: Sequence[Meldung] = ()) -> None:
        """
        ``vorgaben`` je Feld der :data:`VORGABEN` seine Zahl, wie sie
        eingegeben ist; ``meldungen`` sind die der Beschreibung: ein Verweis
        ins Leere, eine doppelte Kennung.
        """
        self.name = name
        self.kennung = kennung
        self.id = praefix
        self.wand = wand
        self.fuss = wand.fuss
        """Wie ihr Fuss gehalten ist: danach richtet sich die Gruppe «Ränder» der Vorgaben."""
        self.mauerwerk = mauerwerk
        self.meldungen = list(meldungen)
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen = []
        for gruppe in VORGABEN:
            for f in gruppe.fuer(self):
                d, vorgabe = f.vorgabe(self.id, self.abschnitt(), gruppe.titel, vorgaben[f.kurz])
                self.definitionen[f.kurz] = d
                self.berechnungen.append(vorgabe)
        g = self.definitionen["g"] = WertDef(id=f"{self.id}.g", symbol="g", einheit=M_PRO_S2,
                                             beschreibung="Erdbeschleunigung", stellen=0)
        self.berechnungen.append(Vorgabe(
            id=g.id, ausgabe=g, groesse=ERDBESCHLEUNIGUNG, abschnitt=self.abschnitt(),
            titel="Erdbeschleunigung für das Eigengewicht (nach Vorgabe des Benutzers)"))
        self.rechnung = WandProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[],
            bezuege=[*(Eingabebezug(k, mauerwerk.id_von(k)) for k in (*GELESEN, "rho")),
                     *(Eingabebezug(k, d.id) for k, d in self.definitionen.items())],
            titel="Mauerwerkswand", abschnitt=self.abschnitt())
        """Die Prozedur, die die Wand rechnet -- ihr Befund ist der :class:`Wandbefund`."""
        self.berechnungen.append(self.rechnung)

    @property
    def baustoffe(self) -> Sequence[Baustoff]:
        return (self.mauerwerk,)

    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Mauerwerk: {self.name}", self.id, thema=THEMA)

    def ziele(self) -> List[str]:
        """Was ein Lauf rechnen muss: die Wand."""
        return [self.rechnung.id]

    def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """
        Die Wand geprüft, ihre Werte umgerechnet, Pfeiler bestimmt, ihre
        Lasten verteilt, Herleitung geschrieben.
        """
        material = {k: e.g(k).zahl for k in GELESEN}
        t_mm = e.g("t").in_einheit(MM)
        w = self.wand
        meldungen = self.meldungen + pruefen(w)
        flaeche = w.flaeche
        # Die Pfeiler hängen nur an der Zeichnung: taugt das Mauerwerk nicht, stehen sie trotzdem.
        gezeichnet = flaeche is not None and not any(m.haelt_an for m in meldungen)
        if gezeichnet:
            meldungen += lasten_pruefen(w)
        zum_mauerwerk = unter_mindestwerten(material, self.mauerwerk.name)
        hinweis = dickenhinweis(self.mauerwerk.sorte, t_mm)
        if hinweis is not None:
            zum_mauerwerk.append(hinweis)
        befund = Wandbefund(w, self.mauerwerk.name, material,
                            wandwerte(material, w.verband, w.vollfugig), t_mm / 1e3, meldungen,
                            zum_mauerwerk, querlast.erdbebenhinweise(w), gezeichnet,
                            pfeiler(flaeche, w.oeffnungen) if gezeichnet else [],
                            g_k=e.g("rho").si * e.g("g").si * t_mm / 1e3,
                            e_u=e.g("e_u").si if "e_u" in self.definitionen else None)
        befund.querlasten = {q.name: querlast.p_E(befund.g_k, e.g("g").si, q) if q.erdbeben
                             else q.p for lf in w.lastfaelle for q in lf.querlasten}
        if gezeichnet and not any(m.haelt_an for m in meldungen):
            self._abtragen(befund)
        herleitung.schreiben(p, befund, e, self.rechnung.id)
        return Ausfuehrung({}, befund=befund)

    def _abtragen(self, befund: Wandbefund) -> None:
        """Je Lastfall und Kombination, was Pfeiler und Stürze tragen -- in den Befund."""
        w = self.wand
        for lf in w.lastfaelle:
            a = befund.faelle[lf.name] = abtragen(w.flaeche, w.oeffnungen, befund.pfeiler,
                                                  lf.lasten, befund.g_k if lf.eigengewicht else 0.0)
            scheibe.abtragen(a, w.flaeche, w.oeffnungen, befund.pfeiler, lf.lasten,
                             befund.werte.E_xd * 1e6, befund.werte.G_d * 1e6, befund.t)
            a.p = sum(befund.querlasten[q.name] for q in lf.querlasten if q.erdbeben is None)
            a.p_E = sum(befund.querlasten[q.name] for q in lf.querlasten if q.erdbeben)
        for k in w.kombinationen:
            befund.kombinationen[k.name] = kombinieren(k.faktoren, befund.faelle, befund.pfeiler,
                                                       w.oeffnungen)
