from handlers.command_handlers import register_command_handlers
from handlers.message_handlers import register_message_handlers
from handlers.callback_query_handlers import register_callback_query_handlers


async def register_handlers(dp, bot, mongo):
    await register_command_handlers(dp, bot, mongo)
    await register_message_handlers(dp, bot, mongo)
    await register_callback_query_handlers(dp, bot, mongo)
