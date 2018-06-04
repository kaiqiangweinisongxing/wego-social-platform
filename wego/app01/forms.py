#!/usr/bin/env python
#_*_coding:utf-8_*_

from django.forms import Form, fields, widgets
from django.core.exceptions import ValidationError
from app01 import models

class LoginForm(Form):
    """
    验证用户登录的Form组件
    """
    # required=True 要求非空     'placeholder': u'用户名' 提示用户
    username = fields.CharField(min_length=3, max_length=12, required=True,
                                error_messages={
                                    'min_length': '用户名太短',
                                    'max_length': '用户名太长',
                                    'required': '用户名不能为空'
                                },
                                widget =widgets.TextInput(attrs={'class': 'form-control', 'placeholder': u'用户名'})
                                )

    passwd = fields.CharField(min_length=6, max_length=64, required=True,
                              error_messages={
                                  'min_length': '密码太短',
                                  'max_length': '密码太长',
                                  'required': '密码不能为空'
                              },
                              widget=widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': u'密码'})
                              )

class RegisterForm(Form):
    """
        验证用户注册的Form组件
    """
    username = fields.CharField(min_length=3, max_length=12, required=True,
                              error_messages={
                                  'min_length':'用户名太短',
                                    'max_length':'用户名太长',
                                    'required':'用户名不能为空'
                                },
                             widget = widgets.TextInput(attrs={'class':'form-control','placeholder': u'用户名'})
    )
    nickname = fields.CharField(min_length=1,max_length=12, required=True,
                              error_messages={
                                  'min_length': '昵称太短',
                                   'max_length' : '昵称太长',
                                     'required': '昵称不能为空'
                                },
                                 widget=widgets.TextInput(attrs={'class': 'form-control','placeholder': u'昵称'})
    )

    passwd = fields.CharField(min_length=6,max_length=32,required=True,
                              error_messages={
                                  'min_length':'密码太短',
                                    'max_length':'密码太长',
                                    'required':'密码不能为空'
                                },
        widget=widgets.PasswordInput(attrs={'class': 'form-control','placeholder': u'密码'})
    )
    passwd2 = fields.CharField(required=True,
                            error_messages={
                                    'required':'密码不能为空'
                                },
        widget=widgets.PasswordInput(attrs={'class': 'form-control','placeholder': u'确认密码'})
    )

    # clean方法是Form组件一定会执行的,判断密码是否一致
    def clean(self):
        p1 = self.cleaned_data.get('passwd')
        p2 = self.cleaned_data.get('passwd2')
        if p1 == p2:
            return None
        self.add_error('passwd2', ValidationError('密码不一致'))
