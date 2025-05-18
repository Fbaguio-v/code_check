from django.urls import path
from . import views

app_name = "c_activities"
urlpatterns = [
	path("", views.CreateActivityView.as_view(), name="create-activity"),
	path("g/", views.StudentGradeView.as_view(), name="grade-a-student"),
	path("t/", views.TurnInView.as_view(), name="turn-in"),
]