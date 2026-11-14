"""
opencivil/web/diagrammdaten.py -- was die Oberflaeche zeichnet, als JSON.

VERANTWORTUNG:
Die Punktfolgen der Diagramme: M-N-Interaktionslinien samt Knickpunkten,
Werkstoffgesetze, Querkraft ueber Moment und ueber Neigung, die Bilder der
Spannung-Dehnung-Analyse. Aus :mod:`opencivil.web.api` herausgeloest, das
damit nur noch Katalog, Mitschrift, Loesung und Zusammenfassung abbildet.

Wie dort wird hier nichts nachgerechnet, was der Kern schon weiss: die Kurven
kommen aus denselben Funktionen wie die Nachweise, hier werden sie in kN,
kNm und mm umgesetzt.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Collection, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil import spannungsanalyse
from opencivil.core.wert import grad_als_text
from opencivil.core.einheiten import KN, KNM, KN_PRO_M, MM, MM2, N_PRO_MM2, PRO_M, PROMILLE
from opencivil.core.rechenwerk import Loesung
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL, Spannungsblock
from opencivil.nachweis.resistenzlinie import Handlinie
from opencivil.nachweis.schubwandnachweis import Schubbefund
from opencivil.projekt import Aufbau
from opencivil.querschnitt.platte import Richtung
from opencivil.web.anzeige import Anzeigegroesse, si, zahl


def linien(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Je gerechneter M-N-Nachweis seine Linien, dazu die Bemessungs- und
    Knickpunkte -- und die Kennung seines Bauteils, damit niemand sie aus
    dem Schluessel lesen muss.
    """
    return {
        kennung: {**linie(nachweis, loesung, aufbau),
                  "bauteil": aufbau.bauteil_von(nachweis).kennung}
        for kennung, nachweis in aufbau.feld("nachweise").items()
        if nachweis.id in loesung.befunde
    }


def querkraftkurven(
    aufbau: Aufbau, loesung: Loesung, gewaehlt: Optional[Mapping[str, float]] = None
) -> dict:
    """
    Der Querkraftwiderstand ueber dem Moment -- eine Kurve je Tragrichtung.

    Eine je Platte ohne Buegel, auch ohne Querkraft: dann rechnet der
    Nachweis still, nur fuer dieses Bild. Die Waagrechte ist vorzeichenbehaftet: rechts das positive
    Moment (Zug unten), links das negative (Zug oben). Beide Aeste im selben
    Bild, weil sie dieselbe Platte beschreiben.

    Einen Ast gibt es nur, wo auf der gezogenen Seite Bewehrung liegt. Fehlt
    sie, gibt es kein ``d`` -- und ohne ``d`` keinen Widerstand.

    ``v_Rd`` haengt ueber ``m_Rd(N_Ed)`` von der Normalkraft ab. Welche gilt,
    waehlt der Benutzer unter dem Diagramm; ``gewaehlt`` bildet die Kennung auf
    diese Normalkraft in kN ab. Ohne Angabe gilt die des ersten Falls dieser
    Richtung -- dann liegen dessen Punkte auf der Kurve.

    Einheiten wie in den anderen Diagrammen: kNm und kN/m.
    """
    gewaehlt = gewaehlt or {}
    kurven: Dict[str, Any] = {}

    for kennung, nachweis in aufbau.feld("querkraft").items():
        befund = loesung.befunde.get(nachweis.id)
        # Mit Buegeln haengt der Widerstand nicht mehr am Moment, sondern an
        # der Neigung der Druckdiagonalen. Dann steht dort das andere Bild --
        # siehe neigungskurven().
        if befund is None or nachweis.buegel is not None:
            continue
        teil = aufbau.bauteil_von(nachweis)

        n_ed = gewaehlt.get(kennung)
        if n_ed is None:
            # Die Normalkraft des ersten Falls -- ohne Fall N = 0.
            n_ed = (befund.ergebnisse[0].fall.N_Ed.in_einheit(KN)
                    if befund.ergebnisse else 0.0)
        kurve = befund.kurve(si(n_ed, KN))

        kurven[kennung] = {
            "querschnitt": teil.kennung,
            "namensraum": teil.raum,
            "name": teil.name,
            "richtung": nachweis.richtung.value,
            "N_Ed": n_ed,
            # Wie der Momentenwiderstand heisst: m_Rd, oder m_Rk, wenn die
            # Tragsicherheit mit charakteristischen Werten rechnet.
            "m_name": f"m_{nachweis.mn.wahl.index}",
            "aeste": [
                {
                    "moment_positiv": ast["moment_positiv"],
                    "m_Rd": zahl(ast["m_Rd"], KNM),
                    "d": zahl(ast["d"], MM),
                    "punkte": [
                        {"M_Ed": zahl(M, KNM), "v_Rd": zahl(v, KN_PRO_M), "plastisch": pl}
                        for M, v, pl in ast["punkte"]
                    ],
                }
                for ast in kurve["aeste"]
            ],
            # Moment vorzeichenbehaftet -- der Fall gehoert auf die Seite, auf
            # der er wirkt. Die Querkraft dagegen als Betrag: ihr Vorzeichen
            # spielt keine Rolle, gerechnet wird ohnehin mit |V_Ed|.
            "faelle": [
                {
                    "name": erg.fall.name,
                    "M_Ed": erg.fall.M_Ed.in_einheit(KNM),
                    "N_Ed": erg.fall.N_Ed.in_einheit(KN),
                    "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                    "v_Rd": zahl(erg.v_Rd, KN_PRO_M),
                    "erfuellt": erg.erfuellt,
                    "plastisch": erg.plastisch,
                    "begruendung": erg.begruendung,
                }
                for erg in befund.ergebnisse
            ],
        }
    return kurven


