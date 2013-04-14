import re

from django import forms
from libs.djangoforms import ModelForm

from models import User, Contest, Setting, AdminSetting


def validate_username(username):
    """ Username validator """
    
    if len(username) < 3:
        raise forms.ValidationError('Username harus lebih dari 3 hurup.')
        
    if re.match("^[a-zA-Z0-9_.-]+$", username) is None:
        raise forms.ValidationError('Username tidak boleh mengandung simbol.')
        
    if re.match("^[0-9]+$", username) is not None:
        raise forms.ValidationError('Username tidak boleh berupa angka saja.')


class ProfileForm(ModelForm):

    class Meta:
        model = User
        exclude = ['id', 'profile_url', 'avatar', 'access_token', 'is_admin']

    def __init__(self, session, *args, **kwargs):
        """ We overrides __init__ so its accepts session param on init"""

        super(ProfileForm, self).__init__(*args, **kwargs)
        self.session = session

    def save(self, *args, **kwargs):
        """ We update user session data after save"""

        super(ProfileForm, self).save(*args, **kwargs)
        user_sess = self.session.get('user')
        user_sess.update({
                        'username': self.cleaned_data.get('username'),
                        'name': self.cleaned_data.get('name'),
                        })
        self.session['user'] = user_sess

    def clean_username(self):
        """ Validate username """
        username = self.cleaned_data.get('username')
        validate_username(username)

        user = User.gql("WHERE username=:1", username).get()
        if user and user.id != self.session['user']['id']:
            raise forms.ValidationError('Username "%s" sudah terpakai.' % username)

        return username


class ContestForm(ModelForm):
    """Contest form"""
    class Meta:
        model = Contest
        exclude = ['banner']


class BaseSettingForm(forms.Form):
    """ Base Form class that wrapped with user object """

    def __init__(self, *args, **kwargs):
        """
        Overrides the __init__ to fill the form initial data
        from database
        """
        user = kwargs.get('user', None)

        initial = {}
        for field_name, obj in self.base_fields.items():
            if user:
                initial[field_name] = Setting.get_setting(user, field_name)
            else:
                initial[field_name] = AdminSetting.get_setting(field_name)

        kwargs['initial'] = initial
        super(BaseSettingForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self):
        """ Custom save method for standard Django Form"""
        data = self.cleaned_data
        for k,v in data.items():
            if self.user:
                Setting.set_setting(self.user, k, v)
            else:
                AdminSetting.set_setting(k, v)


class ContentForm(BaseSettingForm):
    """ Static pages content """
    about_us = forms.CharField(label='About Us', required=False, 
                                    widget=forms.Textarea)
    about_contest = forms.CharField(label='Tentang Kontes', required=False, 
                                    widget=forms.Textarea)
    contest_rule = forms.CharField(label='Peraturan Kontes', required=False, 
                                    widget=forms.Textarea)
