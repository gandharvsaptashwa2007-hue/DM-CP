import unittest
from ui.tour import tour_steps
from ui.design import MODULES


class TourScopeTests(unittest.TestCase):
    def test_shared_steps_only_on_home(self):
        home_selectors = {step[0] for step in tour_steps("Home")}
        self.assertIn(".brand-lockup", home_selectors)
        for module in MODULES:
            selectors = {step[0] for step in tour_steps(module)}
            self.assertFalse(selectors & home_selectors, module)
            self.assertIn(".st-key-workspace [data-testid='stBaseButton-primary']", selectors)
