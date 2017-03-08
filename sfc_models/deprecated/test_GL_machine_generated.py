from unittest import TestCase

import sfc_models.deprecated.GL_machine_generated as GL_machine_generated


class TestFunctions(TestCase):
    def test_get_models(self):
        out = GL_machine_generated.get_models()
        self.assertFalse('[TEST]' in out)
        self.assertTrue('[SIM]' in out)

    def test_build_model(self):
        obj = GL_machine_generated.build_model('TEST')
        self.assertEqual(obj.Endogenous, [('t', '1.0')])

    def test_model_not_there(self):
        with self.assertRaises(ValueError):
            obj = GL_machine_generated.build_model('DSGE_MODELS_SUCK_EGGS')

