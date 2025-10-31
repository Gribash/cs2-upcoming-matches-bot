export interface Tournament {
  id?: number;
  name?: string;
  tier?: string;
}

export interface Team {
  id?: number;
  name?: string;
  acronym?: string;
  image_url?: string;
}

export interface Stream {
  raw_url?: string;
  language?: string;
  platform?: string;
}

export interface MatchResult {
  team_id?: number;
  score?: number;
}

export interface Match {
  id: number;
  name?: string;
  begin_at?: string;
  scheduled_at?: string;
  status?: 'upcoming' | 'running' | 'finished' | 'past' | 'not_started';
  tournament?: Tournament;
  opponents?: Team[];
  winner_id?: number;
  streams?: Stream[];
  results?: MatchResult[];
}


