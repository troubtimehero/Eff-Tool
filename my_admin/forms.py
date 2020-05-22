from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField(label="上传文件", allow_empty_file=False)
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
