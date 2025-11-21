# Booking statuses
STATUS_PENDING = 'pending'
STATUS_CONFIRMED = 'confirmed'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'
STATUS_PAID = 'paid'
STATUS_NO_SHOW = 'no_show'

# Notification methods
NOTIFICATION_TELEGRAM = 'telegram'
NOTIFICATION_EMAIL = 'email'

# Payment statuses
PAYMENT_PENDING = 'pending'
PAYMENT_PAID = 'paid'
PAYMENT_NOT_REQUIRED = 'not_required'

# Session keys
SESSION_PENDING_BOOKING = 'pending_booking'

# Time constants
DEFAULT_WORKING_START_HOUR = 10
DEFAULT_WORKING_START_MINUTE = 0
DEFAULT_WORKING_END_HOUR = 20
DEFAULT_WORKING_END_MINUTE = 0
DEFAULT_TIME_INTERVAL = 30
MAX_BOOKING_DAYS_AHEAD = 90

# Phone validation
PHONE_NORMALIZED_LENGTH = 12
PHONE_PREFIX = '+7'

# Field lengths
PHONE_MAX_LENGTH = 20
NAME_MAX_LENGTH = 100
TELEGRAM_MAX_LENGTH = 100
BOOKING_ID_MAX_LENGTH = 50
STATUS_MAX_LENGTH = 25
PAYMENT_STATUS_MAX_LENGTH = 20
NOTIFICATION_METHOD_MAX_LENGTH = 10

# Template contexts
CONTEXT_FORM = 'form'
CONTEXT_PROCEDURES = 'procedures'
CONTEXT_BOOKING = 'booking'

# Messages
MSG_SESSION_EXPIRED = 'Сессия истекла. Пожалуйста, начните заново.'
MSG_BOOKING_CREATED = 'Заявка создана успешно!'
MSG_NOTIFICATION_SENT = 'Уведомление будет отправлено через {}'
MSG_CLIENT_REGISTERED = 'Новый клиент зарегистрирован.'
MSG_NOTIFICATION_UPDATED = 'Способ уведомления обновлен.'
MSG_TELEGRAM_ERROR = 'Заявка создана, но не удалось отправить уведомление.'
MSG_BOOKING_ERROR = 'Ошибка при создании бронирования: {}'
MSG_CLIENT_ERROR = 'Ошибка при создании клиента: {}'

# URLs
URL_SERVICE_LIST = 'booking:service_list'
URL_BOOKING_SUCCESS = 'booking:booking_success'

# Time generation constants
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60
DEFAULT_PROCEDURE_DURATION_MINUTES = 30
EMPTY_LIST_RESPONSE = []
EMPTY_STRING = ''

# AJAX response messages
AJAX_NO_PROCEDURE_RESPONSE = []
AJAX_NO_MASTER_DATE_RESPONSE = []
AJAX_ERROR_RESPONSE = []

# Status lists for filtering
ACTIVE_BOOKING_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_PAID]
