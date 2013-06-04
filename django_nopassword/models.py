# -*- coding: utf-8 -*-
import string
from random import choice
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django_nopassword.utils import User, get_username


class LoginCode(models.Model):
    user = models.ForeignKey(User, related_name='login_codes', editable=False, verbose_name=_('user'))
    code = models.CharField(max_length=20, editable=False, verbose_name=_('code'))
    timestamp = models.DateTimeField(editable=False)
    next = models.TextField(editable=False, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.user, self.timestamp)

    def save(self, *args, **kwargs):
        self.timestamp = datetime.now()
        if not self.next:
            self.next = '/'
        super(LoginCode, self).save(*args, **kwargs)
        username = get_username(self.user)
        send_mail(
            'Login code',
            'Login with this url http://%s%s?next=%s' % (
                getattr(settings, 'SERVER_URL', 'example.com'),
                reverse('django_nopassword.views.login_with_code', args=[username, self.code]),
                self.next
            ),
            getattr(settings, 'SERVER_EMAIL', 'root@example.com'),
            [self.user.email],
        )

    @classmethod
    def create_code_for_user(cls, user, next=None):
        if not user.is_active:
            return None

        code = cls.generate_code()
        login_code = LoginCode(user=user, code=code)
        if not next is None:
            login_code.next = next
        login_code.save()
        return login_code

    @classmethod
    def generate_code(cls, length=20):
        chars = string.letters + string.digits
        return ''.join([choice(chars) for i in xrange(length)])
