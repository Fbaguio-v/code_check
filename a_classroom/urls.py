from django.urls import path
from . import views

app_name = "a_classroom"
urlpatterns = [
    path("", views.index, name="index"),
    #
    path("subject/<str:subject_id>/", views.view_subject, name="v"),
    #
    path("create/subject/", views.CreateSubjectView.as_view(), name="create-subject"),
    #
    path("approve/<int:user_id>/", views.ApproveUserAdminView.as_view(), name="approve"),
    path("activity/<str:activity_id>/", views.ActivityView.as_view(), name="view-activity"),
    path("settings/", views.user_settings, name="setting"),
    path("edit/", views.EditAccountView.as_view(), name="edit-account"),
    path("users/", views.AdminDashboardView.as_view(), name="get-users"),
    path("pending/", views.PendingUsersView.as_view(), name="pending-users"),
    path("subjects/", views.SubjectListView.as_view(), name="get-subjects"),
    path("archived/", views.ArchivedSubjectListView.as_view(), name="archived-subjects"),
]