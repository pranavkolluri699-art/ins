
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI
from enrollment import save_enrollment

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POLICY_FILE = os.path.join(
    BASE_DIR,
    "LIC_Policy_Details.xlsx"
)

enrollment_state = {}
current_policy = ""


@app.route("/")
def home():
    return "Insura Backend Running Successfully"


@app.route("/chat", methods=["POST"])
def chat():

    global enrollment_state
    global current_policy

    data = request.json

    question = data.get(
        "question",
        ""
    )

    question_lower = question.lower()

    try:

        # Enrollment Flow

        if "enroll" in question_lower:

            current_policy = question

            enrollment_state = {
                "step": "name"
            }

            return jsonify({
                "answer":
                "Sure. Please tell me your full name."
            })

        if enrollment_state:

            if enrollment_state["step"] == "name":

                enrollment_state["name"] = question
                enrollment_state["step"] = "age"

                return jsonify({
                    "answer":
                    "Please enter your age."
                })

            elif enrollment_state["step"] == "age":

                enrollment_state["age"] = question
                enrollment_state["step"] = "phone"

                return jsonify({
                    "answer":
                    "Please enter your phone number."
                })

            elif enrollment_state["step"] == "phone":

                enrollment_state["phone"] = question
                enrollment_state["step"] = "email"

                return jsonify({
                    "answer":
                    "Please enter your email address."
                })

            elif enrollment_state["step"] == "email":

                enrollment_state["email"] = question

                save_enrollment(
                    enrollment_state["name"],
                    enrollment_state["age"],
                    enrollment_state["phone"],
                    enrollment_state["email"],
                    current_policy
                )

                enrollment_state = {}

                return jsonify({
                    "answer":
                    "Enrollment completed successfully."
                })

        # Policy Search

        policy_context = ""

        if os.path.exists(POLICY_FILE):

            xl = pd.ExcelFile(
                POLICY_FILE
            )

            for sheet in xl.sheet_names:

                df = pd.read_excel(
                    POLICY_FILE,
                    sheet_name=sheet
                )

                combined_text = (
                    sheet.lower()
                    + " "
                    + df.to_string().lower()
                )

                keywords = (
                    question_lower
                    .replace("tell me about", "")
                    .replace("explain", "")
                    .split()
                )

                if any(
                    word in combined_text
                    for word in keywords
                ):

                    policy_context += (
                        f"\nPolicy Name: {sheet}\n"
                        + df.head(5).to_string(index=False)
                        + "\n"
                    )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content":
                    """
                    You are Insura,
                    an AI Insurance Assistant.

                    You can:

                    1. Explain LIC policies.
                    2. Recommend policies.
                    3. Compare policies.
                    4. Help customers enroll.

                    Use policy information
                    if provided.

                    Give short,
                    professional answers.
                    keep the customer engaged.
                    keep responses under 150 words.
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


if __name__ == "__main__":
    app.run(
        debug=True
    )
