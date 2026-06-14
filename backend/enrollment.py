
import pandas as pd
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENROLLMENT_FILE = os.path.join(
    BASE_DIR,
    "customer_enrollments.xlsx"
)


def save_enrollment(
    name,
    age,
    phone,
    email,
    policy
):

    new_record = pd.DataFrame([
        {
            "Name": name,
            "Age": age,
            "Phone": phone,
            "Email": email,
            "Policy": policy
        }
    ])

    try:

        if os.path.exists(
            ENROLLMENT_FILE
        ):

            existing = pd.read_excel(
                ENROLLMENT_FILE
            )

            updated = pd.concat(
                [
                    existing,
                    new_record
                ],
                ignore_index=True
            )

        else:

            updated = new_record

        updated.to_excel(
            ENROLLMENT_FILE,
            index=False
        )

        return True

    except Exception as e:

        print(
            "Enrollment Error:",
            str(e)
        )

        return False
