TRANSLATIONS = {
    "en": {
        "greeting": (
            "Hi! I will notify you about upcoming matches.\n"
            "By default, I track only tier-1 tournaments.\n"
            "Use /subscribe_all to get all matches.\n"
            "You can change the language using /language."
        ),
        "choose_language": "Please choose your language:",
        "language_updated": "✅ Language updated to English",
        "no_upcoming": "No upcoming matches",
        "no_live": "No live matches",
        "no_recent": "No recent matches",
        "subscribed_top": "You are now subscribed to top-tier tournaments.",
        "subscribed_all": "You are now subscribed to all tournaments.",
        "unsubscribed": "You have unsubscribed from notifications.",
        "winner": "🏆 Winner:",
        "time_until": "⏳ Starts in:",
        "no_stream": "No stream available",
        "prefix_upcoming": "⏳ <b>Upcoming Matches</b>",
        "prefix_live": "🔴 <b>Live Matches</b>",
        "prefix_recent": "🏁 <b>Recent Matches</b>",
    },
    "ru": {
        "greeting": (
            "Привет! Я буду присылать уведомления о матчах.\n"
            "По умолчанию отслеживаются только тир-1 турниры.\n"
            "Используйте /subscribe_all, чтобы получать все матчи.\n"
            "Вы можете сменить язык с помощью /language."
        ),
        "choose_language": "Пожалуйста, выберите язык:",
        "language_updated": "✅ Язык обновлён на Русский",
        "no_upcoming": "Нет ближайших матчей",
        "no_live": "Сейчас нет активных матчей",
        "no_recent": "Нет результатов недавних матчей",
        "subscribed_top": "Вы подписаны на топ-турниры.",
        "subscribed_all": "Теперь вы подписаны на все турниры.",
        "unsubscribed": "Вы отписаны от уведомлений.",
        "winner": "🏆 Победитель:",
        "time_until": "⏳ Начнётся через:",
        "no_stream": "Трансляция отсутствует",
        "prefix_upcoming": "⏳ <b>Ближайшие матчи</b>",
        "prefix_live": "🔴 <b>Текущие матчи</b>",
        "prefix_recent": "🏁 <b>Недавние матчи</b>",
    },
    "pt": {
        "greeting": (
            "Olá! Vou te enviar notificações sobre partidas.\n"
            "Por padrão, acompanho apenas torneios de tier 1.\n"
            "Use /subscribe_all para receber todas as partidas.\n"
            "Você pode alterar o idioma com /language."
        ),
        "choose_language": "Por favor, escolha seu idioma:",
        "language_updated": "✅ Idioma alterado para Português",
        "no_upcoming": "Sem partidas futuras",
        "no_live": "Nenhuma partida ao vivo agora",
        "no_recent": "Nenhum resultado recente",
        "subscribed_top": "Você está inscrito em torneios de alto nível.",
        "subscribed_all": "Agora você está inscrito em todos os torneios.",
        "unsubscribed": "Você cancelou a inscrição nas notificações.",
        "winner": "🏆 Vencedor:",
        "time_until": "⏳ Começa em:",
        "no_stream": "Sem transmissão disponível",
        "prefix_upcoming": "⏳ <b>Próximas Partidas</b>",
        "prefix_live": "🔴 <b>Partidas Ao Vivo</b>",
        "prefix_recent": "🏁 <b>Partidas Recentes</b>",
    }
}

def t(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)