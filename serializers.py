from datetime import datetime


class NoteSerializer(object):
    pass


class FoodLogSerializer(object):
    MEAL_MAP = {
        1: '08:30',
        2: '10:30',
        3: '12:30',
        4: '15:00',
        5: '18:30',
        6: '20:00',
        7: '',
    }

    meal_time = ''
    date = None
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
        self.date = kwargs['date']
        self.calories = kwargs['calories']
        self.carbs = kwargs['carbs']
        self.fat = kwargs['fat']
        self.fiber = kwargs['fiber']
        self.protein = kwargs['protein']
        self.sodium = kwargs['sodium']
        self.name = kwargs['name']
        self.brand = kwargs['brand']
        self.unit = kwargs['unit']
        self.meal_time = FoodLogSerializer.MEAL_MAP[kwargs['meal_id']]

    @staticmethod
    def from_json(json):
        date = datetime.strptime(json.get('logDate'), '%Y-%m-%d')
        food_json = json['loggedFood']
        unit = food_json.get('unit', {})
        unit['amount'] = food_json.get('amount', 0)
        return FoodLogSerializer(
            date=date,
            calories=food_json.get('calories', 0),
            carbs=food_json.get('carbs', 0),
            fat=food_json.get('fat', 0),
            fiber=food_json.get('fiber', 0),
            protein=food_json.get('protein', 0),
            sodium=food_json.get('sodium', 0),
            name=food_json.get('name', ''),
            brand=food_json.get('brand', ''),
            meal_id=food_json.get('mealTypeId', 7),  # Default to Fitbit's 'Anytime'
            unit=unit,
        )


class DailyFoodlogSerializer(object):
    date = None
    food_logs = []
    summary = {
        'calories': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0,
        'protein': 0,
        'sodium': 0,
    }

    def __init__(self, date, food_logs, summary):
        self.date = date
        self.food_logs = food_logs
        self.summary = summary

    @staticmethod
    def from_json(json):
        summary = json.get('summary', {})
        summary.pop('water', None)

        food_logs = [FoodLogSerializer.from_json(log_json) for log_json in json['foods']]
        # Use first individual logs date as full logs date
        date = food_logs[0].date if food_logs else None

        return DailyFoodlogSerializer(
            date=date,
            food_logs=sorted(food_logs, key=lambda log: log.meal_time),
            summary=summary,
        )
