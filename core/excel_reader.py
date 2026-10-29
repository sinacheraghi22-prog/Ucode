from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd

@dataclass
class ColumnInfo:
    """اطلاعات یک ستون از فایل اکسل"""
    name: str
    dtype: str          # نوع دسته‌بندی شده (numeric, categorical, datetime, boolean)
    pandas_dtype: str   # نوع دقیق پانداس (int64, object, ...)
    non_null: int       # تعداد مقادیر غیرخالی
    null: int           # تعداد مقادیر خالی
    unique: int         # تعداد مقادیر یکتا
    samples: List       # چند نمونه از مقادیر

@dataclass
class ExcelSchema:
    """شناسنامه کامل فایل اکسل"""
    sheet_names: List[str]
    active_sheet: str
    n_rows: int
    n_cols: int
    columns: List[ColumnInfo] = field(default_factory=list)

    def get(self, name: str) -> Optional[ColumnInfo]:
        """گرفتن اطلاعات یک ستون با اسمش"""
        return next((c for c in self.columns if c.name == name), None)

    @property
    def numeric(self): 
        return [c for c in self.columns if c.dtype == "numeric"]
    
    @property
    def categorical(self):  
        return [c for c in self.columns if c.dtype == "categorical"]
    
    @property
    def datetime(self):  
        return [c for c in self.columns if c.dtype == "datetime"]

def _classify(s: pd.Series) -> str:
    """تشخیص نوع ستون بر اساس دیتای پانداس"""
    if pd.api.types.is_bool_dtype(s):
        return "boolean"
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    return "categorical"

def read_excel_schema(file, sheet_name: Optional[str] = None) -> ExcelSchema:
    """تابع اصلی که فایل رو می‌خونه و شیء ExcelSchema رو برمی‌گردونه"""
    # ExcelFile اجازه میده اسم شیت‌ها رو ببینیم و بدونیم کدوم فعاله
    xls = pd.ExcelFile(file)
    sheet = sheet_name or xls.sheet_names[0]
    df = xls.parse(sheet)

    cols = []
    for col in df.columns:
        s = df[col]
        cols.append(ColumnInfo(
            name=str(col),
            dtype=_classify(s),
            pandas_dtype=str(s.dtype),
            non_null=int(s.notna().sum()),
            null=int(s.isna().sum()),
            unique=int(s.nunique()),
            samples=s.dropna().unique()[:3].tolist(), # ۳ نمونه اول غیرخالی
        ))
        return ExcelSchema(
        sheet_names=xls.sheet_names,
        active_sheet=sheet,
        n_rows=len(df),
        n_cols=df.shape[1],
        columns=cols,
    )

# ---------------- تست موقت ----------------
if __name__ == "__main__":
    # این بخش فقط وقتی اجرا میشه که خود فایل رو مستقیم ران کنی
    print("🔍 در حال خواندن data.xlsx...\n")
    
    schema = read_excel_schema("data.xlsx")
    
    print(f"📄 نام شیت: {schema.active_sheet}")
    print(f"📊 تعداد ردیف‌ها: {schema.n_rows}")
    print(f"📈 تعداد ستون‌ها: {schema.n_cols}\n")
    
    print("ساختار ستون‌ها:")
    print("-" * 50)
    for col in schema.columns:
        print(f"نام: {col.name}")
        print(f"  نوع: {col.dtype} ({col.pandas_dtype})")
        print(f"  گمشده: {col.null} | یکتا: {col.unique}")
        print(f"  نمونه‌ها: {col.samples}")
        print("-" * 50)