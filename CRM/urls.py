"""
URL configuration for Perfect_CRM project.

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


from django.urls import path
from CRM import views

urlpatterns = [
    # 首页（你原来的 index）
    path('', views.index, name='index'),                    # /CRM/ 或根路径 include 时用
    path('index.html', views.index, name='index_html'),     # /CRM/index.html

    # 客户列表
    path('customers/', views.customer_list, name='customer_list'),

    # 文本生成 API
    path('api/generate/', views.generate_text, name='api_generate'),
]

