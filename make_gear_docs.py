#!/usr/bin/env python3
"""Regenerate gear.csv and GEAR.md from the live item data in adventure.py.

Run after adding or changing equipment:  python3 make_gear_docs.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adventure as a

FIELDS = ["astab", "aslash", "acrush", "amagic", "arange",
          "dstab", "dslash", "dcrush", "dmagic", "drange",
          "str", "rstr", "mdmg", "prayer"]
CSV_HEAD = ["Slot", "Item", "AStab", "ASlash", "ACrush", "AMagic", "ARange",
            "DStab", "DSlash", "DCrush", "DMagic", "DRange", "MeleeStr",
            "RangeStr", "MagicDmg", "Prayer", "Req Skill", "Req Level",
            "Quest", "2H", "Value", "Members"]
SLOT_ORDER = ["weapon", "shield", "head", "body", "legs", "ammo",
              "cape", "amulet", "gloves", "boots", "ring"]


def rows():
    out = []
    for name, it in a.ITEMS.items():
        eq = it.get("equip")
        if not eq:
            continue
        req = eq.get("req", {})
        req_skill, req_lvl = (next(iter(req.items())) if req else ("", ""))
        out.append({
            "slot": eq.get("slot", "?"), "name": name,
            "stats": [eq.get(f, 0) for f in FIELDS],
            "req_skill": req_skill, "req_lvl": req_lvl,
            "quest": a.ALL_QUESTS.get(eq.get("quest", ""), ""),
            "two_handed": bool(eq.get("two_handed")),
            "value": it.get("value", 0),
            "members": bool(it.get("members")),
        })
    out.sort(key=lambda r: (SLOT_ORDER.index(r["slot"])
                            if r["slot"] in SLOT_ORDER else 99, r["value"]))
    return out


def write_csv(items, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEAD)
        for r in items:
            w.writerow([r["slot"], r["name"], *r["stats"], r["req_skill"],
                        r["req_lvl"], r["quest"],
                        "yes" if r["two_handed"] else "",
                        r["value"], "yes" if r["members"] else "no"])


def write_md(items, path):
    def cell(v):
        return "·" if not v else (f"+{v}" if v > 0 else str(v))

    lines = [
        "# OnlyRunes — Gear & Bonuses (OSRS per-type model)", "",
        "_Auto-generated from `adventure.py` by `make_gear_docs.py`. "
        "`M`=members, `Q`=quest-locked._", "",
    ]
    for slot in SLOT_ORDER:
        group = [r for r in items if r["slot"] == slot]
        if not group:
            continue
        lines += [f"## {slot.title()}", "",
                  "| Item | Stab | Slash | Crush | aMag | aRng | dStab | "
                  "dSlash | dCrush | dMag | dRng | Str | RngStr | Mdmg% | "
                  "Pray | Req | Value | M | Q |",
                  "|" + "---|" * 18]
        for r in group:
            req = f"{r['req_skill']} {r['req_lvl']}".strip()
            lines.append(
                "| " + " | ".join(
                    [r["name"].title()] + [cell(v) for v in r["stats"]]
                    + [req or "·", str(r["value"]),
                       "M" if r["members"] else "",
                       "Q" if r["quest"] else ""]) + " |")
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    items = rows()
    here = os.path.dirname(os.path.abspath(__file__))
    write_csv(items, os.path.join(here, "gear.csv"))
    write_md(items, os.path.join(here, "GEAR.md"))
    print(f"Wrote gear.csv + GEAR.md ({len(items)} equip items).")
