"""QoL batch 2: partial item names resolve everywhere (equip, bank, drop,
shops, GE), autocast is level-gated, goto takes the road to unvisited
cities, and service refusals teach 'goto'."""
import io, sys, contextlib, random, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".."))
import adventure as a

FAILS = []


def check(label, cond, extra=""):
    if cond:
        print(f"  ok  {label}")
    else:
        FAILS.append(label)
        print(f"FAIL  {label}  {extra}")


def do(p, cmd):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        a.dispatch(p, cmd)
    return buf.getvalue()


random.seed(3)

# ---- equip / unequip by partial name -----------------------------------------
p = a.Player("Fumbles")
p.skills["attack"] = a._XP_TABLE[40]
p.add("rune scimitar")
p.add("amulet of strength")
out = do(p, "equip scim")
check("'equip scim' finds the rune scimitar",
      p.equipment["weapon"] == "rune scimitar", out)
out = do(p, "equip amulet")
check("'equip amulet' finds the amulet",
      p.equipment["amulet"] == "amulet of strength", out)
out = do(p, "unequip scim")
check("'unequip scim' works by item name",
      p.equipment["weapon"] is None and p.has("rune scimitar"), out)
p.add("bronze scimitar")
out = do(p, "equip scim")
check("ambiguous equip asks which", "Which one?" in out
      and "rune scimitar" in out, out)

# ---- bank fuzz ----------------------------------------------------------------
p.location = "draynor_village"
p.add("cooked trout", 6)
out = do(p, "deposit trout 4")
check("'deposit trout' finds cooked trout", p.bank.get("cooked trout") == 4,
      out)
out = do(p, "withdraw trout 2")
check("'withdraw trout' finds it in the bank",
      p.bank.get("cooked trout") == 2 and p.count("cooked trout") == 4, out)

# ---- drop fuzz -----------------------------------------------------------------
p.add("raw beef", 3)
out = do(p, "drop beef 2")
check("'drop beef' finds raw beef", p.count("raw beef") == 1, out)

# ---- shop buy/sell fuzz + honest shortfall --------------------------------------
q = a.Player("Shopper")
q.location = "al_kharid_square"          # scimitar shop
q.inventory["coins"] = 2
out = do(q, "buy bronze scim")
check("shop shortfall shows held coins", "You have 2" in out, out)
q.inventory["coins"] = 500
out = do(q, "buy bronze scim")
check("'buy bronze scim' resolves in shop stock", q.has("bronze scimitar"),
      out)
q.add("raw beef", 2)
out = do(q, "sell beef")
check("'sell beef' resolves from your pack", q.count("raw beef") == 1, out)

# ---- GE fuzz + typo suggestion + shortfall ---------------------------------------
g = a.Player("Trader")
g.location = "grand_exchange"
g.inventory["coins"] = 20
out = do(g, "ge buy swrdfish")
check("GE typo suggests the item", "swordfish" in out, out)
out = do(g, "ge buy swordfish 100")
check("GE shortfall shows held coins", "You have 20" in out, out)
g.inventory["coins"] = 5000
out = do(g, "ge buy swordfish 3")
check("GE buy works with plenty", g.count("swordfish") == 3, out)
g.add("cowhide", 5)
out = do(g, "ge sell cowh 5")
check("'ge sell cowh' resolves from your pack", not g.has("cowhide"), out)

# ---- autocast is level-gated -------------------------------------------------------
s = a.Player("Sparks")
out = do(s, "autocast fire blast")
check("autocast refuses spells above your level",
      s.autocast != "fire blast" and "need magic level" in out.lower(), out)
check("refusal lists what you CAN cast", "wind strike" in out, out)
s.skills["magic"] = a._XP_TABLE[60]      # fire blast needs 59
out = do(s, "autocast fire blast")
check("autocast allows it once levelled", s.autocast == "fire blast", out)

# ---- goto takes the road to unvisited cities ----------------------------------------
t = a.Player("Roadie")
out = do(t, "goto varrock")
check("'goto varrock' travels there on a fresh character",
      t.location == a.TRAVEL_HUBS["varrock"] and "road" in out, out[:300])
t.combat = None
out = do(t, "goto ardougne")
check("members city stays gated via travel rules",
      t.location != a.TRAVEL_HUBS.get("ardougne", "x") or t.members, out)

# ---- refusals teach goto -------------------------------------------------------------
u = a.Player("Lost")
u.location = "cow_field"
out = do(u, "bank")
check("bank refusal teaches goto", "goto bank" in out, out)
out = do(u, "smith dagger")
check("anvil refusal teaches goto", "goto anvil" in out, out)
out = do(u, "smelt bronze bar")
check("furnace refusal teaches goto", "goto furnace" in out, out)
out = do(u, "ge buy swordfish")
check("GE refusal teaches goto", "goto ge" in out, out)
out = do(u, "shop")
check("shop refusal teaches goto", "goto shop" in out, out)

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
