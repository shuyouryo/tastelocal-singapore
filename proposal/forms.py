# proposal/forms.py
from django import forms
from .models import Proposal


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['receiver', 'sender_duties', 'receiver_duties']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make “Their commitments” optional in the browser
        self.fields['receiver_duties'].required = False


class ResponseForm(forms.Form):
    ACTION = (
        ('accept', 'Accept as-is'),
        ('reject', 'Reject'),
        ('counter', 'Counter-propose (edit duties below)'),
    )
    action = forms.ChoiceField(choices=ACTION, widget=forms.RadioSelect)
    sender_duties = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}))
    receiver_duties = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('action') == 'counter':
            if not cleaned.get('sender_duties') or not cleaned.get('receiver_duties'):
                raise forms.ValidationError('Both duty fields are required for a counter-proposal.')
        return cleaned
