# دليل Power BI — إعادة بناء الداشبورد بنفسك

هذا الدليل يشرح كيف تعيد بناء لوحة **Czech Bank Transaction & Spending Analytics** في **Power BI Desktop** على جهازك خلال ~15 دقيقة.

> 📌 المرجع البصري للشكل النهائي: ملف **`dashboard.png`** في هذا المجلد — افتحه جنبك وأنت تشتغل عشان تطابق التخطيط.

ملف البيانات: **`data/bank_transactions.csv`** — أعمدته الحقيقية:
`trans_id` · `account_id` · `date` · `type` · `operation` · `amount` · `balance` · `k_symbol` · `bank` · `account`

---

## ⚡ الطريقة الأسرع (موصى بها): Python Visuals — صفحتان جاهزتان

### المتطلب المسبق (مرة واحدة فقط)
1. ثبّت Python من python.org (أي إصدار 3.9+).
2. افتح CMD ونفّذ:
   ```
   pip install pandas matplotlib
   ```
3. في Power BI Desktop: ‏**File ← Options and settings ← Options ← Python scripting** وتأكد أن Power BI متعرف على تثبيت البايثون (Detected Python home). لو ما ظهر، اختر مسار التثبيت يدويًا.

### الصفحة 1 — النظرة العامة (Overview)
1. **Get Data ← Text/CSV** ← اختر ملف `data/bank_transactions.csv` ← **Load**.
2. أضف **Python visual** (أيقونة Py) إلى الصفحة 1.
3. من قائمة الحقول (Fields) **اسحب الأعمدة التالية إلى خانة Values** — بالضبط هذه الأسماء:
   - `date` · `type` · `amount` · `balance` · `operation` · `account_id`
4. انسخ كامل محتوى ملف **`powerbi-page1-overview.py`** والصقه في محرر البايثون ثم اضغط **Run**.
5. خلاص ✅ — بطاقات KPIs + الترند الشهري + متوسط الرصيد السنوي + حصة الحجم + أعلى العمليات + صافي التدفق السنوي تظهر مباشرة.

### الصفحة 2 — التفاصيل (Details)
1. أضف صفحة ثانية في التقرير، وضع فيها **Python visual** جديد.
2. **اسحب الأعمدة التالية إلى خانة Values**:
   - `date` · `type` · `operation` · `amount` · `k_symbol`
3. انسخ كامل محتوى ملف **`powerbi-page2-details.py`** والصقه في المحرر ثم اضغط **Run**.
4. خلاص ✅ — مزيج أنواع العمليات + مزيج k_symbol + توزيع المبالغ + الحجم السنوي المكدس + الوسيط حسب النوع.

> ملاحظة: السكربتان يقرآن فقط الـ `dataset` المحقون من Power BI (الأعمدة المسحوبة) — بدون تحميل ملفات وبدون `plt.show()`. والترجمة من التشيكية للإنجليزية (PRIJEM ← Credit إلخ) تتم داخل السكربت تلقائيًا.

### 🎛️ الـ Slicers (الفلاتر) — تشتغل مع الـ Python visuals
أضف Slicers عادية في أعلى كل صفحة من هذه الأعمدة:
- `date` ← Year / Month (فلتر زمني)
- `type` (النوع: Credit / Debit / Withdrawal)
- `operation` (نوع العملية)

**ملاحظة صادقة:** الـ Slicers **تفلتر الـ Python visuals فعليًا** — لأن Power BI يمرر للسكربت فقط الصفوف المفلترة في الـ `dataset`، فالأرقام والرسوم تتحدث تلقائيًا مع كل فلتر. ✅
لكن انتبه: الـ Python visuals **لا تستقبل تفاعلات النقر/التظليل (cross-highlight)** من الرسوم الأخرى — يعني لو ضغطت على شريط في رسم أصلي، الـ Python visual ما يتظلل، لكن الـ Slicers تشتغل عليه عادي.

---

