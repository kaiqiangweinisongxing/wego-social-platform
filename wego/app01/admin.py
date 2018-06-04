from django.contrib import admin
from app01 import models

class ArticleInline(admin.TabularInline):
    model = models.Article
    # extra = 8  #默认显示条目的数量

class CommentInline(admin.TabularInline):
    model = models.Comment

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname', 'password', 'create_time')     # 展示
    search_fields = ('nid', 'username', 'nickname', 'password',)    # 搜索
    list_filter = ('nickname','create_time')  # 过滤器
    ordering = ('-create_time',)

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 9
    date_hierarchy = 'create_time'
    # list_editable 设置默认可编辑字段
    # list_editable = ['nickname', 'password']

    # 多对多字段过滤器  filter_vertical
    filter_horizontal = ('friend',)

    # 布局
    fieldsets = [
        ('基本信息', {'fields': ['username',"nickname", 'password']}),
        ('添加好友', {'fields': ['friend',], 'classes': ['collapse']}),
    ]

    inlines = [ArticleInline,]    #Inline把ArticleInline关联进来
    # readonly_fields = ('username',)  # 用户名只读

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('nid', 'user', 'content', 'create_time')
    search_fields = ('user', 'content')
    list_filter = ('user', 'create_time')
    ordering = ('-create_time',)
    list_per_page = 19
    date_hierarchy = 'create_time'
    fieldsets = [
        ('文章信息', {'fields': ['user', 'content']}),
    ]
    inlines = [CommentInline, ]

class CommentAdmin(admin.ModelAdmin):
    list_display = ('nid', 'user', 'article', 'content', 'create_time')
    search_fields = ('user', 'article', 'content')
    list_filter = ('user', 'create_time')
    ordering = ('-create_time',)
    list_per_page = 19
    date_hierarchy = 'create_time'

    fieldsets = [
        ('评论信息', {'fields': ['user', 'article', 'content']}),
    ]

class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'time')
    search_fields = ('sender', 'receiver', 'content')
    list_filter = ('sender', 'receiver', 'time')
    ordering = ('-time',)
    list_per_page = 12
    date_hierarchy = 'time'
    fieldsets = [
        ('聊天记录', {'fields': [('sender', 'receiver'), 'content']}),
    ]

class User2UserAdmin(admin.ModelAdmin):
    list_display = ('u_sendReq', 'u_receiveReq',)
    search_fields = ('u_sendReq', 'u_receiveReq',)
    list_filter = ('u_sendReq', 'u_receiveReq',)
    list_per_page = 19

admin.site.site_header = 'WeGo社交平台后台管理系统'  # 设置页面显示标题
admin.site.site_title = 'WeGo'                       # 设置页面头部标题
admin.site.register(models.UserInfo, UserInfoAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Chat, ChatAdmin)
admin.site.register(models.User2User, User2UserAdmin)
