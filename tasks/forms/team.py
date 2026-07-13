from typing import cast

from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelMultipleChoiceField

from tasks.models import Team

User = get_user_model()


class TeamCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Add Members to Team",
    )

    class Meta:
        model = Team
        fields = ("name", "description", "members")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2.5 rounded-xl border border-gray-200 "
                             "focus:outline-hidden focus:ring-2 focus:ring-indigo-500 "
                             "text-sm",
                    "placeholder": "e.g., Frontend Avengers",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2.5 rounded-xl border border-gray-200 "
                             "focus:outline-hidden focus:ring-2 focus:ring-indigo-500 "
                             "text-sm h-24 resize-none",
                    "placeholder": "What is this team responsible for...",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        auth_user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if auth_user and auth_user.is_authenticated:
            members_field = cast(ModelMultipleChoiceField, self.fields.get("members"))
            if members_field:
                members_field.queryset = User.objects.exclude(id=auth_user.id)

        self.fields["name"].label = "Team Name"
        self.fields["description"].label = "Description"
