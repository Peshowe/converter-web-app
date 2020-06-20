from django.shortcuts import render
from django.http import JsonResponse
from .converter import Converter

converter = Converter()

def index(request):
    context = {
    }
    return render(request, 'converter/index.html', context)


def convert_text(request):
    data = {}

    if request.method == "POST":
        text=request.POST.get('input_text')
        converted_text = converter.convertText(text)
        data['text'] = converted_text
        print(text)

    return JsonResponse(data)
