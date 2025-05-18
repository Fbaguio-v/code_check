from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
import requests
import json
import time

# Create your views here.
class RunCodeView(View):
    def get(self, request):
        return render(request, 'd_compiler/playground.html')
    def post(self, request):
        json_data = json.loads(request.body)
        test_data = json_data.get("test_data")
        code = json_data.get("code")
        language_id = json_data.get("language")
        if not language_id or not code:
            return JsonResponse({"error": "Missing code or language ID"}, status=400)
        try:
            language_id = int(language_id)
        except ValueError:
            return JsonResponse({"error" : "Invalid language ID"}, status=400)

        data = {
            "source_code": code,
            "language_id": language_id,
            "stdin": "",
        }

        response = requests.post(f"{settings.JUDGE0_URL}?base64_encoded=false&wait=false", headers= settings.HEADERS, json=data)
        response_data = response.json()

        if "token" not in response_data:
            return JsonResponse({"error": "Submission failed"}, status=500)

        token = response_data["token"]
        result_url = f"{settings.JUDGE0_URL}/{token}?base64_encoded=false"

        for _ in range(10):
            result_response = requests.get(result_url, headers= settings.HEADERS)
            result_data = result_response.json()

            if result_data["status"]["id"] in [1, 2]:
                time.sleep(1)
                continue
            return JsonResponse({"result": result_data})

        return JsonResponse({"error": "Timeout retrieving result"}, status=500)