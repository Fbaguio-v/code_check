from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Section, Subject
from c_activities.models import Activity, ActivitySubmission
from b_enrollment.models import UserProfile, StudentSubject
from django.urls import reverse
import json
from django.http import JsonResponse, HttpResponseRedirect, HttpRequest
from .forms import CreateSubjectForm
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.core.paginator import Paginator
# Create your views here.
def index(request):
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, "Your account is incomplete. Please contact the administrator.")
        return redirect('register:login')

    if request.user.userprofile.role == "Admin":
        if request.headers.get("HX-Request") == "true":
            return render(request, 'a_classroom/sidebar/sidebar.html')
        return render(request, 'a_classroom/a.admin/admin.html')

    elif request.user.userprofile.role == "Instructor":
        subjects = Subject.objects.filter(instructor=request.user).order_by('-subject_id')
        if request.headers.get("HX-Request") == "true":
            return render(request, 'a_classroom/sidebar/sidebar.html', {"subjects": subjects})

        return render(request, 'a_classroom/b.instructor/instructor.html', {"subjects" : subjects})

    elif request.user.userprofile.role == "Student":
        subjects = list(request.user.joined_subjects.all())
        if request.headers.get("HX-Request") == "true":
            return render(request, 'a_classroom/sidebar/sidebar.html', {"subjects" : subjects})

        return render(request, 'a_classroom/c.student/student.html', {"subjects" : subjects})

    return render(request, 'a_classroom/index.html')

@method_decorator(never_cache, name='dispatch')
class CreateSubjectView(View):
    def get(self, request):
        form = CreateSubjectForm()
        sections = Section.objects.all()
        return render(request, 'a_classroom/create_subject.html', {"form": form, "sections" : sections})
    
    def post(self, request):
        form = CreateSubjectForm(request.POST)
        if form.is_valid():
            course_code = form.cleaned_data["course_code"]
            section_name = form.cleaned_data["section_name"]
            name = form.cleaned_data["name"]

            section, created = Section.objects.get_or_create(name=section_name)

            subject = Subject.objects.filter(
                instructor=request.user, 
                course_code=course_code,
                section=section, 
                name=name).first()

            if subject:
                messages.error(request, f"{course_code} for section {section_name} already exists.")
            else:
                subject = Subject.objects.create(
                    instructor=request.user,
                    course_code=course_code,
                    section=section,
                    name=name
                )
                messages.success(request, f"{course_code} for section {section_name} has been created.")
            
            form = CreateSubjectForm() 
            
            return HttpResponseRedirect(reverse("a_classroom:v", args=[subject.subject_id]))

        return render(request, 'a_classroom/create_subject.html', {"form": form})

def user_settings(request):
    user_profile = UserProfile.objects.select_related('user').get(user = request.user)
    email = request.user.email
    return render(request, 'a_classroom/setting.html', {"user_profile" : user_profile, "email" : email})

@never_cache
def view_subject(request, subject_id):
    subject = get_object_or_404(Subject, subject_id = subject_id)
    activities = subject.activities.all().order_by('-created_at')
    students = subject.students.all()
    instructor = subject.instructor.get_full_name()
    trigger = request.headers.get("HX-Trigger")
    if request.headers.get("HX-Request") == "true":
        if trigger == "subject":
            return render(request, 'a_classroom/subject.partials/subject.html', {
                "subject" : subject,
                "activities" : activities
            })
        elif trigger == "classwork":
            return render(request, 'a_classroom/subject.partials/classworks.html', {
                "activities" : activities
            })
        elif trigger == "students":
            return render(request, 'a_classroom/subject.partials/people.html', {
                "subject" : subject,
                "instructor" : instructor,
                "students" : students
            })
    return render(request, 'a_classroom/subject_view.html', {"subject" : subject})

