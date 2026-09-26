/**
 * CardioCheck - Client-side Controller
 * Manages slider syncing, sample presets, AJAX risk calculation, and printable reports.
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('heart-prediction-form');
  const btnPredict = document.getElementById('btn-predict');
  const btnRandom = document.getElementById('btn-random-patient');
  const btnPrint = document.getElementById('btn-print-report');
  const presetButtons = document.querySelectorAll('.preset-btn');
  const patientNameInput = document.getElementById('input-patient-name');

  // Sliders and number inputs to sync
  const sliderMappings = [
    { slider: 'slider-age', input: 'input-age', pill: 'pill-val-age', suffix: ' years' },
    { slider: 'slider-resting-bp', input: 'input-resting-bp', pill: 'pill-val-resting-bp', suffix: ' mm Hg' },
    { slider: 'slider-cholesterol', input: 'input-cholesterol', pill: 'pill-val-cholesterol', suffix: ' mg/dL' },
    { slider: 'slider-max-hr', input: 'input-max-hr', pill: 'pill-val-max-hr', suffix: ' bpm' },
    { slider: 'slider-oldpeak', input: 'input-oldpeak', pill: 'pill-val-oldpeak', suffix: '' }
  ];

  // Synchronize range sliders & numeric inputs
  sliderMappings.forEach(item => {
    const sliderEl = document.getElementById(item.slider);
    const inputEl = document.getElementById(item.input);
    const pillEl = document.getElementById(item.pill);

    if (sliderEl && inputEl && pillEl) {
      sliderEl.addEventListener('input', (e) => {
        const val = e.target.value;
        inputEl.value = val;
        pillEl.textContent = val + item.suffix;
      });

      inputEl.addEventListener('input', (e) => {
        const val = e.target.value;
        sliderEl.value = val;
        pillEl.textContent = val + item.suffix;
      });
    }
  });

  // Handle Preset Patient selection
  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      presetButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const presetDataStr = btn.getAttribute('data-preset');
      if (!presetDataStr) return;

      try {
        const p = JSON.parse(presetDataStr);
        loadPatientData(p);
        calculateRisk();
      } catch (err) {
        console.error('Error parsing preset:', err);
      }
    });
  });

  // Random patient generator
  if (btnRandom) {
    btnRandom.addEventListener('click', () => {
      presetButtons.forEach(b => b.classList.remove('active'));
      const randomPatient = generateRandomPatient();
      loadPatientData(randomPatient);
      calculateRisk();
    });
  }

  // Print clinical summary
  if (btnPrint) {
    btnPrint.addEventListener('click', () => {
      window.print();
    });
  }

  // Intercept form submission for smooth AJAX
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      calculateRisk();
    });
  }

  /**
   * Load data into inputs
   */
  function loadPatientData(data) {
    if (patientNameInput && data.name) {
      patientNameInput.value = data.name;
    }

    setFieldValue('slider-age', 'input-age', 'pill-val-age', data.age, ' years');
    setFieldValue('slider-resting-bp', 'input-resting-bp', 'pill-val-resting-bp', data.resting_bp, ' mm Hg');
    setFieldValue('slider-cholesterol', 'input-cholesterol', 'pill-val-cholesterol', data.cholesterol, ' mg/dL');
    setFieldValue('slider-max-hr', 'input-max-hr', 'pill-val-max-hr', data.max_hr, ' bpm');
    setFieldValue('slider-oldpeak', 'input-oldpeak', 'pill-val-oldpeak', data.oldpeak, '');

    setRadioValue('sex', data.sex);
    setRadioValue('chest_pain', data.chest_pain);
    setRadioValue('fasting_bs', data.fasting_bs);
    setRadioValue('resting_ecg', data.resting_ecg);
    setRadioValue('exercise_angina', data.exercise_angina);
    setRadioValue('st_slope', data.st_slope);
  }

  function setFieldValue(sliderId, inputId, pillId, value, suffix) {
    const s = document.getElementById(sliderId);
    const i = document.getElementById(inputId);
    const p = document.getElementById(pillId);
    if (s) s.value = value;
    if (i) i.value = value;
    if (p) p.textContent = value + suffix;
  }

  function setRadioValue(name, value) {
    const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
    if (radio) {
      radio.checked = true;
    }
  }

  /**
   * Generate realistic patient data
   */
  function generateRandomPatient() {
    const names = ['Michael Chang', 'Emma Thompson', 'Carlos Rodriguez', 'Amina Patel', 'Thomas Becker', 'Linda Johnson'];
    const sexes = ['M', 'F'];
    const chestTypes = ['ASY', 'ATA', 'NAP', 'TA'];
    const ecgTypes = ['Normal', 'ST', 'LVH'];
    const slopes = ['Up', 'Flat', 'Down'];
    const anginas = ['Y', 'N'];
    const fasting = [0, 1];

    const age = Math.floor(Math.random() * (72 - 25 + 1)) + 25;
    return {
      name: names[Math.floor(Math.random() * names.length)],
      age: age,
      sex: sexes[Math.floor(Math.random() * sexes.length)],
      chest_pain: chestTypes[Math.floor(Math.random() * chestTypes.length)],
      resting_bp: Math.floor(Math.random() * (165 - 105 + 1)) + 105,
      cholesterol: Math.floor(Math.random() * (310 - 150 + 1)) + 150,
      fasting_bs: fasting[Math.floor(Math.random() * fasting.length)],
      resting_ecg: ecgTypes[Math.floor(Math.random() * ecgTypes.length)],
      max_hr: Math.floor(Math.random() * (190 - 95 + 1)) + 95,
      exercise_angina: anginas[Math.floor(Math.random() * anginas.length)],
      oldpeak: +(Math.random() * 3.2).toFixed(1),
      st_slope: slopes[Math.floor(Math.random() * slopes.length)]
    };
  }

  /**
   * Submit to API and render results
   */
  async function calculateRisk() {
    if (!form) return;

    if (btnPredict) {
      btnPredict.disabled = true;
      btnPredict.innerHTML = `
        <svg style="width:18px;height:18px;fill:currentColor;animation:spin 1s linear infinite;" viewBox="0 0 24 24">
          <path d="M12 4V2A10 10 0 0 0 2 12h2a8 8 0 0 1 8-8z"/>
        </svg>
        Calculating...
      `;
    }

    const formData = new FormData(form);
    const payload = {};
    formData.forEach((val, key) => {
      payload[key] = val;
    });

    try {
      const response = await fetch('/api/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(payload)
      });

      const res = await response.json();
      if (res.success && res.data) {
        renderResults(res.data, payload.patient_name || 'Patient');
      } else {
        alert('Assessment Error: ' + (res.error || 'Unable to compute risk.'));
      }
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      if (btnPredict) {
        btnPredict.disabled = false;
        btnPredict.innerHTML = `
          <svg style="width:18px;height:18px;fill:currentColor;" viewBox="0 0 24 24">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
          </svg>
          Calculate Heart Disease Risk
        `;
      }
    }
  }

  /**
   * Render results cleanly into the UI
   */
  function renderResults(data, patientName) {
    // Show results card and hide waiting placeholder
    const resultsCard = document.getElementById('results-card');
    const resultsPlaceholder = document.getElementById('results-placeholder');
    if (resultsPlaceholder) resultsPlaceholder.style.display = 'none';
    if (resultsCard) resultsCard.style.display = 'block';

    const riskPercentage = data.risk_percentage;
    const safePercentage = data.safe_percentage;

    // 1. Animate Score Number
    const riskNumEl = document.getElementById('risk-score-value');
    if (riskNumEl) {
      animateValue(riskNumEl, parseFloat(riskNumEl.textContent) || 0, riskPercentage, 600);
    }

    // 2. Verdict Banner
    const verdictBanner = document.getElementById('verdict-banner');
    const verdictIcon = document.getElementById('verdict-icon');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictDesc = document.getElementById('verdict-desc');

    if (verdictBanner && verdictTitle && verdictDesc) {
      if (data.is_high_risk) {
        verdictBanner.className = 'status-banner danger';
        if (verdictIcon) verdictIcon.textContent = '⚠️';
        verdictTitle.textContent = 'High Risk of Heart Disease Detected';
        verdictDesc.textContent = 'Statistical markers suggest elevated risk of coronary artery disease. A consultation with a cardiologist is recommended.';
      } else if (riskPercentage >= 30) {
        verdictBanner.className = 'status-banner warning';
        if (verdictIcon) verdictIcon.textContent = '⚠️';
        verdictTitle.textContent = 'Moderate / Borderline Risk';
        verdictDesc.textContent = 'Some indicators (such as blood pressure or cholesterol) are slightly elevated. Lifestyle modifications and monitoring are advised.';
      } else {
        verdictBanner.className = 'status-banner success';
        if (verdictIcon) verdictIcon.textContent = '✓';
        verdictTitle.textContent = 'Low Risk — Healthy Cardiovascular Profile';
        verdictDesc.textContent = 'Current clinical vitals and ECG results reflect a low probability of heart disease. Keep up healthy dietary and exercise habits.';
      }
    }

    // 3. Probability Meters
    const fillHigh = document.getElementById('fill-prob-high');
    const valHigh = document.getElementById('val-prob-high');
    const fillLow = document.getElementById('fill-prob-low');
    const valLow = document.getElementById('val-prob-low');

    if (fillHigh && valHigh) {
      fillHigh.style.width = `${riskPercentage}%`;
      valHigh.textContent = `${riskPercentage}%`;
    }
    if (fillLow && valLow) {
      fillLow.style.width = `${safePercentage}%`;
      valLow.textContent = `${safePercentage}%`;
    }

    // 4. Observations & Findings
    const factorsContainer = document.getElementById('factors-list-container');
    if (factorsContainer) {
      let html = '';

      if (data.risk_factors && data.risk_factors.length > 0) {
        data.risk_factors.forEach(f => {
          const cls = f.severity === 'high' ? 'danger' : 'warning';
          html += `
            <div class="finding-item ${cls}">
              <span>⚠️</span>
              <div><strong>${escapeHtml(f.name)}:</strong> ${escapeHtml(f.detail)}</div>
            </div>
          `;
        });
      }

      if (data.protective_factors && data.protective_factors.length > 0) {
        data.protective_factors.forEach(p => {
          html += `
            <div class="finding-item success">
              <span>✓</span>
              <div><strong>${escapeHtml(p.name)}:</strong> ${escapeHtml(p.detail)}</div>
            </div>
          `;
        });
      }

      factorsContainer.innerHTML = html;
    }

    // 5. Clinical Recommendations
    const recContainer = document.getElementById('recommendations-list');
    if (recContainer && data.recommendations) {
      recContainer.innerHTML = data.recommendations.map(r => `
        <li>${escapeHtml(r)}</li>
      `).join('');
    }

    // 6. Summary Table
    const summarySheet = document.getElementById('patient-summary-tbody');
    if (summarySheet && data.inputs) {
      summarySheet.innerHTML = `
        <tr><td>Patient Name</td><td>${escapeHtml(patientName)}</td></tr>
        <tr><td>Age & Gender</td><td>${data.inputs.age} years • ${data.inputs.sex}</td></tr>
        <tr><td>Resting Blood Pressure</td><td>${data.inputs.resting_bp}</td></tr>
        <tr><td>Serum Cholesterol</td><td>${data.inputs.cholesterol}</td></tr>
        <tr><td>Fasting Blood Sugar</td><td>${data.inputs.fasting_bs}</td></tr>
        <tr><td>Chest Pain Presentation</td><td>${data.inputs.chest_pain}</td></tr>
        <tr><td>Resting ECG</td><td>${data.inputs.resting_ecg}</td></tr>
        <tr><td>Max Heart Rate Reached</td><td>${data.inputs.max_hr}</td></tr>
        <tr><td>Exercise Induced Angina</td><td>${data.inputs.exercise_angina}</td></tr>
        <tr><td>ST Depression (Oldpeak)</td><td>${data.inputs.oldpeak}</td></tr>
        <tr><td>ST Segment Slope</td><td>${data.inputs.st_slope}</td></tr>
      `;
    }
  }

  function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const current = Math.floor(progress * (end - start) + start);
      obj.textContent = current;
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        obj.textContent = end;
      }
    };
    window.requestAnimationFrame(step);
  }

  function getCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
  }
});
