from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Google Sheets API 授權範圍
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# 載入憑證
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# 開啟 Google Sheet（換成你的試算表ID）
spreadsheet = client.open_by_key('1hS1cv7r4a7ZouAGy6yxCqYSbVLl9AcfXsRObsYaClk4')
sheet = spreadsheet.worksheet("ans")  # 選擇第一個工作表

# 取得會員資料（用手機號碼查詢）
def get_user_data(phone):
    try:
        records = sheet.get_all_records()
        phone_last9 = phone[-9:]
        print(f"[DEBUG] 所有會員資料: {records}")  # ← 加這行
        for record in records:
            sheet_phone = str(record.get('手機號碼'))
            # 取sheet手機號碼最後9碼比對
            sheet_phone_last9 = sheet_phone[-9:]
            if sheet_phone_last9 == phone_last9:
                return record.get('姓名', ''), record.get('教練', '')
        print(f"[DEBUG] 沒有找到手機號碼：{phone}")
    except Exception as e:
        print(f"[ERROR] get_user_data 發生錯誤：{e}")
    return '', ''


@app.route("/", methods=["GET", "POST"])
def input_phone():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        name, coach = get_user_data(phone)
        is_new = (name == "" and coach == "")
        print(f"[DEBUG] 收到手機號碼: {phone}, 姓名: {name}, 教練: {coach}, 是否新會員: {is_new}")
        # 傳 readonly 狀態給 template 控制欄位是否可編輯
        readonly = not is_new
        return render_template("form.html", phone=phone, name=name, coach=coach, readonly=readonly)
    return render_template("phone_only.html")

@app.route("/submit", methods=["POST"])
def submit():
    phone = request.form.get("phone", "").strip()
    purpose = request.form.get("purpose", "")
    custom = request.form.get("custom", "")
    name = request.form.get("name", "").strip()
    coach = request.form.get("coach", "").strip()

    old_name, old_coach = get_user_data(phone)
    if old_name == "" and old_coach == "":
        final_name = name
        final_coach = coach
    else:
        final_name = old_name
        final_coach = old_coach

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 寫入時間、手機號碼、姓名、教練、入場目的、補充說明
    sheet.append_row([now, phone, final_name, final_coach, purpose, custom])
    return render_template("done.html")

if __name__ == "__main__":
    app.run(debug=True)
