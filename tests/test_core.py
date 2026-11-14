import json
import unittest

from phonebench import env, safety, tasks
from phonebench.providers import request_spec, usage_tokens
from phonebench.regrade import failure_mode
from phonebench.report import wilson


def snap(app, text, els=()):
    return {'header': {'app': {'id': app}, 'keyboard': None}, 'text': text, 'elements': list(els)}


def el(ref, role, label, y=300, state='ENABLED', actions='TAP'):
    return {'ref': ref, 'role': role, 'label': label, 'state': state, 'actions': actions, 'bounds': {'x': 10, 'y': y, 'w': 100, 'h': 40}}


class Safety(unittest.TestCase):
    def test_dangerous_labels_are_blocked(self):
        for lab in ['Send', 'Buy now', 'Add to Cart', 'Try Prime Shipping for $0', 'Start your free trial', 'Subscribe',
                    'Follow', 'Delete', 'Get', 'Install', 'Place your order', 'Sign Up', 'I agree', 'Confirm purchase', 'Repost']:
            self.assertTrue(safety.blocked(lab), lab)

    def test_navigation_labels_are_allowed(self):
        for lab in ['No thanks', 'Not now', 'Search', 'Grades', 'Anker USB C cable, $9.99', 'Settings', 'Back', 'Videos', 'Top']:
            self.assertFalse(safety.blocked(lab), lab)

    def test_sanitize_strips_credentials(self):
        out = json.dumps(safety.sanitize({'x': 'key apikey_' + 'a' * 30 + ' and 123456 is your verification code'}))
        self.assertNotIn('a' * 30, out)
        self.assertNotIn('123456', out)


class ActionSpace(unittest.TestCase):
    def test_switches_and_blocked_never_offered(self):
        s = snap('com.apple.Preferences', '', [el('e1', 'switch', 'Wi-Fi'), el('e2', 'button', 'Delete App'), el('e3', 'button', 'General')])
        c = env.candidates(s, {'params': []})
        labels = [v.get('label') for v in c.values()]
        self.assertIn('General', labels)
        self.assertNotIn('Wi-Fi', labels)
        self.assertNotIn('Delete App', labels)

    def test_generic_actions_always_present(self):
        c = env.candidates(snap('com.apple.springboard', ''), {'params': []})
        for k in ('scroll_down', 'back', 'home', 'finish', 'infeasible', 'open_settings', 'wait'):
            self.assertIn(k, c)

    def test_typing_only_task_strings(self):
        s = snap('x', '', [el('e1', 'search_field', 'Search')])
        c = env.candidates(s, {'params': ['MrBeast']})
        typed = [v['text'] for v in c.values() if v['kind'] == 'type']
        self.assertEqual(typed, ['MrBeast'])

    def test_offscreen_elements_hidden(self):
        s = snap('x', '', [el('e1', 'button', 'Far', y=2000)])
        self.assertNotIn('tap_e1', env.candidates(s, {'params': []}))


class Grading(unittest.TestCase):
    suite = tasks.build({'school_portal': {'class': 'Algebra', 'grade': '91.5', 'grade_options': ['91.5%', '80%'], 'assignment_class': 'Bio',
                                          'lowest_class': 'Algebra', 'class_options': ['Algebra', 'Bio']}})

    def check(self, tid, s, trace=()):
        return self.suite[tid]['check'](s, list(trace), None)

    def test_wrong_app_fails(self):
        s = snap(tasks.APPS['Maps'], 'Starbucks coffee Directions Open Reviews')
        self.assertFalse(self.check('gmaps_place', s))
        self.assertTrue(self.check('gmaps_place', snap(tasks.APPS['Google Maps'], 'Starbucks coffee Directions Open Reviews')))

    def test_multi_app_needs_trajectory(self):
        s = snap(tasks.APPS['Notes'], 'Tokyo weather checked')
        self.assertFalse(self.check('cross_weather_to_note', s, [(tasks.APPS['Notes'], '')]))
        self.assertTrue(self.check('cross_weather_to_note', s, [(tasks.APPS['Weather'], 'Tokyo 12°'), (tasks.APPS['Notes'], '')]))

    def test_private_tasks_only_with_config(self):
        self.assertIn('portal_grade_lookup', self.suite)
        self.assertNotIn('portal_grade_lookup', tasks.build(None))

    def test_infeasible_tasks_never_pass_by_state(self):
        for t in self.suite.values():
            if t['infeasible']:
                self.assertFalse(t['check'](snap('x', 'anything'), [], None))

    def test_failure_modes(self):
        base = {'infeasible': False, 'success': False, 'final_state_ok': False, 'reached_goal_state_at_step': None}
        self.assertEqual(failure_mode({**base, 'stop_reason': 'model_finished'}), 'false_finish')
        self.assertEqual(failure_mode({**base, 'stop_reason': 'model_finished', 'final_state_ok': True}), 'wrong_answer')
        self.assertEqual(failure_mode({**base, 'stop_reason': 'stuck', 'reached_goal_state_at_step': 3}), 'reached_no_finish')
        self.assertEqual(failure_mode({**base, 'stop_reason': 'model_infeasible'}), 'false_infeasible')
        self.assertEqual(failure_mode({**base, 'infeasible': True, 'stop_reason': 'model_finished'}), 'missed_infeasible')


class Providers(unittest.TestCase):
    def test_wire_formats(self):
        import os
        os.environ.update({'TYPESAFE_API_KEY': 'k', 'GEMINI_API_KEY': 'k', 'CLOUDFLARE_API_TOKEN': 'k', 'CLOUDFLARE_ACCOUNT_ID': 'abc123'})
        q = {'a': {'type': 'noul', 'instructions': 'x'}}
        url, h, b = request_spec('jev-1.14', {'s': 1}, q, b'png')
        self.assertEqual(b['model'], 'jev-1.14.0')
        self.assertEqual(h['TypeSafe-Danger-Zone-Images'], 'true')
        url, h, b = request_spec('gemini-decision-1', {'s': 1}, q, b'png')
        self.assertEqual(b['input'][1]['type'], 'image')
        url, h, b = request_spec('clef-omni', {'s': 1}, q)
        self.assertIn('@cf/cloudflare/clef-omni', url)

    def test_usage_shapes(self):
        self.assertEqual(usage_tokens({'input_tokens': 5, 'output_tokens': 2}), (5, 2))
        self.assertEqual(usage_tokens({'total_input_tokens': 7, 'total_output_tokens': 0}), (7, 0))
        self.assertEqual(usage_tokens(None), (0, 0))


class Stats(unittest.TestCase):
    def test_wilson(self):
        lo, hi = wilson(14, 15)
        self.assertTrue(0.6 < lo < 0.75 and 0.95 < hi <= 1)
        self.assertEqual(wilson(0, 0), (0.0, 0.0))


if __name__ == '__main__':
    unittest.main()
