from player import Player

EPSILON = 0.05
GAMMA = 0.8
ALPHA = 0.2

class QLearningPlayer(Player):

    def __init__(self):
        super(QLearningPlayer, self).__init__()
        self.Q_values = {}
        self.alpha = ALPHA
        self.epsilon = EPSILON
        self.discount = GAMMA

    def get_Q_value(self, state, action):
        if not state in self.Q_values:
            return 0.0
        return self.Q_values[state][action]

    def get_value(self, state):
        actions = self.get_legal_actions(state)
        if not actions:
            return 0.0
        return max(self.get_Q_value(state, action) for action in actions)

    def get_policy(self, state):
        actions = self.get_legal_actions(state)
        if not actions:
            return None

        q = Counter()
        for action in actions:
            q[action] = self.get_Q_value(state, action)
        return arq_max(q)

    def get_action(self, state):
        legal_actions = self.get_legal_actions(state)
        if not legal_actions:
            return None
        is_random = flip_coin(self.epsilon)
        return random.choice(legal_actions) if is_random else self.get_policy(state)

    def update(self, state, action, nextState, reward):
        sample = reward + self.discount * self.get_value(nextState)
        if state not in self.Q_values:
            self.Q_values[state] = Counter()
        self.Q_values[state][action] = (1 - self.alpha) * self.Q_values[state][action] + self.alpha * sample


