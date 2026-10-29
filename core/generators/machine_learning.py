"""تولید کد آموزش مدل ML با scikit-learn."""
from typing import Dict, List
from core.excel_reader import ExcelSchema, ColumnInfo


def _detect_task(target: ColumnInfo) -> str:
    """تشخیص خودکار نوع مسئله (طبقه‌بندی یا رگرسیون)"""
    if target.dtype in ("categorical", "boolean"):
        return "classification"
    if target.dtype == "numeric" and target.unique > 20:
        return "regression"
    return "classification"  # عددی با مقادیر کم = احتمالاً کلاس


def generate(schema: ExcelSchema, target: str) -> List[Dict]:
    tcol = schema.get(target)
    if not tcol:
        return [{"title": "خطا", "code": "", "explanation": "ستون هدف پیدا نشد."}]

    task = _detect_task(tcol)
    
    # تعیین مدل و معیارها بر اساس نوع مسئله
    if task == "classification":
        model_import = "from sklearn.ensemble import RandomForestClassifier"
        model_cls = "RandomForestClassifier"
        metric_import = "from sklearn.metrics import classification_report, confusion_matrix, accuracy_score"
    else:
        model_import = "from sklearn.ensemble import RandomForestRegressor"
        model_cls = "RandomForestRegressor"
        metric_import = "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score"

    sections = []

    # ---------- ۱. آماده‌سازی ----------
    sections.append({
        "title": "۱. بارگذاری و جدا کردن ویژگی/هدف",
        "code": f'''import pandas as pd
import numpy as np

TARGET = "{target}"     # ← ستون هدف (تشخیص خودکار: {'طبقه‌بندی' if task == 'classification' else 'رگرسیون'})

df = pd.read_excel("data.xlsx", sheet_name=0)

X = df.drop(columns=[TARGET])
y = df[TARGET]

# حذف ردیف‌هایی که مقدار هدف ندارند
mask = y.notna()
X, y = X[mask], y[mask]

print("X :", X.shape, "| y :", y.shape)
''',
        "explanation": f"""**توضیح:**
- ستون **هدف** = چیزی که می‌خواهیم پیش‌بینی کنیم = `{target}`.
- بقیه‌ی ستون‌ها **ویژگی** (feature) هستند.
- **نوع مسئله:** چون هدف از نوع `{tcol.dtype}` است و {tcol.unique} مقدار یکتا دارد، به‌صورت خودکار **{'طبقه‌بندی (classification)' if task == 'classification' else 'رگرسیون (regression)'}** تشخیص داده شد."""
    })

    # ---------- ۲. Split ----------
    sections.append({
        "title": "۲. تقسیم به train / test",
        "code": f'''from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    {'stratify=y  # حفظ نسبت کلاس‌ها' if task == 'classification' else '# regression: stratify لازم نیست'}
)

print(f"train: {{len(X_train)}} | test: {{len(X_test)}}")
''',
        "explanation": """**توضیح:**
- **۸۰٪** داده برای آموزش، **۲۰٪** برای تست.
- `random_state=42` برای تکرارپذیری.
- `stratify=y` (فقط برای طبقه‌بندی) تضمین می‌کند نسبت کلاس‌ها در train و test حفظ شود."""
    })

    # ---------- ۳. Pipeline ----------
    num_cols = [c.name for c in schema.columns if c.dtype == "numeric" and c.name != target]
    cat_cols = [c.name for c in schema.columns if c.dtype in ("categorical", "boolean") and c.name != target]
    
    pre_lines = []
    if num_cols:
        pre_lines.append(f'        ("num", StandardScaler(), {num_cols!r}),')
    if cat_cols:
        pre_lines.append(f'        ("cat", OneHotEncoder(handle_unknown="ignore"), {cat_cols!r}),')

    sections.append({
        "title": "۳. Pipeline پیش‌پردازش + مدل",
        "code": f'''from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
{model_import}

preprocessor = ColumnTransformer(
    transformers=[
{chr(10).join(pre_lines)}
    ],
    remainder="drop",
)

model = Pipeline([
    ("prep", preprocessor),
    ("model", {model_cls}(n_estimators=200, random_state=42, n_jobs=-1)),
])
''',
        "explanation": f"""**توضیح — مهم‌ترین بخش کد:**
- `ColumnTransformer` به‌صورت موازی ستون‌های عددی و متنی را پردازش می‌کند.
- `StandardScaler` داده‌های عددی را نرمال می‌کند.
- `OneHotEncoder` متن‌ها را به عدد (0/1) تبدیل می‌کند.
- **چرا Pipeline؟** اگر Scaling را بیرون از Pipeline انجام دهیم، دیتای تست به مدل «نشت» می‌کند (Data Leakage) که تقلب محسوب می‌شود. Pipeline این مشکل را حل می‌کند."""
    })

    # ---------- ۴. آموزش ----------
    sections.append({
        "title": "۴. آموزش مدل",
        "code": '''import time

t0 = time.time()
model.fit(X_train, y_train)
print(f"✅ آموزش در {time.time() - t0:.2f} ثانیه تمام شد.")
''',
        "explanation": """**توضیح:**
- `.fit()` کل Pipeline را آموزش می‌دهد: اول پیش‌پردازش یاد می‌گیرد، بعد مدل روی داده‌های تبدیل‌شده آموزش می‌بیند."""
    })

    # ---------- ۵. ارزیابی ----------
    if task == "classification":
        eval_code = '''from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\\nگزارش کامل:")
print(classification_report(y_test, y_pred))
print("\\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
'''
        eval_exp = """**توضیح معیارها:**
- **Accuracy**: درصد پیش‌بینی‌های درست.
- **Precision**: از بین موارد مثبت پیش‌بینی شده، چندتا واقعاً مثبت بودند.
- **Recall**: از بین تمام موارد مثبت واقعی، چندتا را پیدا کردیم.
- **F1**: میانگین هارمونیک Precision و Recall."""
    else:
        eval_code = '''from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

y_pred = model.predict(X_test)

mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")
'''
        eval_exp = """**توضیح معیارها:**
- **MAE**: میانگین قدرمطلق خطا (هم‌واحد با هدف).
- **RMSE**: ریشه میانگین مربعات خطا (خطاهای بزرگ را بیشتر جریمه می‌کند).
- **R²**: چه نسبتی از واریانس هدف توضیح داده شده (نزدیک به ۱ خوب است)."""
    
    sections.append({
        "title": "۵. ارزیابی روی تست",
        "code": eval_code,
        "explanation": eval_exp,
    })

    # ---------- ۶. ذخیره ----------
    sections.append({
        "title": "۶. ذخیره مدل",
        "code": '''import joblib

# ذخیره‌ی کل Pipeline (پیش‌پردازش + مدل با هم)
joblib.dump(model, "model.pkl")
print("✅ مدل ذخیره شد.")

# نحوه استفاده در آینده:
# loaded_model = joblib.load("model.pkl")
# loaded_model.predict(new_data)
''',
        "explanation": """**توضیح:**
- `joblib` برای ذخیره‌سازی سریع مدل‌های scikit-learn استفاده می‌شود.
- **مهم:** همیشه کل Pipeline را ذخیره کن، نه فقط مدل را. چون برای داده‌های جدید باید همان پیش‌پردازش هم اجرا شود."""
    })

    return sections