#: Wie weit die Neigungskurve mindestens reicht, in Grad. Die beiden Grenzen
#: des Benutzers liegen normalerweise darin; gehen sie darueber hinaus, waechst
#: die Achse mit -- ein abgeschnittener Ast waere schlimmer als eine breite
#: Achse.
NEIGUNG_VON = 25
NEIGUNG_BIS = 45


def neigungskurven(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Der Querkraftwiderstand ueber der Neigung der Druckdiagonalen.

    Nur wo Buegel liegen -- sonst haengt der Widerstand am Moment und das
    andere Diagramm gilt.

    **Ein Bild je statischer Hoehe und Neigungsbereich.** Beides haengt am
    einzelnen Fall: ``d`` am Vorzeichen des Moments, der Bereich am Vorzeichen
    der Normalkraft. Faelle, die darin uebereinstimmen, liegen auf derselben
    Kurve und kommen ins selbe Bild; die anderen bekommen ihr eigenes.

    Gezeichnet wird ueber den ganzen Achsenbereich, auch ausserhalb der beiden
    Grenzen -- dort blass. Die Oberflaeche entscheidet das an ``gewaehlt``,
    gerechnet wird beides hier.
    """
    kurven: Dict[str, Any] = {}

    for kennung, nachweis in aufbau.feld("querkraft").items():
        befund = loesung.befunde.get(nachweis.id)
        if nachweis.buegel is None or befund is None:
            continue
        teil = aufbau.bauteil_von(nachweis)

        # Nach (statischer Hoehe, Grenzen) gruppieren -- in dieser Reihenfolge
        # gefunden, damit die Bilder in der Reihenfolge der Faelle stehen.
        # Ohne Fall der Ast ohne Einwirkung: ein Bild ohne Punkt darauf.
        gruppen: Dict[tuple, List[Any]] = {}
        for erg in befund.ergebnisse or [befund.ohne_einwirkung]:
            if erg is None or erg.massgebend is None:
                continue
            gruppen.setdefault(
                (round(erg.d, 9), erg.alpha_min, erg.alpha_max), []).append(erg)

        for nummer, ((d, a_min, a_max), gruppe) in enumerate(gruppen.items(), start=1):
            von = min(NEIGUNG_VON, a_min)
            bis = max(NEIGUNG_BIS, a_max)
            punkte = befund.neigungsverlauf(d, von, bis)
            kurven[f"{kennung}.{nummer}"] = {
                "querschnitt": teil.kennung,
                "namensraum": teil.raum,
                "name": teil.name,
                "richtung": nachweis.richtung.value,
                "d": zahl(d, MM),
                "alpha_min": a_min,
                "alpha_max": a_max,
                "zug": gruppe[0].zug_hebt_alpha,
                "punkte": [
                    {"alpha": q.alpha,
                     "V_Rd_s": zahl(q.V_Rd_s, KN_PRO_M),
                     "V_Rd_c": zahl(q.V_Rd_c, KN_PRO_M),
                     "V_Rd": zahl(q.V_Rd, KN_PRO_M),
                     "im_bereich": a_min <= q.alpha <= a_max}
                    for q in punkte
                ],
                "faelle": [
                    {
                        "name": erg.fall.name,
                        "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                        "alpha": erg.massgebend.alpha,
                        "V_Rd": zahl(erg.v_Rd, KN_PRO_M),
                        "erfuellt": erg.erfuellt,
                        "begruendung": erg.begruendung,
                    }
                    for erg in gruppe if erg is not befund.ohne_einwirkung
                ],
            }
    return kurven


def _bild_dict(bild) -> dict:
    """Ein Querschnittsbild in Zeichengroessen: mm, Promille, N/mm², kN."""
    return {
        "eps_m": zahl(bild.eps_m, PROMILLE), "chi": bild.chi,
        "N": zahl(bild.N, KN), "M": zahl(bild.M, KNM),
        "h": zahl(bild.h, MM),
        "nulllinie": zahl(bild.nulllinie, MM),
        "beton": [{"z": zahl(f.z, MM), "eps": zahl(f.eps, PROMILLE),
                   "sigma": zahl(f.sigma, N_PRO_MM2)}
                  for f in bild.beton],
        "stahl": [{"z": zahl(s.z, MM), "eps": zahl(s.eps, PROMILLE),
                   "sigma": zahl(s.sigma, N_PRO_MM2), "nummer": s.nummer, "name": s.name,
                   "a_s": zahl(s.a_s, MM2), "kraft": zahl(s.kraft, KN)}
                  for s in bild.stahl],
        "konvergiert": bild.konvergiert, "hinweis": bild.hinweis,
    }


def spannungsanalysen(aufbau: Aufbau, loesung: Loesung, *,
                      nur: Optional[Collection[str]] = None) -> dict:
    """
    Die Auswertungen am Querschnitt, je Platte und je gezeichnetem Querschnitt
    -- fertig zum Zeichnen; mit ``nur`` die dieser Bauteile.

    Gerechnet wird in :func:`opencivil.spannungsanalyse.analysen`; hier wird
    nur in Zeichengroessen abgebildet.
    """
    return {kennung: [_analyse_dict(a) for a in liste]
            for kennung, liste in spannungsanalyse.analysen(aufbau, loesung, nur=nur).items()}


def _analyse_dict(analyse) -> dict:
    kopf = {"name": analyse.fall.name, "art": analyse.art.value,
            "richtung": analyse.richtung.value, "richtung_text": analyse.richtung_text,
            "titel": analyse.art.beschriftung}
    if not analyse.moeglich:
        return {**kopf, "moeglich": False, "hinweis": analyse.hinweis}
    paar = analyse.paar
    # Wo die Mitteldehnung gilt -- an der Achse der N-eps-Linie.
    kopf["bezugsort"] = paar.bezugsort
    # Womit gerechnet wurde, beim Bild angeschrieben -- und wie ein Widerstand
    # darum heisst: R_d oder R_k sagt der Kern, nicht die Oberflaeche.
    wahl = paar.wahl
    kopf["wahl"] = {"phi": wahl.kriechzahl, "satz": wahl.satz.value,
                    "rechenart": wahl.art.value, "index": wahl.index}
    if isinstance(analyse.kurve, spannungsanalyse.Modullinie):
        return {**kopf, "moeglich": True, "kurve": _modul_dict(analyse.kurve)}
    if analyse.kurve is not None:
        return {**kopf, "moeglich": True, "kurve": _linie_dict(analyse.kurve)}
    return {**kopf, "moeglich": True, "bild": _bild_dict(analyse.bild)}


#: Was eine Linie zeigt, je Art ihrer Linie: die laufende Kraft, die
#: festgehaltene und die Verformung. Massstab und Beschriftung an einer
#: Stelle -- bis 2026-10-18 skalierte der Kern hier, und spannungsbild.js
#: schrieb Zeichen und Einheiten ein zweites Mal daneben (LINIEN, MODULE).
_LINIENGROESSEN: Dict[Any, Tuple[Anzeigegroesse, Anzeigegroesse, Anzeigegroesse]] = {
    spannungsanalyse.Analyseart.MOMENT_KRUEMMUNG: (
        Anzeigegroesse("M", KNM), Anzeigegroesse("N", KN), Anzeigegroesse("χ", PRO_M, r"\chi", 4)),
    spannungsanalyse.Analyseart.NORMALKRAFT_DEHNUNG: (
        Anzeigegroesse("N", KN), Anzeigegroesse("M", KNM),
        Anzeigegroesse("ε_m", PROMILLE, r"\varepsilon_{m}", 2, am_bezugsort=True)),
}

#: Der aequivalente Modul, ueber der laufenden Kraft.
_MODUL = Anzeigegroesse("E_eq", N_PRO_MM2, "E_{eq}", 0)


def liniengroessen(art) -> Optional[dict]:
    """
    Was die Linie einer Frage zeigt -- Kraft, Festgehaltenes, Verformung --,
    wie es in ihren Daten steht; ``None`` fuer die beiden Bilder. Fuer den
    Katalog: die Maske nennt damit, wie weit eine Linie laeuft.
    """
    if art.linie is None:
        return None
    kraft, fest, verformung = _LINIENGROESSEN[art.linie]
    return {"kraft": kraft.als_dict(), "fest": fest.als_dict(),
            "verformung": verformung.als_dict()}

#: Die Randdehnungen beim Bruch.
_RANDDEHNUNG = Anzeigegroesse("ε", PROMILLE, r"\varepsilon", 2)


def _linie_dict(linie) -> dict:
    """
    Eine Linie in Zeichengroessen: die Kraft in kNm bzw. kN, die Verformung
    als Kruemmung in 1/m bzw. als Dehnung in Promille -- und unter
    ``groessen`` Zeichen und Einheit dazu (:data:`_LINIENGROESSEN`).
    """
    kraft, fest, verformung = _LINIENGROESSEN[linie.art.linie]
    v = verformung.zahl

    def eck(e) -> Optional[dict]:
        return None if e is None else {"kraft": kraft.zahl(e.kraft), "verformung": v(e.verformung)}

    sprung = linie.sprung
    bruch = linie.bruch
    return {
        "groessen": liniengroessen(linie.art),
        "fest": fest.zahl(linie.fest), "riss": kraft.zahl(linie.riss),
        "punkte": [{"kraft": kraft.zahl(p.kraft), "verformung": v(p.verformung),
                    "gerissen": p.gerissen, "verformung_I": v(p.verformung_I),
                    "verformung_II": v(p.verformung_II)}
                   for p in linie.punkte],
        # Der Sprung beim Reissen: dieselbe Kraft, zwei Verformungen.
        "sprung": (None if sprung is None else
                   {"kraft": kraft.zahl(sprung[0].kraft), "vor": v(sprung[0].verformung),
                    "nach": v(sprung[1].verformung)}),
        "fliessen": eck(linie.fliessen),
        "bruch": (None if bruch is None else
                  {**eck(bruch), "eps_oben": _RANDDEHNUNG.zahl(bruch.eps_oben),
                   "eps_unten": _RANDDEHNUNG.zahl(bruch.eps_unten),
                   "massgebend": bruch.massgebend}),
        "tragfaehig": linie.tragfaehig,
        "hinweis": linie.hinweis,
    }


def _modul_dict(modul) -> dict:
    """
    Der aequivalente E-Modul in Zeichengroessen: die laufende Kraft in kNm
    bzw. kN, der Modul in N/mm², dazu E_cm, an dem er sich misst -- und
    sein Vielfaches von E_cm, wo er angeschrieben wird: je Punkt daneben, an
    den Ecken mit ihm (``{"wert", "vielfaches"}``). Gerechnet ist alles im
    Kern (:class:`~opencivil.spannungsanalyse.Modullinie`); bis 2026-10-18
    teilte die Oberflaeche selbst durch E_cm.
    """
    linie = modul.linie
    kraft, fest, _ = _LINIENGROESSEN[linie.art.linie]
    E = _MODUL.zahl

    def vielfaches(x: Optional[float]) -> Optional[float]:
        return None if x is None else x / modul.E_cm

    def angeschrieben(x: Optional[float]) -> Optional[dict]:
        """Ein Modul an einer Ecke, mit seinem Vielfachen von E_cm."""
        return None if x is None else {"wert": E(x), "vielfaches": vielfaches(x)}

    sprung = linie.sprung
    return {
        "groessen": {"kraft": kraft.als_dict(), "fest": fest.als_dict(), "modul": _MODUL.als_dict()},
        "fest": fest.zahl(linie.fest), "riss": kraft.zahl(linie.riss), "E_cm": E(modul.E_cm),
        "punkte": [{"kraft": kraft.zahl(p.kraft), "modul": E(p.modul),
                    "vielfaches": vielfaches(p.modul), "gerissen": p.gerissen,
                    "modul_I": E(p.modul_I), "modul_II": E(p.modul_II)}
                   for p in modul.punkte],
        # Der Sprung beim Reissen: dieselbe Kraft, zwei Moduln.
        "sprung": (None if sprung is None else
                   {"kraft": kraft.zahl(sprung[0].kraft),
                    "vor": angeschrieben(modul.modul(sprung[0].kraft, sprung[0].verformung)),
                    "nach": angeschrieben(modul.riss)}),
        "fliessen": (None if linie.fliessen is None else
                     {"kraft": kraft.zahl(linie.fliessen.kraft),
                      "modul": angeschrieben(modul.fliessen)}),
        "bruch": (None if linie.bruch is None else
                  {"kraft": kraft.zahl(linie.bruch.kraft), "modul": angeschrieben(modul.ende),
                   "massgebend": linie.bruch.massgebend}),
        "tragfaehig": linie.tragfaehig,
        "hinweis": linie.hinweis,
    }


def werkstoffgesetze(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Punktfolgen der Spannungs-Dehnungs-Beziehungen, je Material.

    Gerechnet wird mit denselben Gesetzen wie im Nachweis -- die Kurve zeigt
    also genau das, was der Querschnittsintegration zugrunde liegt, und nicht
    eine zweite, nachgebaute Fassung.

    Vorzeichen wie im ganzen Werkzeug: Zug positiv. Der Beton liegt damit im
    dritten Quadranten, der Stahl spannt sich ueber beide.
    """
    ergebnis: Dict[str, dict] = {}

    for kennung, stoff in aufbau.baustoffe.items():
        def wert(kurzname: str) -> Optional[float]:
            eintrag = loesung.werte.get(stoff.definitionen[kurzname].id)
            return eintrag.groesse.si if eintrag else None

        try:
            if stoff.art.value == "beton":
                eintrag = _betonkurve(stoff, wert)
            else:
                eintrag = _stahlkurve(stoff, wert)
        except (KeyError, TypeError):
            continue  # Kennwerte noch nicht gerechnet
        if eintrag:
            eintrag["name"] = stoff.name
            eintrag["art"] = stoff.art.value
            ergebnis[kennung] = eintrag
    return ergebnis


def _betonkurve(stoff, wert, schritte: int = 80) -> Optional[dict]:
    """
    Parabel-Rechteck-Beziehung, von null bis zur Bruchdehnung -- mit
    Bemessungswerten, ohne Kriechen, gebaut wie in jeder Rechnung: der
    Beiwert aus ``E_cm`` (:meth:`Betongesetz.mit_modul`).
    """
    from opencivil.querschnitt.werkstoffgesetz import Betongesetz

    f_cd, eps_c1d = wert("f_cd"), wert("eps_c1d")
    eps_c2d, E_cm = wert("eps_c2d"), wert("E_cm")
    if None in (f_cd, eps_c1d, eps_c2d, E_cm):
        return None

    gesetz = Betongesetz.mit_modul(f_c=abs(f_cd), E_c=abs(E_cm), eps_c1d=abs(eps_c1d),
                                   eps_c2d=abs(eps_c2d))
    punkte = []
    for i in range(schritte + 1):
        eps = -abs(eps_c2d) * i / schritte
        punkte.append({"eps": zahl(eps, PROMILLE), "sigma": zahl(gesetz.spannung(eps), N_PRO_MM2)})

    return {
        "punkte": punkte,
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Beton – Parabel-Rechteck-Beziehung",
        "referenz": "SIA 262:2025, 4.2.1.5, Figur 12; 4.2.1.6, (27)",
        "marken": [
            {"eps": zahl(-abs(eps_c1d), PROMILLE), "sigma": zahl(-abs(f_cd), N_PRO_MM2),
             "text": "ε_c1d"},
            {"eps": zahl(-abs(eps_c2d), PROMILLE), "sigma": zahl(-abs(f_cd), N_PRO_MM2),
             "text": "ε_c2d"},
        ],
        "vereinfacht": _spannungsblock(abs(f_cd), abs(eps_c2d)),
    }


def _spannungsblock(f_cd: float, eps_c2d: float) -> dict:
    """
    Der vereinfachte, rechteckige Spannungsverlauf.

    Unterhalb von ``(1 - 0.85) * eps_c2d`` wird keine Spannung angesetzt,
    darueber durchgehend ``f_cd``. Das ist dieselbe Vereinfachung, die auch der
    Handrechnung zugrunde liegt -- dort als Druckzone der Hoehe ``0.85 x``.
    Beide Bilder gehoeren zusammen, und genau deshalb steht die Stufe hier neben
    der Parabel: man sieht, was man aufgibt, wenn man von Hand rechnet.
    """
    block = Spannungsblock(f_cd=f_cd, eps_c2d=eps_c2d)
    ecken = [
        (0.0, 0.0),
        (-block.eps_knick, 0.0),
        (-block.eps_knick, -block.f_cd),
        (-eps_c2d, -block.f_cd),
    ]
    return {
        "punkte": [{"eps": zahl(e, PROMILLE), "sigma": zahl(s, N_PRO_MM2)} for e, s in ecken],
        "titel": "vereinfacht (Spannungsblock)",
        "beschreibung": (
            f"σ = 0 bis {1 - BLOCKANTEIL:.2f}·ε_c2d, darüber f_cd. "
            f"Entspricht der Druckzone {BLOCKANTEIL}·x der Handrechnung."
        ),
    }


def _stahlkurve(stoff, wert) -> Optional[dict]:
    """
    Bilineare Beziehung ohne Verfestigung.

    Fuenf Eckpunkte genuegen -- dazwischen ist sie gerade, und mehr Punkte
    wuerden nur vortaeuschen, dass etwas gekruemmt waere.
    """
    E_s, f_yd = wert("E_s"), wert("f_yd")
    f_yd_druck, eps_ud = wert("f_yd_druck"), wert("eps_ud")
    if None in (E_s, f_yd, f_yd_druck, eps_ud):
        return None

    eps_yd, eps_yd_druck = f_yd / E_s, abs(f_yd_druck) / E_s
    ecken = [
        (-abs(eps_ud), -abs(f_yd_druck)),
        (-eps_yd_druck, -abs(f_yd_druck)),
        (0.0, 0.0),
        (eps_yd, f_yd),
        (abs(eps_ud), f_yd),
    ]
    return {
        "punkte": [{"eps": zahl(e, PROMILLE), "sigma": zahl(s, N_PRO_MM2)} for e, s in ecken],
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Betonstahl – bilineare Beziehung",
        "referenz": "SIA 262:2025, 4.2.2.2, Figur 16",
        "marken": [
            {"eps": zahl(eps_yd, PROMILLE), "sigma": zahl(f_yd, N_PRO_MM2), "text": "ε_yd"},
            {"eps": zahl(abs(eps_ud), PROMILLE), "sigma": zahl(f_yd, N_PRO_MM2), "text": "ε_ud"},
        ],
    }


def _knickpunkte(aufbau, nachweis, loesung) -> list:
    """
    Die Knicknachweise als Punktepaare fuer das M-N-Diagramm.

    Zu jedem Fall zwei Punkte auf derselben Hoehe N_Ed: das Moment 1. Ordnung
    und das am verformten System. Die Strecke dazwischen ist der Zuwachs aus
    Schiefstellung und Verformung -- im Diagramm sieht man sofort, ob er den
    Punkt ueber die Linie schiebt.

    Nur in x-Richtung, denn nur dort gibt es einen Knicknachweis.
    """
    knicken = _knicken(aufbau, nachweis)
    befund = loesung.befunde.get(knicken.id) if knicken is not None else None
    if befund is None:
        return []
    punkte = []
    for erg in befund.ergebnisse:
        if erg.fall.N_Ed.si >= 0.0:
            continue
        punkte.append({
            "name": erg.fall.name,
            "N_Ed": erg.fall.N_Ed.in_einheit(KN),
            "M_Ed_1": abs(erg.fall.M_Ed_1.in_einheit(KNM)),
            "M_Ed_II": zahl(abs(erg.M_ges), KNM),
            "N_Rd": zahl(erg.N_Rd, KN),
            "M_bei_N_Rd": zahl(erg.M_bei_N_Rd, KNM),
            "erfuellungsgrad": erg.erfuellungsgrad,
            "grad_text": grad_als_text(erg.erfuellungsgrad, erg.erfuellt),
            "erfuellt": erg.erfuellt,
            "stabil": erg.stabil,
            "begruendung": erg.begruendung,
        })
    return punkte


def _knicken(aufbau, nachweis):
    """Der Knicknachweis zu diesem M-N-Nachweis -- nur in x, nur wenn es ihn gibt."""
    if aufbau is None or nachweis.richtung is not Richtung.X:
        return None
    knicken = aufbau.bauteil_von(nachweis).im_feld("knicken")
    return knicken[0] if knicken else None


def _linienzug(linie) -> Optional[dict]:
    """
    Eine Resistenzlinie zum Zeichnen. ``ecken``: ob ihre Punkte Eckpunkte mit
    Namen sind -- beim Polygon der Handrechnung --, oder Stuetzstellen eines
    Randes, die man nicht einzeln markiert.
    """
    if linie is None:
        return None
    ecken = isinstance(linie, Handlinie)
    return {
        "beschriftung": linie.beschriftung,
        "ecken": ecken,
        "punkte": [{"N": zahl(p.N, KN), "M": zahl(p.M, KNM),
                    **({"name": p.name} if ecken else {})}
                   for p in linie.punkte],
    }


def linie(nachweis, loesung: Loesung, aufbau=None) -> dict:
    """
    Die M-N-Interaktionslinien zum Zeichnen -- in kN und kNm.

    Die massgebende Linie, gegen die nachgewiesen wird, und daneben die zum
    Vergleich: die Parabel neben der Handrechnung, sonst die Handrechnung.
    So sieht man, was die gewaehlte Rechenart gegenueber der anderen kostet
    oder bringt.
    """
    befund = loesung.befund(nachweis)
    knicken = _knicken(aufbau, nachweis)
    knickbefund = loesung.befunde.get(knicken.id) if knicken is not None else None
    return {
        "richtung": nachweis.richtung.value,
        "querschnitt": nachweis.querschnitt.name,
        "massgebend": _linienzug(befund.massgebend),
        "vergleich": _linienzug(befund.vergleich),
        # Waehlt das Knicken fuer seinen Widerstand anders als die
        # Tragsicherheit, liegen seine Punkte auf seiner eigenen Linie.
        "knicklinie": _linienzug(knickbefund.linie if knickbefund is not None
                                 and knicken.eigene_linie else None),
        "kombinationen": [
            {
                "name": a.schnittgroessen.name,
                "M_Ed": a.schnittgroessen.M_Ed.in_einheit(KNM),
                "N_Ed": a.schnittgroessen.N_Ed.in_einheit(KN),
                "art": a.schnittgroessen.art.value,
                "art_text": a.schnittgroessen.art.beschriftung,
                "innerhalb": a.innerhalb,
                "erfuellungsgrad": a.erfuellungsgrad,
                "grad_text": grad_als_text(a.erfuellungsgrad, a.erfuellt),
                "groesse": a.achse.name,
                "massstab": a.massstab.value,
                "massstab_text": a.massstab.beschriftung,
                "widerstand": (
                    {"N": zahl(a.widerstand[0], KN), "M": zahl(a.widerstand[1], KNM)}
                    if a.widerstand
                    else None
                ),
                "begruendung": a.begruendung,
            }
            for a in befund.auswertungen
        ],
        # Die Knickfaelle gehoeren in dasselbe Bild: sie tragen dieselbe
        # Normalkraft gegen dieselbe Linie, nur mit einem groesseren Moment.
        "knickfaelle": _knickpunkte(aufbau, nachweis, loesung) if aufbau else [],
    }


# ===========================================================================
# Querschnittsanalyse
# ===========================================================================

Punkt = Tuple[float, float]


def analyse(aufbau: Aufbau, loesung: Loesung, kennung: str,
            schnitt: Tuple[str, float] = ("M_z", 0.0)) -> dict:
    """
    Die Diagramme einer Querschnittsanalyse -- in mm, kN und kNm.

    Das Interaktionsdiagramm: die Flaeche aller Bruchzustaende, geschnitten
    bei ``schnitt`` -- der festen Groesse (N, M_y oder M_z) und ihrem Wert in
    kN bzw. kNm. Welche beiden anderen auf welcher Achse stehen, waehlt die
    Oberflaeche; die Punkte tragen alle drei. Es ist das einzige
    Interaktionsdiagramm der Analyse: je Lastfall stehen darin seine
    Einwirkung und der Widerstand seines Nachweises, ebenfalls mit allen
    drei Groessen.

    Je Lastfall ausserdem der Bruchzustand im Schnitt (Nulllinie, Druckzone,
    die Dehnung jedes Stabs) und der Schubfluss in den Waenden. Was die
    Nachweise schon wissen, kommt aus ihren Befunden in ``loesung``; neu
    gerechnet wird nur die Flaeche, nach der kein Nachweis fragt -- an
    demselben Querschnitt.

    Die Einwirkung steht so da, wie nachgewiesen: mit der Laengszugkraft aus
    Querkraft und Torsion, wo sie zugeschaltet ist.
    """
    bauteil = aufbau.querschnittsanalysen[kennung]
    biegung = aufbau.feld("qa_biegung").get(kennung)
    schub = aufbau.feld("qa_schub").get(kennung)
    # Ohne Befund lief der Nachweis nicht -- etwa, weil ein Baustoff fehlt.
    gebogen = loesung.befunde.get(biegung.id) if biegung is not None else None
    geschoben = loesung.befunde.get(schub.id) if schub is not None else None
    q = gebogen.querschnitt if gebogen is not None else None

    faelle = []
    for erg in (gebogen.ergebnisse if gebogen is not None else []):
        p = erg.punkt
        faelle.append({
            "name": erg.fall.name,
            "N_Ed": zahl(erg.N, KN),
            "M_y_Ed": zahl(erg.M_y, KNM),
            "M_z_Ed": zahl(erg.M_z, KNM),
            "erfuellt": erg.erfuellt,
            "grad_text": grad_als_text(erg.erfuellungsgrad, erg.erfuellt),
            # Der Bruchzustand, gegen den der Nachweis misst -- bei N_Ed, in
            # der Richtung des Moments. Ohne Moment gibt es keinen.
            "widerstand": None if p is None else _als_kn([(p.N, p.M_y, p.M_z)])[0],
            "bruch": _bruch(q, bauteil, p) if p is not None else None,
            "schub": _schubfluss(geschoben, erg.fall) if geschoben is not None else None,
        })
    einachsig = bauteil.biegung.einachsig
    return {
        "kennung": kennung,
        "name": bauteil.name,
        "einachsig": einachsig,
        "laengszug": biegung is not None and biegung.laengszug is not None,
        "zeichnung": _zeichnung(bauteil),
        "interaktion": _interaktion(q, einachsig, *schnitt) if q is not None else None,
        "faelle": faelle,
    }


def _als_kn(punkte) -> List[dict]:
    """Punkte ``(N, M_y, M_z)`` in N und Nm -- fuer die Oberflaeche in kN und kNm."""
    return [{"N": zahl(N, KN), "M_y": zahl(M_y, KNM), "M_z": zahl(M_z, KNM)}
            for N, M_y, M_z in punkte]


def _faecherpaar(q, psi: float):
    """Der Faecher bei ψ und der gegenueber -- zusammen eine geschlossene Linie."""
    return q.faecher(psi) + list(reversed(q.faecher(psi + math.pi)))


def _interaktion(q, einachsig: bool, fest: str, wert: float) -> dict:
    """
    Das Interaktionsdiagramm der Analyse: die Flaeche der Bruchzustaende,
    geschnitten bei ``fest = wert`` (kN bzw. kNm).

    Einachsig gibt es nur die Linie um y: die Nulllinie bleibt waagrecht,
    und das M_z, das ein unsymmetrischer Querschnitt dabei weckt, zaehlt
    nicht -- dieselben Faecher wie im Nachweis.
    """
    if einachsig:
        return {"fest": None, "wert": None,
                "punkte": _als_kn((p.N, p.M_y, p.M_z) for p in _faecherpaar(q, -math.pi / 2.0))}
    return {"fest": fest, "wert": wert,
            "punkte": _als_kn(q.schnitt(fest, si(wert, KN if fest == "N" else KNM)))}


def _tiefe(eltern: Sequence[Optional[int]], i: int) -> int:
    """Wie oft ein Polygon in einem anderen liegt -- Eltern werden zuerst gezeichnet."""
    t, j = 0, eltern[i]
    while j is not None:
        t, j = t + 1, eltern[j]
    return t


def _zeichnung(bauteil) -> dict:
    """Was im Schnitt zu sehen ist, in mm -- die Stäbe der Linien schon aufgeloest."""
    return {
        "polygone": [
            {"punkte": [list(p) for p in f.punkte], "material": f.stoff is not None,
             "tiefe": _tiefe(bauteil.eltern, i)}
            for i, f in enumerate(bauteil.flaechen)],
        "staebe": [{"y": p[0], "z": p[1], "d": g.durchmesser}
                   for g in bauteil.bewehrungselemente for p in g.punkte],
        "flaechenlinien": [{"von": list(g.von), "bis": list(g.bis)}
                           for g in bauteil.bewehrungselemente if g.verschmiert],
        "waende": [{"name": w.name, "von": list(w.von), "bis": list(w.bis), "dicke": w.dicke}
                   for w in bauteil.waende],
        "schwerpunkt": [bauteil.brutto.y_S, bauteil.brutto.z_S],
    }


def _halbebene(punkte: Sequence[Punkt], innen: Callable[[Punkt], float]) -> List[List[float]]:
    """
    Das Stueck eines Polygons, auf dem ``innen(p) <= 0`` gilt -- nach
    Sutherland und Hodgman, gegen eine einzige Gerade.
    """
    aus: List[List[float]] = []
    for i, p in enumerate(punkte):
        q = punkte[(i + 1) % len(punkte)]
        a, b = innen(p), innen(q)
        if a <= 0.0:
            aus.append([p[0], p[1]])
        if (a <= 0.0) != (b <= 0.0):
            t = a / (a - b)
            aus.append([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])])
    return aus if len(aus) >= 3 else []


