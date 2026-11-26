import gspread
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

credentials_file = BASE_DIR / "EXP_TRK.json"

gc = gspread.service_account(
    filename=credentials_file
)

spreadsheet = gc.open_by_key(
    "11-9jG4JHnVQxwaJ5L6ZdQCYSJ9li48CU6siYidVOCdQ"
)


expense_sheet = spreadsheet.sheet1

user_sheet = spreadsheet.worksheet("User_Info")