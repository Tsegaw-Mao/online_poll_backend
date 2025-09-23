from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PollViewSet, UserRegisterView, logout_view, cast_vote

router = DefaultRouter()
router.register(r'polls', PollViewSet, basename="poll")

urlpatterns = [
    # Auth
    path("auth/register/", UserRegisterView.as_view(), name="user-register"),
    path("auth/logout/", logout_view, name="user-logout"),

    # Poll voting
    path("vote/", cast_vote, name="vote"),

    # Poll CRUD
    path("", include(router.urls)),
]
