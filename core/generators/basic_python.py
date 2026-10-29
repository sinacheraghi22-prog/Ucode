"""تولید کد پایتون پایه (بدون pandas) برای خواندن و پردازش اکسل."""
from typing import Dict, List
from core.excel_reader import ExcelSchema


def _pick_columns(schema: ExcelSchema):
    """یه ستون عددی و یه ستون متنی برای مثال انتخاب می‌کنه"""
    num = schema.numeric[0].name if schema.numeric else "نام_ستون_عددی"
    cat = schema.categorical[0].name if schema.categorical else "نام_ستون_متنی"
    return num, cat


def generate(schema: ExcelSchema) -> List[Dict]:
    """خروجی: لیستی از بخش‌ها، هر بخش شامل title, code, explanation."""
    num_col, cat_col = _pick_columns(schema)
    
    
    cat_sample = "مقدار_مورد_نظر"
    cat_info = schema.get(cat_col)
    if cat_info and cat_info.samples:
        cat_sample = cat_info.samples[0]

    sections = []

    # ---------- بخش ۱: باز کردن فایل ----------
    sections.append({
        "title": "۱. باز کردن فایل اکسل",
        "code": '''from openpyxl import load_workbook

wb = load_workbook("data.xlsx", data_only=True)
ws = wb.active

print("نام شیت :", ws.title)
print("ردیف‌ها :", ws.max_row)
print("ستون‌ها :", ws.max_column)
''',
        "explanation": """**این کد چه می‌کند؟**

- `load_workbook(path, data_only=True)` فایل اکسل را باز می‌کند.  
  پارامتر `data_only=True` باعث می‌شود به‌جای فرمول‌ها، **مقدار محاسبه‌شده** را بخوانیم.
- `wb.active` اولین شیت (شیت فعال) را انتخاب می‌کند.
- `ws.title` نام شیت، `ws.max_row` تعداد ردیف و `ws.max_column` تعداد ستون را برمی‌گرداند.

💡 **نکته:** `openpyxl` فقط فایل `.xlsx` را می‌خواند. برای `.xls` قدیمی از `xlrd` استفاده کن."""
    })

    # ---------- بخش ۲: حلقه روی ردیف‌ها ----------
    sections.append({
        "title": "۲. حلقه زدن روی ردیف‌ها (for loop)",
        "code": f'''# فرض: ستون «{num_col}» در فایل شما وجود دارد
# برای سادگی، ایندکس ستون دوم (1) را در نظر می‌گیریم
column_index = 1  

total = 0
count = 0

for row in ws.iter_rows(min_row=2, values_only=True):   # از ردیف ۲ (ردیف ۱ عنوان است)
    value = row[column_index]
    if value is None:
        continue                                        # اگر خالی بود رد کن
    total += value
    count += 1

average = total / count if count else 0
print("جمع :", total)
print("میانگین :", round(average, 2))
''',
        "explanation": f"""**این کد چه می‌کند؟**

- `ws.iter_rows(min_row=2, values_only=True)` ردیف‌ها را یکی‌یکی پیمایش می‌کند  
  و فقط **مقادیر** را برمی‌گرداند (نه آبجکت سلول).
- `min_row=2` یعنی از ردیف دوم شروع کن (چون ردیف اول معمولاً سرستون است).
- `row[column_index]` مقدار ستون موردنظر از هر ردیف را برمی‌دارد. (ایندکس در پایتون از صفر شروع می‌شود).
- `if value is None: continue` ردیف‌های خالی را نادیده می‌گیرد.
- در پایان مجموع و میانگین ستون «{num_col}» را چاپ می‌کنیم."""
    })

    # ---------- بخش ۳: شرط (فیلتر) ----------
    sections.append({
        "title": "۳. فیلتر کردن با شرط (if)",
        "code": f'''# فرض: ستون «{cat_col}» در ستون اول (ایندکس 0) قرار دارد
filter_value = "{cat_sample}"

matches = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[0] == filter_value:
        matches.append(row)

print(f"تعداد ردیف‌های با {{filter_value}} =", len(matches))
''',
        "explanation": f"""**این کد چه می‌کند؟**

- یک مقدار هدف (`filter_value`) تعیین می‌کنیم (در اینجا از داده‌های خودت نمونه برداشتیم: `{cat_sample}`).
- در حلقه، هر ردیف را با آن مقدار مقایسه می‌کنیم.
- اگر برابر بود، ردیف را به لیست `matches` اضافه می‌کنیم.
- در نهایت تعداد ردیف‌های مطابق را چاپ می‌کنیم.

💡 **مثال کاربرد:** فیلتر مشتری‌های یک شهر خاص، سفارش‌های یک تاریخ خاص، و غیره."""
    })

    # ---------- بخش ۴: تابع ----------
    sections.append({
        "title": "۴. بسته‌بندی در قالب تابع (function)",
        "code": f'''def load_rows(file_path: str):
    """همه‌ی ردیف‌های شیت اول را به‌صورت لیست دیکشنری برمی‌گرداند."""
    from openpyxl import load_workbook

    wb = load_workbook(file_path, data_only=True)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]          # ردیف اول = سرستون‌ها
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        rows.append(dict(zip(headers, row)))           # ترکیب سرستون با مقدار
    return rows


if __name__ == "__main__":
    data = load_rows("data.xlsx")
    print("تعداد ردیف‌ها:", len(data))
    print("نمونه دیتای ردیف اول:", data[0])
''',
        "explanation": """**این کد چه می‌کند؟**

- `load_rows` فایل اکسل را می‌خواند و هر ردیف را به یک **دیکشنری** تبدیل می‌کند:
  کلید = نام ستون، مقدار = مقدار آن ردیف.  
  این کار باعث می‌شود بعداً به‌جای `row[2]` بنویسیم `row["نام ستون"]` که خیلی خواناتر است.
- `ws[1]` ردیف اول (سرستون‌ها) را می‌گیرد.
- `dict(zip(headers, row))` سرستون‌ها را با مقادیر همان ردیف جفت می‌کند."""
    })

    return sections