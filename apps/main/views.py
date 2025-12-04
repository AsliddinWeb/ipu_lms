# apps/main/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests

from apps.courses.models import Course
from apps.accounts.models import User, Faculty


def landing_page(request):
    """Landing page"""
    # if request.user.is_authenticated:
    #     return redirect('accounts:dashboard')

    total_courses = Course.objects.filter(is_active=True).count()
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_faculties = Faculty.objects.count()
    popular_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:6]

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_faculties': total_faculties,
        'popular_courses': popular_courses,
    }
    return render(request, 'main/landing.html', context)


def about_page(request):
    """Biz haqimizda"""
    return render(request, 'main/about.html')


def contact_page(request):
    """Bog'lanish"""
    return render(request, 'main/contact.html')


@csrf_exempt
def chatbot_api(request):
    """AI Chatbot API"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Groq API ga so'rov
        response = get_ai_response(user_message)

        return JsonResponse({'response': response})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_ai_response(user_message):
    """Groq API orqali javob olish"""

    api_key = getattr(settings, 'GROQ_API_KEY', None)
    university_info = getattr(settings, 'UNIVERSITY_INFO', '')

    if not api_key:
        return fallback_response(user_message)

    system_prompt = f"""Sen IPU LMS platformasining yordamchi AI chatbotisan. 
Sening vazifang foydalanuvchilarga universitet va platforma haqida ma'lumot berish.

Quyidagi ma'lumotlardan foydalanib javob ber:

{university_info}

Qoidalar:
1. Faqat o'zbek tilida javob ber
2. Qisqa va aniq javob ber
3. Agar ma'lumot yo'q bo'lsa, "Bu haqida ma'lumotim yo'q" de
4. Doimo xushmuomala bo'l
5. Emoji ishlatishingiz mumkin
6. Agar savol universitet yoki LMS bilan bog'liq bo'lmasa, "Men faqat universitet va LMS haqida savollarga javob bera olaman" de
"""

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }

        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return fallback_response(user_message)

    except Exception as e:
        print(f"AI Error: {e}")
        return fallback_response(user_message)


def fallback_response(user_message):
    """API ishlamasa, oddiy javoblar"""

    message = user_message.lower()

    responses = {
        'salom': "Salom! 👋 Men IPU LMS yordamchisiman. Sizga qanday yordam bera olaman?",
        'qayerda': "📍 IPU Toshkent shahri, Mirzo Ulug'bek tumani, Ziyolilar ko'chasi, 9-uyda joylashgan.",
        'manzil': "📍 IPU Toshkent shahri, Mirzo Ulug'bek tumani, Ziyolilar ko'chasi, 9-uyda joylashgan.",
        'rektor': "👨‍💼 IPU rektori - Prof. Dr. Muzaffar Djalalov",
        'telefon': "📞 Telefon: +998 71 289 99 99",
        'email': "📧 Email: info@inha.uz",
        'kontrakt': "💰 Kontrakt narxi yo'nalishga qarab 22-33 million so'm atrofida.",
        'narx': "💰 Kontrakt narxi yo'nalishga qarab 22-33 million so'm atrofida.",
        'qabul': "📋 Qabul uchun: pasport, diplom/attestat, 3x4 rasm (6 dona), tibbiy ma'lumotnoma kerak.",
        'hujjat': "📋 Qabul uchun: pasport, diplom/attestat, 3x4 rasm (6 dona), tibbiy ma'lumotnoma kerak.",
        'fakultet': "📚 Fakultetlar: IT, Iqtisodiyot va menejment, Logistika va biznes",
        'ish vaqt': "⏰ Ish vaqti: Dushanba - Juma, 09:00 - 18:00",
        'website': "🌐 Website: https://inha.uz",
        'sayt': "🌐 Website: https://inha.uz",
        'rahmat': "Arzimaydi! 😊 Yana savollaringiz bo'lsa, bemalol so'rang.",
        'yordam': "Men quyidagilar haqida ma'lumot bera olaman:\n• Universitet manzili\n• Rektor haqida\n• Kontrakt narxi\n• Qabul hujjatlari\n• Fakultetlar\n• Aloqa ma'lumotlari",
    }

    for key, response in responses.items():
        if key in message:
            return response

    return "Kechirasiz, bu savolga javob bera olmadim. 🤔 Iltimos, universitet yoki LMS haqida savol bering. Masalan: 'Universitet qayerda joylashgan?' yoki 'Rektor kim?'"
