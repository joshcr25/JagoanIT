import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Start an MLflow run
with mlflow.start_run() as run:
    # Load data
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, random_state=42)

    # Train a model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Define a description for your model
    model_description = (
        "A RandomForestClassifier trained on the Iris dataset. "
        "This model predicts the species of iris flowers based on their "
        "sepal and petal measurements. It was trained with 100 estimators and a random state of 42."
    )

    # Log the model with a description
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="iris_rf_model",
        description=model_description,
        # You can also register the model directly
        registered_model_name="IrisRandomForestClassifier",
    )

    print(f"Model logged to: {mlflow.get_artifact_uri('iris_rf_model')}")
    print(f"Run ID: {run.info.run_id}")