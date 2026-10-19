from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from thesis.views import (
    home,
    thesis_list,
    thesis_detail,
    read_thesis,
    download_thesis,
)
from thesis.views import (
    home,
    user_login,
    user_logout,
    user_register,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("theses/",thesis_list,name="thesis_list"),
    path("theses/<int:pk>/",thesis_detail,name="thesis_detail"),
    path( "theses/<int:pk>/read/", read_thesis, name="read_thesis"),
    path( "theses/<int:pk>/download/",download_thesis,name="download_thesis"),
    path(
    "login/",
    user_login,
    name="login"
            ),

path(
    "logout/",
    user_logout,
    name="logout"
                ),
path(
    "register/",
    user_register,
    name="register"
),
]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)