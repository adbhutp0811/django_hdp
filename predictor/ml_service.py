import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings

_MODEL = None
_SCALER = None
_COLUMNS = None

def get_ml_artifacts():
    """
    Lazy loads and caches the KNN model, standard scaler, and feature columns list.
    """
    global _MODEL, _SCALER, _COLUMNS
    if _MODEL is None or _SCALER is None or _COLUMNS is None:
        base_dir = settings.BASE_DIR
        model_path = os.path.join(base_dir, 'knn_heart_model.pkl')
        scaler_path = os.path.join(base_dir, 'heart_scaler.pkl')
        cols_path = os.path.join(base_dir, 'heart_columns.pkl')

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        if not os.path.exists(cols_path):
            raise FileNotFoundError(f"Columns file not found: {cols_path}")

        _MODEL = joblib.load(model_path)
        _SCALER = joblib.load(scaler_path)
        _COLUMNS = joblib.load(cols_path)
    return _MODEL, _SCALER, _COLUMNS


def get_model_info():
    """
    Returns metadata about the loaded ML model for analytics and display.
    """
    model, scaler, columns = get_ml_artifacts()
    return {
        'model_name': 'K-Nearest Neighbors Classifier',
        'n_neighbors': getattr(model, 'n_neighbors', 5),
        'metric': getattr(model, 'metric', 'minkowski'),
        'weights': getattr(model, 'weights', 'uniform'),
        'training_samples': getattr(model, '_fit_X', np.array([])).shape[0],
        'num_features': len(columns),
        'feature_names': columns,
        'scaler_type': type(scaler).__name__,
    }


