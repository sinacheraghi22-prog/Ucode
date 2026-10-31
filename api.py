"""Ucode API — بک‌اند FastAPI برای تولید کد از روی فایل اکسل."""
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import asdict

# ایمپورت کردن منطق اصلی پروژه (همون کدهای قبلی)
from core.excel_reader import read_excel_schema
from core.generators import basic_python, data_analysis, machine_learning

app = FastAPI(
    title="Ucode API",
    description="API تبدیل فایل اکسل به کد پایتون",
    version="1.0.0"
)

# تنظیم CORS (اجازه دادن به فرانت‌اند برای ارتباط با بک‌اند)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # فعلاً برای توسعه همه رو مجاز می‌کنیم
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Ucode API is running! ⚡"}

@app.post("/api/generate")
async def generate_code(
    file: UploadFile = File(...),
    generator: str = Form(...),
    target_col: str = Form(None)
):
    # ۱. خواندن فایل آپلود شده
    content = await file.read()
    
    try:
        # ۲. استخراج ساختار (استفاده از کد قبلی)
        schema = read_excel_schema(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"خطا در خواندن فایل: {str(e)}")

    # ۳. انتخاب Generator بر اساس درخواست کاربر
    try:
        if generator == "basic":
            sections = basic_python.generate(schema)
        elif generator == "eda":
            sections = data_analysis.generate(schema)
        elif generator == "ml":
            if not target_col:
                raise HTTPException(status_code=400, detail="برای یادگیری ماشین باید ستون هدف را انتخاب کنید.")
            sections = machine_learning.generate(schema, target_col)
        else:
            raise HTTPException(status_code=400, detail="نوع Generator نامعتبر است.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # ۴. آماده‌سازی اطلاعات ساختار برای ارسال به فرانت‌اند
    schema_dict = {
        "sheet_names": schema.sheet_names,
        "active_sheet": schema.active_sheet,
        "n_rows": schema.n_rows,
        "n_cols": schema.n_cols,
        "columns": [asdict(c) for c in schema.columns]
    }

    # ۵. برگرداندن جواب به صورت JSON
    return {
        "schema": schema_dict,
        "sections": sections
    }