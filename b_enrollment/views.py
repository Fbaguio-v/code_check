from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import StudentSubject
from a_classroom.models import Subject
from .forms import UploadImageForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import json

# Create your views here.
class JoinClassView(View):
	def get(self, request):
		trigger = request.headers.get("HX-Trigger")
		if request.headers.get("HX-Request") == "true":
			if trigger == "join-class":
				return render(request, 'b_enrollment/form/form.html')

	def post(self, request):
		data = json.loads(request.body)
		subject_id = data.get("subject_id")

		subject = get_object_or_404(Subject, subject_id = subject_id)

		if subject.instructor == request.user:
			messages.error(request, 'You are the instructor of this class.')

		enrolled = StudentSubject.objects.filter(student = request.user, subject = subject).exists()
		if not enrolled:
			StudentSubject.objects.create(student = request.user, subject = subject)

			messages.success(request, 'You successfully enrolled in the subject!')

			return JsonResponse({"status": 200, "message": "You successfully enrolled!", "redirect_url": reverse("a_classroom:v", args=[subject.subject_id])})

		return JsonResponse({"status" : 200, "message" : "You joined a subject successfully."})

class UploadProfileView(View):
	def get(self, request):
		trigger = request.headers.get("HX-Trigger")
		if request.headers.get("HX-Request") == "true":
			form = UploadImageForm()
			if trigger == "upload-profile":
				return render(request, 'b_enrollment/profile/upload.profile.html', {"form" : form})

	def post(self, request):
		form = UploadImageForm(request.POST, request.FILES, instance=request.user.userprofile)
		if form.is_valid():
			form.save()
			messages.success(request, 'You successfully uploaded a profile photo!')
			return redirect("a_classroom:setting")

		return render(request, 'b_enrollment/profile/upload.profile.html', {"form" : form})