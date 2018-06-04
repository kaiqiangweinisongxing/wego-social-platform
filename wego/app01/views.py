from django.shortcuts import render,redirect,HttpResponse
from app01 import models
from app01 import forms
from django.db import transaction
from django.core.exceptions import NON_FIELD_ERRORS
import os,json
from django.db.models import Count
from utils.Pager import PageInfo
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import hashlib

current_user = None             # 当前用户

# MD5加密密码
def md5_encryption(password):
    hl = hashlib.md5()
    hl.update(password.encode(encoding='utf-8'))
    md5_password = hl.hexdigest()
    print('MD5加密前为 ：' + password)
    print('MD5加密后为 ：' + md5_password)     # 32位
    return md5_password

# 装饰器验证是否在登录状态
def auth(func):
    def inner(request, *args, **kwargs):
        try:
            is_login = request.session.get('user_info')
            if is_login:
                return func(request, *args, **kwargs)
            else:
                return redirect('/')
        except Exception as e:
            print(e)
            return redirect('/')
    return inner

# 欢迎页
def welcome(request):
    return render(request, 'welcome.html')

# 注册
def register(request):
    try:
        msg = ''
        if request.method == "POST":
            form = forms.RegisterForm(request.POST)
            if form.is_valid():  # 验证成功后将用户信息写入数据库
                username = request.POST.get('username')
                nickname = request.POST.get('nickname')
                passwd = request.POST.get('passwd')
                # 查询用户是否已存在
                isExist = models.UserInfo.objects.filter(username=username).first()  # 去数据库里查询用户是否存在
                if isExist:
                    form = forms.RegisterForm(request.POST)
                    msg = '用户名已存在，请重新输入！'
                else:
                    with transaction.atomic():  # 事物,原子性操作
                        models.UserInfo.objects.create(username=username, nickname=nickname,
                                                             password=md5_encryption(username + passwd))
                    return redirect('/')
        else:  # GET
            form = forms.RegisterForm()
        return render(request, 'register.html', {'form': form, 'msg': msg})
    except Exception as e:
        return HttpResponse("错误信息：" + str(e))

# 注销
def logout(request):
    global current_user
    current_user = None
    request.session.clear()
    return redirect('/')

# 好友请求
@auth
def friend_request(request):
    if request.method == 'POST':
        f_id = request.POST.get('f_id')
        selection = request.POST.get('selection')
        f_user = models.UserInfo.objects.filter(nid=f_id).first()
        #  解开pre_friend关系
        u2u = models.User2User.objects.filter(
            Q(u_sendReq_id=current_user.nid, u_receiveReq_id=f_user.nid) | Q(u_receiveReq_id=current_user.nid,
                                                                             u_sendReq_id=f_user.nid))
        u2u.delete()
        if (selection == 'accept'):  # 接受：建立friend关系
            current_user.friend.add(f_user)
    preFriends = models.User2User.objects.filter(u_receiveReq_id=current_user.nid)
    return render(request, 'request_msg.html', {'preFriends': preFriends})

# 登录
def login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():  # 如果提交的数据合法(在Form中校验)
            # username = form.cleaned_data['username']
            username = request.POST.get('username')
            passwd = request.POST.get('passwd')
            passwd = md5_encryption(username + passwd)
            user = models.UserInfo.objects.filter(username=username, password=passwd).first()  # 去数据库里查询用户是否存在
            if not user:  # 用户不存在则返回相应的错误提示
                msg = '用户名或密码错误，请检查你输入的信息是否正确！'
                return render(request, 'login.html', {'msg': msg, 'form': form})
            else:  # 存在则把用户相关信息写入session中，再跳转到首页
                request.session['user_info'] = {'user_id': user.nid}
                global current_user
                current_user = user
                return redirect('/friends/')

    else:  # Get
        form = forms.LoginForm()
    return render(request, 'login.html', {'form': form})

# 好友列表
@auth
def friends(request):
    if request.method == 'GET':
        # 显示好友列表
        try:
            # 分页
            friend_list = current_user.friend.all()
            friend_count = friend_list.count()  # 获取数据库中指定对象的总条数
            friend_page_info = PageInfo(request.GET.get('page'), friend_count, 12, '/friends/', 8)
            friend_list_perpage = friend_list[friend_page_info.start():friend_page_info.end()]  # 每页显示的数据
        except Exception as e:
            friend_list=[]
            friend_count=0
            friend_page_info = None
            friend_list_perpage = []
        return render(request, 'friends.html', {'user': current_user,  # 当前登录用户
                                       'friend_list_page': friend_list_perpage,        # 每页的数据
                                       'page_info': friend_page_info})                  # 页码对象

# 查看资料
@auth
def seeData(request):
    f_id = request.POST.get('f_id')
    f_user = models.UserInfo.objects.filter(nid=f_id).first()
    return HttpResponse(json.dumps({'username': f_user.username, 'nickname': f_user.nickname}))

# 删除好友
@auth
def deleteFriend(request, *args, **kwargs):
    if(request.method == 'POST'):
        f_id = request.POST.get('f_id')
        f_user = models.UserInfo.objects.filter(nid=f_id).first()
        current_user.friend.remove(f_user)
        response = {'status': '200', 'msg': '删除好友成功！'}
        return HttpResponse(json.dumps(response))

