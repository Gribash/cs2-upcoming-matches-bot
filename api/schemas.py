from typing import List, Optional, Literal

from pydantic import BaseModel


class Tournament(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    tier: Optional[str] = None


class Team(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    acronym: Optional[str] = None
    image_url: Optional[str] = None


class Stream(BaseModel):
    raw_url: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None


class MatchResult(BaseModel):
    team_id: Optional[int] = None
    score: Optional[int] = None


class Match(BaseModel):
    id: int
    name: Optional[str] = None
    begin_at: Optional[str] = None
    scheduled_at: Optional[str] = None
    status: Optional[Literal["upcoming", "running", "finished", "past", "not_started"]]
    tournament: Optional[Tournament] = None
    opponents: Optional[List[Team]] = None
    winner_id: Optional[int] = None
    streams: Optional[List[Stream]] = None
    results: Optional[List[MatchResult]] = None


