from django import forms
from django.contrib.auth import user_logged_in

from tasks.models import Project, Team


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "teams")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2.5 rounded-xl border border-gray-200 "
                             "focus:outline-hidden focus:ring-2 focus:ring-indigo-500 "
                             "focus:border-indigo-500 transition-all text-sm",
                    "placeholder": "e.g., Mobile App MVP",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2.5 rounded-xl border border-gray-200 "
                             "focus:outline-hidden focus:ring-2 focus:ring-indigo-500 "
                             "focus:border-indigo-500 transition-all "
                             "text-sm h-32 resize-none",
                    "placeholder": "Describe the goals and scope of this project...",
                }
            ),
            "teams": forms.CheckboxSelectMultiple(
                attrs={
                    "class": "rounded border-gray-300 text-indigo-600 "
                             "focus:ring-indigo-500"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        auth_user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user_logged_in:
            self.fields["teams"].queryset = Team.objects.filter(members=auth_user)

        self.fields["name"].label = "Project Name"
        self.fields["description"].label = "Description"
        self.fields["teams"].label = "Assign to Teams (Optional)"


class ProjectSearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search project by name"}),
    )
