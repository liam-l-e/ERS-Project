class GameAction: 
    def __init__(self, type, player, time):
        self.action_type = type
        self.player = player
        self.time = time

    def __lt__(self, other):
        # Less than: self < other
        if isinstance(other, GameAction):
            return self.time < other.time
        return NotImplemented

    def __le__(self, other):
        # Less than or equal to: self <= other
        if isinstance(other, GameAction):
            return self.time <= other.time
        return NotImplemented

    def __eq__(self, other):
        # Equal to: self == other
        if isinstance(other, GameAction):
            return self.time == other.time
        return NotImplemented

    def __ne__(self, other):
        # Not equal to: self != other
        if isinstance(other, GameAction):
            return self.time != other.time
        return NotImplemented

    def __gt__(self, other):
        # Greater than: self > other
        if isinstance(other, GameAction):
            return self.time > other.time
        return NotImplemented

    def __ge__(self, other):
        # Greater than or equal to: self >= other
        if isinstance(other, GameAction):
            return self.time >= other.time
        return NotImplemented
    
    def __str__(self) -> str:
        return f"GameAction: player {self.player.name}, action {self.action_type}, time {self.time}"