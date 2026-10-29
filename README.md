# ⚡ Ucode

> **تبدیل هوشمند فایل اکسل به کد پایتون آماده اجرا — همراه با توضیحات خط‌به‌خط.**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ ویژگی‌ها

- 📤 **آپلود آسان** — فقط یک فایل `.xlsx` کافی است
- 🔍 **تشخیص خودکار ساختار** — نوع هر ستون (عددی، دسته‌ای، تاریخ) خودکار شناسایی می‌شود
- 🐍 **سه دسته کد:**
  - **پایتون پایه** — خواندن، حلقه، شرط، تابع (بدون pandas)
  - **تحلیل داده** — آمار توصیفی، مقدار گمشده، همبستگی، تمیزکاری
  - **یادگیری ماشین** — Pipeline کامل با scikit-learn + ارزیابی
- 🧠 **هوشمندی در ML** — تشخیص خودکار مسئله (طبقه‌بندی/رگرسیون) بر اساس ستون هدف
- 📖 **توضیحات خط‌به‌خط** — مناسب برای یادگیری
- ⬇️ **دانلود کد نهایی** — به‌صورت فایل `.py`

## 🚀 اجرای محلی

```bash
git clone https://github.com/YOUR_USERNAME/ucode.git
cd ucode
python -m venv .venv
# ویندوز:
.venv\Scripts\activate
# مک/لینوکس:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py