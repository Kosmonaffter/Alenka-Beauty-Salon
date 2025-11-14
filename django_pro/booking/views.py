from datetime import datetime, timedelta, time as time_type

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, TemplateView

from catalog.models import Procedure
from masters.models import Master
from notifications.telegram_utils import send_booking_notification
from user.models import Client, PaymentSettings
from .constants import (
    ACTIVE_BOOKING_STATUSES,
    CONTEXT_BOOKING,
    CONTEXT_FORM,
    CONTEXT_PROCEDURES,
    DEFAULT_PROCEDURE_DURATION_MINUTES,
    DEFAULT_TIME_INTERVAL,
    DEFAULT_WORKING_END_HOUR,
    DEFAULT_WORKING_END_MINUTE,
    DEFAULT_WORKING_START_HOUR,
    DEFAULT_WORKING_START_MINUTE,
    EMPTY_LIST_RESPONSE,
    MSG_BOOKING_ERROR,
    MSG_CLIENT_ERROR,
    MSG_SESSION_EXPIRED,
    MSG_TELEGRAM_ERROR,
    PAYMENT_NOT_REQUIRED,
    PAYMENT_PENDING,
    SESSION_PENDING_BOOKING,
    STATUS_PENDING,
    URL_BOOKING_SUCCESS,
    URL_SERVICE_LIST,
)
from .forms import BookingForm, PhoneNumberForm
from .models import Booking, WorkingHoursSettings


class ServiceListView(TemplateView):
    """Отображение списка доступных процедур."""

    template_name = 'booking/services.html'

    def get_context_data(self, **kwargs):
        """Добавление списка процедур в контекст."""
        context = super().get_context_data(**kwargs)
        procedures = Procedure.objects.filter(is_available=True)
        context[CONTEXT_PROCEDURES] = procedures
        return context


class BookingCreateView(View):
    """View для создания бронирования."""

    def get(self, request, procedure_id=None):
        """Отображение формы бронирования."""
        form = BookingForm()
        if procedure_id:
            form = self._prefill_form_with_procedure(procedure_id, form)

        context = {
            CONTEXT_FORM: form,
            CONTEXT_PROCEDURES: Procedure.objects.filter(
                is_available=True
            ),
        }
        return render(request, 'booking/booking_form.html', context)

    def post(self, request, procedure_id=None):
        """Обработка данных формы бронирования."""
        form = BookingForm(request.POST)
        if form.is_valid():
            return self._handle_valid_form(form, request)

        context = {
            CONTEXT_FORM: form,
            CONTEXT_PROCEDURES: Procedure.objects.filter(
                is_available=True
            ),
        }
        return render(request, 'booking/booking_form.html', context)

    def _prefill_form_with_procedure(self, procedure_id, form):
        """Предзаполнение формы выбранной процедурой."""
        procedure = get_object_or_404(
            Procedure, id=procedure_id, is_available=True
        )
        form.initial['procedure'] = procedure.id  # type: ignore
        form.fields['master'].queryset = Master.objects.filter(
            procedures=procedure, is_active=True
        )
        return form

    def _handle_valid_form(self, form, request):
        """Обработка валидной формы бронирования."""
        booking = form.save(commit=False)
        request.session[SESSION_PENDING_BOOKING] = {
            'procedure_id': booking.procedure.id,
            'master_id': booking.master.id,
            'booking_date': booking.booking_date.isoformat(),
            'booking_time': booking.booking_time.isoformat(),
            'client_phone': booking.client_phone,
        }
        return redirect('booking:phone_confirmation')