def _gerade_im_rahmen(stuetz: Punkt, richtung: Punkt,
                      rahmen: Tuple[float, float, float, float]) -> Optional[List[List[float]]]:
    """Das Stueck der Geraden ``stuetz + s·richtung``, das im Rahmen liegt (Liang-Barsky)."""
    y0, y1, z0, z1 = rahmen
    von, bis = -math.inf, math.inf
    for d, a, unten, oben in ((richtung[0], stuetz[0], y0, y1), (richtung[1], stuetz[1], z0, z1)):
        if abs(d) < 1e-12:
            if not unten <= a <= oben:
                return None
            continue
        s1, s2 = (unten - a) / d, (oben - a) / d
        von, bis = max(von, min(s1, s2)), min(bis, max(s1, s2))
    if von >= bis:
        return None
    return [[stuetz[0] + von * richtung[0], stuetz[1] + von * richtung[1]],
            [stuetz[0] + bis * richtung[0], stuetz[1] + bis * richtung[1]]]


def _bruch(q, bauteil, punkt) -> dict:
    """
    Der Bruchzustand im Schnitt: die Nulllinie, die gedrueckte Flaeche je
    Polygon und die Dehnung jedes Stabs -- in mm und ‰.

    Gedrueckt ist die Seite kleiner v: die Kruemmung zeigt nie gegen die
    Zugrichtung. Ohne Kruemmung ist alles gedrueckt oder nichts.
    """
    sy, sz = zahl(q.bezug[0], MM), zahl(q.bezug[1], MM)
    n = punkt.zugrichtung
    punkte = [p for f in bauteil.flaechen for p in f.punkte]
    rahmen = (min(p[0] for p in punkte), max(p[0] for p in punkte),
              min(p[1] for p in punkte), max(p[1] for p in punkte))

    def v(p: Punkt) -> float:
        return n[0] * (p[0] - sy) + n[1] * (p[1] - sz)

    if punkt.chi > 0.0:
        v0 = zahl(-punkt.eps_m / punkt.chi, MM)
        nulllinie = _gerade_im_rahmen((sy + v0 * n[0], sz + v0 * n[1]), (-n[1], n[0]), rahmen)
        druckzone = [_halbebene(f.punkte, lambda p, v0=v0: v(p) - v0) for f in bauteil.flaechen]
    else:
        nulllinie = None
        druckzone = [[list(p) for p in f.punkte] if punkt.eps_m < 0.0 else []
                     for f in bauteil.flaechen]
    x, d = q.druckzone(punkt)
    return {
        "nulllinie": nulllinie,
        "druckzone": [
            {"punkte": zone, "material": f.stoff is not None,
             "tiefe": _tiefe(bauteil.eltern, i)}
            for i, (f, zone) in enumerate(zip(bauteil.flaechen, druckzone)) if zone],
        "staebe": [
            {"y": p[0], "z": p[1], "d": g.durchmesser,
             "eps": zahl(q.dehnung(punkt, (si(p[0], MM), si(p[1], MM))), PROMILLE)}
            for g in bauteil.bewehrungselemente for p in g.punkte],
        "x": zahl(x, MM),
        "d": zahl(d, MM),
        "neigung": math.degrees(punkt.psi),
    }


