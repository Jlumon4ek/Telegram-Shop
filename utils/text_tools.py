async def chunk_messages(message_text, max_length=4096):
    lines = message_text.split('\n')
    messages = []
    current_message = []

    for line in lines:
        # Добавляем строку в текущее сообщение
        current_message.append(line)
        # Если строка содержит 'state :' это означает, что текущий блок данных завершён
        if 'state :' in line:
            # Собираем строки текущего сообщения в одну строку
            message_as_str = '\n'.join(current_message)
            # Проверяем длину текущего сообщения
            if len(message_as_str) > max_length:
                # Если длина превышает максимально допустимую, начинаем новое сообщение
                # Отправляем предыдущее сообщение и начинаем новое
                messages.append(
                    '\n'.join(current_message[:-len(current_message)]))
                current_message = current_message[-len(current_message):]
            # Очищаем текущее сообщение для следующего блока
            current_message = []

    # Добавляем последнее сообщение, если оно есть
    if current_message:
        messages.append('\n'.join(current_message))

    return messages


# async def TextFormatting(text):
#     text = text.replace('.', '\\.').replace('-', '\\-').replace('+', '\\+').replace('=', '\\=').replace('(', '\\(').replace(')', '\\)').replace('[', '\\[').replace(']', '\\]').replace(
#         '{', '\\{').replace('}', '\\}').replace('!', '\\!').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('|', '\\|').replace('~', '\\~')

#     return text