## 🛠️ الطريقة البديلة: مسار Power BI الأصلي (DAX + Visuals)

لو تبي تبنيها بفيجوالز Power BI الأصلية بدل البايثون:

### 1) تحميل البيانات
**Get Data ← Text/CSV** ← `data/bank_transactions.csv` ← Load. جدول واحد فقط — **لا تحتاج علاقات (Relationships)** لأن كل شيء في جدول `bank_transactions`.

### 2) تنظيف Power Query (خطوات سريعة)
1. عمود `date`: غيّر نوعه إلى **Date**.
2. عمود `type`: ‏**Replace Values**: ‏`PRIJEM` ← `Credit`، ‏`VYDAJ` ← `Debit`، ‏`VYBER` ← `Withdrawal`.
3. عمود `operation`: ‏Replace Values: ‏`VKLAD` ← `Cash credit`، ‏`VYBER` ← `Cash withdrawal`، ‏`VYBER KARTOU` ← `Credit-card withdrawal`، ‏`PREVOD Z UCTU` ← `Collection from another bank`، ‏`PREVOD NA UCET` ← `Remittance to another bank`، ثم استبدل القيم الفارغة (null) بـ `Other`.
4. عمود `k_symbol`: ‏Replace Values: ‏`POJISTNE` ← `Insurance payment`، ‏`SLUZBY` ← `Payment for statement`، ‏`UROK` ← `Interest credited`، ‏`SANKC. UROK` ← `Sanction interest`، ‏`SIPO` ← `Household payment`، ‏`DUCHOD` ← `Old-age pension`، ‏`UVER` ← `Loan payment`، ثم القيم الفارغة ← `None`.
5. أضف عمود **YearMonth**: ‏Add Column ← Date ← Year ثم Month، أو عمود مخصص بالصيغة: `Date.ToText([date], "yyyy-MM")`.

### 3) مقاييس DAX (انسخ والصق كما هي)

```dax
Transaction Count = COUNTROWS ( 'bank_transactions' )

Total Volume = SUM ( 'bank_transactions'[amount] )

Credit Volume =
CALCULATE (
    SUM ( 'bank_transactions'[amount] ),
    'bank_transactions'[type] = "Credit"
)

Debit Volume =
CALCULATE (
    SUM ( 'bank_transactions'[amount] ),
    'bank_transactions'[type] = "Debit"
)

Net Flow = [Credit Volume] - [Debit Volume]

Account Count = DISTINCTCOUNT ( 'bank_transactions'[account_id] )

Avg Balance = AVERAGE ( 'bank_transactions'[balance] )

Credit Share % = DIVIDE ( [Credit Volume], [Total Volume] )
```

### 4) الفيجوالز (طابق `dashboard.png`)

**صفحة النظرة العامة:** بطاقات Cards للمقاييس الستة · Line chart للترند الشهري (X = YearMonth، Y = Credit Volume + Debit Volume) · Line chart لمتوسط الرصيد السنوي (X = Year، Y = Avg Balance) · Bar chart أفقي لأعلى العمليات حجمًا (Y = operation، X = Total Volume، فلتر Top 5).

**صفحة التفاصيل:** Bar chart لمزيج العمليات (Y = operation، X = Transaction Count) · Bar chart لمزيج k_symbol · Column chart لتوزيع المبالغ على عمود Amount Bin* (Legend = type) · Stacked column chart للحجم السنوي حسب النوع (X = Year، Y = Total Volume، Legend = type).

\* عمود `Amount Bin`: أنشئ عمود محسوب يجمّع المبالغ (مثال: `"<1K"`, `"1K–10K"`, `"10K+"`) — أو استخدم الطريقة الأسرع (Python visual) للرسم اللوغاريتمي الدقيق.

---

بالتوفيق! أي رقم في الدليل محسوب من البيانات الحقيقية — جرّب تطابق الأرقام مع `dashboard.png` عشان تتأكد أن كل شيء صح. 💪