class PhoneConfirmationView(View):
    """View для подтверждения номера телефона."""

    def get(self, request):
        """Отображение формы ввода телефона."""
        if SESSION_PENDING_BOOKING not in request.session:
            messages.error(request, MSG_SESSION_EXPIRED)
            return redirect(URL_SERVICE_LIST)

        pending_booking = request.session[SESSION_PENDING_BOOKING]
        phone = pending_booking.get('client_phone', '')
        existing_client = self._get_existing_client_by_phone(phone)
        if existing_client:
            try:
                booking = self._create_booking_for_existing_client(
                    existing_client, pending_booking
                )
                self._send_telegram_notification(booking, request)
                del request.session[SESSION_PENDING_BOOKING]

                return redirect(
                    URL_BOOKING_SUCCESS,
                    booking_id=booking.booking_id,
                )

            except Exception as e:
                messages.error(request, MSG_BOOKING_ERROR.format(str(e)))
                return redirect(URL_SERVICE_LIST)
        form = PhoneNumberForm(existing_client=existing_client)

        context = {
            CONTEXT_FORM: form,
            'existing_client': bool(existing_client),
        }
        return render(request, 'booking/phone_confirmation.html', context)

    def post(self, request):
        """Обработка данных подтверждения (только для новых клиентов)."""
        pending_booking = request.session.get(SESSION_PENDING_BOOKING)

        if not pending_booking:
            messages.error(request, MSG_SESSION_EXPIRED)
            return redirect(URL_SERVICE_LIST)

        form = PhoneNumberForm(request.POST, existing_client=False)

        if form.is_valid():
            return self._handle_valid_confirmation_form(
                form, request, pending_booking
            )

        return render(
            request,
            'booking/phone_confirmation.html',
            {
                CONTEXT_FORM: form,
                'existing_client': False,
            },
        )

    def _handle_valid_confirmation_form(
        self,
        form,
        request,
        pending_booking,
    ):
        """Обработка валидной формы подтверждения для нового клиента."""
        phone = pending_booking['client_phone']
        notification_method = form.cleaned_data['notification_method']
        email = form.cleaned_data.get('email')
        client_name = form.cleaned_data.get('client_name', '')

        try:
            # Создаем нового клиента
            client = Client.objects.create(
                phone=phone,
                name=client_name,
                email=email,
                notification_method=notification_method,
                is_new=True,
            )

            booking = self._create_booking(
                pending_booking=pending_booking,
                phone=phone,
                client_name=client_name,
                notification_method=notification_method,
                email=email,
                client=client,
            )

            self._send_telegram_notification(booking, request)
            del request.session[SESSION_PENDING_BOOKING]

            return redirect(
                URL_BOOKING_SUCCESS,
                booking_id=booking.booking_id,
            )

        except Exception as e:
            messages.error(request, MSG_CLIENT_ERROR.format(str(e)))
            return redirect(URL_SERVICE_LIST)

    def _get_existing_client_by_phone(self, phone):
        """Ищет существующего клиента по номеру телефона."""
        try:
            return Client.objects.get(phone=phone)
        except Client.DoesNotExist:
            return None
        except Client.MultipleObjectsReturned:
            return Client.objects.filter(phone=phone).first()

    def _create_booking_for_existing_client(self, client, pending_booking):
        """Создает бронирование для существующего клиента."""
        master = Master.objects.get(id=pending_booking['master_id'])
        payment_settings = PaymentSettings.objects.filter(
            is_active=True
        ).first()

        prepayment_required = getattr(client, 'always_prepayment', False)
        payment_phone = self._get_payment_phone(payment_settings, master)

        booking = Booking(
            procedure_id=pending_booking['procedure_id'],
            master_id=pending_booking['master_id'],
            booking_date=pending_booking['booking_date'],
            booking_time=pending_booking['booking_time'],
            client_name=client.name,  # Используем имя из профиля клиента
            client_phone=client.phone,
            client_email=client.email,
            notification_method=client.notification_method,
            client=client,
            personal_data_agreement=True,
            status=STATUS_PENDING,
            prepayment_required=prepayment_required,
            payment_status=(
                PAYMENT_PENDING if prepayment_required
                else PAYMENT_NOT_REQUIRED
            ),
            payment_phone=payment_phone,
        )
        booking.save()
        return booking

    def _create_booking(
        self,
        pending_booking,
        phone,
        client_name,
        notification_method,
        email,
        client,
    ):
        """Создание объекта бронирования для нового клиента."""
        master = Master.objects.get(id=pending_booking['master_id'])
        payment_settings = PaymentSettings.objects.filter(
            is_active=True
        ).first()

        prepayment_required = (
            client.is_new or getattr(client, 'always_prepayment', False)
        )
        payment_phone = self._get_payment_phone(payment_settings, master)

        booking = Booking(
            procedure_id=pending_booking['procedure_id'],
            master_id=pending_booking['master_id'],
            booking_date=pending_booking['booking_date'],
            booking_time=pending_booking['booking_time'],
            client_name=client_name,
            client_phone=phone,
            client_email=email,
            notification_method=notification_method,
            client=client,
            personal_data_agreement=True,
            status=STATUS_PENDING,
            prepayment_required=prepayment_required,
            payment_status=(
                PAYMENT_PENDING if prepayment_required
                else PAYMENT_NOT_REQUIRED
            ),
            payment_phone=payment_phone,
        )
        booking.save()
        return booking

    def _get_payment_phone(self, payment_settings, master):
        """Возвращает телефон для оплаты."""
        if payment_settings:
            return payment_settings.admin_phone
        elif master.phone:
            return master.phone
        return ''

    def _send_telegram_notification(self, booking, request):
        """Отправка уведомления в Telegram."""
        try:
            success = send_booking_notification(booking)
            if not success:
                messages.warning(request, MSG_TELEGRAM_ERROR)
        except Exception as e:
            print(f'Error sending Telegram notification: {e}')
            messages.warning(request, MSG_TELEGRAM_ERROR)


