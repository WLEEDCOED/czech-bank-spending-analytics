"""Czech Bank Transaction & Spending Analytics (Berka / PKDD'99)

Reads data/bank_transactions.csv (deterministic 100k-row sample, seed 42)
and renders one polished 1600x1000 px dashboard PNG.

Design language (distinct for this project):
  burgundy/wine #7F1D1D + cream #FEF7ED + gold #C9A227 accents,
  rounded KPI cards, asymmetric panel spans, subtle grids.
All labels use English translations of the Czech codes.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(BASE, "data", "bank_transactions.csv")
OUT = os.path.join(BASE, "dashboard.png")

# ---------- Palette ----------
CREAM = "#FEF7ED"
WINE = "#7F1D1D"
WINE_DEEP = "#5C1414"
GOLD = "#C9A227"
GOLD_DARK = "#B45309"
INK = "#431407"
MUTED = "#7C6A54"
SPINE = "#E3D3B3"
GRID = "#EBDCBE"

TYPE_SHORT = {"PRIJEM": "Credit", "VYDAJ": "Debit", "VYBER": "Withdrawal"}
OP_EN = {
    "VKLAD": "Cash credit",
    "VYBER": "Cash withdrawal",
    "VYBER KARTOU": "Credit-card withdrawal",
    "PREVOD Z UCTU": "Collection from another bank",
    "PREVOD NA UCET": "Remittance to another bank",
    "": "Other",
}
KSYM_EN = {
    "POJISTNE": "Insurance payment",
    "SLUZBY": "Payment for statement",
    "UROK": "Interest credited",
    "SANKC. UROK": "Sanction interest (neg. balance)",
    "SIPO": "Household payment",
    "DUCHOD": "Old-age pension",
    "UVER": "Loan payment",
    "": "None",
}

df = pd.read_csv(CSV, parse_dates=["date"]).fillna("")
df["type_en"] = df["type"].map(TYPE_SHORT)
df["op_en"] = df["operation"].map(OP_EN)
df["ksym_en"] = df["k_symbol"].map(KSYM_EN)

# ---------- KPIs ----------
n_tx = len(df)
total_vol = df["amount"].sum()
n_acct = df["account_id"].nunique()
dmin, dmax = df["date"].min(), df["date"].max()
credit_vol = df.loc[df["type"] == "PRIJEM", "amount"].sum()
debit_vol = df.loc[df["type"] == "VYDAJ", "amount"].sum()

# ---------- Aggregations ----------
monthly = (
    df.assign(ym=df["date"].dt.to_period("M").dt.to_timestamp())
      .groupby(["ym", "type_en"])["amount"].sum()
      .unstack(fill_value=0)
)
op_mix = df["op_en"].value_counts()
ksym_mix = df["ksym_en"].value_counts()
avg_bal_year = df.assign(y=df["date"].dt.year).groupby("y")["balance"].mean()
top_op_vol = df.groupby("op_en")["amount"].sum().sort_values(ascending=True)

# ---------- Figure ----------
fig = plt.figure(figsize=(16, 10), dpi=100)
fig.patch.set_facecolor(CREAM)

fig.text(0.5, 0.962, "Czech Bank Transaction & Spending Analytics  (Berka / PKDD'99)",
         ha="center", va="center", fontsize=21, fontweight="bold", color=INK)
fig.text(0.5, 0.933,
         "100,000 real anonymized transactions  ·  Czech koruna (CZK)  ·  Jan 1993 – Dec 1998  |  folder name is legacy",
         ha="center", va="center", fontsize=10.5, color=MUTED)

# thin gold rule under the title
rule = fig.add_axes([0.06, 0.918, 0.88, 0.004])
rule.set_axis_off()
rule.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0",
                              facecolor=GOLD, edgecolor="none"))

# ---------- Rounded KPI cards ----------
kpis = [
    ("Transactions (sample)", f"{n_tx:,}"),
    ("Total volume", f"{total_vol/1e6:,.1f}M CZK"),
    ("Accounts", f"{n_acct:,}"),
    ("Date range", f"{dmin:%Y-%m-%d} → {dmax:%Y-%m-%d}"),
    ("Credit volume", f"{credit_vol/1e6:,.1f}M CZK"),
    ("Debit volume", f"{debit_vol/1e6:,.1f}M CZK"),
]
kax = fig.add_axes([0.055, 0.822, 0.89, 0.088])
kax.set_axis_off()
kax.set_xlim(0, 6); kax.set_ylim(0, 1)
for i, (label, val) in enumerate(kpis):
    kax.add_patch(FancyBboxPatch(
        (i + 0.07, 0.05), 0.86, 0.90,
        boxstyle="round,pad=0.01,rounding_size=0.10",
        facecolor="white", edgecolor=GOLD, linewidth=1.4))
    kax.text(i + 0.5, 0.60, val, ha="center", va="center",
             fontsize=13.5 if len(val) <= 12 else 10.2, fontweight="bold",
             color=WINE)
    kax.text(i + 0.5, 0.25, label, ha="center", va="center",
             fontsize=9, color=MUTED)

# ---------- Asymmetric panel layout (wide first column) ----------
gs = fig.add_gridspec(2, 3, left=0.055, right=0.97, bottom=0.075, top=0.795,
                      width_ratios=[1.55, 1.0, 1.0], hspace=0.52, wspace=0.30)

def style(ax):
    ax.set_facecolor("white")
    for s in ax.spines.values():
        s.set_color(SPINE)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)

def ptitle(ax, text):
    ax.set_title(text, fontsize=12, fontweight="bold", color=INK, pad=10)

# 1. Monthly volume trend (wide panel)
ax = fig.add_subplot(gs[0, 0]); style(ax)
if "Credit" in monthly.columns:
    ax.plot(monthly.index, monthly["Credit"] / 1e6, label="Credit",
            color=WINE, lw=2.1)
    ax.fill_between(monthly.index, monthly["Credit"] / 1e6, alpha=0.07, color=WINE)
if "Debit" in monthly.columns:
    ax.plot(monthly.index, monthly["Debit"] / 1e6, label="Debit",
            color=GOLD_DARK, lw=2.1)
ptitle(ax, "Monthly volume: credit vs debit (M CZK)")
ax.set_ylabel("M CZK", fontsize=9)
ax.tick_params(axis="x", labelrotation=45, labelsize=7.5)
ax.legend(fontsize=9, frameon=False, loc="upper left")
ax.grid(alpha=0.7, axis="y", color=GRID, lw=0.7)

# 2. Operation-type mix
ax = fig.add_subplot(gs[0, 1]); style(ax)
ax.barh(op_mix.index, op_mix.values, color=WINE, edgecolor="white", height=0.62)
ptitle(ax, "Operation-type mix")
for i, v in enumerate(op_mix.values):
    ax.text(v, i, f"  {v:,}", va="center", fontsize=8.4, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, op_mix.values.max() * 1.18)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

# 3. k_symbol category mix
ax = fig.add_subplot(gs[0, 2]); style(ax)
ax.barh(ksym_mix.index, ksym_mix.values, color=GOLD_DARK, edgecolor="white",
        height=0.62)
ptitle(ax, "Characterization mix (k_symbol)")
for i, v in enumerate(ksym_mix.values):
    ax.text(v, i, f"  {v:,}", va="center", fontsize=8.4, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, ksym_mix.values.max() * 1.18)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

# 4. Amount distribution, log scale
ax = fig.add_subplot(gs[1, 0]); style(ax)
cred = df.loc[df["type"] == "PRIJEM", "amount"]
deb = df.loc[df["type"] == "VYDAJ", "amount"]
bins = np.logspace(np.log10(df["amount"].min()), np.log10(df["amount"].max()), 60)
ax.hist(cred, bins=bins, color=WINE, alpha=0.55, label="Credit")
ax.hist(deb, bins=bins, color=GOLD_DARK, alpha=0.55, label="Debit")
ax.set_xscale("log"); ax.set_yscale("log")
ptitle(ax, "Amount distribution (log scale, credit vs debit)")
ax.set_xlabel("Amount (CZK, log scale)", fontsize=9)
ax.set_ylabel("Transactions (log scale)", fontsize=9)
ax.legend(fontsize=9, frameon=False)
ax.grid(alpha=0.5, color=GRID, lw=0.7)

# 5. Average balance by year
ax = fig.add_subplot(gs[1, 1]); style(ax)
ax.plot(avg_bal_year.index, avg_bal_year.values / 1e3, color=WINE, lw=2.4,
        marker="o", ms=7, mfc=GOLD, mec=WINE, mew=1.6)
ptitle(ax, "Average balance by year")
ax.set_ylabel("Avg balance (K CZK)", fontsize=9)
ax.set_xticks(avg_bal_year.index)
ax.grid(alpha=0.7, color=GRID, lw=0.7)
for x, y in zip(avg_bal_year.index, avg_bal_year.values / 1e3):
    ax.annotate(f"{y:,.1f}k", (x, y), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=7.8, color=WINE_DEEP,
                fontweight="bold")

# 6. Top operation types by volume
ax = fig.add_subplot(gs[1, 2]); style(ax)
ax.barh(top_op_vol.index, top_op_vol.values / 1e6, color=WINE,
        edgecolor="white", height=0.62)
ptitle(ax, "Top operations by volume (M CZK)")
for i, v in enumerate(top_op_vol.values / 1e6):
    ax.text(v, i, f"  {v:,.1f}", va="center", fontsize=8.4, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, (top_op_vol.values / 1e6).max() * 1.20)
ax.set_xlabel("M CZK", fontsize=9)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

fig.text(0.5, 0.018,
         "Source: Berka / PKDD'99 Discovery Challenge financial dataset "
         "(Czech bank, 1993–1998), anonymized real transactions. "
         "Sample: 100,000 rows (seed 42) of 1,056,306 clean records.",
         ha="center", fontsize=8, color=MUTED, style="italic")

fig.savefig(OUT, dpi=100, facecolor=CREAM)
print("Saved", OUT)
