from enum import Enum


class OrderStatus(Enum):
    PROCESSING = "В обработке"  # Заказ отправлен и находится в обработке
    PREPARING = "Готовится"  # Заказ готовится
    DELIVERY = "В доставке"  # Заказ доставляется
    COMPLETED = "Завершен"  # Заказ завершен


class OrderFieldsLang(Enum):
    phone = "номер"  # Заказ отправлен и находится в обработке
    comment = "комментарий"  # Заказ готовится
    address = "адрес"  # Заказ доставляется
    status = "статус"  # Заказ завершен
    username = ""  # Заказ завершен
