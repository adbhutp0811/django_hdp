# CardioGuard AI - Django Heart Disease Risk Assessment System

A modern clinical decision support web application built with **Django**, **Vanilla CSS**, and **Scikit-Learn**, powered by the trained **K-Nearest Neighbors (KNN)** classification pipeline and **StandardScaler**.

---

## 🔬 Model Artifacts Analyzed

The system integrates the 3 machine learning artifacts in this directory:

1. **`heart_columns.pkl`**:
   - Contains the 15 expected feature columns in exact ordering:
     `['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'Oldpeak', 'Sex_M', 'ChestPainType_ATA', 'ChestPainType_NAP', 'ChestPainType_TA', 'RestingECG_Normal', 'RestingECG_ST', 'ExerciseAngina_Y', 'ST_Slope_Flat', 'ST_Slope_Up']`
2. **`heart_scaler.pkl`**:
   - Pre-fitted `StandardScaler` used to normalize incoming patient biometrics to zero mean and unit variance.
3. **`knn_heart_model.pkl`**:
   - Scikit-Learn `KNeighborsClassifier` (k=5 neighbors, Minkowski metric, uniform weights) trained on 734 clinical patient records.

---

## 🚀 How to Run the Django Application

The server is currently running locally at:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

To manually run or restart the server in the future:

```bash
python manage.py runserver 127.0.0.1:8000
```

---

## 🌟 Key Application Features

- **Clinical Glassmorphism UI**: High-contrast modern medical dark theme with responsive typography, animated heartbeat pulse, and glowing feedback.
- **1-Click Clinical Presets Toolbar**:
  - 🟢 **Healthy Adult**: 32y female baseline with normal ECG and upsloping ST.
  - 🏃 **Endurance Athlete**: 28y male with 195 bpm max HR capacity and optimal lipids.
  - 🟡 **Borderline Case**: 54y male with mild stage 1 hypertension and flat ST slope.
  - 🔴 **Critical Cardiac Alert**: 63y male with severe hypertension, high cholesterol, exertional angina, and ST depression.
- **Dynamic Risk Gauge / Meter**: Animated circular gauge displaying predicted heart disease risk from 0% to 100%.
- **Live Biomarker Breakdown**: Identifies exact risk flags (hypertension stages, hypercholesterolemia, diabetic fasting sugar, ischemic ST depression, flat/downsloping ST segments) and protective factors.
- **Physician Next-Steps & Lifestyle Recommendations**: Actionable next clinical steps tailored to entered values.
- **Instant Random Cohort Generator**: One-click generation of realistic randomized patient parameters.
- **Print / PDF Summary Report**: Formatted clinical datasheet ready to print or save to PDF.
- **Model Insights Page** (`/insights/`): Comprehensive documentation of the 15 features, KNN parameters, and Kaggle/UCI benchmark dataset background.
