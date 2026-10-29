"""Ucode — تبدیل فایل اکسل به کد پایتون آماده اجرا."""
import streamlit as st
import pandas as pd
from io import BytesIO

from core.excel_reader import read_excel_schema
from core.generators import basic_python
# from core.generators import data_analysis, machine_learning # بعداً اضافه میشن

# ---------- تنظیمات صفحه ----------
st.set_page_config(
    page_title="Ucode | Portfolio",
    page_icon="⚡",
    layout="wide",
)

# RTL ساده (کدها LTR می‌مانند)
st.markdown(
    """
    <style>
    .stApp { direction: rtl; text-align: right; }
    [data-testid="stCodeBlock"] { direction: ltr; text-align: left; }
    [data-testid="stFileUploaderDropzone"] { direction: ltr; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- هدر ----------
st.title("⚡ Ucode")
st.caption(
    "فایل اکسل خود را آپلود کنید، نوع کدی که می‌خواهید را انتخاب کنید، "
    "و کد پایتون آماده‌ی اجرا با توضیحات کامل دریافت کنید."
)
st.divider()

# ---------- آپلود ----------
uploaded = st.file_uploader(
    "📤 فایل اکسل را اینجا رها کنید",
    type=["xlsx", "xls"],
    help="فرمت‌های پشتیبانی‌شده: .xlsx و .xls",
)

if uploaded is None:
    st.info("👉 برای شروع، یک فایل اکسل آپلود کنید.")
    st.stop()

# خواندن بایت‌ها (چون file pointer بعداً مصرف می‌شود)
raw = uploaded.getvalue()

# ---------- تشخیص ساختار ----------
try:
    schema = read_excel_schema(BytesIO(raw))
except Exception as e:
    st.error(f"خطا در خواندن فایل: {e}")
    st.stop()

# ---------- پیش‌نمایش ساختار ----------
st.subheader("🔍 ساختار فایل شما")

c1, c2, c3 = st.columns(3)
c1.metric("تعداد ردیف", f"{schema.n_rows:,}")
c2.metric("تعداد ستون", schema.n_cols)
c3.metric("شیت فعال", schema.active_sheet)

st.dataframe(
    pd.DataFrame([
        {
            "ستون": c.name,
            "نوع": c.dtype,
            "مقدار گمشده": c.null,
            "یکتا": c.unique,
            "نمونه": ", ".join(map(str, c.samples)) if c.samples else "—",
        }
        for c in schema.columns
    ]),
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ---------- نمایش بخش‌ها ----------
def render_sections(sections, key_prefix):
    for i, sec in enumerate(sections):
        with st.expander(f"**{sec['title']}**", expanded=(i == 0)):
            st.markdown("#### 📝 کد")
            st.code(sec["code"], language="python")
            st.markdown("#### 💡 توضیحات")
            st.markdown(sec["explanation"])

    # دکمه دانلود کل کد
    full = "\n\n".join(
        f"# {'=' * 60}\n# {s['title']}\n# {'=' * 60}\n\n{s['code']}"
        for s in sections
    )
    st.download_button(
        "⬇️ دانلود کل کد (فایل .py)",
        data=full,
        file_name=f"{key_prefix}_code.py",
        mime="text/x-python",
        use_container_width=True,
    )

# ---------- تب‌ها ----------
tab1, tab2, tab3 = st.tabs([
    "🐍 پایتون پایه",
    "📊 تحلیل داده (به‌زودی)",
    "🤖 یادگیری ماشین (به‌زودی)",
])

with tab1:
    st.markdown(
        "کدی ساده و بدون کتابخانه‌ی سنگین (فقط `openpyxl`) برای خواندن، "
        "پیمایش و پردازش فایل اکسل. مناسب برای یادگیری مفاهیم پایه."
    )
    sections = basic_python.generate(schema)
    render_sections(sections, "basic")

with tab2:
    st.info("این بخش در فازهای بعدی تکمیل می‌شود.")

with tab3:
    st.info("این بخش در فازهای بعدی تکمیل می‌شود.")