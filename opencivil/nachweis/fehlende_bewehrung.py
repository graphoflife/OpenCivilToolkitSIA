"""
opencivil/nachweis/fehlende_bewehrung.py -- Nachweise, die mangels Bewehrung entfallen.

VERANTWORTUNG:
Sagt, dass in dieser Tragrichtung nichts zu rechnen ist -- und sagt es
sichtbar. Gerechnet wird hier nichts.

WARUM ES DEN BAUSTEIN GIBT:
Liegt in einer Richtung keine Bewehrung, laesst sich weder die Resistenzlinie
der Handrechnung aufstellen noch eine statische Hoehe bestimmen. Frueher entfiel
der Nachweis darum stillschweigend: wer eine Einwirkung in y-Richtung angegeben
hatte, fand sie in der Zusammenfassung nirgends wieder. Ein leerer Platz liest
sich aber wie *geprueft und in Ordnung*.

Ohne Stahl ist der Momentenwiderstand der Handrechnung **null** -- nicht etwa
das, was der Beton allein noch aufnaehme. Der Erfuellungsgrad ist damit
ebenfalls null und der Nachweis nicht erfuellt. Genau das steht jetzt da.

NICHT ZU VERWECHSELN MIT:
Der Fall, dass nur *eine Seite* unbewehrt ist -- untere Lage vorhanden, obere
nicht --, wird von den Nachweisen selbst behandelt. Hier geht es um eine
Richtung, in der ueberhaupt kein Posten liegt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from opencivil.core.berechnung import Eingaben, Nachweis, NachweisUrteil, grad_def
from opencivil.core.einheiten import EINHEITSLOS, Einheit, Groesse
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.core.wert import kennung_aus
from opencivil.querschnitt.platte import Plattenquerschnitt, Richtung


@dataclass(frozen=True)
class Ausgefallen:
    """Ein einzelner Nachweis, der nicht gefuehrt werden kann."""

    art: str
    """Kurzzeichen der Nachweisart -- ``M-N`` oder ``V``."""

    langname: str
    """Die Nachweisart ausgeschrieben, mit Richtung."""

    fall: str
    """Name der Einwirkungskombination."""

    symbol: str
    """Symbol des Widerstands, z.B. ``M_{Rd,y}``."""

    einwirkung_symbol: str
    einwirkung: Groesse
    einheit: Einheit

    @property
    def kennung(self) -> str:
        return kennung_aus(f"{self.art}_{self.fall}")


class FehlendeBewehrung(Nachweis):
    """
    Die Nachweise einer unbewehrten Tragrichtung -- alle nicht erfuellt.

    Ein Baustein je Platte und Richtung, ein Urteil je ausgefallenem Nachweis.
    Er hat keine Eingaenge: es gibt nichts zu beschaffen, wenn nichts da ist.
    """

    def __init__(
        self,
        querschnitt: Plattenquerschnitt,
        richtung: Richtung,
        faelle: Sequence[Ausgefallen],
    ) -> None:
        if not faelle:
            raise ValueError(
                "Ohne ausgefallene Nachweise gibt es nichts zu melden.")
        self.querschnitt = querschnitt
        self.richtung = richtung
        self.faelle = list(faelle)

        r = richtung.value
        basis = f"{querschnitt.id}.nachweis.fehlt.{r}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.kennung: grad_def(
                f"{basis}.{f.kennung}.erfuellungsgrad",
                rf"\alpha_{{eff,{f.art},{r},{als_text(f.fall)}}}",
                (f"Erfüllungsgrad {f.art} {richtung.beschriftung} – "
                 f"{f.fall} (keine Bewehrung)"),
            )
            for f in self.faelle
        }

        super().__init__(
            basis,
            ausgaben=list(self.d_ausnutzung.values()),
            bezuege=[],
            titel=f"Ohne Bewehrung {richtung.beschriftung} – {querschnitt.name}",
            abschnitt=querschnitt.abschnitt,
        )

    @property
    def grund(self) -> str:
        return (f"Keine Bewehrung in {self.richtung.beschriftung} → Widerstand 0, "
                f"nicht erfüllt.")

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(f"Ohne Bewehrung – {self.richtung.beschriftung}")
        p.text(self.grund)

        ergebnis: Dict[str, Groesse] = {}
        urteile: List[NachweisUrteil] = []
        for fall in self.faelle:
            ergebnis[self.d_ausnutzung[fall.kennung].id] = Groesse(0.0, EINHEITSLOS)
            urteile.append(NachweisUrteil(
                name=f"{fall.art} {self.richtung.value} – {fall.fall}",
                art=fall.art,
                ziel=self.d_ausnutzung[fall.kennung].id,
                langname=fall.langname,
                fall=fall.fall,
                erfuellt=False,
                erfuellungsgrad=Groesse(0.0, EINHEITSLOS),
                begruendung=self.grund,
                hinweis=self.grund,
                # Die Einwirkung steht da: sie wurde ja angegeben, und ohne sie
                # bliebe unklar, wogegen der Widerstand null nicht ausreicht.
                einwirkung=WertDef(
                    id=f"{self.id}.{fall.kennung}.Ed",
                    symbol=fall.einwirkung_symbol,
                    einheit=fall.einheit, beschreibung="Einwirkung", stellen=1,
                ).belegen(fall.einwirkung),
                widerstand=WertDef(
                    id=f"{self.id}.{fall.kennung}.Rd",
                    symbol=fall.symbol,
                    einheit=fall.einheit, beschreibung="Widerstand", stellen=1,
                ).belegen(Groesse(0.0, fall.einheit)),
            ))
        return ergebnis, urteile
