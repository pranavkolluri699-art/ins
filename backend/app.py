from flask import Flask,request,jsonify
from flask_cors import CORS
import pandas as pd
app=Flask(__name__)
CORS(app)
excel_file="LIC_Policy_Details.xlsx"
@app.route("/policy",methods=["POST"])
def get_policy():
    data=request.json
    question=data["question"]
    xl=pd.ExcelFile(excel_file)
    result=""
    for sheet in xl.sheet_names:
        if question.lower() in sheet.lower():
            df=pd.read_excel(excel_file,sheet_name=sheet)
            result=df.to_string()
            break
    if result == "":
        result="Sorry, I couldnt find that policy."
    return jsonify({"answer":result})
if __name__=="__main__":
    app.run(debug=True)