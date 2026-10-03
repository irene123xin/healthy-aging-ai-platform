from src.training.attention import AttentionGenerator
from src.training.language import LanguageGenerator
from src.training.memory import MemoryGenerator
from src.training.movement import MovementGenerator
from src.training.reasoning import ReasoningGenerator


class ExerciseFactory:
    def __init__(self):
        self.generators = {g.category: g for g in [MemoryGenerator(), AttentionGenerator(), ReasoningGenerator(), LanguageGenerator(), MovementGenerator()]}

    def generate(self, category, difficulty, seed=None):
        if category not in self.generators: raise ValueError(f"Unknown category: {category}")
        return self.generators[category].generate(difficulty, seed)

