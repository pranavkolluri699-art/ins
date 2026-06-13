
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
print("API key loaded:",os.getenv("GROQ_API_KEY") )
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POLICY_FILE = os.path.join(
    BASE_DIR,
    "LIC_Policy_Details.xlsx"
)

ENROLLMENT_FILE = os.path.join(
    BASE_DIR,
    "customer_enrollments.xlsx"
)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


@app.route("/")
def home():
    return "Insura Backend Running Successfully"



@app.route("/search", methods=["POST"])
def search_policy():

    data = request.json

    question = data.get("question", "").lower()

    question = (
        question
        .replace("tell me about", "")
        .replace("explain", "")
        .replace("what is", "")
        .replace("give details of", "")
        .strip()
    )

    try:

        xl = pd.ExcelFile(POLICY_FILE)

        policy_context = ""

        for sheet in xl.sheet_names:

            df = pd.read_excel(
                POLICY_FILE,
                sheet_name=sheet
            )

            sheet_text = (
                sheet.lower()
                + " "
                + df.to_string().lower()
            )

            keywords = question.split()

            if any(
                word in sheet_text
                for word in keywords
            ):

                policy_context = (
                    f"Policy Name: {sheet}\n\n"
                    + df.to_string(index=False)
                )

                break

        if policy_context == "":

            return jsonify({
                "answer":
                "Sorry, I could not find a matching policy."
            })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content":
                    """
                    You are Insura,
                    an AI Insurance Assistant.

                    Explain LIC policies
                    in simple language.

                    Give concise,
                    customer-friendly answers.
                    """
                },
                {
                    "role": "user",
                    "content":
                    f"""
                    User Question:
                    {question}

                    Policy Information:
                    {policy_context}
                    """
                }
            ]
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        return jsonify({
            "answer": str(e)
        })



@app.route("/recommend", methods=["POST"])
def recommend_policy():

    data = request.json

    age = int(data.get("age", 0))
    goal = data.get("goal", "").lower()

    if age < 18:
        recommendation = "Amritbaal"

    elif "child" in goal:
        recommendation = "Amritbaal"

    elif "retirement" in goal:
        recommendation = "Jeevan Umang"

    elif "savings" in goal:
        recommendation = "New Jeevan Anand"

    else:
        recommendation = "Jeevan Labh"

    return jsonify({
        "answer":
        f"Recommended Policy: {recommendation}"
    })



@app.route("/chat", methods=["POST"])
def chat():

    data = request.json

    question = data.get(
        "question",
        ""
    )

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content":
                    """
                    You are Insura,
                    an AI Insurance Assistant.

                    Your responsibilities:

                    1. Explain LIC policies.
                    2. Recommend policies.
                    3. Help users enroll.

                    If the user wants a recommendation,
                    recommend suitable LIC plans.

                    If the user wants enrollment,
                    ask for:
                    Name,
                    Age,
                    Phone Number,
                    Email.

                    Always answer professionally.
                    """
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        return jsonify({
            "answer": str(e)
        })


@app.route("/enroll", methods=["POST"])
def enroll_customer():

    data = request.json

    new_record = pd.DataFrame([
        {
            "Name": data.get("name"),
            "Age": data.get("age"),
            "Phone": data.get("phone"),
            "Email": data.get("email"),
            "Policy": data.get("policy")
        }
    ])

    try:

        if os.path.exists(ENROLLMENT_FILE):

            existing = pd.read_excel(
                ENROLLMENT_FILE
            )

            updated = pd.concat(
                [existing, new_record],
                ignore_index=True
            )

        else:

            updated = new_record

        updated.to_excel(
            ENROLLMENT_FILE,
            index=False
        )

        return jsonify({
            "answer":
            "Enrollment Successful"
        })

    except Exception as e:

        return jsonify({
            "answer": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)
