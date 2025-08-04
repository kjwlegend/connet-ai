"""
DateTime Utilities

This module provides utilities for datetime operations.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import pytz
from dateutil import parser as date_parser

from app.utils.logging import get_logger

logger = get_logger(__name__)


class DateTimeUtils:
    """DateTime utility functions."""
    
    @staticmethod
    def now_utc() -> datetime:
        """Get current UTC datetime."""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def now_local(tz: Optional[str] = None) -> datetime:
        """Get current datetime in specified timezone."""
        if tz:
            timezone_obj = pytz.timezone(tz)
            return datetime.now(timezone_obj)
        return datetime.now()
    
    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Convert datetime to UTC."""
        if dt.tzinfo is None:
            # Assume local timezone
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    
    @staticmethod
    def to_timezone(dt: datetime, tz: str) -> datetime:
        """Convert datetime to specified timezone."""
        timezone_obj = pytz.timezone(tz)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone_obj)
    
    @staticmethod
    def parse_datetime(dt_str: str) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        try:
            return date_parser.parse(dt_str)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse datetime string '{dt_str}': {e}")
            return None
    
    @staticmethod
    def format_datetime(
        dt: datetime,
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Format datetime to string."""
        return dt.strftime(format_str)
    
    @staticmethod
    def format_iso(dt: datetime) -> str:
        """Format datetime to ISO string."""
        return dt.isoformat()
    
    @staticmethod
    def format_rfc3339(dt: datetime) -> str:
        """Format datetime to RFC3339 string."""
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    @staticmethod
    def add_time(
        dt: datetime,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0
    ) -> datetime:
        """Add time to datetime."""
        delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        return dt + delta
    
    @staticmethod
    def subtract_time(
        dt: datetime,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0
    ) -> datetime:
        """Subtract time from datetime."""
        delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        return dt - delta
    
    @staticmethod
    def time_ago(dt: datetime) -> str:
        """Get human-readable time ago string."""
        now = DateTimeUtils.now_utc()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    
    @staticmethod
    def is_expired(dt: datetime, expiry_hours: int = 24) -> bool:
        """Check if datetime is expired."""
        now = DateTimeUtils.now_utc()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        expiry_time = dt + timedelta(hours=expiry_hours)
        return now > expiry_time
    
    @staticmethod
    def get_start_of_day(dt: datetime) -> datetime:
        """Get start of day for datetime."""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_end_of_day(dt: datetime) -> datetime:
        """Get end of day for datetime."""
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def get_start_of_week(dt: datetime) -> datetime:
        """Get start of week (Monday) for datetime."""
        start_of_day = DateTimeUtils.get_start_of_day(dt)
        return start_of_day - timedelta(days=start_of_day.weekday())
    
    @staticmethod
    def get_start_of_month(dt: datetime) -> datetime:
        """Get start of month for datetime."""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_date_range(
        start_date: datetime,
        end_date: datetime
    ) -> list[datetime]:
        """Get list of dates between start and end date."""
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    @staticmethod
    def is_business_day(dt: datetime) -> bool:
        """Check if datetime is a business day (Monday-Friday)."""
        return dt.weekday() < 5
    
    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """Check if datetime is a weekend (Saturday-Sunday)."""
        return dt.weekday() >= 5
    
    @staticmethod
    def next_business_day(dt: datetime) -> datetime:
        """Get next business day."""
        next_day = dt + timedelta(days=1)
        while not DateTimeUtils.is_business_day(next_day):
            next_day += timedelta(days=1)
        return next_day
    
    @staticmethod
    def calculate_age(birth_date: datetime) -> int:
        """Calculate age from birth date."""
        today = DateTimeUtils.now_utc().date()
        birth_date = birth_date.date() if isinstance(birth_date, datetime) else birth_date
        
        age = today.year - birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if today < birth_date.replace(year=today.year):
            age -= 1
        
        return age
    
    @staticmethod
    def get_quarter(dt: datetime) -> int:
        """Get quarter (1-4) for datetime."""
        return (dt.month - 1) // 3 + 1
    
    @staticmethod
    def get_week_number(dt: datetime) -> int:
        """Get week number (1-53) for datetime."""
        return dt.isocalendar()[1]
    
    @staticmethod
    def get_day_of_year(dt: datetime) -> int:
        """Get day of year (1-366) for datetime."""
        return dt.timetuple().tm_yday


# Convenience functions
def now() -> datetime:
    """Get current UTC datetime."""
    return DateTimeUtils.now_utc()


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime string."""
    return DateTimeUtils.parse_datetime(dt_str)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return DateTimeUtils.format_datetime(dt, format_str)


def time_ago(dt: datetime) -> str:
    """Get human-readable time ago string."""
    return DateTimeUtils.time_ago(dt)


def is_expired(dt: datetime, expiry_hours: int = 24) -> bool:
    """Check if datetime is expired."""
    return DateTimeUtils.is_expired(dt, expiry_hours)


# Common datetime formats
class DateTimeFormats:
    """Common datetime format strings."""
    
    ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
    ISO_FORMAT_WITH_TZ = "%Y-%m-%dT%H:%M:%S%z"
    RFC3339_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    DATE_ONLY = "%Y-%m-%d"
    TIME_ONLY = "%H:%M:%S"
    DATETIME_SIMPLE = "%Y-%m-%d %H:%M:%S"
    DATETIME_READABLE = "%B %d, %Y at %I:%M %p"
    LOG_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


# Common timezones
class TimeZones:
    """Common timezone identifiers."""
    
    UTC = "UTC"
    US_EASTERN = "US/Eastern"
    US_CENTRAL = "US/Central"
    US_MOUNTAIN = "US/Mountain"
    US_PACIFIC = "US/Pacific"
    EUROPE_LONDON = "Europe/London"
    EUROPE_PARIS = "Europe/Paris"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_SHANGHAI = "Asia/Shanghai"
    AUSTRALIA_SYDNEY = "Australia/Sydney"