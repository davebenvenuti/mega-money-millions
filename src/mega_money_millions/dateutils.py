import datetime
from enum import Enum


def now():
  return datetime.datetime.now()


def parse_date(date_str, format=None):
  if format is None:
    format = '%Y-%m-%d'
  return datetime.datetime.strptime(date_str, format)


def start_of_day(date):
  return date.replace(hour=0, minute=0, second=0, microsecond=0)


def start_of_day_utc(date):
  return start_of_day(datetime.datetime.utcfromtimestamp(date.timestamp()))


def end_of_day(date):
  return date.replace(hour=23, minute=59, second=59, microsecond=999)


def days_ago(n, from_time=now()):
  return from_time - datetime.timedelta(days=n)


def days_later(n, from_time=now()):
  return from_time + datetime.timedelta(days=n)


class DayOfWeek(Enum):
  SUNDAY = 6
  MONDAY = 0
  TUESDAY = 1
  WEDNESDAY = 2
  THURSDAY = 3
  FRIDAY = 4
  SATURDAY = 5

# Returns the date itself if it's already Midnight Monday UTC.  Otherwise,
# return the next Midnight Monday UTC.


def __generate_next_day_at_midnight_fn(target_day=DayOfWeek.MONDAY):
  def __fn(start_at=now()):
    utc_day = datetime.datetime.utcfromtimestamp(
        start_at.timestamp()).replace(
        hour=0, minute=0, second=0, microsecond=0)
    day_of_week = utc_day.weekday()
    days_until_target_day = ((7 + target_day.value) - day_of_week) % 7

    # Return start_at only if it matches exactly (meaning it's time was midnight)
    if days_until_target_day == 0 and start_at != utc_day:
      days_until_target_day = 7

    return utc_day + datetime.timedelta(days=days_until_target_day)

  return __fn


next_monday_midnight = __generate_next_day_at_midnight_fn(DayOfWeek.MONDAY)
next_tuesday_midnight = __generate_next_day_at_midnight_fn(DayOfWeek.TUESDAY)
next_wednesday_midnight = __generate_next_day_at_midnight_fn(DayOfWeek.WEDNESDAY)
next_thursday_midnight = __generate_next_day_at_midnight_fn(DayOfWeek.THURSDAY)
next_friday_midnight = __generate_next_day_at_midnight_fn(DayOfWeek.FRIDAY)
next_saturday_midnight = __generate_next_day_at_midnight_fn(DayOfWeek.SATURDAY)
next_sunday_midnight = __generate_next_day_at_midnight_fn(DayOfWeek.SUNDAY)


def __generate_all_days_since_fn(target_day=DayOfWeek.MONDAY):
  def __fn(start_at, end_at=now()):
    next_day_at_midnight = __generate_next_day_at_midnight_fn(target_day)

    current = next_day_at_midnight(start_at)
    while current < end_at:
      if current > now():
        break

      yield current
      current += datetime.timedelta(days=7)

  return __fn


# Generator that yields every Monday Midnight UTC from start_at to end_at.
all_mondays_since = __generate_all_days_since_fn(DayOfWeek.MONDAY)
all_tuesdays_since = __generate_all_days_since_fn(DayOfWeek.TUESDAY)
all_wednesdays_since = __generate_all_days_since_fn(DayOfWeek.WEDNESDAY)
all_thursdays_since = __generate_all_days_since_fn(DayOfWeek.THURSDAY)
all_fridays_since = __generate_all_days_since_fn(DayOfWeek.FRIDAY)
all_saturdays_since = __generate_all_days_since_fn(DayOfWeek.SATURDAY)
all_sundays_since = __generate_all_days_since_fn(DayOfWeek.SUNDAY)


def all_days_since(start_at, end_at=now()):
  current = start_at
  while current <= end_at:
    yield current
    current += datetime.timedelta(days=1)