def predict_heart_risk(data):
    """
    Predicts heart disease risk given user inputs.
    
    Expected keys in `data`:
    - age: int (18-100)
    - sex: 'M' or 'F'
    - chest_pain: 'ATA', 'NAP', 'TA', or 'ASY'
    - resting_bp: float/int (mm Hg)
    - cholesterol: float/int (mg/dL)
    - fasting_bs: int (0 or 1)
    - resting_ecg: 'Normal', 'ST', or 'LVH'
    - max_hr: float/int (bpm)
    - exercise_angina: 'Y' or 'N'
    - oldpeak: float (ST depression)
    - st_slope: 'Up', 'Flat', or 'Down'
    """
    model, scaler, expected_columns = get_ml_artifacts()

    # Parse and clean numerical values
    try:
        age = float(data.get('age', 50))
        resting_bp = float(data.get('resting_bp', 120))
        cholesterol = float(data.get('cholesterol', 200))
        fasting_bs = int(data.get('fasting_bs', 0))
        max_hr = float(data.get('max_hr', 140))
        oldpeak = float(data.get('oldpeak', 0.0))
        sex = str(data.get('sex', 'M')).strip().upper()
        chest_pain = str(data.get('chest_pain', 'ATA')).strip().upper()
        resting_ecg = str(data.get('resting_ecg', 'Normal')).strip()
        exercise_angina = str(data.get('exercise_angina', 'N')).strip().upper()
        st_slope = str(data.get('st_slope', 'Up')).strip()
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid input parameters: {e}")

    # Build raw feature dictionary matching one-hot encoded scheme
    raw_input = {
        'Age': age,
        'RestingBP': resting_bp,
        'Cholesterol': cholesterol,
        'FastingBS': fasting_bs,
        'MaxHR': max_hr,
        'Oldpeak': oldpeak,
        f'Sex_{sex}': 1,
        f'ChestPainType_{chest_pain}': 1,
        f'RestingECG_{resting_ecg}': 1,
        f'ExerciseAngina_{exercise_angina}': 1,
        f'ST_Slope_{st_slope}': 1,
    }

    # Create 1-row DataFrame and align with expected columns (defaulting unselected dummies to 0)
    input_df = pd.DataFrame([raw_input])
    for col in expected_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Ensure precise order
    input_df = input_df[expected_columns]

    # Scale inputs using fitted StandardScaler
    scaled_input = scaler.transform(input_df)

    # Make prediction & probability
    prediction = int(model.predict(scaled_input)[0])
    probabilities = model.predict_proba(scaled_input)[0]
    
    prob_low = round(float(probabilities[0]) * 100, 1)
    prob_high = round(float(probabilities[1]) * 100, 1)

    # Determine risk level category
    if prob_high >= 75:
        risk_level = "Critical High Risk"
        risk_color = "#ef4444"
        badge_class = "danger"
    elif prob_high >= 50:
        risk_level = "High Risk"
        risk_color = "#f97316"
        badge_class = "warning"
    elif prob_high >= 30:
        risk_level = "Moderate / Borderline Risk"
        risk_color = "#eab308"
        badge_class = "caution"
    else:
        risk_level = "Low / Normal Risk"
        risk_color = "#10b981"
        badge_class = "success"

    # Analyze clinical risk factors & protective factors
    risk_factors = []
    protective_factors = []
    recommendations = []

    # Blood Pressure analysis
    if resting_bp >= 140:
        risk_factors.append({
            'name': 'Stage 2 Hypertension',
            'detail': f'Resting Blood Pressure is elevated at {resting_bp:.0f} mm Hg (Goal: < 120 mm Hg).',
            'severity': 'high'
        })
        recommendations.append('Consult a physician regarding antihypertensive medication and sodium reduction.')
    elif resting_bp >= 130:
        risk_factors.append({
            'name': 'Stage 1 Hypertension',
            'detail': f'Resting Blood Pressure is elevated at {resting_bp:.0f} mm Hg.',
            'severity': 'medium'
        })
        recommendations.append('Adopt DASH diet guidelines and monitor BP weekly.')
    else:
        protective_factors.append({
            'name': 'Healthy Blood Pressure',
            'detail': f'Optimal resting blood pressure ({resting_bp:.0f} mm Hg).'
        })

    # Cholesterol analysis
    if cholesterol >= 240:
        risk_factors.append({
            'name': 'Severe Hypercholesterolemia',
            'detail': f'Serum cholesterol is high at {cholesterol:.0f} mg/dL (Desirable: < 200 mg/dL).',
            'severity': 'high'
        })
        recommendations.append('Schedule a full fasting lipid panel and evaluate statin/lipid-lowering therapy.')
    elif cholesterol >= 200:
        risk_factors.append({
            'name': 'Borderline High Cholesterol',
            'detail': f'Serum cholesterol is {cholesterol:.0f} mg/dL.',
            'severity': 'medium'
        })
        recommendations.append('Increase soluble fiber intake and restrict saturated fat consumption.')
    elif cholesterol > 0:
        protective_factors.append({
            'name': 'Desirable Cholesterol Level',
            'detail': f'Serum cholesterol within normal range ({cholesterol:.0f} mg/dL).'
        })

    # Fasting Blood Sugar
    if fasting_bs == 1:
        risk_factors.append({
            'name': 'Hyperglycemia (Fasting BS > 120 mg/dL)',
            'detail': 'Indicates pre-diabetes or diabetes, doubling vascular disease risk.',
            'severity': 'high'
        })
        recommendations.append('Conduct HbA1c screening to rule out or manage diabetes.')
    else:
        protective_factors.append({
            'name': 'Normal Fasting Glucose',
            'detail': 'Fasting blood sugar is within the normal non-diabetic range (<= 120 mg/dL).'
        })

    # ST Depression (Oldpeak)
    if oldpeak >= 2.0:
        risk_factors.append({
            'name': 'Significant ST Depression (Oldpeak >= 2.0)',
            'detail': f'Oldpeak at {oldpeak:.1f} indicates severe myocardial ischemia under stress.',
            'severity': 'high'
        })
        recommendations.append('Immediate evaluation by a cardiologist with stress echocardiogram or angiogram.')
    elif oldpeak >= 1.0:
        risk_factors.append({
            'name': 'Moderate ST Depression',
            'detail': f'Oldpeak at {oldpeak:.1f} suggests potential cardiac strain.',
            'severity': 'medium'
        })
    else:
        protective_factors.append({
            'name': 'Minimal/Normal ST Depression',
            'detail': f'Oldpeak ({oldpeak:.1f}) is within safe physiological limits.'
        })

    # ST Slope
    if st_slope.lower() == 'flat':
        risk_factors.append({
            'name': 'Flat ST Slope',
            'detail': 'A flat exercise ST segment is strongly correlated with coronary ischemia.',
            'severity': 'medium'
        })
    elif st_slope.lower() == 'down':
        risk_factors.append({
            'name': 'Downsloping ST Segment',
            'detail': 'Downsloping ST segment carries severe prognostic significance for coronary artery disease.',
            'severity': 'high'
        })
    else:
        protective_factors.append({
            'name': 'Upsloping ST Segment',
            'detail': 'Upsloping ST segments are typical of a healthy cardiac response during exercise.'
        })

    # Exercise Angina
    if exercise_angina == 'Y':
        risk_factors.append({
            'name': 'Exercise-Induced Angina',
            'detail': 'Chest discomfort triggered by physical exertion is a major red flag.',
            'severity': 'high'
        })
        recommendations.append('Avoid strenuous cardiovascular exertion until approved by a cardiologist.')
    else:
        protective_factors.append({
            'name': 'No Exertional Angina',
            'detail': 'No exercise-induced chest discomfort reported.'
        })

    # Chest Pain Type
    if chest_pain == 'ASY':
        risk_factors.append({
            'name': 'Asymptomatic Presentation (Silent Ischemia Risk)',
            'detail': 'Patients presenting with asymptomatic clinical referral frequently have occult ischemic disease.',
            'severity': 'medium'
        })
    elif chest_pain == 'TA':
        risk_factors.append({
            'name': 'Typical Angina Symptoms',
            'detail': 'Substernal chest pressure consistent with myocardial hypoxia.',
            'severity': 'medium'
        })

    # Resting ECG
    if resting_ecg == 'ST':
        risk_factors.append({
            'name': 'ST-T Wave Abnormality',
            'detail': 'ECG reveals T-wave inversions or ST deviations > 0.05 mV at rest.',
            'severity': 'medium'
        })
    elif resting_ecg == 'LVH':
        risk_factors.append({
            'name': 'Left Ventricular Hypertrophy (LVH)',
            'detail': 'Thickening of the heart muscle wall, often due to chronic hypertension.',
            'severity': 'medium'
        })
    else:
        protective_factors.append({
            'name': 'Normal Resting ECG',
            'detail': 'No baseline electrical conduction abnormalities detected.'
        })

    # Heart Rate & Age
    expected_max_hr = 220 - age
    if max_hr < 100:
        risk_factors.append({
            'name': 'Blunted Chronotropic Response',
            'detail': f'Achieved Max HR ({max_hr:.0f} bpm) is significantly below target (~{expected_max_hr:.0f} bpm).',
            'severity': 'medium'
        })
    else:
        protective_factors.append({
            'name': 'Robust Heart Rate Reserve',
            'detail': f'Maximum heart rate attained is {max_hr:.0f} bpm.'
        })

    # General healthy advice if few recommendations
    if not recommendations:
        recommendations.append('Maintain regular cardiovascular exercise (150 minutes/week moderate activity).')
        recommendations.append('Schedule annual cardiovascular preventative wellness exams.')

    return {
        'prediction': prediction,
        'is_high_risk': prediction == 1,
        'risk_level': risk_level,
        'risk_percentage': prob_high,
        'safe_percentage': prob_low,
        'risk_color': risk_color,
        'badge_class': badge_class,
        'risk_factors': risk_factors,
        'protective_factors': protective_factors,
        'recommendations': recommendations,
        'inputs': {
            'age': int(age),
            'sex': 'Male' if sex == 'M' else 'Female',
            'chest_pain': {
                'ASY': 'Asymptomatic (ASY)',
                'ATA': 'Atypical Angina (ATA)',
                'NAP': 'Non-Anginal Pain (NAP)',
                'TA': 'Typical Angina (TA)'
            }.get(chest_pain, chest_pain),
            'resting_bp': f"{resting_bp:.0f} mm Hg",
            'cholesterol': f"{cholesterol:.0f} mg/dL",
            'fasting_bs': 'Yes (> 120 mg/dL)' if fasting_bs == 1 else 'Normal (<= 120 mg/dL)',
            'resting_ecg': {
                'Normal': 'Normal',
                'ST': 'ST-T Wave Abnormality',
                'LVH': 'Left Ventricular Hypertrophy'
            }.get(resting_ecg, resting_ecg),
            'max_hr': f"{max_hr:.0f} bpm",
            'exercise_angina': 'Yes' if exercise_angina == 'Y' else 'No',
            'oldpeak': f"{oldpeak:.1f}",
            'st_slope': {
                'Up': 'Upsloping',
                'Flat': 'Flat',
                'Down': 'Downsloping'
            }.get(st_slope, st_slope)
        }
    }


