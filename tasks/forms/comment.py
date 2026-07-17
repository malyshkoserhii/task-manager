from django import forms

from tasks.models import Comment


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-xl border border-gray-200 "
                             "px-4 py-3 text-sm focus:border-indigo-500 "
                             "focus:ring-indigo-500 bg-white text-gray-900 "
                             "shadow-xs resize-y",
                    "placeholder": "Write your comment here...",
                    "rows": 3,
                }
            )
        }
        labels = {
            "text": "",
        }
