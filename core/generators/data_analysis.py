"""تولید کد EDA (تحلیل اکتشافی) با pandas و seaborn."""
from typing import Dict, List
from core.excel_reader import ExcelSchema


def generate(schema: ExcelSchema) -> List[Dict]:
    num = [c.name for c in schema.numeric]
    cat = [c.name for c in schema.categorical]
    sections = []

    # ---------- ۱. بارگذاری ----------
    sections.append({
        "title": "۱. بارگذاری داده با pandas",
        "code": '''import pandas as pd

df = pd.read_excel("data.xlsx", sheet_name=0)

print("شکل داده :", df.shape)
print(df.head())
''',
        "explanation": """**توضیح:**
- `pd.read_excel` فایل را در یک DataFrame می‌خواند.  
  `sheet_name=0` یعنی شیت اول؛ می‌توانی اسم شیت را هم بدهی.
- `df.shape` یک تاپل `(ردیف, ستون)` برمی‌گرداند.
- `df.head()` ۵ ردیف اول را نشان می‌دهد."""
    })

    # ---------- ۲. خلاصه آماری ----------
    sections.append({
        "title": "۲. خلاصه‌ی آماری و انواع داده",
        "code": '''# انواع ستون‌ها و تعداد مقادیر غیرخالی
df.info()

# آمار توصیفی ستون‌های عددی (mean, std, min, max, quartiles)
print(df.describe())

# آمار توصیفی ستون‌های دسته‌ای (تعداد، یکتا، پرتکرار)
print(df.describe(include="object"))
''',
        "explanation": """**توضیح:**
- `df.info()` نوع هر ستون و تعداد مقادیر غیرخالی را نشان می‌دهد.
- `df.describe()` برای ستون‌های عددی: میانگین، انحراف معیار، کمینه، چارک‌ها، بیشینه.
- `df.describe(include="object")` برای ستون‌های متنی: تعداد مقادیر یکتا و پرتکرارترین مقدار."""
    })

    # ---------- ۳. مقدار گمشده ----------
    sections.append({
        "title": "۳. بررسی مقدار گمشده (Missing Values)",
        "code": '''missing = df.isna().sum().sort_values(ascending=False)
missing_pct = (missing / len(df) * 100).round(2)

report = pd.DataFrame({"count": missing, "percent": missing_pct})
print(report[report["count"] > 0])
''',
        "explanation": """**توضیح:**
- `df.isna()` یک DataFrame بولی می‌سازد (True = گمشده).
- `.sum()` تعداد گمشده‌های هر ستون را می‌شمارد.
- درصد گمشده به تعداد کل ردیف‌ها نرمال می‌شود — برای تصمیم‌گیری مهم‌تر از تعداد خام است."""
    })

    # ---------- ۴. توزیع دسته‌ها ----------
    if cat:
        cat0 = cat[0]
        sections.append({
            "title": f"۴. توزیع مقادیر ستون «{cat0}»",
            "code": f'''counts = df["{cat0}"].value_counts(dropna=False)
print(counts)

# نمودار میله‌ای
import matplotlib.pyplot as plt
counts.head(10).plot(kind="bar")
plt.title("توزیع {cat0}")
plt.tight_layout()
plt.savefig("dist_{cat0}.png", dpi=120)
plt.show()
''',
            "explanation": f"""**توضیح:**
- `value_counts()` هر مقدار یکتا و تعداد تکرارش را برمی‌گرداند.
- `dropna=False` یعنی مقدارهای گمشده هم شمرده شوند.
- `kind="bar"` نمودار میله‌ای می‌کشد؛ `head(10)` فقط ۱۰ دسته‌ی پرتکرار را رسم می‌کند."""
        })

    # ---------- ۵. گروه‌بندی ----------
    if num and cat:
        sections.append({
            "title": f"۵. گروه‌بندی: میانگین «{num[0]}» بر اساس «{cat[0]}»",
            "code": f'''result = (
    df.groupby("{cat[0]}")["{num[0]}"]
      .agg(["count", "mean", "median", "std"])
      .sort_values("mean", ascending=False)
)
print(result)
''',
            "explanation": f"""**توضیح:**
- `groupby` مثل Pivot Table در اکسل عمل می‌کند.
- `.agg([...])` چند آماره را همزمان محاسبه می‌کند.
- `sort_values("mean")` خروجی را بر اساس میانگین مرتب می‌کند."""
        })

    # ---------- ۶. همبستگی ----------
    if len(num) >= 2:
        sections.append({
            "title": "۶. ماتریس همبستگی",
            "code": '''import seaborn as sns
import matplotlib.pyplot as plt

corr = df.select_dtypes("number").corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig("correlation.png", dpi=120)
plt.show()
''',
            "explanation": """**توضیح:**
- `corr()` ضریب همبستگی پیرسون بین ستون‌های عددی را حساب می‌کند.
- Heatmap تصویری خیلی خواناتر می‌دهد.
- برای تشخیص ویژگی‌های تکراری (multicollinearity) مفید است."""
        })

    # ---------- ۷. تمیزکاری ----------
    sections.append({
        "title": "۷. تمیزکاری پایه (Cleaning)",
        "code": '''import numpy as np

df_clean = df.copy()

# ۱. حذف ستون‌هایی با بیش از ۵۰٪ گمشده
thresh = len(df) * 0.5
df_clean = df_clean.dropna(axis=1, thresh=thresh)

# ۲. پر کردن عددی‌ها با میانه
num_cols = df_clean.select_dtypes(include=np.number).columns
df_clean[num_cols] = df_clean[num_cols].fillna(df_clean[num_cols].median())

# ۳. پر کردن دسته‌ای‌ها با مُد
cat_cols = df_clean.select_dtypes(exclude=np.number).columns
for c in cat_cols:
    df_clean[c] = df_clean[c].fillna(df_clean[c].mode().iloc[0])

print("قبل :", df.shape, "بعد :", df_clean.shape)
''',
        "explanation": """**توضیح مراحل:**
1. **حذف ستون‌های خیلی خالی** — ستون‌هایی که بیش از نیمی از مقدارها گمشده‌اند.
2. **پر کردن عددی با میانه** — میانه نسبت به outlierها مقاوم‌تر است.
3. **پر کردن دسته‌ای با mode** — پرتکرارترین مقدار.

⚠️ **نکته حرفه‌ای:** برای پروژه‌های واقعی، imputation را داخل Pipeline یادگیری ماشین انجام بده تا data leakage رخ ندهد."""
    })

    return sections