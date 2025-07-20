import gspread
from google.oauth2.service_account import Credentials

# 用你的 credentials.json 路徑
creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

# 建立 client 物件
client = gspread.authorize(creds)

# 連線到 Google Sheet（請換成你要連線的試算表 ID）
spreadsheet_id = "1IgsKwmdFU8Pj5V1e__Xa6bveH4YUaW8AbW4-_KoREMk"
sheet = client.open_by_key(spreadsheet_id).sheet1

# 測試讀取 A1
print("A1 儲存格內容：", sheet.acell("A1").value)
