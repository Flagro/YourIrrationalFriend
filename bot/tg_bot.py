from telegram import Update, BotCommand
from telegram.ext import (
    AIORateLimiter,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
    Application,
)
from telegram.constants import ParseMode

import logging
from typing import Literal, Optional, List
from functools import partial


class TelegramBot:
    def __init__(
        self,
        telegram_token: str,
        openai_token: str,
        allowed_handles: List[str],
    ):
        self.telegram_token = telegram_token
        self.openai_token = openai_token
        self.allowed_handles = allowed_handles
        self.logger = logging.getLogger("TelegramBot")

    async def post_init(self, application: Application) -> None:
        """
        Post initialization hook for the bot.
        """
        bot_commands = [
            BotCommand(
                command=command.command,
                description=await command.get_localized_description(),
            )
            for command in self.commands
        ]
        await application.bot.set_my_commands(bot_commands)

    def run(self) -> None:
        """
        Runs the bot indefinitely until the user presses Ctrl+C
        """
        application = (
            ApplicationBuilder()
            .token(self.telegram_token)
            .concurrent_updates(True)
            .rate_limiter(AIORateLimiter(max_retries=5))
            .post_init(self.post_init)
            .build()
        )
        command_handlers = [
            CommandHandler(command.command, partial(self.handle, bot_handler=command))
            for command in sorted(
                self.commands, key=lambda x: (x.list_priority_order, x.command)
            )
        ]
        message_handlers = [
            MessageHandler(
                (filters.TEXT | filters.VOICE | filters.PHOTO) & ~filters.COMMAND,
                partial(self.handle, bot_handler=message),
            )
            for message in self.messages
        ]
        application.add_handlers(
            command_handlers + message_handlers
        )
        application.add_error_handler(self.error_handle)
        application.run_polling()

    async def error_handle(self, update: Update, context: CallbackContext) -> None:
        self.logger.error(
            msg="Exception while handling an update:", exc_info=context.error
        )

    async def push_state(
        self,
        update: Update,
        context: CallbackContext,
        state: Literal["sending_text", "sending_image", "sending_audio"],
    ) -> None:
        action_map = {
            "sending_text": "typing",
            "sending_image": "upload_photo",
            "sending_audio": "upload_audio",
        }
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=action_map[state],
        )

    async def send_message(
        self,
        context: CallbackContext,
        chat_id: int,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        reply_message_id: Optional[int] = None,
        thread_id: Optional[int] = None,
        parse_mode: Optional[ParseMode] = ParseMode.HTML,
    ) -> None:
        return await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_message_id,
            parse_mode=parse_mode,
        )
