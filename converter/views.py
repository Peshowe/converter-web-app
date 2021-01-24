from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from .converter import Converter

converter = Converter()
# max allowed input for the converter enpoint
MAX_LEN_INPUT = 15000


def index(request):
    context = {"max_input": MAX_LEN_INPUT}
    return render(request, "converter/index.html", context)


def convert_text(request):
    data = {}

    if request.method == "POST":
        text = request.POST.get("input_text")
        if len(text) > MAX_LEN_INPUT:
            # if exceeding max len, return 422 Unprocessable Entity
            return HttpResponse(status=422)

        converted_text = converter.convertText(text)
        data["text"] = converted_text

    return JsonResponse(data)
