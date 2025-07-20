from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("動脈入場紀錄").sheet1

def get_user_data(phone):
    records = sheet.get_all_records()
    for row in records:
        if str(row["手機號碼"]) == phone:
            return row["姓名"], row["教練"]
    return "", ""

@app.route("/", methods=["GET", "POST"])
def input_phone():
    if request.method == "POST":
        phone = request.form["phone"]
        name, coach = get_user_data(phone)
        is_new = (name == "" and coach == "")
        return render_template("form.html", phone=phone, name=name, coach=coach, is_new=is_new)
    return render_template("phone_only.html")

@app.route("/submit", methods=["POST"])
def submit():
    phone = request.form["phone"]
    purpose = request.form.get("purpose")
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
    sheet.append_row([now, phone, final_name, final_coach, purpose, custom])
    return render_template("done.html")

if __name__ == "__main__":
    app.run(debug=True)
