"""Declare main classes for controling bot behavior."""
import logging
import random
import uuid
from pathlib import Path
from telegram.ext import (
    Updater,
    CommandHandler,
    Filters,
    MessageHandler,
    ConversationHandler,
)
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from typing import Any, Dict


class ConfigConversation:
    """Get configuration conversation."""

    GENDER, AGE, TATAR_LEVEL, RUSSIAN_LEVEL, CONCL = range(5)
    level_keyboard = [
        ["Начинающий", "Продолжающий"],
        ["Высокий", "Носитель"]
    ]
    level_markup = ReplyKeyboardMarkup(level_keyboard, resize_keyboard=True)

    @classmethod
    def level_checker(cls, possible_ans):
        """Check if level has propriate value."""
        return possible_ans in (cls.level_keyboard[0] + cls.level_keyboard[1])

    @classmethod
    def _begin(cls, update, context):
        keyboard = [['Мужской', 'Женский']]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            'Отлично! Для начала разберемся с полом.',
            reply_markup=markup,
        )
        return cls.AGE

    @classmethod
    def _age(cls, update, context):
        """Get age from conversation."""
        context.user_data['gender'] = update.message.text
        update.message.reply_text(
            "Отлично, с полом определились. Давайте узнаем Ваш возраст.",
            reply_markup=ReplyKeyboardRemove())
        return cls.TATAR_LEVEL

    @classmethod
    def _tatar_level(cls, update, context):
        """Get level of tatar language from conversation."""
        possible_age = update.message.text
        if not possible_age.isdigit() or len(possible_age) > 2:
            update.message.reply_text(
                "Возраст введен неверно.\
 Вводите свой настоящий возраст числом.",
                reply_markup=ReplyKeyboardRemove()
            )
            return cls.TATAR_LEVEL
        context.user_data['age'] = possible_age
        update.message.reply_text(
            "Отлично! Теперь давай узнаем твой уровень татарского языка.",
            reply_markup=cls.level_markup
        )
        return cls.RUSSIAN_LEVEL

    @classmethod
    def _russian_level(cls, update, context):
        """Get level of russian language from conversation."""
        possible_level = update.message.text
        if not cls.level_checker(possible_level):
            update.message.reply_text(
                "Мы не расспознали ваше владение татарским,\
 введите его еще раз, пожалуйста.",
                reply_markup=cls.level_markup
            )
            return cls.RUSSIAN_LEVEL
        context.user_data['tatar'] = possible_level
        update.message.reply_text(
            "Отлично! Теперь давай узнаем твой уровень русского языка.",
            reply_markup=cls.level_markup
        )
        return cls.CONCL

    @classmethod
    def _conclude_conv(cls, update, context):
        """Sum up configuration part."""
        possible_level = update.message.text
        if not cls.level_checker(possible_level):
            update.message.reply_text(
                "Мы не расспознали твой уровень русского языка, введи его еще раз.",
                reply_markup=cls.level_markup
            )
            return cls.CONCL
        context.user_data['russian'] = possible_level
        keyboard = [['/read']]
        update.message.reply_text(
            "Спасибо за обратную связь!\
 Мы будем очень благодарны, если вы прочтете что-то из наших текстов.\
 Для этого введите комманду: /read",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ConversationHandler.END

    @property
    def handler(self) -> ConversationHandler:
        """Get conversation handler to specify info."""
        conv_handler: ConversationHandler = ConversationHandler(
            entry_points=[CommandHandler('configure', self._begin)],
            states={
                self.AGE: [MessageHandler(Filters.text, self._age)],
                self.GENDER: [MessageHandler(Filters.text, self._begin)],
                self.TATAR_LEVEL: [MessageHandler(Filters.text, self._tatar_level)],
                self.RUSSIAN_LEVEL: [
                    MessageHandler(Filters.text, self._russian_level)
                ],
                self.CONCL: [MessageHandler(Filters.text, self._conclude_conv)]
            },
            fallbacks=[CommandHandler('exit', self._conclude_conv)],
        )
        return conv_handler


class ReadFileConversation:
    """Basic conversation which loads audio data."""

    LOAD_AUDIO = 1
    total_texts = 1000
    file_loader = None

    @staticmethod
    def generate_load_string(obj: Dict[str, Any]) -> str:
        """Generate simple filename to load file to bucket."""

        obj['age'] = obj.get('age') or '0'
        obj['tatar'] = obj.get('tatar') or 'not'
        obj['russian'] = obj.get('russian') or 'not'
        obj['gender'] = obj.get('gender') or 'not'

        return f"{obj['text']}_{obj['age']}_{obj['gender']}\
_{obj['tatar']}_{obj['russian']}_{uuid.uuid4()}.mp3"

    @classmethod
    def _read(cls, update, context):
        """Start reading data from user."""
        current_text = random.randint(1, cls.total_texts)
        context.user_data['text'] = current_text
        update.message.reply_text(
            Path(f'source/texts/{current_text}.txt').read_text(),
            reply_markup=ReplyKeyboardRemove())
        return cls.LOAD_AUDIO

    @classmethod
    def _load_audio(cls, update, context):
        """Load file from update context to google cloud bucket."""
        keyboard = [['/read']]
        update.message.reply_text(
            "Спасибо за Ваш\
 вклад в наше исследование. Можете прочитать еще раз: /read",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        new_file = None

        if update.message.voice is not None:
            new_file = update.message.bot.get_file(update.message.voice.file_id)
            new_file.download("upload.mp3")

        if update.message.audio is not None:
            new_file = update.message.bot.get_file(update.message.audio.file_id)
            new_file.download("upload.mp3")

        if new_file is None:
            update.message.reply_text(
                "Мы не смогли распознать аудио. Отправьте, пожалуйста, еще раз.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return cls.LOAD_AUDIO

        cls.file_loader.upload_file(
            'upload.mp3',
            cls.generate_load_string(context.user_data),
            upload_binary=True,
        )
        return ConversationHandler.END

    @classmethod
    def _stop(cls, update, context):
        """Stop current audio report."""
        keyboard = [['/read']]
        update.message.reply_text(
            "Вы можете повторить попытку\
 в любое время. Только введите: /read",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )

    @property
    def handler(self) -> ConversationHandler:
        """Return handler related to loading audiofile."""
        conv_handler: ConversationHandler = ConversationHandler(
            entry_points=[CommandHandler('read', self._read)],
            states={
                self.LOAD_AUDIO: [
                    MessageHandler(Filters.audio | Filters.voice, self._load_audio)
                ]
            },
            fallbacks=[CommandHandler('stop', self._stop)]
        )
        return conv_handler


class BotConfiguration:
    """Declare main callbacks and structure of the bot."""

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    _logger = logging.getLogger(__name__)

    def __init__(self, tg_token: str, file_loader: Any, total_texts: int = 1000):
        """Create updater, dispatcher and declare main interface."""
        self._updater = Updater(tg_token, use_context=True)
        self._dp = self._updater.dispatcher
        self._file_loader = file_loader
        self._config_conversation = ConfigConversation()
        ReadFileConversation.file_loader = self._file_loader
        ReadFileConversation.total_texts = total_texts
        self._read_file_conversation = ReadFileConversation()

    @classmethod
    def _start(cls, update, context):
        """Upload start handler."""
        keyboard = [['/configure']]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            "Привет!\
 Этот бот помогает лингвистам изучать речевые\
 особенности носителей татарского и русского языков.\
 Для начала давай немного познакомимся. Эти данные нужны\
 будут нам только подтверждения некоторых наших гипотез😃",
            reply_markup=markup
        )

    @classmethod
    def _error(cls, update, context):
        """Log Errors caused by Updates."""
        cls._logger.warning('Update "%s" caused error "%s"', update, context.error)

    @property
    def _handlers(self):
        return [
            CommandHandler('start', self._start),
            self._config_conversation.handler,
            self._read_file_conversation.handler,
        ]

    def start_bot(self):
        """Start bot."""
        # Add different commands to answer in telegram
        for handler in self._handlers:
            self._dp.add_handler(handler)

        # Log errors
        self._dp.add_error_handler(self._error)
        # Start bot
        self._updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self._updater.idle()
