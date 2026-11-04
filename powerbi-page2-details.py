# =====================================================================
# سكربت Power BI — Python Visual — الصفحة 2: التفاصيل (Details)
# لوحة: Czech Bank Transaction & Spending Analytics (Berka / PKDD'99)
# =====================================================================
# طريقة الاستخدام:
#  1) في Power BI Desktop: Get Data ← حمّل ملف data/bank_transactions.csv
#     (نفس الجدول المستخدم في الصفحة 1)
#  2) أضف Python visual ثانيًا إلى الصفحة 2
#  3) اسحب الأعمدة التالية إلى خانة Values في الـ visual:
#       date , type , operation , amount , k_symbol
#  4) الصق هذا السكربت كاملًا في محرر البايثون ثم اضغط Run
#
# ENGLISH — PAGE 2 "Details & breakdowns":
#  1) Power BI Desktop: Get Data -> load data/bank_transactions.csv
#     (same table as page 1)
#  2) Insert a second Python visual on page 2
#  3) Drag EXACTLY these columns into the visual's Values well:
#       date, type, operation, amount, k_symbol
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

# ---------- Read the injected Power BI dataset ----------
df = dataset.copy()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df[df["date"].notna()].copy()
for c in ("type", "operation", "k_symbol"):
    df[c] = df[c].where(df[c].notna(), "").astype(str).str.strip()
df["type_en"] = df["type"].map(TYPE_SHORT).fillna(df["type"])
df["op_en"] = df["operation"].map(OP_EN).fillna(df["operation"])
df["ksym_en"] = df["k_symbol"].map(KSYM_EN).fillna(df["k_symbol"])
df["year"] = df["date"].dt.year

op_mix = df["op_en"].value_counts()
ksym_mix = df["ksym_en"].value_counts()
yearly_type = (df.groupby(["year", "type_en"])["amount"].sum()
                 .unstack(fill_value=0).reindex(columns=["Credit", "Debit", "Withdrawal"])
                 .fillna(0))
median_by_type = df.groupby("type_en")["amount"].median()

# ---------- Figure ----------
fig = plt.figure(figsize=(16, 10), dpi=100)
fig.patch.set_facecolor(CREAM)

fig.text(0.5, 0.962, "Czech Bank Analytics — Details & Breakdowns  (Berka / PKDD'99)",
         ha="center", va="center", fontsize=21, fontweight="bold", color=INK)
fig.text(0.5, 0.933,
         "Operation mix  ·  k_symbol mix  ·  amount distribution  ·  yearly volume by type",
         ha="center", va="center", fontsize=10.5, color=MUTED)
rule = fig.add_axes([0.06, 0.918, 0.88, 0.004])
rule.set_axis_off()
rule.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0",
                              facecolor=GOLD, edgecolor="none"))

gs = fig.add_gridspec(2, 3, left=0.055, right=0.97, bottom=0.075, top=0.885,
                      hspace=0.50, wspace=0.30)

def style(ax):
    ax.set_facecolor("white")
    for s in ax.spines.values():
        s.set_color(SPINE)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)

def ptitle(ax, text):
    ax.set_title(text, fontsize=12, fontweight="bold", color=INK, pad=10)

# 1. Operation-type mix — shift right so long y-labels fit
ax = fig.add_subplot(gs[0, 0]); style(ax)
_pos = ax.get_position()
ax.set_position([_pos.x0 + 0.055, _pos.y0, _pos.width - 0.055, _pos.height])
ax.barh(op_mix.index, op_mix.values, color=WINE, edgecolor="white", height=0.62)
ptitle(ax, "Operation-type mix (transactions)")
for i, v in enumerate(op_mix.values):
    ax.text(v, i, f"  {v:,}", va="center", fontsize=8.4, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, op_mix.values.max() * 1.18)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

# 2. k_symbol category mix
ax = fig.add_subplot(gs[0, 1]); style(ax)
ax.barh(ksym_mix.index, ksym_mix.values, color=GOLD_DARK, edgecolor="white",
        height=0.62)
ptitle(ax, "Characterization mix (k_symbol)")
for i, v in enumerate(ksym_mix.values):
    ax.text(v, i, f"  {v:,}", va="center", fontsize=8.4, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, ksym_mix.values.max() * 1.18)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

# 3. Amount distribution, log scale
ax = fig.add_subplot(gs[0, 2]); style(ax)
cred = df.loc[df["type"] == "PRIJEM", "amount"]
deb = df.loc[df["type"] == "VYDAJ", "amount"]
lo = max(df["amount"].min(), 0.01)
bins = np.logspace(np.log10(lo), np.log10(df["amount"].max()), 60)
ax.hist(cred, bins=bins, color=WINE, alpha=0.55, label="Credit")
ax.hist(deb, bins=bins, color=GOLD_DARK, alpha=0.55, label="Debit")
ax.set_xscale("log"); ax.set_yscale("log")
ptitle(ax, "Amount distribution (log scale)")
ax.set_xlabel("Amount (CZK, log scale)", fontsize=9)
ax.set_ylabel("Transactions (log scale)", fontsize=9)
ax.legend(fontsize=9, frameon=False)
ax.grid(alpha=0.5, color=GRID, lw=0.7)

# 4. Yearly volume by type (stacked)
ax = fig.add_subplot(gs[1, 0:2]); style(ax)
x = yearly_type.index.astype(str)
bottom = np.zeros(len(yearly_type))
tcols = {"Credit": WINE, "Debit": GOLD_DARK, "Withdrawal": "#A16207"}
for t in ("Credit", "Debit", "Withdrawal"):
    vals = (yearly_type[t] / 1e6).values
    ax.bar(x, vals, bottom=bottom, label=t, color=tcols[t], edgecolor="white",
           width=0.6)
    bottom += vals
ptitle(ax, "Yearly volume by type, stacked (M CZK)")
ax.set_ylabel("M CZK", fontsize=9)
ax.legend(fontsize=9, frameon=False, ncol=3)
ax.grid(alpha=0.7, axis="y", color=GRID, lw=0.7)

# 5. Median ticket by type
ax = fig.add_subplot(gs[1, 2]); style(ax)
med = median_by_type.reindex(["Credit", "Debit", "Withdrawal"]).dropna()
ax.barh(med.index, med.values,
        color=[tcols.get(t, WINE) for t in med.index],
        edgecolor="white", height=0.55)
ptitle(ax, "Median amount by type (CZK)")
for i, v in enumerate(med.values):
    ax.text(v, i, f"  {v:,.0f}", va="center", fontsize=8.8, color=WINE_DEEP,
            fontweight="bold")
ax.set_xlim(0, med.values.max() * 1.28)
ax.grid(alpha=0.7, axis="x", color=GRID, lw=0.7)

fig.text(0.5, 0.018,
         "Source: Berka / PKDD'99 Discovery Challenge financial dataset "
         "(Czech bank, 1993–1998), anonymized real transactions.  Page 2 of 2 — Details.",
         ha="center", fontsize=8, color=MUTED, style="italic")

plt.gcf()  # Power BI renders this figure automatically (no plt.show())
