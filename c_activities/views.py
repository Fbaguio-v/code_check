from django.shortcuts import render, redirect, get_object_or_404
from .models import Activity, ActivitySubmission, ActivityExample
from a_classroom.models import Subject
from b_enrollment.models import UserProfile
from django.views import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from openai import OpenAI
import torch
import requests
import json

# Create your views here.
client = OpenAI(api_key=settings.OPENAI_API_KEY)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-multi").to(device)
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-multi")
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

def prompt_to_code(prompt, activity):
    outputs = pipe(prompt, max_length=100, num_return_sequences=5, do_sample=True, top_k=50, truncation=True)
    
    saved_examples = []
    for output in outputs:
        example = ActivityExample.objects.create(
            activity=activity,
            example_text=output['generated_text']
        )
        saved_examples.append(example.example_text)
    
    return saved_examples

def evaluate_student_code(instruction, code, examples):
    prompt = f"""
    Evaluate the following code based on.
    - *Instruction* : {instruction}
    - *Syntax* : Are there any syntax errors or formatting issues?
    - *Correctness* : Does the code logically perform the intended task?
    - *Structure* : Is the code well-structured and organized?

    Code:
    {code}

    Compare the code to the 5 examples given
    Example:
    {examples}

    Based on the criterias and examples provided grade the code from 1 to 100 and give an insight.
    Delete the **Instruction**, **Syntax**, **Correctnes**, and **Structure** only return an Insight and Grading of the code.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a Python and Java code reviewer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.5,
    )

    return response.choices[0].message.content

@method_decorator(never_cache, name='dispatch')
class CreateActivityView(View):
	def get(self, request):
		trigger = request.headers.get("HX-Trigger")
		if request.headers.get("HX-Request") == "true":
			if trigger == "form":
				subject_id = request.GET.get("subject_id")
				return render(request, "c_activities/create.activity.partial/create.activity.form.html", {"subject_id" : subject_id})
			elif trigger == "generate-code":
				subject_id = request.GET.get("subject_id")
				return render(request, "c_activities/create.activity.partial/generate.code.html", {"subject_id" : subject_id})

	def post(self, request):
		data = json.loads(request.body)
		subject_id = data.get("subject_id")
		title = data.get("title")
		description = data.get("description")
		max_score = data.get("max_score")
		due_at = data.get("due_at")

		print(f"Title : {title}\n Description : {description}\n Max Score : {max_score}\n Due At : {due_at}")

		subject = get_object_or_404(Subject, subject_id = subject_id)
		exists = Activity.objects.filter(subject = subject, title = title, description = description).exists()

		if exists:
			messages.error(request, "activity already existed.")
			return JsonResponse({"status" : 200, "message" : "activity already existed."})

		subject_instance = get_object_or_404(Subject, subject_id = subject_id)

		activity = Activity.objects.create(
					subject = subject_instance,
					title = title,
					description = description,
					max_score = max_score,
					due_at = due_at
				)
		code_examples = prompt_to_code(description, activity)
		messages.success(request, "Activity created successfully.")
		return JsonResponse({"status" : 200, "message" : "Activity created successfully.", "examples" : code_examples})

class StudentGradeView(View):
	def get(self, request):
		trigger = request.headers.get("HX-Trigger")
		submission_id = request.GET.get("submission_id")

		if request.headers.get("HX-Request") == "true" and submission_id:
			if trigger == "grade":
				return render(request, 'c_activities/activity.partial/student.score.html', {"submission_id": submission_id})
			elif trigger and trigger.startswith("replace-grade"):
				submission = get_object_or_404(ActivitySubmission, id=submission_id)
				score = submission.score
				return render(request, 'c_activities/activity.partial/student.score.html', {
					"submission_id": submission_id,
					"score": score
				})

		return HttpResponseBadRequest("Invalid request")

	def post(self, request):
		trigger = request.headers.get("HX-Trigger")
		if request.headers.get("HX-Request") == "true":
			if trigger == "score-form":
				submission_id = request.POST.get("submission-id")
				score = request.POST.get("score")
				submission = get_object_or_404(ActivitySubmission, id = submission_id)
				submission.score = int(score)
				submission.save()
				return HttpResponse(score)

		return HttpResponseBadRequest("Invalid POST request")

def get_activity_examples():
	examples = []
	example_text = ActivityExample.objects.all()
	for example in example_text:
		examples.append(example.example_text)

	return examples

class TurnInView(View):
	def post(self, request):
		json_data = json.loads(request.body)
		subject_id = json_data.get("subject_id")
		activity_id = json_data.get("activity_id")
		code = json_data.get("code")
		print("Subject ID:", subject_id)
		student = request.user
		subject = get_object_or_404(Subject, subject_id = subject_id)
		activity = get_object_or_404(Activity, subject = subject, activity_id = activity_id)

		if ActivitySubmission.objects.filter(student = student, activity = activity).exists():
			return JsonResponse({"error" : "You have already submitted this activity."}, status = 400)

		# saved_examples = list(activity.examples.values_list('example_text', flat=True)) this is for the 5 examples

		submission = ActivitySubmission.objects.create(
			student = student,
			activity = activity,
			submitted_code = code,
			submitted_at = timezone.now(),
			)

		instruction = activity.description

		examples = get_activity_examples()

		code = evaluate_student_code(instruction, code, examples)
		print(code)

		return JsonResponse({"subject_id" : subject_id, "activity_id" : activity_id, "message" : "Submission Successful."})