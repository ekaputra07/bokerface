from libs import djangoforms

from models import User

class ProfileForm(djangoforms.ModelForm):

    class Meta:
        model = User
        exclude = ['id', 'profile_url', 'avatar', 'access_token']
