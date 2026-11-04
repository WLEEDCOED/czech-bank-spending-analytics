# =====================================================================
# سكربت Power BI — Python Visual — الصفحة 1: النظرة العامة (Overview)
# لوحة: Czech Bank Transaction & Spending Analytics (Berka / PKDD'99)
# =====================================================================
# طريقة الاستخدام:
#  1) في Power BI Desktop: Get Data ← حمّل ملف data/bank_transactions.csv
#  2) أضف Python visual إلى الصفحة 1
#  3) اسحب الأعمدة التالية إلى خانة Values في الـ visual:
#       date , type , amount , balance , operation , account_id
#  4) الصق هذا السكربت كاملًا في محرر البايثون ثم اضغط Run
#
# ENGLISH — PAGE 1 "Overview" (KPI cards + main trends):
#  1) Power BI Desktop: Get Data -> load data/bank_transactions.csv
#  2) Insert a Python visual on page 1
#  3) Drag EXACTLY these columns into the visual's Values well:
#       date, type, amount, balance, operation, account_id
#  4) Paste this whole script into the Python editor and click Run
#
# Reads ONLY the injected `dataset` DataFrame. No file loading,
# no hardcoded paths, no plt.show() — Power BI renders the returned
# figure automatically. Czech codes are translated to English inside.
# Design: burgundy/wine #7F1D1D + cream #FEF7ED + gold #C9A227 accents.
# =====================================================================

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import numpy as np

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

# ---------- Read the injected Power BI dataset ----------
df = dataset.copy()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df[df["date"].notna()].copy()
for c in ("type", "operation"):
    df[c] = df[c].where(df[c].notna(), "").astype(str).str.strip()
df["type_en"] = df["type"].map(TYPE_SHORT).fillna(df["type"])
df["op_en"] = df["operation"].map(OP_EN).fillna(df["operation"])
df["ym"] = df["date"].dt.to_period("M").dt.to_timestamp()
df["year"] = df["date"].dt.year

# ---------- KPIs ----------
n_tx = len(df)
total_vol = df["amount"].sum()
n_acct = df["account_id"].nunique()
dmin, dmax = df["date"].min(), df["date"].max()
credit_vol = df.loc[df["type"] == "PRIJEM", "amount"].sum()
debit_vol = df.loc[df["type"] == "VYDAJ", "amount"].sum()

monthly = df.groupby(["ym", "type_en"])["amount"].sum().unstack(fill_value=0)
avg_bal_year = df.groupby("year")["balance"].mean()
top_op_vol = df.groupby("op_en")["amount"].sum().sort_values(ascending=True)
vol_by_type = df.groupby("type_en")["amount"].sum().sort_values(ascending=True)

# ---------- Figure ----------
fig = plt.figure(figsize=(16, 10), dpi=100)
fig.patch.set_facecolor(CREAM)

fig.text(0.5, 0.962, "Czech Bank Analytics — Executive Overview  (Berka / PKDD'99)",
         ha="center", va="center", fontsize=21, fontweight="bold", color=INK)
fig.text(0.5, 0.933,
         "Real anonymized transactions  ·  Czech koruna (CZK)  ·  Jan 1993 – Dec 1998",
         ha="center", va="center", fontsize=10.5, color=MUTED)
rule = fig.add_axes([0.06, 0.918, 0.88, 0.004])
rule.set_axis_off()
rule.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0",
                              facecolor=GOLD, edgecolor="none"))

kpis = [
    ("Transactions", f"{n_tx:,}"),
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
             fontsize=13.5 if len(val) <= 12 else 10.2,
             fontweight="bold", color=WINE)
    kax.text(i + 0.5, 0.25, label, ha="center", va="center",
             fontsize=9, color=MUTED)

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

# 1. Monthly volume trend (wide)
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

# 2. Average balance by year
ax = fig.add_subplot(gs[0, 1]); style(ax)
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

# 3. Volume share by type
ax = fig.add_subplot(gs[0, 2]); style(ax)
tcols = {"Credit": WINE, "Debit": GOLD_DARK, "Withdrawal": "#A16207"}
ax.barh(vol_by_type.index,
        vol_by_type.values / 1e6,
        color=[tcols.get(t, WINE) for t in vol_by_type.index],
        edgecolor="white", height=0.55)
ptitle(ax, "Volume share by type (M CZK)")
for i, v in enumerate(vol_by_type.values / 1e6):
    ax.text(v, i, f"  {v:,.1f}", va="center", fontsize=8.6, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, (vol_by_type.values / 1e6).max() * 1.22)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

# 4. Top operations by volume (wide) — shift right so long y-labels fit
ax = fig.add_subplot(gs[1, 0:2]); style(ax)
_pos = ax.get_position()
ax.set_position([_pos.x0 + 0.055, _pos.y0, _pos.width - 0.055, _pos.height])
ax.barh(top_op_vol.index, top_op_vol.values / 1e6, color=WINE,
        edgecolor="white", height=0.60)
ptitle(ax, "Top operation types by volume (M CZK)")
for i, v in enumerate(top_op_vol.values / 1e6):
    ax.text(v, i, f"  {v:,.1f}", va="center", fontsize=8.8, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, (top_op_vol.values / 1e6).max() * 1.20)
ax.set_xlabel("M CZK", fontsize=9)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

# 5. Net flow by year (credit − debit)
net_year = (df[df["type"] == "PRIJEM"].groupby("year")["amount"].sum()
            - df[df["type"] == "VYDAJ"].groupby("year")["amount"].sum())
ax = fig.add_subplot(gs[1, 2]); style(ax)
barcols = [WINE if v >= 0 else GOLD_DARK for v in net_year.values]
ax.bar(net_year.index.astype(str), net_year.values / 1e6, color=barcols,
       edgecolor="white", width=0.6)
ptitle(ax, "Net flow by year (M CZK)")
ax.set_ylabel("Credit − debit (M CZK)", fontsize=9)
ax.tick_params(axis="x", labelsize=8)
ax.grid(alpha=0.7, axis="y", color=GRID, lw=0.7)
for x, y in zip(net_year.index.astype(str), net_year.values / 1e6):
    ax.annotate(f"{y:,.1f}", (x, y), textcoords="offset points",
                xytext=(0, 5), ha="center", fontsize=7.8, color=WINE_DEEP,
                fontweight="bold")

fig.text(0.5, 0.018,
         "Source: Berka / PKDD'99 Discovery Challenge financial dataset "
         "(Czech bank, 1993–1998), anonymized real transactions.  Page 1 of 2 — Overview.",
         ha="center", fontsize=8, color=MUTED, style="italic")

plt.gcf()  # Power BI renders this figure automatically (no plt.show())
