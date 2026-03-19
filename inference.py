from database import get_db

def diagnose(symptoms):
    conn = get_db()
    rules = conn.execute("SELECT * FROM rules").fetchall()
    conn.close()

    for rule in rules:
        conditions = [c.strip() for c in rule["conditions"].split(",")]

        if all(cond in symptoms for cond in conditions):
            return {
                "disease": rule["disease"],
                "treatment": rule["treatment"],
                "cf": rule["cf"],
                "conditions": conditions,
                "input_symptoms": symptoms   # 👈 ADD THIS
            }

    return None