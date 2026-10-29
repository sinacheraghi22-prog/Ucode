from core.excel_reader import read_excel_schema
from core.generators import basic_python

# ۱. خواندن ساختار فایل
schema = read_excel_schema("data.xlsx")

# ۲. تولید کدها
sections = basic_python.generate(schema)

# ۳. چاپ نتایج
print("تعداد بخش‌های تولید شده:", len(sections))
print("-" * 50)
for sec in sections:
    print(f"عنوان: {sec['title']}")
    print("کد تولید شده:")
    print(sec['code'][:100] + "...\n") # فقط ۱۰۰ کاراکتر اول کد رو چاپ می‌کنه