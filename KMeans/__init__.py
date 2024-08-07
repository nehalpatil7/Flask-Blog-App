import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import ast
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

app = Flask(__name__)
CORS(app)
app.config["kmeans"] = None


def kmeans_model(num_clusters = None):
    industry_mapping = {
        "Books": 1,
        "Electronics": 2,
        "Industrial": 3,
        "Games": 4,
        "Clothing": 5,
        "Toys": 6,
        "Music": 7,
        "Grocery": 8,
        "Home": 9,
    }
    try:
        employee_data = pd.read_csv("employees.csv")
        employee_data["industry"] = employee_data["industry"].replace(industry_mapping)
        employee_data = employee_data.sample(frac=1).reset_index(drop=True)
        columns = ["industry", "annual_revenue", "no_employees", "no_female_employees"]

        silhouette_scores = []
        for n_clusters in range(2, 11):
            app.config["kmeans"] = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = app.config["kmeans"].fit_predict(employee_data[columns])
            silhouette_avg = silhouette_score(employee_data[columns], cluster_labels)
            silhouette_scores.append(silhouette_avg)

        # optimal_num_clusters = range(2, 11)[silhouette_scores.index(max(silhouette_scores))]
        # print("Optimal number of clusters based on silhouette score:", optimal_num_clusters)

        if num_clusters is None:
            app.config["kmeans"] = KMeans(n_clusters=6, random_state=42, n_init="auto")
        else:
            app.config["kmeans"] = KMeans(n_clusters=num_clusters, random_state=42)
        app.config["kmeans"].fit(employee_data[columns])
        return 1
    except Exception as e:
        return str(e)


def predict_insurer(company_data):
    print(company_data)
    try:
        if app.config["kmeans"] == None:
            kmeans_model()
        return app.config["kmeans"].predict([company_data])
    except Exception as e:
        return str(e)


@app.route("/")
def hello():
    return "<p>Hello, We are Insurance Guys!</p>"


@app.route("/retrain")
def train_model():
    try:
        num_clusters = request.args.get("num_clusters")
        result = kmeans_model(num_clusters)
        if result == 1:
            return jsonify({"message": "Model trained successfully"}), 200
        else:
            return jsonify({"message": "Model training failed"}), 501
    except Exception as e:
        return str(e)


@app.route("/get_quote")
def get_quote():
    industry_mapping = {
        "Books": 1,
        "Electronics": 2,
        "Industrial": 3,
        "Games": 4,
        "Clothing": 5,
        "Toys": 6,
        "Music": 7,
        "Grocery": 8,
        "Home": 9
    }
    insurance_mapping = {
        1: "Oscar",
        2: "Ambetter",
        3: "Blue Cross and Blue Shield of Illinois",
        4: "United Healthcare",
        5: "Cigna Healthcare",
        6: "Aetna",
    }
    try:
        if not app.config["kmeans"]:
            kmeans_model()
        request_data = request.json
        if request_data:
            company_name = request_data["company_name"]
            industry = request_data["industry"]
            annual_revenue = request_data["annual_revenue"]
            no_of_employees = request_data["no_of_employees"]
            no_female_employees = request_data["no_female_employees"]

            if industry in industry_mapping.keys():
                industry = industry_mapping[industry]
                predicted_insurer = predict_insurer(
                    [
                        industry,
                        float(annual_revenue),
                        int(no_of_employees),
                        int(no_female_employees),
                    ]
                )
            else:
                predicted_insurer = predict_insurer(
                    [
                        10,
                        float(annual_revenue),
                        int(no_of_employees),
                        int(no_female_employees),
                    ]
                )

            print("predicted_insurer", predicted_insurer)

            result = {
                "company_name": company_name,
                "industry": industry,
                "annual_revenue": annual_revenue,
                "no_of_employees": no_of_employees,
                "no_female_employees": no_female_employees,
                "predicted_insurer_id": predicted_insurer[0],
                "predicted_insurer": insurance_mapping[int(predicted_insurer[0]) + 1],
            }
            print(result)
            return jsonify({"message": "Model trained successfully", "data": result}), 200
        return "FAILED"
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run()
