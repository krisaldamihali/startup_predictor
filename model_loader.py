import os
import joblib
import pandas as pd
from typing import Dict, Any


class StartupSuccessModel:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.model = joblib.load(os.path.join(base_dir, "models", "startup_model.joblib"))
        self.feature_names = joblib.load(os.path.join(base_dir, "models", "feature_names.joblib"))
        self.scaler = joblib.load(os.path.join(base_dir, "models", "scaler.joblib"))

        print("✓ Model loaded")
        print(f"✓ {len(self.feature_names)} features loaded")
        print("✓ Scaler loaded")
        print(f"First 10 features: {self.feature_names[:10]}")
        if hasattr(self.model, "classes_"):
            print("Model classes_:", self.model.classes_)

    @staticmethod
    def _norm(val: Any) -> str:
        return str(val).strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    def _defaults_from_scaler_mean(self) -> Dict[str, float]:
        if hasattr(self.scaler, "mean_") and len(self.scaler.mean_) == len(self.feature_names):
            return {f: float(m) for f, m in zip(self.feature_names, self.scaler.mean_)}
        return {f: 0.0 for f in self.feature_names}

    def apply_defaults(self, user_input: Dict[str, Any]) -> pd.DataFrame:
        features = self._defaults_from_scaler_mean()

        # ----- numeric basics -----
        def set_if_exists(name, value):
            if name in features:
                features[name] = float(value)

        funding_total = float(user_input.get("funding_total", features.get("funding_total_usd", 0)) or 0)
        funding_rounds = int(user_input.get("funding_rounds", features.get("funding_rounds", 0)) or 0)
        startup_age = float(user_input.get("startup_age", features.get("startup_age", 0)) or 0)
        milestones = int(user_input.get("milestones", features.get("milestones", 0)) or 0)
        relationships = int(user_input.get("relationships", features.get("relationships", 0)) or 0)
        avg_participants = float(user_input.get("avg_participants", features.get("avg_participants", 0)) or 0)

        set_if_exists("funding_total_usd", funding_total)
        set_if_exists("funding_rounds", funding_rounds)
        set_if_exists("startup_age", startup_age)
        set_if_exists("milestones", milestones)
        set_if_exists("relationships", relationships)
        set_if_exists("avg_participants", avg_participants)

        # ----- booleans -----
        if "has_VC" in features:
            features["has_VC"] = int(user_input.get("has_vc", 0) or 0)
        if "has_angel" in features:
            features["has_angel"] = int(user_input.get("has_angel", 0) or 0)
        if "has_roundA" in features:
            features["has_roundA"] = int(user_input.get("has_roundA", 0) or 0)
        if "is_top500" in features:
            features["is_top500"] = int(user_input.get("is_top500", 0) or 0)

        for col in [
            "is_software", "is_web", "is_mobile", "is_enterprise", "is_advertising",
            "is_gamesvideo", "is_ecommerce", "is_biotech", "is_consulting", "is_othercategory"
        ]:
            if col in features:
                features[col] = 0

        cat = self._norm(user_input.get("category", "software"))
        cat_map = {
            "software": "is_software",
            "web": "is_web",
            "mobile": "is_mobile",
            "enterprise": "is_enterprise",
            "advertising": "is_advertising",
            "gamesvideo": "is_gamesvideo",
            "ecommerce": "is_ecommerce",
            "biotech": "is_biotech",
            "consulting": "is_consulting",
        }
        chosen_cat_col = cat_map.get(cat, "is_othercategory")
        if chosen_cat_col in features:
            features[chosen_cat_col] = 1

        for col in ["is_CA", "is_NY", "is_MA", "is_TX", "is_otherstate"]:
            if col in features:
                features[col] = 0

        st = self._norm(user_input.get("state", "other"))
        st_map = {"ca": "is_CA", "ny": "is_NY", "ma": "is_MA", "tx": "is_TX"}
        chosen_state_col = st_map.get(st, "is_otherstate")
        if chosen_state_col in features:
            features[chosen_state_col] = 1

        if "funding_per_round" in features:
            features["funding_per_round"] = (funding_total / funding_rounds) if funding_rounds > 0 else 0

        if "funding_velocity" in features:
            features["funding_velocity"] = (funding_total / startup_age) if startup_age > 0 else 0

        if "milestone_per_year" in features:
            features["milestone_per_year"] = (milestones / startup_age) if startup_age > 0 else 0

        if "relationships_per_year" in features:
            features["relationships_per_year"] = (relationships / startup_age) if startup_age > 0 else 0

        if "multiple_rounds" in features:
            features["multiple_rounds"] = 1 if funding_rounds >= 2 else 0

        if "has_both_vc_angel" in features:
            features["has_both_vc_angel"] = 1 if (features.get("has_VC", 0) == 1 and features.get("has_angel", 0) == 1) else 0

        if "strong_network" in features:
            features["strong_network"] = 1 if relationships >= 10 else 0

        if "early_stage" in features and "growth_stage" in features and "mature_stage" in features:
            features["early_stage"] = 1 if startup_age < 3 else 0
            features["growth_stage"] = 1 if (3 <= startup_age < 7) else 0
            features["mature_stage"] = 1 if startup_age >= 7 else 0

        if "in_major_hub" in features:
            features["in_major_hub"] = 1 if chosen_state_col in ("is_CA", "is_NY", "is_MA", "is_TX") else 0

        if "is_tech" in features:
            features["is_tech"] = 1 if chosen_cat_col in ("is_software", "is_web", "is_mobile", "is_enterprise", "is_ecommerce", "is_biotech") else 0

        if "hub_tech_combo" in features:
            features["hub_tech_combo"] = 1 if (features.get("in_major_hub", 0) == 1 and features.get("is_tech", 0) == 1) else 0

        df = pd.DataFrame([features])[self.feature_names].fillna(0)
        return df

    def predict(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        X = self.apply_defaults(user_input)
        X_scaled = self.scaler.transform(X)

        proba = self.model.predict_proba(X_scaled)[0]

        idx = 1
        if hasattr(self.model, "classes_"):
            classes = list(self.model.classes_)
            if any(str(c).lower() == "acquired" for c in classes):
                idx = [str(c).lower() for c in classes].index("acquired")
            elif 1 in classes:
                idx = classes.index(1)

        p_acquired = float(proba[idx])
        prediction = "Acquired" if p_acquired >= 0.5 else "Closed"
        confidence = max(p_acquired, 1 - p_acquired)

        if p_acquired >= 0.75:
            risk_level = "Low"
        elif p_acquired >= 0.5:
            risk_level = "Medium"
        else:
            risk_level = "High"

        return {
            "prediction": prediction,
            "success_probability": round(p_acquired, 4),
            "confidence": round(float(confidence), 4),
            "risk_level": risk_level,
        }


model = StartupSuccessModel()
