import json
from datetime import datetime, timedelta

# this option isn't ready yet

class SchedulesManager:
    def __init__(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                self.schedules = json.load(file)
        except Exception:
            print("No schedules path found or file unreadable.")
            self.schedules = []
        self.filter_and_save()

    @staticmethod
    def get_today_day_name(): # spanish
        days = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo"
        }
        return days[datetime.today().weekday()]

    def get_remaining_time(self, time_range):
        now = datetime.now()
        try:
            start_str = time_range.split('-')[0]
            start_time = datetime.strptime(start_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if now < start_time:
                delta = start_time - now
                hours, remainder = divmod(delta.seconds, 3600)
                minutes = remainder // 60
                return f"{hours}h {minutes}m"
            else:
                # Check if the class is already finished
                end_str = time_range.split('-')[1]
                end_time = datetime.strptime(end_str, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day
                )
                if now <= end_time:
                    return "In progress"
                else:
                    return "Finished"
        except Exception:
            return "Invalid time"
    
    def get_hours_since_finished(self, time_range):
        now = datetime.now()
        try:
            end_str = time_range.split('-')[1]
            end_time = datetime.strptime(end_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if now > end_time:
                delta = now - end_time
                hours = delta.total_seconds() // 3600
                minutes = (delta.total_seconds() % 3600) // 60
                return f"{int(hours)}h {int(minutes)}m"
            else:
                return None
        except Exception:
            return None
    
    def filter_and_save(self):
        today = self.get_today_day_name()
        filtered_items = [item for item in self.schedules if item.get("Dia") == today]

        for item in filtered_items:
            time_left = self.get_remaining_time(item.get('Hora', '00:00-00:00'))
            item['RemainingTime'] = time_left
            item['SavedAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if time_left == "Finished":
                time_passed = self.get_hours_since_finished(item.get('Hora', '00:00-00:00'))
                item['HoursSinceFinished'] = time_passed or "Unknown time"

        with open("Python/packages/schedules_today.json", "w", encoding="utf-8") as f:
            json.dump(filtered_items, f, ensure_ascii=False, indent=4)
    
    def load_today_schedule(self):
        today = self.get_today_day_name()
        result = []

        for item in self.schedules:
            if item.get("Dia") != today:
                continue

            # Recalculate times in real-time
            time_range = item.get('Hora', '00:00-00:00')
            time_left = self.get_remaining_time(time_range)
            item_copy = item.copy()  # Avoid mutating the original list if you don't want to
            item_copy['RemainingTimeToStart'] = time_left

            if time_left == "Finished":
                time_passed = self.get_hours_since_finished(time_range)
                item_copy['HoursSinceFinished'] = time_passed or "Unknown time"
            else:
                item_copy.pop('HoursSinceFinished', None)

            result.append(item_copy)

        if not result:
            return ["No classes for today\n"]
        return result

    def start(self):
        pass