# Preset clinical profiles for demonstration and testing
PRESET_PATIENTS = {
    'healthy': {
        'title': 'Healthy Active Adult',
        'subtitle': 'Low cardiovascular risk baseline',
        'age': 32,
        'sex': 'F',
        'chest_pain': 'ATA',
        'resting_bp': 112,
        'cholesterol': 175,
        'fasting_bs': 0,
        'resting_ecg': 'Normal',
        'max_hr': 178,
        'exercise_angina': 'N',
        'oldpeak': 0.0,
        'st_slope': 'Up'
    },
    'high_risk': {
        'title': 'Acute Cardiac Risk Patient',
        'subtitle': 'Hypertension, high cholesterol & ischemic changes',
        'age': 63,
        'sex': 'M',
        'chest_pain': 'ASY',
        'resting_bp': 160,
        'cholesterol': 288,
        'fasting_bs': 1,
        'resting_ecg': 'ST',
        'max_hr': 118,
        'exercise_angina': 'Y',
        'oldpeak': 2.6,
        'st_slope': 'Flat'
    },
    'borderline': {
        'title': 'Borderline / Moderate Risk',
        'subtitle': 'Middle-aged with mild hypertension & non-anginal pain',
        'age': 54,
        'sex': 'M',
        'chest_pain': 'NAP',
        'resting_bp': 135,
        'cholesterol': 225,
        'fasting_bs': 0,
        'resting_ecg': 'Normal',
        'max_hr': 142,
        'exercise_angina': 'N',
        'oldpeak': 1.0,
        'st_slope': 'Flat'
    },
    'athlete': {
        'title': 'Endurance Athlete',
        'subtitle': 'Low resting BP, high cardiac reserve',
        'age': 28,
        'sex': 'M',
        'chest_pain': 'ATA',
        'resting_bp': 105,
        'cholesterol': 160,
        'fasting_bs': 0,
        'resting_ecg': 'Normal',
        'max_hr': 195,
        'exercise_angina': 'N',
        'oldpeak': 0.0,
        'st_slope': 'Up'
    }
}
