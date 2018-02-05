class NoteSerializer(object):
    pass


class FoodLogSerializer(object):
    MEAL_MAP = {
        1: 'Breakfast',
        2: 'Morning Snack',
        3: 'Lunch',
        4: 'Afternoon Snack',
        5: 'Dinner',
        6: 'Evening Snack',
        7: 'Anytime',
    }

    meal = ''
    calories = 0
    carbs = 0
    fat = 0
    fiber = 0
    protein = 0
    sodium = 0
    name = ''
    brand = ''
    unit = {
        'plural': '',
        'name': '',
        'amount': 0,
    }

    def __init__(self, *args, **kwargs):
        self.calories = kwargs['calories']
        self.carbs = kwargs['carbs']
        self.fat = kwargs['fat']
        self.fiber = kwargs['fiber']
        self.protein = kwargs['protein']
        self.sodium = kwargs['sodium']
        self.name = kwargs['name']
        self.brand = kwargs['brand']
        self.unit = kwargs['unit']
        self.meal = FoodLogSerializer.MEAL_MAP[kwargs['meal_id']]

    @staticmethod
    def from_json(json):
        unit = json.get('unit', {})
        unit['amount'] = json.get('amount', 0)
        return FoodLogSerializer(
            calories=json.get('calories', 0),
            carbs=json.get('carbs', 0),
            fat=json.get('fat', 0),
            fiber=json.get('fiber', 0),
            protein=json.get('protein', 0),
            sodium=json.get('sodium', 0),
            name=json.get('name', ''),
            brand=json.get('brand', ''),
            meal_id=json.get('mealTypeId', 7),  # Default to 'Anytime'
            unit=unit,
        )


class DailyFoodlogSerializer(object):
    food_logs = []  # Unordered FoodLog objects
    meals = {meal_name: [] for meal_name in FoodLogSerializer.MEAL_MAP.values()}  # {'Breakfast': [], ...}
    summary = {
        'calories': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0,
        'protein': 0,
        'sodium': 0,
    }

    def __init__(self, food_logs, meals, summary):
        self.food_logs = food_logs
        self.meals = meals
        self.summary = summary

    @staticmethod
    def from_json(json):
        summary = json.get('summary', {})
        summary.pop('water', None)

        food_logs = [FoodLogSerializer.from_json(log_json['loggedFood']) for log_json in json['foods']]
        meals = {}
        for fl in food_logs:
            meals.setdefault(fl.meal, []).append(fl)

        return DailyFoodlogSerializer(
            food_logs=food_logs,
            meals=meals,
            summary=summary,
        )
