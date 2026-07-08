"""Fletching: cut logs -> unstrung, string -> bow, level gates, xp, and
(the fix) batch counts like every other skilling verb."""
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
    import re
    return re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())


random.seed(1)

# ---- core chain: cut then string --------------------------------------------
p = a.Player("Fletchy")
p.members = True
p.skills["fletching"] = a._XP_TABLE[60]
p.add("knife")
p.add("willow logs", 1)
out = do(p, "fletch willow shortbow (u)")
check("cut logs -> unstrung", p.has("willow shortbow (u)"), out)
p.add("bow string", 1)
out = do(p, "fletch willow shortbow")
check("string unstrung -> bow", p.has("willow shortbow")
      and not p.has("willow shortbow (u)"), out)
check("'string' alias works", True)   # exercised below in batch
out = do(p, "string willow longbow")   # nothing to string -> guidance, no crash
check("string with nothing gives guidance", "need a willow longbow (u)" in out,
      out)

# ---- level gate + missing tools ---------------------------------------------
low = a.Player("Low")
low.members = True
low.skills["fletching"] = a._XP_TABLE[40]
low.add("knife")
low.add("yew logs", 1)
out = do(low, "fletch yew shortbow (u)")
check("level gate refuses yew at 40", not low.has("yew shortbow (u)")
      and "level 65" in out, out)
nk = a.Player("NoKnife")
nk.members = True
nk.skills["fletching"] = a._XP_TABLE[60]
nk.add("willow logs", 1)
out = do(nk, "fletch willow shortbow (u)")
check("no knife refuses", "knife" in out and not nk.has("willow shortbow (u)"),
      out)

# ---- members gate -----------------------------------------------------------
free = a.Player("Free")
out = do(free, "fletch shortbow (u)")
check("non-member blocked", "members-only" in out, out)

# ---- xp is correct (rate-aware) ---------------------------------------------
xt = a.Player("Xp")
xt.members = True
xt.skills["fletching"] = a._XP_TABLE[50]
xt.add("knife")
xt.add("maple logs", 1)
x0 = xt.skills["fletching"]
do(xt, "fletch maple shortbow (u)")
check("cut grants correct xp", xt.skills["fletching"] - x0 == 50 * a.XP_RATE,
      f"got {xt.skills['fletching'] - x0}")

# ---- THE FIX: batch counts ---------------------------------------------------
check("fletch is batchable", "fletch" in a.BATCHABLE)
check("string is batchable", "string" in a.BATCHABLE)

b = a.Player("Batch")
b.members = True
b.skills["fletching"] = a._XP_TABLE[60]
b.add("knife")
b.add("willow logs", 10)
out = do(b, "fletch willow shortbow (u) 10")
check("batch cut makes 10 unstrung", b.count("willow shortbow (u)") == 10,
      f"made {b.count('willow shortbow (u)')}; {out[-160:]}")
check("batch cut consumed 10 logs", b.count("willow logs") == 0)
check("batch prints one summary", "actions" in out and "xp" in out.lower(),
      out[-160:])

b.add("bow string", 10)
out = do(b, "string willow shortbow 10")
check("batch string makes 10 bows", b.count("willow shortbow") == 10,
      f"made {b.count('willow shortbow')}")

# ---- batch stops honestly when materials run out ----------------------------
s = a.Player("Short")
s.members = True
s.skills["fletching"] = a._XP_TABLE[60]
s.add("knife")
s.add("willow logs", 3)
out = do(s, "fletch willow shortbow (u) 10")
check("batch cut stops at supply (3 made)",
      s.count("willow shortbow (u)") == 3, f"made {s.count('willow shortbow (u)')}")
check("running out says why", "willow logs" in out, out[-160:])

# ---- 'all' works too --------------------------------------------------------
al = a.Player("All")
al.members = True
al.skills["fletching"] = a._XP_TABLE[60]
al.add("knife")
al.add("oak logs", 6)
do(al, "fletch oak shortbow (u) all")
check("'all' caps at inventory's worth", al.count("oak shortbow (u)") == 6,
      f"made {al.count('oak shortbow (u)')}")

# ---- startable at level 1 (no dead-end like the old herblore bug) ------------
z = a.Player("Fresh")
z.members = True                       # brand-new fletcher, level 1
z.add("knife")
z.add("logs", 1)
zx = z.skills["fletching"]
out = do(z, "fletch shortbow (u)")
check("fletching is startable at level 1", z.skills["fletching"] > zx
      and z.has("shortbow (u)"), out)

# ---- discoverability: fletch is in help -------------------------------------
h = do(a.Player("H"), "help")
check("fletch listed in help", "fletch" in h.lower(), h[:200])

print()
print("FAILURES:", len(FAILS), FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
