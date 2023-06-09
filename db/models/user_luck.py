class UserLuck:
    def __init__(self,user_id,user,lucky,unlucky,last_roll_date,luckyStreak,unluckyStreak):
        self.user_id = user_id
        self.user = user
        self.lucky = lucky
        self.unlucky = unlucky
        self.last_roll_date = last_roll_date
        self.currentLuckyStreak = luckyStreak
        self.currentUnluckyStreak = unluckyStreak