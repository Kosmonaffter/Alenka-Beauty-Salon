from django.views.generic import TemplateView

from .models import Master


CONTEXT_MASTERS = 'masters'


class MastersListView(TemplateView):
    """Отображение списка доступных мастеров."""

    template_name = 'masters/index.html'

    def get_context_data(self, **kwargs):
        """Добавление списка мастеров в контекст."""
        context = super().get_context_data(**kwargs)
        masters = Master.objects.filter(is_active=True)
        context[CONTEXT_MASTERS] = masters
        return context
