from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'result', 'confidence', 'created_at')
    list_filter = ('result', 'created_at')
    search_fields = ('user__username',)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            qs = response.context_data['cl'].queryset

            total = qs.count()
            approved = qs.filter(result="Approved").count()
            rejected = qs.filter(result="Rejected").count()

            response.context_data['summary'] = {
                'total': total,
                'approved': approved,
                'rejected': rejected
            }
        except:
            pass

        return response