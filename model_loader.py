import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any
import os

class StartupSuccessModel:
    def __init__(self):
        """Load trained model, scaler, and feature names"""
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Load model
        model_path = os.path.join(BASE_DIR, 'models', 'startup_model.joblib')
        self.model = joblib.load(model_path)
        print("✓ Model loaded")
        
        # Load feature names
        feature_path = os.path.join(BASE_DIR, 'models', 'feature_names.joblib')
        self.feature_names = joblib.load(feature_path)
        print(f"✓ {len(self.feature_names)} features loaded")
        
        # Load scaler
        scaler_path = os.path.join(BASE_DIR, 'models', 'scaler.joblib')
        self.scaler = joblib.load(scaler_path)
        print("✓ Scaler loaded")
        
        print(f"First 10 features: {self.feature_names[:10]}")
    
    def apply_defaults(self, user_input: Dict[str, Any]) -> pd.DataFrame:
        """Convert user input + defaults to feature vector"""
        
        # Initialize all features with 0
        features = {feat: 0 for feat in self.feature_names}
        
        # Map user inputs to actual feature names (CORRECTED)
        if 'funding_total' in user_input:
            features['funding_total_usd'] = user_input['funding_total']
        
        if 'funding_rounds' in user_input:
            features['funding_rounds'] = user_input['funding_rounds']
        
        if 'relationships' in user_input:
            features['relationships'] = user_input['relationships']
        
        if 'milestones' in user_input:
            features['milestones'] = user_input['milestones']
        
        if 'avg_participants' in user_input:
            features['avg_participants'] = user_input['avg_participants']
        
        # Boolean features
        if 'has_vc' in user_input:
            features['has_VC'] = user_input['has_vc']
        
        if 'has_angel' in user_input:
            features['has_angel'] = user_input['has_angel']
        
        if 'has_series_a' in user_input:
            features['has_roundA'] = user_input['has_series_a']
        
        if 'is_top500' in user_input:
            features['is_top500'] = user_input['is_top500']
        
        if 'startup_age' in user_input:
            features['startup_age'] = user_input['startup_age']
        
        # Calculate derived features if columns exist
        if 'funding_velocity' in features and 'startup_age' in features:
            if features['startup_age'] > 0 and features['funding_total_usd'] > 0:
                features['funding_velocity'] = features['funding_total_usd'] / features['startup_age']
        
        if 'funding_per_round' in features and 'funding_rounds' in features:
            if features['funding_rounds'] > 0 and features['funding_total_usd'] > 0:
                features['funding_per_round'] = features['funding_total_usd'] / features['funding_rounds']
        
        # Create DataFrame with exact column order
        df = pd.DataFrame([features])
        df = df[self.feature_names]
        
        return df.fillna(0)
    
    def predict(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Full prediction pipeline"""
        # Step 1: Prepare features
        X = self.apply_defaults(user_input)
        
        # Step 2: Scale features
        X_scaled = self.scaler.transform(X)
        
        # Step 3: Predict
        probability = self.model.predict_proba(X_scaled)[0][1]
        prediction = "Acquired" if probability >= 0.5 else "Closed"
        confidence = max(probability, 1 - probability)
        
        # Step 4: Risk level
        if probability >= 0.75:
            risk_level = "Low"
        elif probability >= 0.5:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return {
            'prediction': prediction,
            'success_probability': round(float(probability), 4),
            'confidence': round(float(confidence), 4),
            'risk_level': risk_level
        }


# Global instance
model = StartupSuccessModel()
