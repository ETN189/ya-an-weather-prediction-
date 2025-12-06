"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from bigdata import views as bigdata_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bigdata/", include("bigdata.urls")),  # 添加 bigdata 路由
    path("api/", include("bigdata.urls")),  # 添加 api 路由前缀
    path("", bigdata_views.root_api, name="root_api"),  # 支持 ?GetTodayWea=true
]
