from enum import Enum


class OrderStatus(Enum):
    PROCESSING = "На подтверждении"  # Заказ отправлен и находится в обработке
    CONFIRMED = "Подтвержден"  # Заказ готовится
    CANCELLED = "Отменен"  # Заказ готовится


class OrderFieldsLang(Enum):
    phone = "номер"  # Заказ отправлен и находится в обработке
    comment = "комментарий"  # Заказ готовится
    address = "адрес"  # Заказ доставляется
    status = "статус"  # Заказ завершен
    username = ""  # Заказ завершен
