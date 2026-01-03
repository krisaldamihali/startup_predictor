import joblib

# Load and print the feature names
feature_names = joblib.load('models/feature_names.joblib')
print("Total features:", len(feature_names))
print("\nAll features:")
for i, feat in enumerate(feature_names):
    print(f"{i+1}. {feat}")