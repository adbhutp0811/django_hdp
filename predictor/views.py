import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ml_service import predict_heart_risk, get_model_info, PRESET_PATIENTS

def index(request):
    """
    Renders the main heart disease prediction interface.
    Supports both GET (initial page load) and POST (traditional form submission fallback).
    """
    context = {
        'presets': PRESET_PATIENTS,
        'model_info': get_model_info(),
        'default_patient': PRESET_PATIENTS['healthy'],
        'result': None,
        'form_data': PRESET_PATIENTS['healthy']
    }

    if request.method == 'POST':
        # Traditional form submission
        form_data = {
            'age': request.POST.get('age', 50),
            'sex': request.POST.get('sex', 'M'),
            'chest_pain': request.POST.get('chest_pain', 'ATA'),
            'resting_bp': request.POST.get('resting_bp', 120),
            'cholesterol': request.POST.get('cholesterol', 200),
            'fasting_bs': request.POST.get('fasting_bs', 0),
            'resting_ecg': request.POST.get('resting_ecg', 'Normal'),
            'max_hr': request.POST.get('max_hr', 140),
            'exercise_angina': request.POST.get('exercise_angina', 'N'),
            'oldpeak': request.POST.get('oldpeak', 0.0),
            'st_slope': request.POST.get('st_slope', 'Up'),
        }
        try:
            result = predict_heart_risk(form_data)
            context['result'] = result
            context['form_data'] = form_data
        except Exception as e:
            context['error'] = str(e)

    return render(request, 'predictor/index.html', context)


def api_predict(request):
    """
    JSON API endpoint for AJAX instant calculation.
    Accepts JSON body or POST form data.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        result = predict_heart_risk(data)
        return JsonResponse({'success': True, 'data': result})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def model_insights(request):
    """
    Renders the model architecture, feature breakdown, and diagnostic documentation.
    """
    model_info = get_model_info()
    return render(request, 'predictor/insights.html', {'model_info': model_info})
