"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from app01 import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 注册登录注销
    url(r'^register/', views.register, name='register'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),

    # 好友管理
    url(r'^friends/', views.friends, name='friendsList'),
    url(r'^delete/', views.deleteFriend, name='delete'),                                # 删除好友
    url(r'^addFriend/', views.addFriend, name='addFriend'),
    url(r'^friend_request/', views.friend_request, name='friend_request'),         # 匹配范围越大，写在越后
    url(r'^seeData/', views.seeData, name='seeData'),                   # 查看资料

    # 私聊
    url(r'^chatroom/(?P<friend_id>\d+)/', views.chatroom, name='chatWith_id'),
    url(r'^chat_post/', views.chat_post, name='chat_post'),

    # 朋友圈
    url(r'^moments/', views.article, name='moments'),
    url(r'^reply/', views.comments, name='reply'),

    # 首页
    url(r'^$', views.welcome, name='welcome'),
]
