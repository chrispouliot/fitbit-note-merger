from datetime import datetime
from pytz import timezone


class NoteSerializer(object):
    _model = None

    id = 0
    text = ''
    classifier = ''

    def __init__(self, model):
        self.model = model
        self.id = model.id
        self.text = model.text
        self.classifier = model.classifier

    @property
    def created_date(self):
        # Janky PST (temporary [famous last words])
        return self.model.created_date.astimezone(timezone('US/Pacific'))


class FoodLogSerializer(object):
    _MEAL_ID_TIME_MAP = {
        1: '08:30',
        2: '10:30',
        3: '12:30',
        4: '15:00',
        5: '18:30',
        6: '20:00',
        7: '',
    }

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

    @staticmethod
    def from_json(json):
        # Inner JSON. The original JSON contains useful metadata
        food_json = json['loggedFood']
        # Format
        meal_id = food_json.get('mealTypeId', 7)  # Default to Fitbit's 'Anytime'
        meal_time = FoodLogSerializer._MEAL_ID_TIME_MAP[meal_id]
        # Create a PST date for the FoodLog
        naive_date = datetime.strptime('{} {}'.format(json.get('logDate'), meal_time), '%Y-%m-%d %H:%M')
        date = timezone('US/Pacific').localize(naive_date)

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
        summary.pop('water', None)  # Don't need to display water

        food_logs = [FoodLogSerializer.from_json(log_json) for log_json in json['foods']]

        return DailyFoodlogSerializer(
            date=food_logs[0].date if food_logs else None,
            food_logs=sorted(food_logs, key=lambda log: log.date),
            summary=summary,
        )
