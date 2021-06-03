import unittest
from datetime import date

from .scheduledtask import PeriodicScheduler
from dateutils import Weekdays

class PeriodicSchedulerTest(unittest.TestCase):
    "test PeriodicScheduler."
    def single_case(self, scheduler, start, expected):
        result = scheduler.next_occurrance_after(start.toordinal())
        self.assertEqual(result.date(), expected)
    
    def setUp(self) -> None:
        self.weekly_scheduler_wendesday = PeriodicScheduler(-1, -1, -1, Weekdays.WEDNESDAY)
        self.monthly_scheduler_15 = PeriodicScheduler(-1, -1, 15, -1)
        self.monthly_scheduler_30 = PeriodicScheduler(-1, -1, 30, -1)
        self.yearly_scheduler_5_15 = PeriodicScheduler(-1, 5, 15, -1)
        self.yearly_scheduler_2_29 = PeriodicScheduler(-1, 2, 29, -1)
        self.once_scheduler_2021_5_15 = PeriodicScheduler(2021, 5, 15, -1)
    
    def test_weekly_scheduler_type(self):
        self.assertEqual(self.weekly_scheduler_wendesday.get_type(), 'w')
        
    def test_week_scheduler_on_the_day(self):
        self.single_case(self.weekly_scheduler_wendesday,
            date(2021, 5, 12),
            date(2021, 5, 12))
        
    def test_week_scheduler_after_the_day(self):
        self.single_case(self.weekly_scheduler_wendesday,
            date(2021, 5, 10),
            date(2021, 5, 12))
        
    def test_week_scheduler_before_the_day(self):
        self.single_case(self.weekly_scheduler_wendesday,
            date(2021, 5, 14),
            date(2021, 5, 19))
        
    def test_monthly_schedule_type(self):
        self.assertEqual('m', self.monthly_scheduler_15.get_type())
        self.assertEqual('m', self.monthly_scheduler_30.get_type())
        
    def test_monthly_schedue_on_the_day(self):
        self.single_case(self.monthly_scheduler_15,
            date(2021, 5, 15),
            date(2021, 5, 15))
    
    def test_monthly_schedule_before_the_day(self):
        self.single_case(self.monthly_scheduler_15,
            date(2021, 5, 10),
            date(2021, 5, 15))
    
    def test_monthly_schedule_after_the_day(self):
        self.single_case(self.monthly_scheduler_15,
            date(2021, 5, 20),
            date(2021, 6, 15))
    
    def test_monthly_schedule_schedule_ahead(self):
        self.single_case(self.monthly_scheduler_30,
            date(2021, 2, 10),
            date(2021, 2, 28))
    
    def test_monthly_schedule_cross_year(self):
        self.single_case(self.monthly_scheduler_15,
            date(2020, 12, 20),
            date(2021, 1, 15))
            
    def test_yearly_schedule_type(self):
        self.assertEqual('y', self.yearly_scheduler_2_29.get_type())
        self.assertEqual('y', self.yearly_scheduler_5_15.get_type())
        
    def test_yearly_schedule_on_the_day(self):
        self.single_case(self.yearly_scheduler_5_15,
            date(2020, 5, 15),
            date(2020, 5, 15))
            
    def test_yearly_schedule_after_the_day(self):
        self.single_case(self.yearly_scheduler_5_15,
            date(2020, 5, 20),
            date(2021, 5, 15))
    
    def test_yearly_schedule_before_the_day(self):
        self.single_case(self.yearly_scheduler_5_15,
            date(2020, 5, 10),
            date(2020, 5, 15))
            
    def test_once_schedule_type(self):
        self.assertEqual('o', self.once_scheduler_2021_5_15.get_type()) 
        
    def test_once_schedule_on_the_day(self):
        self.single_case(self.once_scheduler_2021_5_15,
            date(2021, 5, 15),
            date(2021, 5, 15))
            
    def test_once_schedule_after_the_day(self):
        noexist = self.once_scheduler_2021_5_15.next_occurrance_after(date(2021, 5, 16).toordinal())
        self.assertEqual(noexist, None)
            
    def test_once_schedule_before_the_day(self):
        the_day = self.once_scheduler_2021_5_15.next_occurrance_after(date(2021, 5, 14).toordinal())
        self.assertEqual(the_day.date(), date(2021, 5, 15))