class BookingSuccessView(DetailView):
    """Отображение страницы успешного бронирования."""

    model = Booking
    template_name = 'booking/booking_success.html'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'
    context_object_name = CONTEXT_BOOKING


def get_available_masters(request):
    """AJAX endpoint для получения мастеров по процедуре."""
    procedure_id = request.GET.get('procedure_id')
    if not procedure_id:
        return JsonResponse(EMPTY_LIST_RESPONSE, safe=False)

    procedure = get_object_or_404(Procedure, id=procedure_id)
    masters = Master.objects.filter(
        procedures=procedure, is_active=True
    ).values('id', 'name')
    return JsonResponse(list(masters), safe=False)


def get_available_times(request):
    """AJAX endpoint для получения доступного времени."""
    master_id = request.GET.get('master_id')
    date_str = request.GET.get('date')
    procedure_id = request.GET.get('procedure_id')

    if not all([master_id, date_str]):
        return JsonResponse(EMPTY_LIST_RESPONSE, safe=False)

    try:
        master = Master.objects.get(id=master_id)
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        bookings = Booking.objects.filter(
            master=master,
            booking_date=selected_date,
            status__in=ACTIVE_BOOKING_STATUSES,
        ).select_related('procedure')

        procedure_duration = None
        if procedure_id:
            try:
                procedure = Procedure.objects.get(id=procedure_id)
                procedure_duration = procedure.duration
            except Procedure.DoesNotExist:
                pass

        available_times = _generate_available_times(
            bookings,
            procedure_duration,
            selected_date,
        )
        return JsonResponse(available_times, safe=False)

    except (Master.DoesNotExist, ValueError):
        return JsonResponse(EMPTY_LIST_RESPONSE, safe=False)


def _generate_available_times(
    bookings,
    procedure_duration=None,
    selected_date=None,
):
    """Генерация списка доступного времени."""
    available_times = []
    now = timezone.localtime(timezone.now())
    today = now.date()
    current_time = now.time()

    try:
        working_settings = WorkingHoursSettings.objects.filter(
            is_active=True
        ).first()
        if working_settings:
            start_time = working_settings.start_time
            end_time = working_settings.end_time
            interval = working_settings.time_interval
        else:
            start_time = time_type(
                DEFAULT_WORKING_START_HOUR,
                DEFAULT_WORKING_START_MINUTE,
            )
            end_time = time_type(
                DEFAULT_WORKING_END_HOUR,
                DEFAULT_WORKING_END_MINUTE,
            )
            interval = DEFAULT_TIME_INTERVAL
    except Exception:
        start_time = time_type(
            DEFAULT_WORKING_START_HOUR,
            DEFAULT_WORKING_START_MINUTE,
        )
        end_time = time_type(
            DEFAULT_WORKING_END_HOUR,
            DEFAULT_WORKING_END_MINUTE,
        )
        interval = DEFAULT_TIME_INTERVAL

    if isinstance(interval, dict):
        interval = DEFAULT_TIME_INTERVAL
    elif not isinstance(interval, int):
        try:
            interval = int(interval)
        except (ValueError, TypeError):
            interval = DEFAULT_TIME_INTERVAL

    busy_intervals = []
    for booking in bookings:
        booking_start = booking.booking_time
        booking_start_datetime = datetime.combine(
            datetime.today(),
            booking_start,
        )
        booking_end_datetime = (
            booking_start_datetime + booking.procedure.duration
        )
        booking_end = booking_end_datetime.time()
        busy_intervals.append({'start': booking_start, 'end': booking_end})

    current_time_slot = start_time
    while current_time_slot < end_time:
        time_str = current_time_slot.strftime('%H:%M')
        current_datetime = datetime.combine(
            datetime.today(),
            current_time_slot,
        )

        if selected_date and selected_date == today:
            if current_time_slot <= current_time:
                current_datetime += timedelta(minutes=interval)
                current_time_slot = current_datetime.time()
                continue

        if procedure_duration:
            current_end_datetime = current_datetime + procedure_duration
        else:
            current_end_datetime = current_datetime + timedelta(
                minutes=DEFAULT_PROCEDURE_DURATION_MINUTES
            )

        current_end_time = current_end_datetime.time()
        if current_end_time > end_time:
            current_datetime += timedelta(minutes=interval)
            current_time_slot = current_datetime.time()
            continue

        is_available = True
        for busy in busy_intervals:
            busy_start = datetime.combine(datetime.today(), busy['start'])
            busy_end = datetime.combine(datetime.today(), busy['end'])
            if (
                current_datetime < busy_end
                and current_end_datetime > busy_start
            ):
                is_available = False
                break

        if is_available:
            available_times.append(time_str)

        current_datetime += timedelta(minutes=interval)
        current_time_slot = current_datetime.time()

    return available_times
