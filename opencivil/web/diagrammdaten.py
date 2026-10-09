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
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil import spannungsanalyse
from opencivil.core.berechnung import grad_als_text
from opencivil.core.einheiten import KN, KNM, KN_PRO_M
from opencivil.core.rechenwerk import Loesung
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL, Spannungsblock
from opencivil.nachweis.querkraft import NUR_KURVE
from opencivil.projekt import Aufbau
from opencivil.querschnitt.platte import Richtung


def linien(aufbau: Aufbau) -> dict:
    """Je M-N-Nachweis mit Linie ihre Punkte, dazu die Bemessungs- und Knickpunkte."""
    return {
        kennung: linie(nachweis, aufbau)
        for kennung, nachweis in aufbau.nachweise.items()
        if nachweis.linie
    }


def querkraftkurven(
    aufbau: Aufbau, gewaehlt: Optional[Mapping[str, float]] = None
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

    for kennung, nachweis in aufbau.querkraft.items():
        if not nachweis.ergebnisse:
            continue
        # Mit Buegeln haengt der Widerstand nicht mehr am Moment, sondern an
        # der Neigung der Druckdiagonalen. Dann steht dort das andere Bild --
        # siehe neigungskurven().
        if nachweis.buegel is not None:
            continue
        querschnitt_kennung = kennung.split(".", 1)[0]
        querschnitt = aufbau.querschnitte.get(querschnitt_kennung)

        n_ed = gewaehlt.get(kennung)
        if n_ed is None:
            n_ed = nachweis.ergebnisse[0].fall.N_Ed.in_einheit(KN)
        kurve = nachweis.kurve(n_ed * 1e3)

        kurven[kennung] = {
            "querschnitt": querschnitt_kennung,
            "namensraum": querschnitt.id if querschnitt else "",
            "name": querschnitt.name if querschnitt else querschnitt_kennung,
            "richtung": nachweis.richtung.value,
            "N_Ed": n_ed,
            "aeste": [
                {
                    "moment_positiv": ast["moment_positiv"],
                    "zugseite": "unten" if ast["moment_positiv"] else "oben",
                    "m_Rd": ast["m_Rd"] / 1e3,
                    "d": ast["d"] * 1e3,
                    "punkte": [
                        {"M_Ed": M / 1e3, "v_Rd": v / 1e3, "plastisch": pl}
                        for M, v, pl in ast["punkte"]
                    ],
                }
                for ast in kurve["aeste"]
            ],
            # Moment vorzeichenbehaftet -- der Fall gehoert auf die Seite, auf
            # der er wirkt. Die Querkraft dagegen als Betrag: ihr Vorzeichen
            # spielt keine Rolle, gerechnet wird ohnehin mit |V_Ed|.
            # Der Nullfall ist keine Einwirkung und kein Punkt im Bild.
            "faelle": [
                {
                    "name": erg.fall.name,
                    "M_Ed": erg.fall.M_Ed.in_einheit(KNM),
                    "N_Ed": erg.fall.N_Ed.in_einheit(KN),
                    "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                    "v_Rd": erg.v_Rd / 1e3,
                    "erfuellt": erg.erfuellt,
                    "plastisch": erg.plastisch,
                    "begruendung": erg.begruendung,
                }
                for erg in nachweis.ergebnisse if erg.fall is not NUR_KURVE
            ],
        }
    return kurven


#: Wie weit die Neigungskurve mindestens reicht, in Grad. Die beiden Grenzen
#: des Benutzers liegen normalerweise darin; gehen sie darueber hinaus, waechst
#: die Achse mit -- ein abgeschnittener Ast waere schlimmer als eine breite
#: Achse.
NEIGUNG_VON = 25
NEIGUNG_BIS = 45


def neigungskurven(aufbau: Aufbau) -> dict:
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

    for kennung, nachweis in aufbau.querkraft.items():
        if nachweis.buegel is None or not nachweis.ergebnisse:
            continue
        querschnitt_kennung = kennung.split(".", 1)[0]
        querschnitt = aufbau.querschnitte.get(querschnitt_kennung)

        # Nach (statischer Hoehe, Grenzen) gruppieren -- in dieser Reihenfolge
        # gefunden, damit die Bilder in der Reihenfolge der Faelle stehen.
        gruppen: Dict[tuple, List[Any]] = {}
        for erg in nachweis.ergebnisse:
            if erg.massgebend is None:
                continue
            gruppen.setdefault(
                (round(erg.d, 9), erg.alpha_min, erg.alpha_max), []).append(erg)

        for nummer, ((d, a_min, a_max), gruppe) in enumerate(gruppen.items(), start=1):
            von = min(NEIGUNG_VON, a_min)
            bis = max(NEIGUNG_BIS, a_max)
            punkte = nachweis.neigungsverlauf(d, von, bis)
            kurven[f"{kennung}.{nummer}"] = {
                "querschnitt": querschnitt_kennung,
                "namensraum": querschnitt.id if querschnitt else "",
                "name": querschnitt.name if querschnitt else querschnitt_kennung,
                "richtung": nachweis.richtung.value,
                "d": d * 1e3,
                "alpha_min": a_min,
                "alpha_max": a_max,
                "zug": gruppe[0].zug_hebt_alpha,
                "punkte": [
                    {"alpha": q.alpha,
                     "V_Rd_s": q.V_Rd_s / 1e3,
                     "V_Rd_c": q.V_Rd_c / 1e3,
                     "V_Rd": q.V_Rd / 1e3,
                     "im_bereich": a_min <= q.alpha <= a_max}
                    for q in punkte
                ],
                "faelle": [
                    {
                        "name": erg.fall.name,
                        "V_Ed": abs(erg.fall.V_Ed.in_einheit(KN_PRO_M)),
                        "alpha": erg.massgebend.alpha,
                        "V_Rd": erg.v_Rd / 1e3,
                        "erfuellt": erg.erfuellt,
                        "begruendung": erg.begruendung,
                    }
                    for erg in gruppe if erg.fall is not NUR_KURVE
                ],
            }
    return kurven


def _bild_dict(bild, h: float) -> dict:
    """Ein Querschnittsbild in Zeichengroessen: mm, Promille, N/mm², kN."""
    return {
        "eps_m": bild.eps_m * 1e3, "chi": bild.chi,
        "N": bild.N / 1e3, "M": bild.M / 1e3,
        "h": h * 1e3,
        "nulllinie": (bild.nulllinie * 1e3
                      if bild.nulllinie is not None else None),
        "beton": [{"z": f.z * 1e3, "eps": f.eps * 1e3, "sigma": f.sigma / 1e6}
                  for f in bild.beton],
        "stahl": [{"z": s.z * 1e3, "eps": s.eps * 1e3, "sigma": s.sigma / 1e6,
                   "nummer": s.nummer, "a_s": s.a_s * 1e6, "kraft": s.kraft / 1e3}
                  for s in bild.stahl],
        "konvergiert": bild.konvergiert, "hinweis": bild.hinweis,
    }


def spannungsanalysen(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Die Auswertungen am Querschnitt, je Platte -- fertig zum Zeichnen.

    Gerechnet wird in :func:`opencivil.spannungsanalyse.analysen`; hier wird
    nur in Zeichengroessen abgebildet.
    """
    return {kennung: [_analyse_dict(a) for a in liste]
            for kennung, liste in spannungsanalyse.analysen(aufbau, loesung).items()}


def _analyse_dict(analyse) -> dict:
    kopf = {"name": analyse.fall.name, "art": analyse.art.value,
            "richtung": analyse.richtung.value,
            "titel": analyse.art.beschriftung}
    if not analyse.moeglich:
        return {**kopf, "moeglich": False, "hinweis": analyse.hinweis}
    paar = analyse.paar
    # Womit gerechnet wurde -- die Kriechzahl auch dann, wenn sie die der
    # Platte ist: so steht die Zahl beim Bild, die wirklich galt.
    kopf["wahl"] = {"phi": paar.phi, "phi_eigen": paar.phi_eigen,
                    "satz": paar.satz.value, "gesetz": paar.gesetz}
    if analyse.kurve is not None:
        return {**kopf, "moeglich": True, "kurve": _linie_dict(analyse.kurve)}
    return {**kopf, "moeglich": True, "bild": _bild_dict(analyse.bild, analyse.h)}


def _linie_dict(linie) -> dict:
    """
    Eine Linie in Zeichengroessen: die Kraft in kNm bzw. kN, die Verformung
    als Kruemmung in 1/m bzw. als Dehnung in Promille.
    """
    pro_mille = linie.art is spannungsanalyse.Analyseart.NORMALKRAFT_DEHNUNG
    v = 1e3 if pro_mille else 1.0

    def verformung(x: Optional[float]) -> Optional[float]:
        return None if x is None else x * v

    def eck(e) -> Optional[dict]:
        return None if e is None else {"kraft": e.kraft / 1e3, "verformung": e.verformung * v}

    sprung = linie.sprung
    bruch = linie.bruch
    return {
        "fest": linie.fest / 1e3, "riss": linie.riss / 1e3,
        "punkte": [{"kraft": p.kraft / 1e3, "verformung": p.verformung * v,
                    "gerissen": p.gerissen, "verformung_I": verformung(p.verformung_I),
                    "verformung_II": verformung(p.verformung_II)}
                   for p in linie.punkte],
        # Der Sprung beim Reissen: dieselbe Kraft, zwei Verformungen.
        "sprung": (None if sprung is None else
                   {"kraft": sprung[0].kraft / 1e3, "vor": sprung[0].verformung * v,
                    "nach": sprung[1].verformung * v}),
        "fliessen": eck(linie.fliessen),
        "bruch": (None if bruch is None else
                  {**eck(bruch), "eps_oben": bruch.eps_oben * 1e3,
                   "eps_unten": bruch.eps_unten * 1e3, "massgebend": bruch.massgebend}),
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
    """Parabel-Rechteck-Beziehung, von null bis zur Bruchdehnung."""
    from opencivil.querschnitt.werkstoffgesetz import Betongesetz

    f_cd, eps_c1d = wert("f_cd"), wert("eps_c1d")
    eps_c2d, k_sigma = wert("eps_c2d"), wert("k_sigma")
    if None in (f_cd, eps_c1d, eps_c2d, k_sigma):
        return None

    gesetz = Betongesetz(f_cd=abs(f_cd), eps_c1d=abs(eps_c1d),
                         eps_c2d=abs(eps_c2d), k_sigma=k_sigma)
    punkte = []
    for i in range(schritte + 1):
        eps = -abs(eps_c2d) * i / schritte
        punkte.append({"eps": eps * 1e3, "sigma": gesetz.spannung(eps) / 1e6})

    return {
        "punkte": punkte,
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Beton – Parabel-Rechteck-Beziehung",
        "referenz": "SIA 262:2025, 4.2.1.6",
        "marken": [
            {"eps": -abs(eps_c1d) * 1e3, "sigma": -abs(f_cd) / 1e6, "text": "ε_c1d"},
            {"eps": -abs(eps_c2d) * 1e3, "sigma": -abs(f_cd) / 1e6, "text": "ε_c2d"},
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
        "punkte": [{"eps": e * 1e3, "sigma": s / 1e6} for e, s in ecken],
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
        "punkte": [{"eps": e * 1e3, "sigma": s / 1e6} for e, s in ecken],
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Betonstahl – bilineare Beziehung",
        "referenz": "SIA 262:2025, 4.2.2.4",
        "marken": [
            {"eps": eps_yd * 1e3, "sigma": f_yd / 1e6, "text": "ε_yd"},
            {"eps": abs(eps_ud) * 1e3, "sigma": f_yd / 1e6, "text": "ε_ud"},
        ],
    }


def _knickpunkte(aufbau, nachweis) -> list:
    """
    Die Knicknachweise als Punktepaare fuer das M-N-Diagramm.

    Zu jedem Fall zwei Punkte auf derselben Hoehe N_Ed: das Moment 1. Ordnung
    und das am verformten System. Die Strecke dazwischen ist der Zuwachs aus
    Schiefstellung und Verformung -- im Diagramm sieht man sofort, ob er den
    Punkt ueber die Linie schiebt.

    Nur in x-Richtung, denn nur dort gibt es einen Knicknachweis.
    """
    if nachweis.richtung is not Richtung.X:
        return []
    kennung = nachweis.querschnitt.id.rsplit(".", 1)[-1]
    knicken = (aufbau.knicken or {}).get(kennung)
    if knicken is None:
        return []
    punkte = []
    for erg in knicken.ergebnisse:
        if erg.fall.N_Ed.si >= 0.0:
            continue
        punkte.append({
            "name": erg.fall.name,
            "N_Ed": erg.fall.N_Ed.in_einheit(KN),
            "M_Ed_1": abs(erg.fall.M_Ed_1.in_einheit(KNM)),
            "M_Ed_II": abs(erg.M_ges) / 1e3,
            "N_Rd": erg.N_Rd / 1e3,
            "M_bei_N_Rd": erg.M_bei_N_Rd / 1e3,
            "erfuellungsgrad": erg.erfuellungsgrad,
            "grad_text": grad_als_text(erg.erfuellungsgrad, erg.erfuellt),
            "erfuellt": erg.erfuellt,
            "stabil": erg.stabil,
            "begruendung": erg.begruendung,
        })
    return punkte


def linie(nachweis, aufbau=None) -> dict:
    """
    Die M-N-Interaktionslinien zum Zeichnen -- in kN und kNm.

    Zwei Linien: die genaue aus Dehnungsebenen (``punkte``) und das Polygon aus
    der Handrechnung (``handpunkte``). Nachgewiesen wird gegen das Polygon; die
    genaue Linie steht daneben, damit man sieht, wie viel die Vereinfachung
    kostet.
    """
    return {
        "richtung": nachweis.richtung.value,
        "querschnitt": nachweis.querschnitt.name,
        "punkte": [
            {"N": p.N / 1e3, "M": p.M / 1e3, "abschnitt": p.abschnitt}
            for p in nachweis.linie
        ],
        "handpunkte": [
            {"N": p.N / 1e3, "M": p.M / 1e3, "name": p.name}
            for p in getattr(nachweis, "handlinie", [])
        ],
        "kombinationen": [
            {
                "name": a.schnittgroessen.name,
                "M_Ed": a.schnittgroessen.M_Ed.in_einheit(KNM),
                "N_Ed": a.schnittgroessen.N_Ed.in_einheit(KN),
                "art": a.schnittgroessen.art.value,
                "art_text": a.schnittgroessen.art.beschriftung,
                "innerhalb": a.innerhalb,
                "erfuellungsgrad": a.erfuellungsgrad,
                "grad_text": grad_als_text(a.erfuellungsgrad, a.innerhalb),
                "groesse": a.achse.name,
                "massstab": a.massstab.value,
                "massstab_text": a.massstab.beschriftung,
                "widerstand": (
                    {"N": a.widerstand[0] / 1e3, "M": a.widerstand[1] / 1e3}
                    if a.widerstand
                    else None
                ),
                "begruendung": a.begruendung,
            }
            for a in nachweis.auswertungen
        ],
        # Die Knickfaelle gehoeren in dasselbe Bild: sie tragen dieselbe
        # Normalkraft gegen dieselbe Linie, nur mit einem groesseren Moment.
        "knickfaelle": _knickpunkte(aufbau, nachweis) if aufbau else [],
    }


# ===========================================================================
# Querschnittsanalyse
# ===========================================================================

Punkt = Tuple[float, float]


def analyse(aufbau: Aufbau, kennung: str, schnitt: Tuple[str, float] = ("M_z", 0.0)) -> dict:
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
    Nachweise schon wissen, kommt aus ihren Objekten; neu gerechnet wird nur
    die Flaeche, nach der kein Nachweis fragt -- an demselben Querschnitt.

    Die Einwirkung steht so da, wie nachgewiesen: mit der Laengszugkraft aus
    Querkraft und Torsion, wo sie zugeschaltet ist.
    """
    bauteil = aufbau.querschnittsanalysen[kennung]
    biegung = aufbau.qa_biegung.get(kennung)
    schub = aufbau.qa_schub.get(kennung)
    q = biegung.querschnitt if biegung is not None else None

    faelle = []
    for erg in (biegung.ergebnisse if q is not None else []):
        erfuellt = erg.erfuellungsgrad >= 1.0
        p = erg.punkt
        faelle.append({
            "name": erg.fall.name,
            "N_Ed": erg.N / 1e3,
            "M_y_Ed": erg.M_y / 1e3,
            "M_z_Ed": erg.M_z / 1e3,
            "erfuellt": erfuellt,
            "grad_text": grad_als_text(erg.erfuellungsgrad, erfuellt),
            # Der Bruchzustand, gegen den der Nachweis misst -- bei N_Ed, in
            # der Richtung des Moments. Ohne Moment gibt es keinen.
            "widerstand": None if p is None else _als_kn([(p.N, p.M_y, p.M_z)])[0],
            "bruch": _bruch(q, bauteil, p) if p is not None else None,
            "schub": _schubfluss(schub, erg.fall) if schub is not None else None,
        })
    einachsig = bool(biegung.einachsig) if biegung is not None else False
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
    return [{"N": N / 1e3, "M_y": M_y / 1e3, "M_z": M_z / 1e3} for N, M_y, M_z in punkte]


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
    return {"fest": fest, "wert": wert, "punkte": _als_kn(q.schnitt(fest, wert * 1e3))}


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
                   for g in bauteil.gruppen if g.art != "flaeche" for p in g.punkte],
        "flaechenlinien": [{"von": list(g.von), "bis": list(g.bis)}
                           for g in bauteil.gruppen if g.art == "flaeche"],
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
    sy, sz = q.bezug[0] * 1e3, q.bezug[1] * 1e3
    n = punkt.zugrichtung
    punkte = [p for f in bauteil.flaechen for p in f.punkte]
    rahmen = (min(p[0] for p in punkte), max(p[0] for p in punkte),
              min(p[1] for p in punkte), max(p[1] for p in punkte))

    def v(p: Punkt) -> float:
        return n[0] * (p[0] - sy) + n[1] * (p[1] - sz)

    if punkt.chi > 0.0:
        v0 = -punkt.eps_m / punkt.chi * 1e3
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
             "eps": q.dehnung(punkt, (p[0] * 1e-3, p[1] * 1e-3)) * 1e3}
            for g in bauteil.gruppen if g.art != "flaeche" for p in g.punkte],
        "x": x * 1e3,
        "d": d * 1e3,
        "neigung": math.degrees(punkt.psi),
    }


