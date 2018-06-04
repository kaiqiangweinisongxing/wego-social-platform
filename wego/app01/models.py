#!/usr/bin/env python
#_*_coding:utf-8_*_
from django.db import models

class User2User(models.Model):
    """
    好友请求表
    """
    u_sendReq = models.ForeignKey("UserInfo",related_name ='send_receives', verbose_name='发送者')
    u_receiveReq = models.ForeignKey("UserInfo",related_name ='receive_sends', verbose_name='接收者')

class UserInfo(models.Model):
    """
    用户信息表
    """
    nid = models.BigAutoField(primary_key=True)         # 自增
    username = models.CharField(verbose_name='用户名', max_length=12, unique=True)
    nickname = models.CharField(verbose_name='昵称', max_length=12)
    password = models.CharField(verbose_name='密码', max_length=32)
    friend = models.ManyToManyField('self', verbose_name='好友')         # 好友
    create_time = models.DateTimeField(verbose_name='注册时间', auto_now=True)
    def __str__(self):
        return self.username

class Article(models.Model):
    """
    文章表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name='用户名', to='UserInfo', to_field='nid', related_name='user_articles')
    content = models.TextField(verbose_name='内容', max_length=1000)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    def __str__(self):
        return u"%s" %(self.content)

class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.TextField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', related_name='article_comments')
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', related_name='user_comments')

    def __str__(self):
        return u'%s' % self.content

class Chat(models.Model):
    """
    聊天表
    """
    sender = models.ForeignKey(verbose_name='发送者', to='UserInfo', related_name='sender_chats')
    receiver = models.ForeignKey(verbose_name='接收者', to='UserInfo', default="", related_name='receiver_chats')
    content = models.TextField(verbose_name='聊天内容', max_length=255)
    time = models.DateTimeField(verbose_name='发送时间',  auto_now_add=True, null=True)

    def __str__(self):
        return u'%s' % self.content