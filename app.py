from flask import Flask, render_template, request
import pickle
import numpy as np
import json
import csv
import os

app = Flask(__name__)

# Load trained model
model = pickle.load(open("churn_prediction_model.pkl", "rb"))

# Load columns
with open("columns.json", "r") as f:
    columns = json.load(f)["data_columns"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.form

    # Server-side validation
    required_fields = [
        "tenure", "city_tier", "warehouse_to_home", "hour_spend_on_app",
        "number_of_device_registered", "satisfaction_score", "number_of_address",
        "complain", "order_amount_hike", "coupon_used", "order_count",
        "days_since_last_order", "cashback_amount", "gender", "marital_status"
    ]

    for field in required_fields:
        if field not in data or data[field] == "":
            return f"Error: Missing input for {field}", 400

    # One-hot encoding
    gender_female = 1 if data["gender"] == "Female" else 0
    gender_male = 1 if data["gender"] == "Male" else 0

    maritalstatus_divorced = 1 if data["marital_status"] == "Divorced" else 0
    maritalstatus_married = 1 if data["marital_status"] == "Married" else 0
    maritalstatus_single = 1 if data["marital_status"] == "Single" else 0

    # Final input feature list
    final_features = [
        int(data["tenure"]),
        int(data["city_tier"]),
        int(data["warehouse_to_home"]),
        int(data["hour_spend_on_app"]),
        int(data["number_of_device_registered"]),
        int(data["satisfaction_score"]),
        int(data["number_of_address"]),
        int(data["complain"]),
        int(data["order_amount_hike"]),
        int(data["coupon_used"]),
        int(data["order_count"]),
        int(data["days_since_last_order"]),
        float(data["cashback_amount"]),
        gender_female,
        gender_male,
        maritalstatus_divorced,
        maritalstatus_married,
        maritalstatus_single
    ]

    input_array = np.array(final_features).reshape(1, -1)

    prediction = model.predict(input_array)
    probability = model.predict_proba(input_array)[0][1]
    result = "Churn" if prediction[0] == 1 else "No Churn"

    # Logging to CSV
    log_file = "prediction_logs.csv"
    file_exists = os.path.isfile(log_file)

    # Convert to native types
    row = [float(x) if isinstance(x, (np.float32, np.float64)) 
           else int(x) if isinstance(x, (np.int32, np.int64)) 
           else x for x in final_features]
    row += [result, round(float(probability), 4)]

    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(columns + ["prediction", "probability"])
        writer.writerow(row)

    # Return result
    return render_template(
        "result.html",
        result=result,
        probability=round(probability, 4)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