def _schubfluss(schub, fall) -> Optional[dict]:
    """
    Der Schubfluss je Stueck einer Wand, mit Vorzeichen entlang der Wand, in
    kN/m -- und je Wand der Widerstand bei der Neigung, die der Nachweis
    gewaehlt hat. Ohne Verteilung (keine Wand, keine Last) nichts.
    """
    v = schub.verteilungen.get(fall.name)
    if v is None or schub.modell is None:
        return None
    widerstaende = schub.widerstaende.get(fall.name, [])
    stuecke = [{"wand": schub.waende[s.wand].name,
                "von": [s.von[0] * 1e3, s.von[1] * 1e3],
                "bis": [s.bis[0] * 1e3, s.bis[1] * 1e3],
                "q": fluss / 1e3}
               for s, fluss in zip(schub.modell.stuecke, v.fluss)]
    waende = []
    for i, (w, r) in enumerate(zip(schub.waende, widerstaende)):
        q_max = max((abs(f) for s, f in zip(schub.modell.stuecke, v.fluss) if s.wand == i),
                    default=0.0)
        grad = r.v_Rd / q_max if q_max > 1e-6 else math.inf
        waende.append({"name": w.name, "q_max": q_max / 1e3, "v_Rd": r.v_Rd / 1e3,
                       "alpha": r.alpha, "erfuellt": grad >= 1.0,
                       "grad_text": grad_als_text(grad, grad >= 1.0)})
    return {"stuecke": stuecke, "waende": waende,
            "zellen": [q_k / 1e3 for q_k in v.zellenfluss]}
