"""
opencivil/projekt.py -- Serialisierbare Beschreibung eines ganzen Projekts.

VERANTWORTUNG:
Bis hierher wurden Materialien und Querschnitte in Python zusammengesetzt. Eine
Oberflaeche braucht sie als Daten: etwas, das sich als JSON speichern, im Browser
bearbeiten und wieder zu einem :class:`Rechenwerk` zusammenbauen laesst.

Genau das ist ein :class:`Projekt` -- eine reine Beschreibung ohne Rechenlogik.
:meth:`Projekt.aufbauen` giesst daraus die Baustoffe, Querschnitte und Nachweise
und meldet sie beim Rechenwerk an.

EINHEITEN IN DER BESCHREIBUNG:
Alle Zahlen stehen in der Anzeige-Einheit des jeweiligen Kennwerts (mm, N/mm^2,
kNm, ...) -- also so, wie der Benutzer sie eintippt. Die Umrechnung in SI
geschieht erst beim Aufbau, ueber die :class:`Groesse`. Damit bleibt die
JSON-Darstellung lesbar und die Einheitenpruefung trotzdem lueckenlos.

EIGENSTAENDIG NUTZBAR::

    projekt = Projekt.beispiel()
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, MM, Einheit, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoff
from opencivil.material.beton import BETONSORTEN, beton
from opencivil.material.betonstahl import STAHLSORTEN, betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.querschnitt.platte import Bewehrungslage, Plattenquerschnitt


class ProjektFehler(Exception):
    """Die Projektbeschreibung ist in sich nicht stimmig."""


# ===========================================================================
# Bausteine der Beschreibung
# ===========================================================================


@dataclass
class MaterialEintrag:
    """Ein Baustoff, wie ihn die Oberflaeche beschreibt."""

    kennung: str
    """Stabile Kennung innerhalb des Projekts, z.B. ``m1``."""

    art: str
    """``beton`` oder ``betonstahl``."""

    sorte: str
    name: str = ""
    abweichungen: Dict[str, float] = field(default_factory=dict)
    """Sortenwerte, die abweichen -- Kurzname -> Zahl in der Anzeige-Einheit."""

    ueberschreibungen: Dict[str, float] = field(default_factory=dict)
    """Berechnete Kennwerte, die der Benutzer von Hand gesetzt hat."""

    def als_dict(self) -> dict:
        return {
            "kennung": self.kennung,
            "art": self.art,
            "sorte": self.sorte,
            "name": self.name,
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
            abweichungen={k: float(v) for k, v in (d.get("abweichungen") or {}).items()},
            ueberschreibungen={
                k: float(v) for k, v in (d.get("ueberschreibungen") or {}).items()
            },
        )


@dataclass
class LageEintrag:
    """Eine Bewehrungslage."""

    durchmesser: float
    """in mm"""

    stahl: str
    """Kennung des Betonstahls."""

    abstand: Optional[float] = None
    """Stababstand in mm."""

    anzahl: Optional[float] = None
    lichter_abstand: float = 0.0

    def als_dict(self) -> dict:
        return {
            "durchmesser": self.durchmesser,
            "stahl": self.stahl,
            "abstand": self.abstand,
            "anzahl": self.anzahl,
            "lichter_abstand": self.lichter_abstand,
        }

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "LageEintrag":
        abstand = d.get("abstand")
        anzahl = d.get("anzahl")
        return cls(
            durchmesser=float(d["durchmesser"]),
            stahl=str(d["stahl"]),
            abstand=None if abstand in (None, "") else float(abstand),
            anzahl=None if anzahl in (None, "") else float(anzahl),
            lichter_abstand=float(d.get("lichter_abstand") or 0.0),
        )


@dataclass
class KombinationEintrag:
    """Eine zu pruefende Schnittgroessenkombination."""

    name: str
    M_Ed: float = 0.0
    """in kNm"""

    N_Ed: float = 0.0
    """in kN"""

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


@dataclass
class QuerschnittEintrag:
    """Ein Plattenquerschnitt samt seiner Nachweiskombinationen."""

    kennung: str
    name: str
    beton: str
    """Kennung des Betons."""

    h: float = 300.0
    b: float = 1000.0
    ueberdeckung_unten: float = 30.0
    ueberdeckung_oben: float = 30.0
    lagen_unten: List[LageEintrag] = field(default_factory=list)
    lagen_oben: List[LageEintrag] = field(default_factory=list)
    kombinationen: List[KombinationEintrag] = field(default_factory=list)

    def als_dict(self) -> dict:
        return {
            "kennung": self.kennung,
            "name": self.name,
            "beton": self.beton,
            "h": self.h,
            "b": self.b,
            "ueberdeckung_unten": self.ueberdeckung_unten,
            "ueberdeckung_oben": self.ueberdeckung_oben,
            "lagen_unten": [l.als_dict() for l in self.lagen_unten],
            "lagen_oben": [l.als_dict() for l in self.lagen_oben],
            "kombinationen": [k.als_dict() for k in self.kombinationen],
        }

    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "QuerschnittEintrag":
        return cls(
            kennung=str(d["kennung"]),
            name=str(d.get("name") or d["kennung"]),
            beton=str(d["beton"]),
            h=float(d.get("h") or 300.0),
            b=float(d.get("b") or 1000.0),
            ueberdeckung_unten=float(d.get("ueberdeckung_unten") or 30.0),
            ueberdeckung_oben=float(d.get("ueberdeckung_oben") or 30.0),
            lagen_unten=[LageEintrag.aus_dict(x) for x in (d.get("lagen_unten") or [])],
            lagen_oben=[LageEintrag.aus_dict(x) for x in (d.get("lagen_oben") or [])],
            kombinationen=[
                KombinationEintrag.aus_dict(x) for x in (d.get("kombinationen") or [])
            ],
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
    warnungen: List[str] = field(default_factory=list)

    def alle_nachweisziele(self) -> List[str]:
        """Alle Ausnutzungsgrade -- das uebliche Ziel eines Laufs."""
        return [
            d.id
            for nachweis in self.nachweise.values()
            for d in nachweis.d_ausnutzung.values()
        ]

    def eckwertziele(self) -> List[str]:
        return [
            d.id
            for nachweis in self.nachweise.values()
            for d in nachweis.d_eckwerte.values()
        ]


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
            q.kennung for q in self.querschnitte
        }
        i = 1
        while f"{vorsilbe}{i}" in vergeben:
            i += 1
        return f"{vorsilbe}{i}"

    # -- Aufbau -------------------------------------------------------------

    def aufbauen(self) -> Aufbau:
        """
        Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

        Wirft :class:`ProjektFehler`, wenn die Beschreibung nicht stimmig ist --
        etwa wenn ein Querschnitt auf ein geloeschtes Material verweist.
        """
        werk = Rechenwerk()
        aufbau = Aufbau(werk=werk)

        for eintrag in self.materialien:
            aufbau.baustoffe[eintrag.kennung] = self._baustoff(eintrag)

        for eintrag in self.querschnitte:
            querschnitt = self._querschnitt(eintrag, aufbau.baustoffe)
            aufbau.querschnitte[eintrag.kennung] = querschnitt
            querschnitt.ins_rechenwerk(werk)

            if eintrag.kombinationen:
                nachweis = BiegungNormalkraft(
                    querschnitt, [self._kombination(k) for k in eintrag.kombinationen]
                )
                werk.registriere(nachweis)
                aufbau.nachweise[eintrag.kennung] = nachweis
            else:
                aufbau.warnungen.append(
                    f"Querschnitt '{eintrag.name}': keine Schnittgrössen angegeben, "
                    f"also kein Nachweis möglich."
                )

        # Nicht verwendete Materialien trotzdem anmelden, damit ihre Kennwerte
        # in der Oberflaeche gerechnet und angezeigt werden koennen.
        for kennung, baustoff in aufbau.baustoffe.items():
            if not any(b.id.startswith(baustoff.id + ".") for b in werk.berechnungen):
                baustoff.ins_rechenwerk(werk)

        self._ueberschreibungen_setzen(werk, aufbau)
        return aufbau

    def _baustoff(self, eintrag: MaterialEintrag) -> Baustoff:
        bauer = {"beton": beton, "betonstahl": betonstahl}.get(eintrag.art)
        if bauer is None:
            raise ProjektFehler(
                f"Unbekannte Materialart '{eintrag.art}'. "
                f"Möglich sind 'beton' und 'betonstahl'."
            )
        sorten = BETONSORTEN if eintrag.art == "beton" else STAHLSORTEN
        if eintrag.sorte not in sorten:
            raise ProjektFehler(
                f"Unbekannte Sorte '{eintrag.sorte}' für {eintrag.art}. "
                f"Verfügbar: {', '.join(sorten)}."
            )
        # Zuerst ohne Abweichungen bauen, um an die Anzeige-Einheiten zu kommen.
        roh = bauer(eintrag.sorte, praefix=f"{eintrag.art}.{eintrag.kennung}")
        abweichungen = {
            kurzname: Groesse(zahl, roh.definition(kurzname).einheit)
            for kurzname, zahl in eintrag.abweichungen.items()
            if kurzname in roh.definitionen
        }
        return bauer(
            eintrag.sorte,
            name=eintrag.name or eintrag.sorte,
            praefix=f"{eintrag.art}.{eintrag.kennung}",
            abweichungen=abweichungen,
        )

    def _querschnitt(
        self, eintrag: QuerschnittEintrag, baustoffe: Mapping[str, Baustoff]
    ) -> Plattenquerschnitt:
        beton_stoff = baustoffe.get(eintrag.beton)
        if beton_stoff is None:
            raise ProjektFehler(
                f"Querschnitt '{eintrag.name}' verweist auf das Material "
                f"'{eintrag.beton}', das es nicht (mehr) gibt."
            )
        if not (eintrag.lagen_unten or eintrag.lagen_oben):
            raise ProjektFehler(
                f"Querschnitt '{eintrag.name}': ohne Bewehrungslage lässt sich "
                f"kein Widerstand bestimmen."
            )
        return Plattenquerschnitt(
            name=eintrag.name,
            h=Groesse(eintrag.h, MM),
            b=Groesse(eintrag.b, MM),
            beton=beton_stoff,
            lagen_unten=[self._lage(l, baustoffe, eintrag.name) for l in eintrag.lagen_unten],
            lagen_oben=[self._lage(l, baustoffe, eintrag.name) for l in eintrag.lagen_oben],
            ueberdeckung_unten=Groesse(eintrag.ueberdeckung_unten, MM),
            ueberdeckung_oben=Groesse(eintrag.ueberdeckung_oben, MM),
            praefix=f"querschnitt.{eintrag.kennung}",
        )

    def _lage(
        self, eintrag: LageEintrag, baustoffe: Mapping[str, Baustoff], wo: str
    ) -> Bewehrungslage:
        stahl = baustoffe.get(eintrag.stahl)
        if stahl is None:
            raise ProjektFehler(
                f"Eine Bewehrungslage in '{wo}' verweist auf den Stahl "
                f"'{eintrag.stahl}', den es nicht (mehr) gibt."
            )
        return Bewehrungslage(
            durchmesser=Groesse(eintrag.durchmesser, MM),
            stahl=stahl,
            abstand=Groesse(eintrag.abstand, MM) if eintrag.abstand else None,
            anzahl=eintrag.anzahl if not eintrag.abstand else None,
            lichter_abstand=Groesse(eintrag.lichter_abstand, MM),
        )

    def _kombination(self, eintrag: KombinationEintrag) -> Schnittgroessen:
        try:
            art = Erfuellungsart(eintrag.art)
        except ValueError:
            raise ProjektFehler(
                f"Unbekannter Massstab '{eintrag.art}'. Möglich sind: "
                f"{', '.join(a.value for a in Erfuellungsart)}."
            ) from None
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
                        f"unbekannt, die Überschreibung wird übergangen."
                    )
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
            querschnitte=[
                QuerschnittEintrag.aus_dict(x) for x in (d.get("querschnitte") or [])
            ],
        )

    def speichern(self, pfad: str | Path) -> Path:
        ziel = Path(pfad)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(
            json.dumps(self.als_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return ziel

    @classmethod
    def laden(cls, pfad: str | Path) -> "Projekt":
        return cls.aus_dict(json.loads(Path(pfad).read_text(encoding="utf-8")))

    # -- Startpunkt ---------------------------------------------------------

    @classmethod
    def beispiel(cls) -> "Projekt":
        """Ein lauffähiges Beispiel, damit die Oberfläche nicht leer startet."""
        return cls(
            name="Beispiel – Decke über EG",
            materialien=[
                MaterialEintrag(kennung="b1", art="beton", sorte="C30/37", name="C30/37"),
                MaterialEintrag(
                    kennung="s1", art="betonstahl", sorte="B500B", name="B500B"
                ),
            ],
            querschnitte=[
                QuerschnittEintrag(
                    kennung="q1",
                    name="Decke über EG",
                    beton="b1",
                    h=300.0,
                    b=1000.0,
                    lagen_unten=[
                        LageEintrag(durchmesser=18.0, stahl="s1", abstand=150.0),
                        LageEintrag(durchmesser=12.0, stahl="s1", abstand=150.0),
                    ],
                    lagen_oben=[LageEintrag(durchmesser=12.0, stahl="s1", abstand=150.0)],
                    kombinationen=[
                        KombinationEintrag(name="Feld", M_Ed=150.0, N_Ed=0.0),
                        KombinationEintrag(
                            name="Feld mit Druck", M_Ed=150.0, N_Ed=-300.0
                        ),
                        KombinationEintrag(name="Stütze", M_Ed=-60.0, N_Ed=0.0),
                    ],
                )
            ],
        )