class EditAccountView(View):
    def get(self, request):
        trigger = request.headers.get("HX-Trigger")
        if request.headers.get("HX-Request") == "true":
            if trigger == "edit-account":
                user = get_object_or_404(User, id = request.user.id)
                return render(request, 'a_classroom/profile/edit.account.html', {"user" : user})

    def post(self, request):
        user = get_object_or_404(User, id = request.user.id)

        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        if password:
            user.set_password(password)
            update_session_auth_hash(request, user)

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, 'You profile has been updated successfully!')

        return redirect('a_classroom:setting')

class ActivityView(View):
    def get(self, request, activity_id):
        subject_id = request.GET.get('subject_id')
        user_profile = UserProfile.objects.select_related('user').get(user = request.user)
        subject = get_object_or_404(Subject, subject_id = subject_id)
        activity = get_object_or_404(Activity, subject = subject, activity_id = activity_id)
        if request.user.userprofile.role == "Instructor":
            submissions = ActivitySubmission.objects.filter(activity = activity).select_related('student')
            return render(request, 'c_activities/activity.partial/student.submission.html', {"submissions" : submissions, "user_profile" : user_profile, "subject_id" : subject_id})
        elif request.user.userprofile.role == "Student":
            submission = ActivitySubmission.objects.filter(activity = activity, student = request.user).first()
            submissions = [submission] if submission else []
            return render(request, 'c_activities/activity.partial/student.compiler.html', {"activity" : activity, "submissions" : submissions, "user_profile" : user_profile, "subject_id" : subject_id, "subject" : subject})
        return HttpResponse("Unhandled request case.", status=400)

class HtmxTemplateView(View):
    queryset = None
    template = None
    htmx_template = None
    htmx_trigger = None
    context_name = None

    def get(self, request: HttpRequest):
        data = self.queryset() if callable(self.queryset) else self.queryset
        trigger = request.headers.get("HX-Trigger")

        if request.headers.get("HX-Request") == "true" and trigger == self.htmx_trigger:
            return render(request, self.htmx_template, {self.context_name: data})

        return render(request, self.template, {self.context_name: data})

class AdminDashboardView(HtmxTemplateView):
    queryset = User.objects.all
    template = 'a_classroom/a.admin/admin.html'
    htmx_template = 'a_classroom/a.admin/users/users.html'
    htmx_trigger = 'all-user'
    context_name = 'all_users'

class PendingUsersView(HtmxTemplateView):
    queryset = lambda self: User.objects.filter(is_active=False)
    template = 'a_classroom/a.admin/users/pending.html'
    htmx_template = 'a_classroom/a.admin/users/pending/pending.users.html'
    htmx_trigger = 'pending'
    context_name = 'pending_users'

class SubjectListView(HtmxTemplateView):
    queryset = Subject.objects.all
    template = 'a_classroom/a.admin/users/subject.html'
    htmx_template = 'a_classroom/a.admin/users/subject/subjects.html'
    htmx_trigger = 'all-subject'
    context_name = 'subjects'

class ArchivedSubjectListView(HtmxTemplateView):
    queryset = lambda self: Subject.objects.filter(is_archived=True)
    template = 'a_classroom/a.admin/users/archived.html'
    htmx_template = 'a_classroom/a.admin/users/subject/archived.subjects.html'
    htmx_trigger = 'archived'
    context_name = 'archived_subjects'

class ApproveUserAdminView(View):
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        trigger = request.headers.get("HX-Trigger")

        if request.headers.get("HX-Request") == "true" and trigger == "approve-button":
            user.is_active = True
            user.save()

            # Send approval email
            subject = "Your Account Has Been Approved"
            message = f"""Hello {user.first_name},

            Your account has been approved by the admin.

            If you signed up with Google, your default password is 123. Please change your password after logging in.
            If you registered normally, your account is now active and ready to use.

            Best regards,  
            Admin Team
            """
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            except Exception as e:
                print(f"❌ Email send failed: {e}")
            pending_users = User.objects.filter(is_active=False)
            return render(
                request,
                'a_classroom/a.admin/users/pending/pending.users.html',
                {"pending_users": pending_users}
            )

        return JsonResponse({"message": "This endpoint only handles HTMX requests"}, status=400)
