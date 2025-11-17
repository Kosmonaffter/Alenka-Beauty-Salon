import re
from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.safestring import mark_safe

from catalog.models import Procedure
from masters.models import Master
from .constants import (
    MAX_BOOKING_DAYS_AHEAD,
    NOTIFICATION_EMAIL,
    NOTIFICATION_TELEGRAM,
    PHONE_MAX_LENGTH,
    PHONE_NORMALIZED_LENGTH,
    PHONE_PREFIX,
)
from .models import Booking


class PhoneNumberForm(forms.Form):
    """Форма для подтверждения номера телефона и данных клиента."""

    NOTIFICATION_CHOICES = [
        (NOTIFICATION_TELEGRAM, '📱 Telegram - мгновенные уведомления'),
        (NOTIFICATION_EMAIL, '📧 Email - уведомления на почту'),
    ]

    client_name = forms.CharField(
        max_length=PHONE_MAX_LENGTH,
        required=False,
        label='👤 Ваше имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )
    notification_method = forms.ChoiceField(
        choices=NOTIFICATION_CHOICES,
        initial=NOTIFICATION_TELEGRAM,
        label='🔔 Как вас уведомить о записи?',
        widget=forms.RadioSelect(attrs={'class': 'notification-method'})
    )
    email = forms.EmailField(
        required=False,
        label='📧 Email адрес',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ваш@email.com',
            'id': 'email-input',
        })
    )
    personal_data_agreement = forms.BooleanField(
        required=True,
        label='',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        self.existing_client = kwargs.pop('existing_client', False)
        super().__init__(*args, **kwargs)
        if self.existing_client:
            self.fields['client_name'].required = False
        else:
            self.fields['client_name'].required = True

        self.fields['personal_data_agreement'].label = (
            self._get_agreement_label()
        )

    def _get_agreement_label(self):
        """Возвращает HTML для label с подробным описанием."""
        return mark_safe("""
            <div class="agreement-text">
                ✅ Я соглашаюсь на
                <a href="#" class="agreement-link" data-bs-toggle="modal"
                   data-bs-target="#agreementModal">
                    обработку персональных данных
                </a>
                и получение уведомлений о записи через Telegram,
                либо Email в зависимости от моего выбора.
            </div>
        """)

    def clean(self):
        """Валидация зависимых полей."""
        cleaned_data = super().clean()
        notification_method = cleaned_data.get('notification_method')
        email = cleaned_data.get('email')

        if (notification_method == NOTIFICATION_EMAIL
                and not email):
            raise ValidationError({
                'email': 'Для уведомлений по '
                'email необходимо указать адрес почты.'
            })
        return cleaned_data


class BookingForm(forms.ModelForm):
    """Форма для создания бронирования (только основная информация)."""

    master = forms.ModelChoiceField(
        queryset=Master.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Мастер'
    )

    class Meta:
        model = Booking
        fields = [
            'procedure',
            'master',
            'booking_date',
            'booking_time',
            'client_phone',
        ]
        widgets = {
            'procedure': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_procedure'
            }),
            'booking_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'booking-date',
                'min': timezone.now().date().isoformat()
            }),
            'booking_time': forms.Select(attrs={
                'class': 'form-control',
                'id': 'booking-time'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 000-00-00',
                'id': 'phone-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы с динамическим queryset."""
        super().__init__(*args, **kwargs)
        self.fields[
            'procedure'
        ].queryset = Procedure.objects.filter(  # type: ignore
            is_available=True
        )
        self.fields['procedure'].required = True

        today = timezone.now().date()
        self.fields['booking_date'].widget.attrs['min'] = today.isoformat()
        self._setup_master_queryset()

    def _setup_master_queryset(self):
        """Настройка queryset для поля master."""
        if self.initial.get('procedure'):
            procedure = self.initial['procedure']
            self._set_master_queryset(procedure)
        elif self.data:
            procedure_id = self.data.get('procedure')
            if procedure_id:
                self._set_master_queryset_by_id(procedure_id)
            else:
                self.fields[
                    'master'
                ].queryset = Master.objects.none()  # type: ignore
        elif self.instance and self.instance.pk:
            self._set_master_queryset(self.instance.procedure)
        else:
            self.fields[
                'master'
            ].queryset = Master.objects.none()  # type: ignore

    def _set_master_queryset(self, procedure):
        """Устанавливает queryset мастеров для процедуры."""
        self.fields['master'].queryset = Master.objects.filter(  # type: ignore
            procedures=procedure, is_active=True
        ).distinct()

    def _set_master_queryset_by_id(self, procedure_id):
        """Устанавливает queryset мастеров по ID процедуры."""
        self.fields['master'].queryset = Master.objects.filter(  # type: ignore
            procedures__id=procedure_id, is_active=True
        ).distinct()

    def clean_booking_date(self):
        """Валидация даты бронирования."""
        booking_date = self.cleaned_data['booking_date']
        today = timezone.now().date()

        if booking_date < today:
            raise ValidationError('Нельзя выбрать прошедшую дату')

        max_date = today + timedelta(days=MAX_BOOKING_DAYS_AHEAD)
        if booking_date > max_date:
            raise ValidationError(
                f'Максимальная дата бронирования - '
                f'{MAX_BOOKING_DAYS_AHEAD} дней вперед'
            )
        return booking_date

    def clean_client_phone(self):
        """Валидация и нормализация номера телефона."""
        phone = self.cleaned_data['client_phone']
        phone = re.sub(r'[^\d+]', '', phone)

        if not phone.startswith(PHONE_PREFIX):
            if phone.startswith('8'):
                phone = PHONE_PREFIX + phone[1:]
            elif phone.startswith('7'):
                phone = '+' + phone
            else:
                phone = PHONE_PREFIX + phone

        if len(phone) != PHONE_NORMALIZED_LENGTH:
            raise ValidationError('Введите корректный номер телефона')

        return phone