def _schubfluss(schub: Schubbefund, fall) -> Optional[dict]:
    """
    Der Schubfluss je Stueck einer Wand, mit Vorzeichen entlang der Wand, in
    kN/m -- und je Wand der Widerstand bei der Neigung, die der Nachweis
    gewaehlt hat. Ohne Verteilung (keine Wand, keine Last) nichts.
    """
    v = schub.verteilungen.get(fall.name)
    if v is None:
        return None
    stuecke = [{"wand": schub.waende[s.wand].name,
                "von": [zahl(s.von[0], MM), zahl(s.von[1], MM)],
                "bis": [zahl(s.bis[0], MM), zahl(s.bis[1], MM)],
                "q": zahl(fluss, KN_PRO_M)}
               for s, fluss in zip(schub.modell.stuecke, v.fluss)]
    waende = [{"name": w.name, "q_max": zahl(vergleich.einwirkung.groesse.si, KN_PRO_M),
               "v_Rd": zahl(r.v_Rd, KN_PRO_M), "alpha": r.alpha, "erfuellt": vergleich.erfuellt,
               "grad_text": grad_als_text(vergleich.grad, vergleich.erfuellt)}
              for w, r, vergleich in zip(schub.waende, schub.widerstaende[fall.name],
                                         schub.vergleiche[fall.name])]
    return {"stuecke": stuecke, "waende": waende,
            "zellen": [zahl(q_k, KN_PRO_M) for q_k in v.zellenfluss]}
