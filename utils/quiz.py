from dataclasses import dataclass, field
from typing import Optional
from typing import List, Dict

@dataclass
class QuizSession:
    category_id: int
    category_name: str
    difficulty: str
    questions: List[dict]
    current_index: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    score: int = 0
    total_xp: int = 0
    start_time: float = 0.0

# In-memory xotira tezkor sessionlar uchun
QUIZ_SESSIONS: Dict[int, QuizSession] = {}

@dataclass
class BattleRoom:
    room_id: str
    player1_id: int
    player2_id: int
    player1_score: int = 0
    player2_score: int = 0
    player1_finished: bool = False
    player2_finished: bool = False
    questions: list = field(default_factory=list)
    current_question_idx: int = 0

# Matchmaking navbati va faol duel xonalari
BATTLE_QUEUE: list[int] = []
BATTLE_ROOMS: Dict[str, BattleRoom] = {}
USER_BATTLE_ROOM: Dict[int, str] = {}