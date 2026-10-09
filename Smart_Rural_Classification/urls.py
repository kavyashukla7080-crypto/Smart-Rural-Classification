from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views as mainView
from admins import views as admins
from users import views as usr


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mainView.index, name='index'),
    path('index/', mainView.index, name='index'),
    path("UserRegister/", usr.UserRegisterActions, name="UserRegister"),
    path("AdminLogin/", mainView.AdminLogin, name="AdminLogin"),
    path("UserLogin/", mainView.UserLogin, name="UserLogin"),

    path("UserRegisterActions/", usr.UserRegisterActions, name="UserRegisterActions"),
    path("UserLoginCheck/", usr.UserLoginCheck, name="UserLoginCheck"),
    path("UserHome/", usr.UserHome, name="UserHome"),
    path("UserLogout/", usr.UserLogout, name="UserLogout"),

    # User module pages
    path("UserDataset/", usr.UserDataset, name="UserDataset"),
    path("UserTraining/", usr.UserTraining, name="UserTraining"),
    path("UserPrediction/", usr.UserPrediction, name="UserPrediction"),
    path("UserEDA/", usr.UserEDA, name="UserEDA"),

    path("AdminLoginCheck/", admins.AdminLoginCheck, name="AdminLoginCheck"),
    path("AdminHome/", admins.AdminHome, name="AdminHome"),
    path("ViewRegisteredUsers/", admins.ViewRegisteredUsers, name="ViewRegisteredUsers"),
    path("AdminActivaUsers/", admins.AdminActivaUsers, name="AdminActivaUsers"),
    path("DeleteUsers/", admins.DeleteUsers, name="DeleteUsers"),
    path("AdminLogout/", admins.AdminLogout, name="AdminLogout"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
