from django.shortcuts import render
from .converter import Converter

def index(request):
    context = {
        'env_var': 'hi',
    }
    return render(request, 'converter/index.html', context)


def convert_text(request):
    if request.method == "POST":
        feedback_text=request.POST.get('input_text')
        print(feedback_text)
    
