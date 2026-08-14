"""
opencivil/projekt.py -- Serialisierbare Beschreibung eines ganzen Projekts.

VERANTWORTUNG:
Eine Oberflaeche braucht Materialien und Querschnitte als Daten: etwas, das sich
als JSON speichern, im Browser bearbeiten und wieder zu einem :class:`Rechenwerk`
zusammenbauen laesst. Genau das ist ein :class:`Projekt` -- eine reine
Beschreibung ohne Rechenlogik.

NORMSORTE ODER EIGENES MATERIAL:
Ein Material ist entweder eine unveraenderte Normsorte oder ein eigenes. Nur die
unveraenderte darf die Sortenbezeichnung tragen: steht 'C30/37' auf einem
Bauteil, muessen die Kennwerte auch die der Norm sein. Wer abweichen will, macht
das Material mit :meth:`Projekt.material_loesen` eigenstaendig; es bekommt dann
einen eigenen Namen wie ``C30/37_1``. So kann keine abgeaenderte Festigkeit unter
dem Deckmantel einer Normbezeichnung im Bericht landen.

EINHEITEN IN DER BESCHREIBUNG:
Alle Zahlen stehen in der Anzeige-Einheit des jeweiligen Kennwerts (mm, N/mm^2,
kNm, ...) -- also so, wie der Benutzer sie eintippt. Die Umrechnung in SI
geschieht erst beim Aufbau, ueber die :class:`Groesse`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from opencivil.core.einheiten import KN, KNM, MM, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoff
from opencivil.material.beton import BETONSORTEN, beton
from opencivil.material.betonstahl import STAHLSORTEN, betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.querschnitt.platte import (
    LAGENZAHL, Bewehrungslage, Bewehrungsposten, Plattenquerschnitt, Richtung,
)


class ProjektFehler(Exception):
    """Die Projektbeschreibung ist in sich nicht stimmig."""


def sorten(art: str) -> Mapping[str, Any]:
    return BETONSORTEN if art == "beton" else STAHLSORTEN


# ===========================================================================
# Material
# ===========================================================================


@dataclass
class MaterialEintrag:
    """Ein Baustoff, wie ihn die Oberflaeche beschreibt."""

    kennung: str
    art: str
    """``beton`` oder ``betonstahl``."""

    sorte: str
    name: str = ""
    eigenstaendig: bool = False
    """
    False = unveraenderte Normsorte, Kennwerte gesperrt, Name = Sorte.
    True  = eigenes Material, aenderbar, mit eigenem Namen.
    """

    abweichungen: Dict[str, float] = field(default_factory=dict)
    ueberschreibungen: Dict[str, float] = field(default_factory=dict)

    @property
    def anzeigename(self) -> str:
        return self.name or self.sorte

    @property
    def ist_normsorte(self) -> bool:
        return not self.eigenstaendig

    def pruefen(self) -> None:
        if self.art not in ("beton", "betonstahl"):
            raise ProjektFehler(
                f"Unbekannte Materialart '{self.art}'. "
                f"Möglich sind 'beton' und 'betonstahl'.")
        if self.sorte not in sorten(self.art):
            raise ProjektFehler(
                f"Unbekannte Sorte '{self.sorte}' für {self.art}. "
                f"Verfügbar: {', '.join(sorten(self.art))}.")
        if self.ist_normsorte:
            if self.abweichungen or self.ueberschreibungen:
                raise ProjektFehler(
                    f"'{self.anzeigename}' ist als Normsorte geführt und darf keine "
                    f"abweichenden Kennwerte haben. Bitte zuerst zu einem eigenen "
                    f"Material machen.")
            if self.name and self.name != self.sorte:
                raise ProjektFehler(
                    f"Eine unveränderte Normsorte muss '{self.sorte}' heissen, "
                    f"nicht '{self.name}'.")

    def als_dict(self) -> dict:
        return {
            "kennung": self.kennung, "art": self.art, "sorte": self.sorte,
            "name": self.anzeigename, "eigenstaendig": self.eigenstaendig,
            "abweichungen": dict(self.abweichungen),
            "ueberschreibungen": dict(self.ueberschreibungen),
        }

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "MaterialEintrag":
        return cls(
            kennung=str(d["kennung"]),
            art=str(d["art"]),
            sorte=str(d.get("sorte", "")),
            name=str(d.get("name", "")),
            eigenstaendig=bool(d.get("eigenstaendig", False)),
            abweichungen={k: float(v) for k, v in (d.get("abweichungen") or {}).items()},
            ueberschreibungen={
                k: float(v) for k, v in (d.get("ueberschreibungen") or {}).items()},
        )


# ===========================================================================
# Bewehrung
# ===========================================================================


@dataclass
class PostenEintrag:
    """Grundbewehrung oder Zulage einer Lage."""

    durchmesser: float = 0.0
    """in mm; 0 bedeutet: nicht vorhanden."""

    abstand: Optional[float] = 150.0
    """Teilung in mm. Genau eines von ``abstand`` und ``anzahl`` ist gesetzt."""

    anzahl: Optional[float] = None

    @property
    def vorhanden(self) -> bool:
        if self.durchmesser <= 0:
            return False
        return bool(self.abstand and self.abstand > 0) or bool(self.anzahl and self.anzahl > 0)

    def als_dict(self) -> dict:
        return {"durchmesser": self.durchmesser, "abstand": self.abstand,
                "anzahl": self.anzahl}

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "PostenEintrag":
        abstand, anzahl = d.get("abstand"), d.get("anzahl")
        return cls(
            durchmesser=float(d.get("durchmesser") or 0.0),
            abstand=None if abstand in (None, "") else float(abstand),
            anzahl=None if anzahl in (None, "") else float(anzahl),
        )

    def als_posten(self) -> Bewehrungsposten:
        return Bewehrungsposten(
            durchmesser=Groesse(self.durchmesser, MM),
            abstand=Groesse(self.abstand, MM) if self.abstand else None,
            anzahl=self.anzahl if not self.abstand else None,
        )


@dataclass
class LageEintrag:
    """Eine der vier Lagen."""

    stahl: str = ""
    grund: PostenEintrag = field(default_factory=PostenEintrag)
    zulage: PostenEintrag = field(default_factory=lambda: PostenEintrag(durchmesser=0.0))

    @property
    def vorhanden(self) -> bool:
        return self.grund.vorhanden or self.zulage.vorhanden

    def als_dict(self) -> dict:
        return {"stahl": self.stahl, "grund": self.grund.als_dict(),
                "zulage": self.zulage.als_dict()}

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "LageEintrag":
        return cls(
            stahl=str(d.get("stahl", "")),
            grund=PostenEintrag.aus_dict(d.get("grund") or {}),
            zulage=PostenEintrag.aus_dict(d.get("zulage") or {"durchmesser": 0.0}),
        )


@dataclass
class KombinationEintrag:
    """Eine zu pruefende Schnittgroessenkombination."""

    name: str
    M_Ed: float = 0.0
    N_Ed: float = 0.0
    art: str = Erfuellungsart.NORMALKRAFT_KONSTANT.value

    def als_dict(self) -> dict:
        return {"name": self.name, "M_Ed": self.M_Ed, "N_Ed": self.N_Ed, "art": self.art}

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "KombinationEintrag":
        return cls(
            name=str(d["name"]),
            M_Ed=float(d.get("M_Ed") or 0.0),
            N_Ed=float(d.get("N_Ed") or 0.0),
            art=str(d.get("art") or Erfuellungsart.NORMALKRAFT_KONSTANT.value),
        )


def _lagen_aus_altem_format(d: Mapping[str, Any]) -> List[dict]:
    """
    Rechnet eine vor dem Vier-Lagen-Modell gespeicherte Platte um.

    Frueher gab es beliebig viele Lagen je Seite, jede mit einem einzigen
    Bewehrungssatz. Uebernommen werden die beiden aeussersten je Seite:

        lagen_unten[0] -> 1. Lage      lagen_oben[0] -> 4. Lage
        lagen_unten[1] -> 2. Lage      lagen_oben[1] -> 3. Lage

    Weitere Lagen der alten Beschreibung gehen dabei verloren -- besser als eine
    gespeicherte Datei gar nicht mehr zu oeffnen, aber der Benutzer sollte sie
    nachsehen.
    """
    def umbauen(alt: Optional[Mapping[str, Any]]) -> dict:
        if not alt:
            return {"stahl": "", "grund": {"durchmesser": 0.0}, "zulage": {"durchmesser": 0.0}}
        return {
            "stahl": alt.get("stahl", ""),
            "grund": {
                "durchmesser": alt.get("durchmesser", 0.0),
                "abstand": alt.get("abstand"),
                "anzahl": alt.get("anzahl"),
            },
            "zulage": {"durchmesser": 0.0},
        }

    unten = list(d.get("lagen_unten") or [])
    oben = list(d.get("lagen_oben") or [])
    return [
        umbauen(unten[0] if len(unten) > 0 else None),   # 1. Lage
        umbauen(unten[1] if len(unten) > 1 else None),   # 2. Lage
        umbauen(oben[1] if len(oben) > 1 else None),     # 3. Lage
        umbauen(oben[0] if len(oben) > 0 else None),     # 4. Lage
    ]


@dataclass
class QuerschnittEintrag:
    """Eine Stahlbeton-Platte mit genau vier Bewehrungslagen."""

    kennung: str
    name: str
    beton: str
    h: float = 300.0
    b: float = 1000.0
    ueberdeckung_unten: float = 30.0
    ueberdeckung_oben: float = 30.0
    lagen: List[LageEintrag] = field(default_factory=list)
    """Genau vier, Index 0 = 1. Lage (unterste)."""

    richtung_lage1: str = "x"
    """Richtung der 1. Lage; die 2. bekommt die Gegenrichtung."""

    richtung_lage4: str = "x"
    """Richtung der 4. Lage; die 3. bekommt die Gegenrichtung."""

    kombinationen: List[KombinationEintrag] = field(default_factory=list)

    def __post_init__(self) -> None:
        while len(self.lagen) < LAGENZAHL:
            self.lagen.append(LageEintrag())
        del self.lagen[LAGENZAHL:]

    def richtung_von(self, nummer: int) -> Richtung:
        """Richtung der Lage 1..4 -- die Paare (1,2) und (3,4) sind gekoppelt."""
        eins = Richtung(self.richtung_lage1)
        vier = Richtung(self.richtung_lage4)
        return {1: eins, 2: eins.gegenrichtung, 3: vier.gegenrichtung, 4: vier}[nummer]

    def als_dict(self) -> dict:
        return {
            "kennung": self.kennung, "name": self.name, "beton": self.beton,
            "h": self.h, "b": self.b,
            "ueberdeckung_unten": self.ueberdeckung_unten,
            "ueberdeckung_oben": self.ueberdeckung_oben,
            "richtung_lage1": self.richtung_lage1,
            "richtung_lage4": self.richtung_lage4,
            "lagen": [l.als_dict() for l in self.lagen],
            "kombinationen": [k.als_dict() for k in self.kombinationen],
        }

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerschnittEintrag":
        lagen = d.get("lagen")
        if lagen is None and ("lagen_unten" in d or "lagen_oben" in d):
            lagen = _lagen_aus_altem_format(d)
        return cls(
            kennung=str(d["kennung"]),
            name=str(d.get("name") or d["kennung"]),
            beton=str(d["beton"]),
            h=float(d.get("h") or 300.0),
            b=float(d.get("b") or 1000.0),
            ueberdeckung_unten=float(d.get("ueberdeckung_unten") or 30.0),
            ueberdeckung_oben=float(d.get("ueberdeckung_oben") or 30.0),
            richtung_lage1=str(d.get("richtung_lage1") or "x"),
            richtung_lage4=str(d.get("richtung_lage4") or "x"),
            lagen=[LageEintrag.aus_dict(x) for x in (lagen or [])],
            kombinationen=[
                KombinationEintrag.aus_dict(x) for x in (d.get("kombinationen") or [])],
        )


# ===========================================================================
# Aufbau
# ===========================================================================


@dataclass
class Aufbau:
    """Was beim Zusammenbauen eines Projekts entsteht."""

    werk: Rechenwerk
    baustoffe: Dict[str, Baustoff] = field(default_factory=dict)
    querschnitte: Dict[str, Plattenquerschnitt] = field(default_factory=dict)
    nachweise: Dict[str, BiegungNormalkraft] = field(default_factory=dict)
    """Schluessel ist ``<querschnitt>.<richtung>``, weil je Richtung geprueft wird."""

    warnungen: List[str] = field(default_factory=list)

    def alle_nachweisziele(self) -> List[str]:
        return [d.id for n in self.nachweise.values() for d in n.d_ausnutzung.values()]

    def eckwertziele(self) -> List[str]:
        return [d.id for n in self.nachweise.values() for d in n.d_eckwerte.values()]


# ===========================================================================
# Projekt
# ===========================================================================


@dataclass
class Projekt:
    """Die vollstaendige, speicherbare Beschreibung eines Projekts."""

    name: str = "Neues Projekt"
    materialien: List[MaterialEintrag] = field(default_factory=list)
    querschnitte: List[QuerschnittEintrag] = field(default_factory=list)

    # -- Zugriff ------------------------------------------------------------

    def material(self, kennung: str) -> MaterialEintrag:
        for m in self.materialien:
            if m.kennung == kennung:
                return m
        raise ProjektFehler(f"Material '{kennung}' gibt es im Projekt nicht.")

    def querschnitt(self, kennung: str) -> QuerschnittEintrag:
        for q in self.querschnitte:
            if q.kennung == kennung:
                return q
        raise ProjektFehler(f"Querschnitt '{kennung}' gibt es im Projekt nicht.")

    def freie_kennung(self, vorsilbe: str) -> str:
        vergeben = {m.kennung for m in self.materialien} | {
            q.kennung for q in self.querschnitte}
        i = 1
        while f"{vorsilbe}{i}" in vergeben:
            i += 1
        return f"{vorsilbe}{i}"

    def freier_name(self, wunsch: str, ausser: str = "") -> str:
        """Haengt bei Bedarf _1, _2, ... an, bis der Name eindeutig ist."""
        vergeben = {m.anzeigename for m in self.materialien if m.kennung != ausser}
        if wunsch not in vergeben:
            return wunsch
        i = 1
        while f"{wunsch}_{i}" in vergeben:
            i += 1
        return f"{wunsch}_{i}"

    def abgeleiteter_name(self, sorte: str, ausser: str = "") -> str:
        """
        Erster freier Name der Form ``<Sorte>_1``, ``<Sorte>_2``, ...

        Nicht ueber :meth:`freier_name` mit dem Wunsch ``C30/37_1``, denn das
        haengte bei Belegung nochmals an und ergaebe ``C30/37_1_1``.
        """
        vergeben = {m.anzeigename for m in self.materialien if m.kennung != ausser}
        i = 1
        while f"{sorte}_{i}" in vergeben:
            i += 1
        return f"{sorte}_{i}"

    def material_loesen(self, kennung: str) -> MaterialEintrag:
        """
        Macht aus einer Normsorte ein eigenstaendiges, aenderbares Material.

        Der Name wird dabei zwingend geaendert -- die Sortenbezeichnung bleibt
        der unveraenderten Norm vorbehalten.
        """
        eintrag = self.material(kennung)
        if eintrag.eigenstaendig:
            return eintrag
        eintrag.eigenstaendig = True
        eintrag.name = self.abgeleiteter_name(eintrag.sorte, ausser=kennung)
        return eintrag

    # -- Pruefung -----------------------------------------------------------

    def pruefen(self) -> None:
        """Prueft die Beschreibung, bevor daraus gerechnet wird."""
        for m in self.materialien:
            m.pruefen()

        gesehen: Dict[str, str] = {}
        for m in self.materialien:
            if m.anzeigename in gesehen:
                raise ProjektFehler(
                    f"Der Name '{m.anzeigename}' ist zweimal vergeben "
                    f"({gesehen[m.anzeigename]} und {m.kennung}). Materialnamen "
                    f"müssen eindeutig sein, sonst lässt sich im Bericht nicht "
                    f"erkennen, welches gemeint ist.")
            gesehen[m.anzeigename] = m.kennung

    # -- Aufbau -------------------------------------------------------------

    def aufbauen(self) -> Aufbau:
        """
        Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

        Wirft :class:`ProjektFehler`, wenn die Beschreibung nicht stimmig ist --
        etwa wenn ein Querschnitt auf ein geloeschtes Material verweist.
        """
        self.pruefen()
        werk = Rechenwerk()
        aufbau = Aufbau(werk=werk)

        # Nur wenn mehrere Materialien derselben Art vorkommen, braucht es
        # Indizes an den Symbolen -- sonst waere f_{cd,C30/37} bloss Ballast.
        je_art: Dict[str, int] = {}
        for m in self.materialien:
            je_art[m.art] = je_art.get(m.art, 0) + 1

        for eintrag in self.materialien:
            index = eintrag.anzeigename if je_art[eintrag.art] > 1 else ""
            aufbau.baustoffe[eintrag.kennung] = self._baustoff(eintrag, index)

        for eintrag in self.querschnitte:
            querschnitt = self._querschnitt(eintrag, aufbau.baustoffe)
            aufbau.querschnitte[eintrag.kennung] = querschnitt
            querschnitt.ins_rechenwerk(werk)

            if not eintrag.kombinationen:
                aufbau.warnungen.append(
                    f"Platte '{eintrag.name}': keine Schnittgrössen angegeben, "
                    f"also kein Nachweis möglich.")
                continue

            kombinationen = [self._kombination(k) for k in eintrag.kombinationen]
            for richtung in querschnitt.richtungen_mit_bewehrung:
                nachweis = BiegungNormalkraft(querschnitt, kombinationen, richtung)
                werk.registriere(nachweis)
                aufbau.nachweise[f"{eintrag.kennung}.{richtung.value}"] = nachweis

        for baustoff in aufbau.baustoffe.values():
            baustoff.ins_rechenwerk(werk)

        self._ueberschreibungen_setzen(werk, aufbau)
        return aufbau

    def _baustoff(self, eintrag: MaterialEintrag, symbol_index: str) -> Baustoff:
        bauer = {"beton": beton, "betonstahl": betonstahl}[eintrag.art]
        roh = bauer(eintrag.sorte, praefix=f"{eintrag.art}.{eintrag.kennung}")
        abweichungen = {
            kurzname: Groesse(zahl, roh.definition(kurzname).einheit)
            for kurzname, zahl in eintrag.abweichungen.items()
            if kurzname in roh.definitionen
        }
        return bauer(
            eintrag.sorte,
            name=eintrag.anzeigename,
            praefix=f"{eintrag.art}.{eintrag.kennung}",
            abweichungen=abweichungen,
            symbol_index=symbol_index,
        )

    def _querschnitt(
        self, eintrag: QuerschnittEintrag, baustoffe: Mapping[str, Baustoff]
    ) -> Plattenquerschnitt:
        beton_stoff = baustoffe.get(eintrag.beton)
        if beton_stoff is None:
            raise ProjektFehler(
                f"Platte '{eintrag.name}' verweist auf das Material "
                f"'{eintrag.beton}', das es nicht (mehr) gibt.")

        lagen: List[Bewehrungslage] = []
        for nummer, lage in enumerate(eintrag.lagen, start=1):
            stahl = baustoffe.get(lage.stahl)
            if stahl is None and lage.vorhanden:
                raise ProjektFehler(
                    f"Die {nummer}. Lage von '{eintrag.name}' verweist auf den Stahl "
                    f"'{lage.stahl}', den es nicht (mehr) gibt.")
            lagen.append(Bewehrungslage(
                nummer=nummer,
                richtung=eintrag.richtung_von(nummer),
                stahl=stahl or next(iter(
                    s for s in baustoffe.values() if s.art.value == "betonstahl"), None),
                grund=lage.grund.als_posten(),
                zulage=lage.zulage.als_posten(),
            ))

        if not any(l.vorhanden for l in lagen):
            raise ProjektFehler(
                f"Platte '{eintrag.name}': ohne Bewehrung lässt sich kein "
                f"Widerstand bestimmen.")

        return Plattenquerschnitt(
            name=eintrag.name,
            h=Groesse(eintrag.h, MM),
            b=Groesse(eintrag.b, MM),
            beton=beton_stoff,
            lagen=lagen,
            ueberdeckung_unten=Groesse(eintrag.ueberdeckung_unten, MM),
            ueberdeckung_oben=Groesse(eintrag.ueberdeckung_oben, MM),
            praefix=f"querschnitt.{eintrag.kennung}",
        )

    def _kombination(self, eintrag: KombinationEintrag) -> Schnittgroessen:
        try:
            art = Erfuellungsart(eintrag.art)
        except ValueError:
            raise ProjektFehler(
                f"Unbekannter Massstab '{eintrag.art}'. Möglich sind: "
                f"{', '.join(a.value for a in Erfuellungsart)}.") from None
        return Schnittgroessen(
            name=eintrag.name,
            M_Ed=Groesse(eintrag.M_Ed, KNM),
            N_Ed=Groesse(eintrag.N_Ed, KN),
            art=art,
        )

    def _ueberschreibungen_setzen(self, werk: Rechenwerk, aufbau: Aufbau) -> None:
        for eintrag in self.materialien:
            baustoff = aufbau.baustoffe[eintrag.kennung]
            for kurzname, zahl in eintrag.ueberschreibungen.items():
                if kurzname not in baustoff.definitionen:
                    aufbau.warnungen.append(
                        f"Material '{baustoff.name}': Kennwert '{kurzname}' ist "
                        f"unbekannt, die Überschreibung wird übergangen.")
                    continue
                definition = baustoff.definition(kurzname)
                werk.setze(definition.id, Groesse(zahl, definition.einheit))

    # -- Speichern ----------------------------------------------------------

    def als_dict(self) -> dict:
        return {
            "name": self.name,
            "materialien": [m.als_dict() for m in self.materialien],
            "querschnitte": [q.als_dict() for q in self.querschnitte],
        }

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "Projekt":
        return cls(
            name=str(d.get("name") or "Neues Projekt"),
            materialien=[MaterialEintrag.aus_dict(x) for x in (d.get("materialien") or [])],
            querschnitte=[QuerschnittEintrag.aus_dict(x) for x in (d.get("querschnitte") or [])],
        )

    def speichern(self, pfad: str | Path) -> Path:
        ziel = Path(pfad)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(
            json.dumps(self.als_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return ziel

    @classmethod
    def laden(cls, pfad: str | Path) -> "Projekt":
        return cls.aus_dict(json.loads(Path(pfad).read_text(encoding="utf-8")))

    # -- Startpunkt ---------------------------------------------------------

    @classmethod
    def beispiel(cls) -> "Projekt":
        """Ein lauffähiges Beispiel, damit die Oberfläche nicht leer startet."""
        def lage(phi: float, zulage: float = 0.0) -> LageEintrag:
            return LageEintrag(
                stahl="s1",
                grund=PostenEintrag(durchmesser=phi, abstand=150.0),
                zulage=PostenEintrag(durchmesser=zulage, abstand=150.0 if zulage else None),
            )

        return cls(
            name="Beispiel – Decke über EG",
            materialien=[
                MaterialEintrag(kennung="b1", art="beton", sorte="C30/37", name="C30/37"),
                MaterialEintrag(kennung="s1", art="betonstahl", sorte="B500B", name="B500B"),
            ],
            querschnitte=[QuerschnittEintrag(
                kennung="q1", name="Decke über EG", beton="b1",
                h=300.0, b=1000.0,
                # 1. Lage in x (Haupttragrichtung unten), 2. Lage damit in y;
                # 4. Lage in x, 3. Lage in y.
                richtung_lage1="x", richtung_lage4="x",
                lagen=[
                    lage(18.0, zulage=12.0),   # 1. Lage x, mit Zulage
                    lage(16.0),                # 2. Lage y
                    lage(12.0),                # 3. Lage y
                    lage(12.0),                # 4. Lage x
                ],
                # Dieselbe Kombination wird in beiden Tragrichtungen geprüft.
                # Die Werte sind so gewählt, dass beide Richtungen aufgehen --
                # das Beispiel soll grün starten.
                kombinationen=[
                    KombinationEintrag(name="Feld", M_Ed=100.0, N_Ed=0.0),
                    KombinationEintrag(name="Feld mit Druck", M_Ed=100.0, N_Ed=-300.0),
                    KombinationEintrag(name="Stütze", M_Ed=-50.0, N_Ed=0.0),
                ])],
        )
