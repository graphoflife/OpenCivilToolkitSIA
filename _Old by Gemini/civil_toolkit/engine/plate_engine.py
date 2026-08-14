"""
civil_toolkit/engine/plate_engine.py – Plate cross-section analysis.

RESPONSIBILITY:
Calculates all physical values for a reinforced concrete plate:
geometry, reinforcement layer stacking, sectional forces (M_Rd, N_Rd).
Returns a list of ``sections`` – a declarative description of the
calculation report – with pre-rendered LaTeX strings ready for KaTeX.

USABLE STANDALONE:
    from civil_toolkit.engine.plate_engine import calculate_plate, create_new_plate
    plate  = create_new_plate("Decke 1", materials=[])
    result = calculate_plate(plate, materials)
    for s in result["sections"]:
        print(s["key"], s.get("latex", ""))
"""

from __future__ import annotations

import math
import uuid
from typing import Any, Dict, List, Optional, Tuple

from civil_toolkit.math_engine import MyVar
from civil_toolkit.engine.material_engine import get_material_vars
from civil_toolkit.engine.types import (
    Plate, Layer, RebarDir, ShearConfig, Material, Unit, VarId,
    Direction, Location, PosMode, RebarType, MaterialType,
    ComputedLayer, LayerGroup, LayerItem, StackingResult,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LAYER_COLORS: List[str] = [
    "#3b82f6",  # blue
    "#ef4444",  # red
    "#10b981",  # green
    "#f59e0b",  # orange
    "#8b5cf6",  # purple
    "#ec4899",  # pink
    "#14b8a6",  # teal
    "#6366f1",  # indigo
]

# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def create_new_plate(name: str, materials: Optional[List[Material]] = None) -> Plate:
    """Returns a default plate data object."""
    materials = materials or []
    default_concrete = next(
        (m for m in materials if m.type == MaterialType.CONCRETE and m.is_default),
        next((m for m in materials if m.type == MaterialType.CONCRETE), None),
    )
    return Plate(
        id=str(uuid.uuid4()),
        name=name,
        is_plate_1m=True,
        h_mm=300,
        b_mm=1000,
        concrete_id=default_concrete.id if default_concrete else None,
        D_max=32,
        cover_top=25,
        cover_bottom=25,
        optimal_einlegen_bottom=True,
        optimal_einlegen_top=False,
        shear=ShearConfig(active=False, diam=10, spacing=150, legs=2),
        top_layers=[],
        bottom_layers=[],
    )


def create_new_layer(main_dir: Direction = Direction.X) -> Layer:
    """Returns a default reinforcement layer object."""
    return Layer(
        main_dir=main_dir,
        pos_mode=PosMode.STANDARD,
        clear_dist=0,
        steel_id="",
        x=RebarDir(
            active=(main_dir == Direction.X),
            diam=12 if main_dir == Direction.X else 0,
            type=RebarType.SPACING,
            spacing=150,
            count=0,
        ),
        y=RebarDir(
            active=(main_dir == Direction.Y),
            diam=12 if main_dir == Direction.Y else 0,
            type=RebarType.SPACING,
            spacing=150,
            count=0,
        ),
    )


# ---------------------------------------------------------------------------
# Layer stacking
# ---------------------------------------------------------------------------


def _calculate_layer_stacking(
    layers: List[Layer],
    base_cover: float,
    optimal_einlegen: bool = True,
    base_cover_str: str = "c_{nom}",
    global_num_fn=None,
) -> StackingResult:
    """Port of calculateLayerStacking() from plateEngine.js."""
    if global_num_fn is None:
        global_num_fn = lambda i: i + 1

    computed_by_index: Dict[int, ComputedLayer] = {}
    groups: List[LayerGroup] = []
    current_group: Optional[LayerGroup] = None
    group_index_counter = 0

    for idx, layer in enumerate(layers):
        out_dir = layer.main_dir
        rebar = layer.x if out_dir == Direction.X else layer.y
        if not rebar or rebar.diam <= 0:
            groups.append(LayerGroup(
                main_dir=out_dir, layers=[], max_diam=0, clear_dist=0,
                group_idx=-1, is_dummy=True, dummy_layer=layer, dummy_idx=idx,
            ))
            current_group = None
            continue

        diam = rebar.diam
        item = LayerItem(layer=layer, idx=idx, diam=diam, rebar=rebar, is_zulage=False)

        if layer.pos_mode == PosMode.ZULAGE:
            if current_group and current_group.main_dir == out_dir:
                item.is_zulage = True
                current_group.layers.append(item)
                current_group.max_diam = max(current_group.max_diam, diam)
            else:
                current_group = LayerGroup(
                    main_dir=out_dir,
                    layers=[item],
                    max_diam=diam,
                    clear_dist=layer.clear_dist,
                    group_idx=group_index_counter,
                )
                group_index_counter += 1
                groups.append(current_group)
        else:
            current_group = LayerGroup(
                main_dir=out_dir,
                layers=[item],
                max_diam=diam,
                clear_dist=layer.clear_dist,
                group_idx=group_index_counter,
            )
            group_index_counter += 1
            groups.append(current_group)

    next_env = base_cover
    next_env_str = base_cover_str

    for g in groups:
        if g.is_dummy:
            computed_by_index[g.dummy_idx] = ComputedLayer(
                layer=g.dummy_layer, main_dir=g.dummy_layer.main_dir,
                bottom_edge_dist=next_env, edge_dist_str=next_env_str,
                group_idx=-1, global_num=-1, is_zulage=False,
            )
            g.dummy_layer._computed_dist = next_env
            continue

        g_num = global_num_fn(g.group_idx)
        clear = g.clear_dist
        clear_str = f" + c_{{z,{g_num}}}" if clear > 0 else ""
        group_outer = next_env + clear
        group_outer_str = next_env_str + clear_str
        group_inner = group_outer + g.max_diam
        group_inner_str = group_outer_str + f" + \\diameter_{{max,{g_num}}}"

        for item in g.layers:
            if optimal_einlegen:
                bed = group_outer
                eds = group_outer_str
            else:
                bed = group_inner - item.diam
                label = f"\\diameter_{{zul,{g_num}}}" if item.is_zulage else f"\\diameter_{{{g_num}}}"
                eds = group_inner_str + f" - {label}"
            computed_by_index[item.idx] = ComputedLayer(
                layer=item.layer, main_dir=item.layer.main_dir,
                bottom_edge_dist=bed, edge_dist_str=eds,
                group_idx=g.group_idx, global_num=g_num, is_zulage=item.is_zulage,
            )
            item.layer._computed_dist = bed

        next_env = group_inner
        next_env_str = group_inner_str

    return StackingResult(
        computed_layers=[computed_by_index[i] for i in range(len(layers))],
        total_groups=group_index_counter,
    )


def compute_plate_layers(plate: Plate) -> Dict[Location, List[ComputedLayer]]:
    """Runs layer stacking for bottom and top, assigns colours and global numbers."""
    bot = _calculate_layer_stacking(
        plate.bottom_layers, plate.cover_bottom,
        plate.optimal_einlegen_bottom, "c_{nom,bot}", lambda i: i + 1,
    )
    top_temp = _calculate_layer_stacking(
        plate.top_layers, plate.cover_top,
        plate.optimal_einlegen_top, "c_{nom,top}",
    )
    bg = bot.total_groups
    tg = top_temp.total_groups
    top = _calculate_layer_stacking(
        plate.top_layers, plate.cover_top,
        plate.optimal_einlegen_top, "c_{nom,top}",
        lambda i: bg + tg - i,
    )
    for comp in bot.computed_layers:
        if comp.group_idx == -1:
            continue
        comp.global_num = comp.group_idx + 1
        comp.color = LAYER_COLORS[(comp.global_num - 1) % len(LAYER_COLORS)]
    for comp in top.computed_layers:
        if comp.group_idx == -1:
            continue
        comp.global_num = bg + (tg - comp.group_idx)
        comp.color = LAYER_COLORS[(comp.global_num - 1) % len(LAYER_COLORS)]
    return {Location.BOT: bot.computed_layers, Location.TOP: top.computed_layers}


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------


def calculate_plate(plate: Plate, materials: List[Material]) -> Dict[str, Any]:
    """
    Calculates all structural values for a plate cross-section.

    Returns
    -------
    dict with keys:
      ``vars``     – all MyVar instances keyed by id
      ``sections`` – ordered list of report section dicts (pre-rendered LaTeX)
    """
    vars_: Dict[str, MyVar] = {}

    # Concrete design value
    mat_c = next((m for m in materials if m.id == plate.concrete_id), None)
    if not mat_c or mat_c.type != MaterialType.CONCRETE:
        raise ValueError("Kein Betonmaterial ausgewählt. Bitte weisen Sie der Platte ein gültiges Betonmaterial zu.")

    c_vars = get_material_vars(mat_c)
    if not c_vars or VarId.F_CD not in c_vars or c_vars[VarId.F_CD].value is None:
        raise ValueError(f"Das Betonmaterial '{mat_c.name or 'Unbekannt'}' ist unvollständig definiert (f_cd fehlt).")

    f_cd_val = c_vars[VarId.F_CD].value

    # Geometry
    vars_[VarId.H] = MyVar(id=VarId.H, symbol="h", unit=Unit.MM, description="Plattendicke",
                          value=plate.h_mm, precision=0)
    vars_[VarId.B] = MyVar(id=VarId.B, symbol="b", unit=Unit.MM, description="Plattenbreite",
                          value=plate.b_mm, precision=0)
    vars_[VarId.C_NOM_BOT] = MyVar(id=VarId.C_NOM_BOT, symbol="c_{nom,bot}", unit=Unit.MM,
                                     description="Untere Überdeckung", value=plate.cover_bottom, precision=0)
    vars_[VarId.C_NOM_TOP] = MyVar(id=VarId.C_NOM_TOP, symbol="c_{nom,top}", unit=Unit.MM,
                                  description="Obere Überdeckung", value=plate.cover_top, precision=0)

    computed = compute_plate_layers(plate)

    # Collect used steel IDs
    used_steel_ids: set = set()
    for loc in Location:
        for comp in computed[loc]:
            for d in Direction:
                r = comp.layer.x if d == Direction.X else comp.layer.y
                if r and r.diam > 0 and comp.layer.steel_id:
                    used_steel_ids.add(comp.layer.steel_id)
    multiple_steels = len(used_steel_ids) > 1

    h = plate.h_mm
    b = plate.b_mm
    unit_m = Unit.KNM_PER_M if b == 1000 else Unit.KNM
    unit_n = Unit.KN_PER_M if b == 1000 else Unit.KN

    # Accumulators keyed by (Direction, Location) tuples
    _as:         Dict[Tuple[Direction, Location], float] = {}
    _fs:         Dict[Tuple[Direction, Location], float] = {}
    _fs_minus:   Dict[Tuple[Direction, Location], float] = {}
    _items:      Dict[Tuple[Direction, Location], List[Dict]] = {}

    def _process_direction(direction: Direction, loc: Location, comp_list: List[ComputedLayer]):
        is_top = loc == Location.TOP
        as_sum = fs_sum = fs_minus_sum = as_d_sum = 0.0
        items = []
        zulage_counts: Dict[int, int] = {}

        for comp in comp_list:
            rebar = comp.layer.x if direction == Direction.X else comp.layer.y
            if not rebar or rebar.diam <= 0:
                continue
            diam = rebar.diam
            count = b / rebar.spacing if rebar.type == RebarType.SPACING else rebar.count
            area = (math.pi * diam ** 2 / 4) * count

            steel_id = comp.layer.steel_id
            if not steel_id:
                raise ValueError(f"Für die {comp.global_num}. Lage ({loc.label}) ist kein Stahlmaterial ausgewählt.")

            s_mat = next((m for m in materials if m.id == steel_id), None)
            if not s_mat:
                raise ValueError(f"Das zugewiesene Stahlmaterial für die {comp.global_num}. Lage existiert nicht mehr.")

            s_vars = get_material_vars(s_mat)
            if not s_vars or VarId.F_YD not in s_vars or s_vars[VarId.F_YD].value is None:
                raise ValueError(f"Stahlmaterial '{s_mat.name or 'Unbekannt'}' ist unvollständig definiert (f_yd fehlt).")

            f_yd = s_vars[VarId.F_YD].value
            f_yd_minus = s_vars[VarId.F_YD_MINUS].value
            grade = s_mat.index or s_mat.grade or ""
            grade_esc = grade.replace("_", "\\_")
            f_yd_sym = f"f_{{yd, \\text{{{grade_esc}}}}}" if multiple_steels else "f_{yd}"
            f_yd_minus_sym = f"f_{{yd, \\text{{{grade_esc}}}}}^{{-}}" if multiple_steels else "f_{yd}^{-}"

            dist_to_edge = comp.bottom_edge_dist + diam / 2
            d_val = dist_to_edge if is_top else h - dist_to_edge
            loc_suffix = loc.suffix

            if comp.is_zulage:
                zulage_counts[comp.global_num] = zulage_counts.get(comp.global_num, 0) + 1
                sub = f"{comp.global_num},z_{{{zulage_counts[comp.global_num]}}}"
            else:
                sub = str(comp.global_num)
            comp.subs[direction] = sub

            if rebar.type == RebarType.SPACING:
                a_form = f"\\pi \\cdot ({diam}\\,\\text{{mm}})^2 / 4 \\cdot {b}\\,\\text{{mm}} / {rebar.spacing}\\,\\text{{mm}}"
            else:
                a_form = f"\\pi \\cdot ({diam}\\,\\text{{mm}})^2 / 4 \\cdot {rebar.count}"

            layer_id = f"{direction}_{loc}_{sub}"
            as_deps = {VarId.B: vars_[VarId.B]} if rebar.type == RebarType.SPACING else {}
            vars_[f"As_{layer_id}"] = MyVar(
                id=f"As_{layer_id}",
                symbol=f"a_{{s{direction}{loc_suffix},{sub}}}",
                unit=Unit.MM2, value=area, precision=1, fundamental=False,
                formula_template=a_form,
                description=f"Bewehrungsfläche Lage {comp.global_num} ({direction})",
                dependencies=as_deps,
            )

            d_sym = f"\\diameter_{{{sub}}}"
            if is_top:
                d_form = f"{comp.edge_dist_str} + \\frac{{{d_sym}}}{{2}}"
                d_vals = f"{comp.bottom_edge_dist:.1f}\\,\\text{{mm}} + \\frac{{{diam}\\,\\text{{mm}}}}{{2}}"
            else:
                d_form = f"h - ({comp.edge_dist_str}) - \\frac{{{d_sym}}}{{2}}"
                d_vals = f"{h}\\,\\text{{mm}} - ({comp.bottom_edge_dist:.1f}\\,\\text{{mm}}) - \\frac{{{diam}\\,\\text{{mm}}}}{{2}}"

            cover_var_id = VarId.C_NOM_TOP if is_top else VarId.C_NOM_BOT
            d_deps = {
                VarId.H: vars_[VarId.H],
                cover_var_id: vars_[cover_var_id],
            }
            vars_[f"d_{layer_id}"] = MyVar(
                id=f"d_{layer_id}",
                symbol=f"d_{{{direction}{loc_suffix},{sub}}}",
                unit=Unit.MM, value=d_val, precision=1, fundamental=False,
                formula_template=f"{d_form} = {d_vals}",
                description=f"Statische Höhe Lage {comp.global_num} ({direction})",
                dependencies=d_deps,
            )

            as_sum += area
            as_d_sum += area * d_val
            fs_sum += area * f_yd
            fs_minus_sum += area * f_yd_minus
            items.append({
                "area": area, "d": d_val, "f_yd": f_yd, "f_yd_minus": f_yd_minus,
                "f_yd_sym": f_yd_sym, "f_yd_minus_sym": f_yd_minus_sym,
                "sub": sub, "layer_id": layer_id, "loc_suffix": loc_suffix,
                "a_form": a_form, "s_vars": s_vars,
            })

        if items:
            key = (direction, loc)
            _as[key] = as_sum
            _fs[key] = fs_sum
            _fs_minus[key] = fs_minus_sum
            _items[key] = items

    _process_direction(Direction.X, Location.BOT, computed[Location.BOT])
    _process_direction(Direction.Y, Location.BOT, computed[Location.BOT])
    _process_direction(Direction.X, Location.TOP, computed[Location.TOP])
    _process_direction(Direction.Y, Location.TOP, computed[Location.TOP])

    # Capacities per direction
    for direction in Direction:
        for loc in Location:
            is_top = loc == Location.TOP
            loc_suffix = loc.suffix
            key = (direction, loc)
            fs_val = _fs.get(key, 0)
            as_val = _as.get(key, 0)
            items = _items.get(key, [])
            if not fs_val or not items:
                continue

            # x (neutral axis depth)
            fs_terms_sym = " + ".join(
                f"a_{{s{direction}{loc_suffix},{it['sub']}}} \\cdot {it['f_yd_sym']}" for it in items
            )
            fs_terms_num = " + ".join(
                f"{it['area']:.1f}\\,\\text{{mm}}^2 \\cdot {it['f_yd']:.2f}\\,\\text{{MPa}}" for it in items
            )
            x_val = fs_val / (0.85 * b * f_cd_val)
            x_deps = {f"dep_{VarId.B}": vars_[VarId.B]}
            if VarId.F_CD in c_vars:
                x_deps[f"dep_{VarId.F_CD}"] = c_vars[VarId.F_CD]
            for it in items:
                if f"As_{it['layer_id']}" in vars_:
                    x_deps[f"dep_As_{it['layer_id']}"] = vars_[f"As_{it['layer_id']}"]
                if VarId.F_YD in it["s_vars"]:
                    x_deps[f"dep_{VarId.F_YD}_{it['layer_id']}"] = it["s_vars"][VarId.F_YD]

            vars_[f"x_{direction}_{loc}"] = MyVar(
                id=f"x_{direction}_{loc}", symbol=f"x_{{{direction}{loc_suffix}}}",
                unit=Unit.MM, value=x_val, precision=1, fundamental=False,
                formula_template=(
                    f"\\frac{{{fs_terms_sym}}}{{0.85 \\cdot b \\cdot f_{{cd}}}} = "
                    f"\\frac{{{fs_terms_num}}}{{0.85 \\cdot {b}\\,\\text{{mm}} \\cdot {f_cd_val:.2f}\\,\\text{{MPa}}}}"
                ),
                description=f"Druckzonenhöhe ({direction}, {loc.label.lower()})",
                dependencies=x_deps,
            )

            # M_Rd (moment capacity at N=0)
            lever_terms_sym = " + ".join(
                f"a_{{s{direction}{loc_suffix},{it['sub']}}} \\cdot {it['f_yd_sym']} \\cdot "
                f"({'h/2 - ' if is_top else ''}d_{{{direction}{loc_suffix},{it['sub']}}}{'- h/2' if not is_top else ''})"
                for it in items
            )
            lever_terms_num = " + ".join(
                f"{it['area']:.1f}\\,\\text{{mm}}^2 \\cdot {it['f_yd']:.2f}\\,\\text{{MPa}} \\cdot "
                + (f"({h/2:.1f}\\,\\text{{mm}} - {it['d']:.1f}\\,\\text{{mm}})" if is_top else f"({it['d']:.1f}\\,\\text{{mm}} - {h/2:.1f}\\,\\text{{mm}})")
                for it in items
            )
            m_rd_h2 = sum(
                (it["area"] * it["f_yd"] * ((h / 2 - it["d"]) if is_top else (it["d"] - h / 2))) / 1e6
                for it in items
            )
            concrete_part = f_cd_val * 0.85 * x_val * b * (h - 0.85 * x_val) / 2 / 1e6
            m_rd = m_rd_h2 + concrete_part

            m_deps = {
                f"dep_x": vars_[f"x_{direction}_{loc}"],
                f"dep_{VarId.H}": vars_[VarId.H],
                f"dep_{VarId.B}": vars_[VarId.B],
            }
            if VarId.F_CD in c_vars:
                m_deps[f"dep_{VarId.F_CD}"] = c_vars[VarId.F_CD]
            for it in items:
                if f"As_{it['layer_id']}" in vars_:
                    m_deps[f"dep_As_{it['layer_id']}"] = vars_[f"As_{it['layer_id']}"]
                if f"d_{it['layer_id']}" in vars_:
                    m_deps[f"dep_d_{it['layer_id']}"] = vars_[f"d_{it['layer_id']}"]
                if VarId.F_YD in it["s_vars"]:
                    m_deps[f"dep_{VarId.F_YD}_{it['layer_id']}"] = it["s_vars"][VarId.F_YD]

            vars_[f"M_Rd_{direction}_{loc}"] = MyVar(
                id=f"M_Rd_{direction}_{loc}", symbol=f"M_{{Rd,{direction}{loc_suffix}}}",
                unit=unit_m, value=m_rd, precision=1, fundamental=False,
                formula_template=(
                    f"{lever_terms_sym} + f_{{cd}} \\cdot 0.85 \\cdot x_{{{direction}{loc_suffix}}} \\cdot b "
                    f"\\cdot \\frac{{h - 0.85 \\cdot x_{{{direction}{loc_suffix}}}}}{{2}} = "
                    f"{lever_terms_num} + {f_cd_val:.2f}\\,\\text{{MPa}} \\cdot 0.85 \\cdot {x_val:.1f}\\,\\text{{mm}} \\cdot {b}\\,\\text{{mm}} "
                    f"\\cdot \\frac{{{h}\\,\\text{{mm}} - 0.85 \\cdot {x_val:.1f}\\,\\text{{mm}}}}{{2}}"
                ),
                description=f"Plastisches Widerstandsmoment ({direction}, {loc.label.lower()}, N_Ed=0)",
                dependencies=m_deps,
            )

            # --- State at x = h/2 ---
            f_c_h2 = (f_cd_val * 0.85 * (h / 2) * b) / 1000  # kN
            n_rd_h2 = -f_c_h2 + (fs_val / 1000)  # kN
            z_c = (h / 2) - (0.85 * (h / 4))  # mm
            m_c_h2 = (f_c_h2 * z_c) / 1000  # kNm
            m_rd_h2_tot = m_rd_h2 + m_c_h2  # kNm


            n_h2_deps = {f"dep_{VarId.H}": vars_[VarId.H], f"dep_{VarId.B}": vars_[VarId.B]}
            if VarId.F_CD in c_vars:
                n_h2_deps[f"dep_{VarId.F_CD}"] = c_vars[VarId.F_CD]
            for it in items:
                if f"As_{it['layer_id']}" in vars_:
                    n_h2_deps[f"dep_As_{it['layer_id']}"] = vars_[f"As_{it['layer_id']}"]
                if VarId.F_YD in it["s_vars"]:
                    n_h2_deps[f"dep_{VarId.F_YD}_{it['layer_id']}"] = it["s_vars"][VarId.F_YD]

            vars_[f"N_Rd_h2_{direction}_{loc}"] = MyVar(
                id=f"N_Rd_h2_{direction}_{loc}", symbol=f"N_{{Rd,h/2,{direction}{loc_suffix}}}",
                unit=unit_n, value=n_rd_h2, precision=1, fundamental=False,
                formula_template=(
                    f"- f_{{cd}} \\cdot 0.85 \\cdot \\frac{{h}}{{2}} \\cdot b + {fs_terms_sym} = "
                    f"- {f_c_h2:.1f}\\,\\text{{kN}} + {fs_terms_num}"
                ),
                description=f"Normalkraftwiderstand bei x = h/2 ({direction}, {loc.label.lower()})",
                dependencies=n_h2_deps,
            )

            m_h2_deps = {f"dep_{VarId.H}": vars_[VarId.H], f"dep_{VarId.B}": vars_[VarId.B]}
            if VarId.F_CD in c_vars:
                m_h2_deps[f"dep_{VarId.F_CD}"] = c_vars[VarId.F_CD]
            for it in items:
                if f"As_{it['layer_id']}" in vars_:
                    m_h2_deps[f"dep_As_{it['layer_id']}"] = vars_[f"As_{it['layer_id']}"]
                if f"d_{it['layer_id']}" in vars_:
                    m_h2_deps[f"dep_d_{it['layer_id']}"] = vars_[f"d_{it['layer_id']}"]
                if VarId.F_YD in it["s_vars"]:
                    m_h2_deps[f"dep_{VarId.F_YD}_{it['layer_id']}"] = it["s_vars"][VarId.F_YD]

            vars_[f"M_Rd_h2_{direction}_{loc}"] = MyVar(
                id=f"M_Rd_h2_{direction}_{loc}", symbol=f"M_{{Rd,h/2,{direction}{loc_suffix}}}",
                unit=unit_m, value=m_rd_h2_tot, precision=1, fundamental=False,
                formula_template=(
                    f"{lever_terms_sym} + f_{{cd}} \\cdot 0.85 \\cdot \\frac{{h}}{{2}} \\cdot b \\cdot \\left(\\frac{{h}}{{2}} - 0.85 \\cdot \\frac{{h}}{{4}}\\right) = "
                    f"{lever_terms_num} + {f_cd_val:.2f}\\,\\text{{MPa}} \\cdot 0.85 \\cdot \\frac{{{h}\\,\\text{{mm}}}}{{2}} \\cdot {b}\\,\\text{{mm}} \\cdot \\left(\\frac{{{h}\\,\\text{{mm}}}}{{2}} - 0.85 \\cdot \\frac{{{h}\\,\\text{{mm}}}}{{4}}\\right)"
                ),
                description=f"Momentenwiderstand bei x = h/2 ({direction}, {loc.label.lower()})",
                dependencies=m_h2_deps,
            )

        # N_Rd (combined for both faces)
        as_bot = _as.get((direction, Location.BOT), 0)
        as_top = _as.get((direction, Location.TOP), 0)
        fs_bot = _fs.get((direction, Location.BOT), 0)
        fs_top = _fs.get((direction, Location.TOP), 0)
        fs_minus_bot = _fs_minus.get((direction, Location.BOT), 0)
        fs_minus_top = _fs_minus.get((direction, Location.TOP), 0)
        bot_items = _items.get((direction, Location.BOT), [])
        top_items = _items.get((direction, Location.TOP), [])
        all_items = bot_items + top_items

        if all_items:
            plus_steel_sym = " + ".join(f"a_{{s{direction}{it['loc_suffix']},{it['sub']}}} \\cdot {it['f_yd_sym']}" for it in all_items)
            plus_steel_num = " + ".join(f"{it['area']:.1f}\\,\\text{{mm}}^2 \\cdot {it['f_yd']:.2f}\\,\\text{{MPa}}" for it in all_items)

            n_rd_plus = (fs_bot + fs_top) / 1000
            plus_deps = {}
            for it in all_items:
                if f"As_{it['layer_id']}" in vars_:
                    plus_deps[f"dep_As_{it['layer_id']}"] = vars_[f"As_{it['layer_id']}"]
                if VarId.F_YD in it["s_vars"]:
                    plus_deps[f"dep_{VarId.F_YD}_{it['layer_id']}"] = it["s_vars"][VarId.F_YD]
            vars_[f"N_Rd_plus_{direction}"] = MyVar(
                id=f"N_Rd_plus_{direction}", symbol=f"N_{{Rd+,{direction}}}",
                unit=unit_n, value=n_rd_plus, precision=1, fundamental=False,
                formula_template=f"{plus_steel_sym} = {plus_steel_num}",
                description=f"Max. Zugkraftkapazität ({direction})",
                dependencies=plus_deps,
            )

            minus_steel_sym = " - ".join(f"a_{{s{direction}{it['loc_suffix']},{it['sub']}}} \\cdot {it['f_yd_minus_sym']}" for it in all_items)
            minus_steel_num = " - ".join(f"{it['area']:.1f}\\,\\text{{mm}}^2 \\cdot {it['f_yd_minus']:.2f}\\,\\text{{MPa}}" for it in all_items)
            as_sum_sym = " - ".join(f"a_{{s{direction}{it['loc_suffix']},{it['sub']}}}" for it in all_items)
            as_sum_num = " - ".join(f"{it['area']:.1f}\\,\\text{{mm}}^2" for it in all_items)

            n_rd_minus = (-fs_minus_bot - fs_minus_top - f_cd_val * (b * h - as_bot - as_top)) / 1000
            minus_deps = {f"dep_{VarId.B}": vars_[VarId.B], f"dep_{VarId.H}": vars_[VarId.H]}
            if VarId.F_CD in c_vars:
                minus_deps[f"dep_{VarId.F_CD}"] = c_vars[VarId.F_CD]
            for it in all_items:
                if f"As_{it['layer_id']}" in vars_:
                    minus_deps[f"dep_As_{it['layer_id']}"] = vars_[f"As_{it['layer_id']}"]
                if VarId.F_YD_MINUS in it["s_vars"]:
                    minus_deps[f"dep_{VarId.F_YD_MINUS}_{it['layer_id']}"] = it["s_vars"][VarId.F_YD_MINUS]
            vars_[f"N_Rd_minus_{direction}"] = MyVar(
                id=f"N_Rd_minus_{direction}", symbol=f"N_{{Rd-,{direction}}}",
                unit=unit_n, value=n_rd_minus, precision=1, fundamental=False,
                formula_template=(
                    f"- {minus_steel_sym} - f_{{cd}} \\cdot \\left(b \\cdot h - {as_sum_sym}\\right) = "
                    f"- {minus_steel_num} - {f_cd_val:.2f}\\,\\text{{MPa}} \\cdot \\left({b}\\,\\text{{mm}} \\cdot {h}\\,\\text{{mm}} - {as_sum_num}\\right)"
                ),
                description=f"Max. Druckkraftkapazität ({direction})",
                dependencies=minus_deps,
            )

    sections = _build_sections(plate, vars_, computed, materials, used_steel_ids, f_cd_val, _items)
    return {"vars": vars_, "sections": sections, "computed": computed}


# ---------------------------------------------------------------------------
# Report section builder
# ---------------------------------------------------------------------------

def _get_mat_grade(mat_id: str, materials: List[Material]) -> str:
    mat = next((m for m in materials if m.id == mat_id), None)
    return mat.index or mat.grade or "Unbekannt" if mat else "Unbekannt"


def _build_sections(
    plate: Plate,
    vars_: Dict[str, MyVar],
    computed: Dict[Location, List[ComputedLayer]],
    materials: List[Material],
    used_steel_ids: set,
    f_cd_val: float,
    _items: Dict[Tuple[Direction, Location], List[Dict]],
) -> List[Dict]:
    sections = []
    h = plate.h_mm
    b = plate.b_mm

    # 1. Geometry
    mat_c = next((m for m in materials if m.id == plate.concrete_id), None)
    c_vars = get_material_vars(mat_c) if mat_c else {}
    f_cd_var = c_vars.get(VarId.F_CD)

    beton_sorte = _get_mat_grade(plate.concrete_id or "", materials)
    sections.append({"key": "geom_title", "type": "section_title", "title": "Geometrie & Überdeckung"})
    if beton_sorte != "Unbekannt":
        sections.append({"key": "geom_beton", "type": "summary", "title": "Betonsorte",
                         "latex": f"\\text{{{beton_sorte.replace('_', chr(92) + '_')}}}",
                         "provides": [f_cd_var.to_dict()] if f_cd_var else []})
    sections.append({"key": "geom_dmax", "type": "summary", "title": "Grösstkorndurchmesser",
                     "latex": f"D_{{max}} = {plate.D_max}\\text{{ mm}}", "provides": []})
    for var_id, title in [(VarId.H, "Plattendicke"), (VarId.B, "Plattenbreite"),
                        (VarId.C_NOM_TOP, "Obere Überdeckung"), (VarId.C_NOM_BOT, "Untere Überdeckung")]:
        v = vars_.get(var_id)
        if v:
            sections.append({"key": str(var_id), "type": "equation", "var": v.to_dict(),
                              "latex": v.to_latex_equation(),
                              "title": title, "provides": [v.to_dict()]})


    # 2. Cross-section drawing placeholder
    sections.append({"key": "querschnitt", "type": "drawing", "title": "Querschnitt"})

    # 3. Reinforcement summary
    if used_steel_ids:
        common_grade = None
        s_provides = []
        if len(used_steel_ids) == 1:
            steel_mat_id = next(iter(used_steel_ids))
            common_grade = _get_mat_grade(steel_mat_id, materials)
            s_mat = next((m for m in materials if m.id == steel_mat_id), None)
            if s_mat:
                s_vars = get_material_vars(s_mat)
                s_provides = [v.to_dict() for k, v in s_vars.items() if k in (VarId.F_YD, VarId.F_YD_MINUS) and v]

        sections.append({"key": "rebar_title", "type": "section_title", "title": "Zusammenfassung der Bewehrung"})
        if common_grade:
            sections.append({"key": "rebar_steel_grade", "type": "summary", "title": "Stahlsorte",
                              "latex": f"\\text{{{common_grade.replace('_', chr(92) + '_')}}}",
                              "provides": s_provides})

        all_layers = (
            [{"comp": c, "loc": Location.TOP} for c in computed[Location.TOP]] +
            [{"comp": c, "loc": Location.BOT} for c in computed[Location.BOT]]
        )
        all_layers.sort(key=lambda x: (-(x["comp"].global_num or 0), x["comp"].is_zulage))

        for item in all_layers:
            comp: ComputedLayer = item["comp"]
            if comp.group_idx == -1:
                continue
            loc: Location = item["loc"]
            loc_suffix = loc.suffix
            for d in Direction:
                rebar = comp.layer.x if d == Direction.X else comp.layer.y
                if not rebar or rebar.diam <= 0:
                    continue
                grade = _get_mat_grade(comp.layer.steel_id or "", materials)
                if grade == "Unbekannt":
                    continue
                diam = rebar.diam
                dir_name = d.label
                color = comp.color
                amount = (f"\\diameter{diam}@{rebar.spacing}" if rebar.type == RebarType.SPACING
                          else f"{rebar.count} \\times \\diameter{diam}")
                sub = comp.subs.get(d, str(comp.global_num))
                as_var = vars_.get(f"As_{d}_{loc}_{sub}")
                grade_str = "" if common_grade else f" \\text{{ mit {grade.replace('_', chr(92) + '_')}}}"
                latex = (
                    f"\\begin{{aligned}}\n"
                    f"  &\\textcolor{{{color}}}{{\\bullet}} \\; "
                    f"\\text{{\\textbf{{{comp.global_num}. Lage {dir_name} ({loc.label}):}}}} "
                    f"\\quad {amount}{grade_str}"
                )
                if as_var:
                    latex += (f" \\\\\n  &\\quad a_{{s{d}{loc_suffix},{sub}}} = "
                              f"{as_var.formula_template} = {as_var.format_value()}\\text{{ mm}}^2")
                latex += "\n\\end{aligned}"
                key = f"rebar_L{comp.global_num}_{d}_{loc}"
                sections.append({"key": key, "type": "summary", "title": f"{comp.global_num}. Lage {dir_name} ({loc.label})",
                                  "latex": latex, "provides": [as_var.to_dict()] if as_var else []})

    # 4. Static heights (d values)
    for d in Direction:
        for loc in Location:
            for item in _items.get((d, loc), []):
                dv = vars_.get(f"d_{item['layer_id']}")
                if dv:
                    sections.append({"key": dv.id, "type": "summary", "title": dv.description,
                                     "latex": dv.to_latex_equation(), "provides": [dv.to_dict()]})

    # 5. Capacities
    for direction in Direction:
        cap_keys = [
            f"x_{direction}_{Location.BOT}", f"M_Rd_{direction}_{Location.BOT}",
            f"N_Rd_h2_{direction}_{Location.BOT}", f"M_Rd_h2_{direction}_{Location.BOT}",
            f"x_{direction}_{Location.TOP}", f"M_Rd_{direction}_{Location.TOP}",
            f"N_Rd_h2_{direction}_{Location.TOP}", f"M_Rd_h2_{direction}_{Location.TOP}",
            f"N_Rd_plus_{direction}", f"N_Rd_minus_{direction}",
        ]
        cap_vars = [vars_[k] for k in cap_keys if k in vars_]
        if not cap_vars:
            continue
        sections.append({"key": f"cap_title_{direction}", "type": "section_title",
                         "title": f"Biege- und Normalkraftwiderstand ({direction.label})"})
        for v in cap_vars:
            latex = v.to_latex_equation()
            if latex.startswith("\\begin{aligned}"):
                display = latex
            else:
                parts = latex.split(" = ")
                if len(parts) == 4:
                    display = f"\\begin{{aligned}}\n{parts[0]} &= {parts[1]} \\\\\n&\\quad= {parts[2]} \\\\\n&\\quad= {parts[3]}\n\\end{{aligned}}"
                elif len(parts) >= 3:
                    display = f"\\begin{{aligned}}\n{parts[0]} &= {parts[1]} \\\\\n&\\quad= {' = '.join(parts[2:])}\n\\end{{aligned}}"
                else:
                    display = latex
            sections.append({"key": v.id, "type": "summary", "title": v.description,
                              "latex": display, "latex_raw": latex, "provides": [v.to_dict()]})
        sections.append({"key": f"mn_chart_{direction}", "type": "chart",
                         "title": f"M-N Interaktionsdiagramm ({direction.label})", "dir": str(direction),
                         "provides": [v.to_dict() for v in cap_vars]})

    return sections
