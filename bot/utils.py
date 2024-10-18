from typing import List, Optional, AsyncIterator

from telegram import Update, constants
from telegram.ext import ContextTypes


async def is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    chat_administrators = await context.bot.get_chat_administrators(chat_id)

    for admin in chat_administrators:
        if admin.user.id == user_id:
            return True

    return False


async def get_args(update: Update, context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    return context.args


def bot_mentioned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    is_private_chat = update.message.chat.type == "private"
    is_bot_mentioned = (
        update.message.text is not None
        and ("@" + context.bot.username) in update.message.text
    )
    bot_in_reply_tree = (
        update.message.reply_to_message is not None
        and update.message.reply_to_message.from_user.id == context.bot.id
    )
    return is_private_chat or bot_in_reply_tree or is_bot_mentioned


def get_thread_id(update: Update) -> Optional[int]:
    """
    Gets the message thread id for the update, if any
    """
    if update.effective_message and update.effective_message.is_topic_message:
        return update.effective_message.message_thread_id
    return None


def min_char_diff_for_buffering(content: str, is_group_chat: bool) -> int:
    """
    Get the minimum string length difference to trigger new yield in the streaming response
    """
    if is_group_chat:
        len_thresholds = [(180, 1000), (120, 200), (90, 50), (50, -1)]
    else:
        len_thresholds = [(90, 1000), (45, 200), (25, 50), (15, -1)]
        
    for char_diff, len_threshold in len_thresholds:
        if len(content) > len_threshold:
            return char_diff # Always reachable since len is always > 0


def is_group_chat(update: Update) -> bool:
    if not update.effective_chat:
        return False
    return update.effective_chat.type in [
        constants.ChatType.GROUP,
        constants.ChatType.SUPERGROUP,
    ]


async def buffer_streaming_response(
    stream: AsyncIterator[str], is_group_chat: bool
) -> AsyncIterator[str]:
    last_response_len = 0
    current_response = None
    i = 0
    async for chunk in stream:
        current_response = chunk
        i += 1
        if len(chunk) - last_response_len > min_char_diff_for_buffering(
            chunk, is_group_chat
        ):
            yield current_response
            current_response = None
            i = 0
            last_response_len = len(chunk)
    if i:
        yield current_response
