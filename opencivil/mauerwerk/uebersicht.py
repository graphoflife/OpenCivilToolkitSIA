"""
opencivil/mauerwerk/uebersicht.py -- was die Zusammenfassung einer Wand über ihren Nachweisen zeigt.

VERANTWORTUNG:
Die Angaben zur Wand -- ihr Mauerwerk, wie es gemauert ist, ihre Dicke
(:func:`angaben`) -- und die Tabelle ihrer Bemessungswerte: je Wert der
des Mauerwerks und der, mit dem die Wand rechnet, im Verband mit seinem
Faktor (:func:`wertetabelle`). Beides aus dem Befund der Wand
(:class:`~opencivil.mauerwerk.werk.Wandbefund`). Bis 2026-11-28 stellte die
Oberfläche diese Tabelle selbst zusammen; seit die Wand Nachweise führt,
steht sie wie bei jedem Bauteil über deren Tabelle, auch im Bericht.
"""

from __future__ import annotations

from opencivil.core.einheiten import EINHEITSLOS
from opencivil.core.latex import Mathe, als_text
from opencivil.core.protokoll import GleichungBlock, TabellenBlock
from opencivil.mauerwerk.kennwerte import quelle
from opencivil.mauerwerk.werk import Mauerwerkswand, Wandbefund

#: Welche Bemessungswerte die Tabelle zeigt, je mit seinen Stellen.
WERTE = (("f_xd", 2), ("f_yd", 2), ("E_xd", 0), ("G_d", 0), ("mu_d", 2))


def angaben(befund: Wandbefund) -> GleichungBlock:
    """
    Was über der Tabelle steht: Mauerwerk, wie gemauert -- im Verband mit
    seinem Faktor, den μ_d nicht trägt --, Stossfugen und Dicke.
    """
    w = befund.wand
    verband = (f" – f, E und G mal {befund.werte.faktor:.2f}" if befund.werte.faktor != 1 else "")
    text = (f"Mauerwerk {befund.mauerwerk}, {w.mauerung.beschriftung}{verband}, "
            f"Stossfugen {w.stossfugen.beschriftung}")
    return GleichungBlock(latex=rf"{als_text(text)} \qquad t_w = {befund.t * 1e3:.0f}"
                                r"~\mathrm{mm}", titel="Angaben zur Wand")


def wertetabelle(wand: Mauerwerkswand, befund: Wandbefund) -> TabellenBlock:
    """
    Die Bemessungswerte des Mauerwerks und der Wand, mit Beschreibung und
    Zeichen des Mauerwerks -- vollfugig f_yd aus dessen f_yd,v.
    """
    zeilen = []
    for kurz, stellen in WERTE:
        d = wand.mauerwerk.definition(quelle(kurz, befund.wand.vollfugig))
        zeilen.append([d.beschreibung, Mathe(d.symbol),
                       f"{befund.material[d.kurzname]:.{stellen}f}",
                       f"{getattr(befund.werte, kurz):.{stellen}f}",
                       "–" if d.einheit == EINHEITSLOS else d.einheit.beschriftung])
    return TabellenBlock(kopf=["Grösse", "Zeichen", befund.mauerwerk, "Wand", "Einheit"],
                         zeilen=zeilen, titel="Bemessungswerte", ausrichtung="llrrl")
