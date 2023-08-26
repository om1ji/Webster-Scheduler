from datetime import datetime

def ampm_to_string(input_str: str) -> int:
    """Переводит строку типа "9am", "7pm" в число часа
    9pm -> 21
    7am -> 7

    :param input_str: Время вида XX(p/a)m
    :type input_str: str
    :return: Час вида XX
    :rtype: int
    """
    try:
        dt = datetime.strptime(input_str, '%I%p')
        return dt.hour - 2 # Timezone correction
    except ValueError:
        return None
    
def string_to_datetime(hour: int):
    """Переводит число часа в datetime-объект

    Args:
        hour (int): Целое число часа вида X/XX

    Returns:
        _type_: datetime-объект
    """
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    
    if now >= target_time:
        target_time += datetime.timedelta(days=1)  # Установка времени на следующий день

    return target_time