class Command:
    pass


class CreateSubscription(Command):
    def __init__(self, user_id: int, plan_name: str, payment_details: dict):
        self.user_id = user_id
        self.plan_name = plan_name
        self.payment_details = payment_details


class CancelSubscription(Command):
    def __init__(self, user_id: int):
        self.user_id = user_id


class RenewSubscription(Command):
    def __init__(self, user_id: int):
        self.user_id = user_id


class ChangeSubscriptionPlan(Command):
    def __init__(self, user_id: int, new_plan_name: str):
        self.user_id = user_id
        self.new_plan_name = new_plan_name
