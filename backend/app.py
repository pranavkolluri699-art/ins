
from flask import Flask,request,jsonify
from flask_cors import CORS
import pandas as pd

app=Flask(__name__)
CORS(app)

EXCEL_FILE="LIC_Policy_Details.xlsx"

@app.route("/search",methods=["POST"])

def search_policy():

    data=request.json

    question=data["question"]

    xl=pd.ExcelFile(EXCEL_FILE)

    for sheet in xl.sheet_names:

        if question.lower() in sheet.lower():

            df=pd.read_excel(
                EXCEL_FILE,
                sheet_name=sheet
            )

            return jsonify({
                "answer":
                df.to_string()
            })

    return jsonify({
        "answer":
        "Policy not found"
    })

if __name__=="__main__":
    app.run(debug=True)
