"""
opencivil/projekt/aufbau/aus_system.py -- die Lastfaelle einer Querschnittsanalyse aus einem Balkensystem.

VERANTWORTUNG:
Was eine Analyse aus ihrem Balkensystem nimmt
(:class:`~opencivil.projekt.aus_system.AusSystemEintrag`), wird hier zu
Lastfaellen (:func:`aus_dem_system`): das System gerechnet, je Kombination
die massgebenden Stellen ihrer Staebe
(:func:`~opencivil.stabwerk.stellen.massgebende_stellen`), jede als
Lastfall der Analyse, dazu die Herleitung. Das geht erst, wenn alle
Balkensysteme gebaut sind -- darum baut die Analyse ihre Nachweise im
zweiten Gang des Aufbaus (:attr:`~opencivil.projekt.aufbau.Bauteilart.danach`).

KEIN KREIS:
Das System liest die Werte der Analyse -- Flaeche und Traegheitsmomente,
auch wenn seine Staebe genau diese Analyse als Querschnitt haben --, die
Nachweise der Analyse lesen die Stellen des Systems. Die Werte haengen an
der Zeichnung, nicht an den Lastfaellen: erst rechnet das System mit den
Werten, dann laufen die Nachweise.

OHNE STELLEN:
Gibt es das System nicht mehr, rechnet es nicht, hat es keine Kombination
oder keinen der Staebe, sagt es ein grauer Satz an der Analyse
(:attr:`AusDemSystem.ohne`) -- sie rechnet mit ihren eigenen Lastfaellen
weiter. Ein unfertiger Zustand ist kein Fehler (Benutzer, 2026-11-19).
Ebenso ein gewaehlter Stab, der im System keiner mehr ist
(:attr:`AusDemSystem.fehlen`): wer auf eine geloeschte Kennung zeigt, sagt
es am Ort (Benutzer, 2026-11-19).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from opencivil.core.sprache import aufgezaehlt
from opencivil.core.wert import kennung_aus
from opencivil.projekt.aus_system import Stabwahl
from opencivil.projekt.querschnittsanalyse import QALastfallEintrag, QuerschnittsanalyseEintrag
from opencivil.projekt.staebe import Querschnittsart
from opencivil.stabwerk.stellen import Stelle, Stellenherleitung, massgebende_stellen

from opencivil.projekt.aufbau.kern import Aufbau


@dataclass
class AusDemSystem:
    """Was eine Analyse aus ihrem Balkensystem nahm -- oder warum nichts."""

    system: str
    """Sein Name -- wie ihn die Liste der Balkensysteme zeigt; leer, wenn es das System nicht mehr gibt."""

    wahl: Stabwahl
    staebe: List[str] = field(default_factory=list)
    """Die Kennungen der Linien, die zaehlen, in der Folge des Systems."""

    fehlen: List[str] = field(default_factory=list)
    """Gewaehlte Linien, die im System kein Stab mehr sind -- geloescht oder ohne Querschnitt."""

    kandidaten: List[Tuple[str, str]] = field(default_factory=list)
    """Was sich im System waehlen laesst: je Stab seine Kennung und der Name seines Querschnitts."""

    stellen: List[Tuple[str, Stelle]] = field(default_factory=list)
    """Je Stelle ihr Name als Lastfall -- eindeutig in der Analyse."""

    ohne: str = ""
    """Warum es keine Stelle gibt, ein Satz -- leer, wenn es welche gibt."""

    @property
    def hinweise(self) -> List[str]:
        """Was grau an der Analyse steht, je ein Satz: warum es keine Stelle gibt, was fehlt."""
        fehlen = (f"{aufgezaehlt(self.fehlen)} {'ist' if len(self.fehlen) == 1 else 'sind'} "
                  f"im System kein Stab mehr." if self.fehlen else "")
        return [s for s in (self.ohne, fehlen) if s]

    @property
    def lastfaelle(self) -> List[QALastfallEintrag]:
        """Die Stellen als Lastfaelle der Analyse, in kN und kNm."""
        return [QALastfallEintrag(name=name, N_Ed=s.werte["N"] / 1e3,
                                  M_y_Ed=s.werte["M_y"] / 1e3, M_z_Ed=s.werte["M_z"] / 1e3,
                                  V_y_Ed=s.werte["V_y"] / 1e3, V_z_Ed=s.werte["V_z"] / 1e3,
                                  T_Ed=s.werte["T"] / 1e3)
                for name, s in self.stellen]

    def herleitung(self, id: str, schwerpunkt: Tuple[str, str],
                   **angaben: Any) -> Stellenherleitung:
        """
        Ihre Herleitung, als Prozedur ohne Ausgabe
        (:class:`~opencivil.stabwerk.stellen.Stellenherleitung`) -- ``schwerpunkt``
        die Wert-IDs von ``y_S`` und ``z_S`` der Analyse.
        """
        titel = "Stellen aus dem Balkensystem" + (f" «{self.system}»" if self.system else "")
        return Stellenherleitung(id, system=self.system, staebe=self.staebe,
                                 wahl=_WAHL[self.wahl], stellen=self.stellen,
                                 hinweise=self.hinweise, schwerpunkt=schwerpunkt,
                                 titel=titel, **angaben)


#: Wie die Herleitung die Wahl der Staebe nennt.
_WAHL = {Stabwahl.MIT_QUERSCHNITT: "die Stäbe mit dieser Querschnittsanalyse als Querschnitt",
         Stabwahl.GEWAEHLT: "die gewählten Stäbe"}


def aus_dem_system(eintrag: QuerschnittsanalyseEintrag, aufbau: Aufbau) -> Optional[AusDemSystem]:
    """
    Was die Analyse ``eintrag`` aus ihrem Balkensystem nimmt -- ``None``
    ohne System. Siehe Dateikopf.
    """
    wahl = eintrag.aus_system
    if not wahl.system:
        return None
    teil = aufbau.teile.get(wahl.system)
    if teil is None:
        unfertig = aufbau.unfertige.get(wahl.system)
        if unfertig is None:
            return AusDemSystem("", wahl.stabwahl, ohne="Das gewählte Balkensystem gibt es "
                                                        "nicht mehr – ein anderes wählen.")
        return AusDemSystem(unfertig.name, wahl.stabwahl,
                            ohne=f"Das Balkensystem «{unfertig.name}» rechnet nicht – warum, "
                                 f"steht bei ihm.")
    staebe, fehlen = _staebe(eintrag, teil.eintrag)
    namen = {q.kennung: q.name for q in teil.eintrag.querschnitte}
    aus = AusDemSystem(teil.name, wahl.stabwahl, staebe=staebe, fehlen=fehlen,
                       kandidaten=[(l.kennung, namen.get(l.querschnitt, ""))
                                   for l in teil.eintrag.linien if l.stab])
    if not staebe:
        aus.ohne = (f"Im System hat noch kein Stab «{eintrag.name}» als Querschnitt."
                    if wahl.stabwahl is Stabwahl.MIT_QUERSCHNITT else "Noch kein Stab gewählt.")
        return aus
    befund = aufbau.befund_im_aufbau(teil.objekt.rechnung.id)
    if befund is None or not befund.ergebnis.faelle:
        aus.ohne = f"Das Balkensystem «{teil.name}» rechnet nicht – warum, steht bei ihm."
        return aus
    kombinationen = [(f.name, befund.verlaeufe(f.name))
                     for f in befund.ergebnis.faelle if f.kombination]
    if not kombinationen:
        aus.ohne = f"Das Balkensystem «{teil.name}» hat noch keine Kombination."
        return aus
    stellen = massgebende_stellen(kombinationen, staebe)
    if not stellen:
        aus.ohne = "In keiner Kombination wirkt auf diese Stäbe eine Schnittgrösse."
        return aus
    aus.stellen = _benannt(stellen, [l.name for l in eintrag.lastfaelle])
    return aus


def _staebe(eintrag: QuerschnittsanalyseEintrag, system: Any) -> Tuple[List[str], List[str]]:
    """
    Die Staebe, die zaehlen, in der Folge des Systems -- und gewaehlte, die
    es dort nicht mehr gibt oder die keinen Querschnitt haben, in der Folge
    der Wahl.
    """
    wahl = eintrag.aus_system
    traegt = [l for l in system.linien if l.stab]
    if wahl.stabwahl is Stabwahl.GEWAEHLT:
        da = {l.kennung for l in traegt}
        return ([l.kennung for l in traegt if l.kennung in wahl.staebe],
                [k for k in wahl.staebe if k not in da])
    eigene = {q.kennung for q in system.querschnitte
              if q.art is Querschnittsart.ANALYSE and q.bezug == eintrag.kennung}
    return [l.kennung for l in traegt if l.querschnitt in eigene], []


def _benannt(stellen: List[Stelle], vergeben: List[str]) -> List[Tuple[str, Stelle]]:
    """
    Je Stelle ihr Name als Lastfall. Die Nachweise fuehren einen Lastfall
    unter der Kennung seines Namens (:func:`~opencivil.core.wert.kennung_aus`);
    gaebe es die schon, bekommt er eine Nummer dazu.
    """
    belegt = {kennung_aus(n) for n in vergeben}
    heraus = []
    for s in stellen:
        name, n = s.name, 1
        while kennung_aus(name) in belegt:
            n += 1
            name = f"{s.name} ({n})"
        belegt.add(kennung_aus(name))
        heraus.append((name, s))
    return heraus