# 添加好友
@auth
def addFriend(request):
    status = 404
    msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        if(request.POST.get('operate') == 'search'):  # 查找
            res = models.UserInfo.objects.filter(username=username).first()  # 去数据库里查询用户是否存在
            if not res:  # 用户不存在则返回相应的错误提示
                msg = '查找的用户不存在'
            else:
                msg = '找到用户：' + res.username + '，昵称：' + res.nickname
                status = 200
        elif (request.POST.get('operate') == 'add'):  # 添加好友
            if (username == current_user_name):
                msg = '不能添加自己为好友！'
            else:
                friend = current_user.friend.all().filter(username=username)
                if (friend.exists()):
                    msg = '已经是好友！'
                else:
                    # 发送好友请求
                    f_user = models.UserInfo.objects.filter(username=username).first()
                    u2u = models.User2User.objects.filter(u_sendReq_id=current_user.nid, u_receiveReq_id=f_user.nid)
                    if(u2u.exists()):
                        msg = '您已经发送过添加请求，请勿重复发送！'
                    else:
                        models.User2User.objects.create(u_sendReq_id=current_user.nid, u_receiveReq_id=f_user.nid)
                        msg = '已经发送添加请求！'
    return HttpResponse(json.dumps({'msg': msg, 'status': status}))

# 发动态
@auth
def article(request, *args, ** kwargs):
    if request.method == 'POST':
        content = request.POST.get('article')
        models.Article.objects.create(user_id=int(current_user.nid), content=content)
        return redirect('/moments/')
    else:  # get
        # 获取自己和好友们的动态和评论
        friends = models.UserInfo.objects.get(nid=current_user.nid).friend.all()
        articles_list = []
        for a in models.Article.objects.filter(user_id=current_user.nid).all():
            article_comment = {}
            article_comment['article']= a
            article_comment['comment']= a.article_comments.all().order_by('-create_time')
            articles_list.append(article_comment)
        for id in [f.nid for f in friends]:
            for a in models.Article.objects.filter(user_id=id).all():
                article_comment = {}
                article_comment['article'] = a
                article_comment['comment'] = a.article_comments.all().order_by('-create_time')
                articles_list.append(article_comment)
        articles_list = sorted(articles_list, key=lambda x: x['article'].create_time, reverse=True)
        # 分页
        articles_count = articles_list.__len__()   # 获取数据库中指定对象的总条数
        article_page_info = PageInfo(request.GET.get('page'), articles_count, 10, '/moments/', 8)
        article_list_perpage = articles_list[article_page_info.start():article_page_info.end()]  # 每页显示的数据

        return render(request, 'article.html', {'articles_list': article_list_perpage,
                                                'page_info': article_page_info,
                                                'current_user_id': current_user.nid,
                                                'user': current_user})

# 评论
@auth
def comments(request, *args, **kwargs):
    current_user_id = request.POST.get('user_id')
    content = request.POST.get('comment')
    article_id = request.POST.get('article_id')
    models.Comment.objects.create(user_id=int(current_user_id), content=content,article_id=article_id)
    return redirect('/moments/')

# 发消息
@auth
def chatroom(request, *args, **kwargs):
    friend_id = int(kwargs.get('friend_id')) if kwargs.get('friend_id') else None
    chat_msg = models.Chat.objects.filter(Q(sender_id=current_user.nid, receiver_id=friend_id) | Q(sender_id=friend_id, receiver_id=current_user.nid)).all().order_by('time')
    chats = list(chat_msg)[-3:]
    return render(request, 'chatroom.html', {'chats': chats, 'friend_id': friend_id, 'user': current_user})

# 发送私聊信息
@csrf_exempt
def chat_post(request):
    friend_id = request.POST.get('friend_id')
    friend_user = models.UserInfo.objects.get(nid=friend_id)
    if request.method == 'POST':
        post_type = request.POST.get('post_type')
        if post_type == 'send_chat':
            new_chat = models.Chat.objects.create(
                content=request.POST.get('content'),
                sender=current_user,
                receiver=friend_user,
            )
            new_chat.save()
            return HttpResponse()
        elif post_type == 'get_chat':
            last_chat_id = int(request.POST.get('last_chat_id')) if request.POST.get('last_chat_id') else -1
            chat_msg = models.Chat.objects.filter(
                Q(sender_id=current_user.nid, receiver_id=friend_id) | Q(sender_id=friend_id, receiver_id=current_user.nid)).all().order_by(
                'time')
            if(chat_msg.exists()):
                if(chat_msg.last().id == last_chat_id):
                    return HttpResponse()
                else:
                    chats = chat_msg.filter(id__gt=last_chat_id)
                    return render(request, 'chat_list.html', {'chats': chats, 'friend_id': friend_id})  # 返回渲染好的html代码
            else:
                return HttpResponse()
            # return HttpResponse(json.dumps({"classes": classes}))  # 返回json数据，前端解析JSON.parse(ret);