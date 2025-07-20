from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.pandascore import format_time_until

def build_match_card(
    match: dict,
    *,
    show_time_until: bool = False,
    show_winner: bool = False,
    stream_button_text: str | None = None
) -> tuple[str, InlineKeyboardMarkup | None]:
    league = match.get("league", {}).get("name", "?")
    tournament = match.get("tournament", {}).get("name", "?")
    serie = match.get("serie", {}).get("full_name", "?")

    opponents = match.get("opponents", [])
    team1 = opponents[0].get("name") if len(opponents) > 0 else "Team1"
    team2 = opponents[1].get("name") if len(opponents) > 1 else "Team2"

    message = f"{league} | {tournament}\n{serie}\n<b>{team1} vs {team2}</b>"

    # Победитель (если матч завершён и указан winner_id)
    if show_winner and match.get("status") == "finished":
        winner_id = match.get("winner_id")
        winner_name = "?"
        for team in opponents:
            if str(team.get("id")) == str(winner_id):
                winner_name = team.get("name") or team.get("acronym") or "?"
                break
        message += f"\n<b>🏆 Победитель:</b> {winner_name}"

    # Время до начала
    if show_time_until:
        begin_at = match.get("begin_at")
        if begin_at:
            time_until = format_time_until(begin_at)
            if time_until != "Время неизвестно":
                message += f"\n<b>Начнётся через:</b> {time_until}"

    # Кнопка трансляции
    stream_url = match.get("stream_url")
    if stream_url and stream_url.startswith("http"):
        button_text = stream_button_text or f"{team1} vs {team2}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=button_text, url=stream_url)]
        ])
    else:
        keyboard = None
        message += "\n<i>Трансляция отсутствует</i>"

    return message, keyboard