def format_match_info(match: dict) -> dict:

    tournament_id = match.get("tournament_id")
    tournament_name = match.get("tournament_name") or f"ID: {tournament_id}"
    league_name = match.get("league_name", "Без лиги")
    stream_url = match.get("stream_url")

    opponents = match.get("opponents", [])
    teams = " vs ".join(
        team.get("acronym") or team.get("name", "Команда") for team in opponents
    ) if opponents else "Команды неизвестны"

    return {
        "tournament_id": tournament_id,
        "tournament_name": tournament_name,
        "league_name": league_name,
        "stream_url": stream_url,
        "teams": teams,
    }