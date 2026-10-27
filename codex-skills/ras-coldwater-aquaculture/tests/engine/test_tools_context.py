"""Unit tests for the tool registry and prompt builder."""
import unittest

from ras_aqua.tools import ToolRegistry, ToolContext
from ras_aqua.context import PromptBuilder, TokenBudget, count_tokens
from ras_aqua.errors import ToolError


class TestToolRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = ToolRegistry()
        cls.ctx = ToolContext()

    def test_default_tools_present(self):
        for name in ("compute_nh3", "compute_do_saturation", "compute_tan_production",
                     "compute_biofilter_capacity", "match_disease_signals",
                     "query_knowledge_base"):
            self.assertIn(name, self.reg.list())

    def test_compute_nh3(self):
        r = self.reg.invoke("compute_nh3",
                            {"TAN_mgL": 1.0, "T_C": 15, "pH": 7.5}, self.ctx)
        self.assertGreater(r["nh3_mgL"], 0.0)
        self.assertEqual(r["units"], "mg/L NH3-N")

    def test_missing_arg_raises(self):
        with self.assertRaises(ToolError):
            self.reg.invoke("compute_nh3", {"T_C": 15, "pH": 7.5}, self.ctx)

    def test_unknown_tool_raises(self):
        with self.assertRaises(ToolError):
            self.reg.invoke("nope", {}, self.ctx)

    def test_match_diseases(self):
        r = self.reg.invoke("match_disease_signals",
                            {"conditions": ["high_NH3", "crowding", "low_DO"]}, self.ctx)
        self.assertIsInstance(r["signals"], list)

    def test_query_knowledge_empty(self):
        r = self.reg.invoke("query_knowledge_base", {"keywords": ["ammonia"]}, self.ctx)
        self.assertEqual(r["coverage"], "low")

    def test_schemas_export(self):
        schemas = self.reg.schemas()
        self.assertEqual(len(schemas), len(self.reg.list()))
        self.assertIn("input_schema", schemas[0])


class TestPromptBuilder(unittest.TestCase):
    def test_render_substitution(self):
        pb = PromptBuilder()
        out = pb.render("gather_requirements",
                        {"user_message": "hello", "attached_log": ""})
        self.assertIn("hello", out)

    def test_missing_template_raises(self):
        pb = PromptBuilder()
        with self.assertRaises(FileNotFoundError):
            pb.load("does_not_exist")

    def test_base_template_loads(self):
        pb = PromptBuilder()
        self.assertIn("SYSTEM", pb.load("base"))


class TestTokenBudget(unittest.TestCase):
    def test_consume_and_available(self):
        b = TokenBudget(max_context_tokens=1000, reserved_output_tokens=100)
        self.assertEqual(b.available, 900)
        b.consume(200)
        self.assertEqual(b.available, 700)

    def test_exhaustion_raises(self):
        from ras_aqua.errors import ContextBudgetError
        b = TokenBudget(max_context_tokens=100, reserved_output_tokens=10)
        with self.assertRaises(ContextBudgetError):
            b.consume(200)

    def test_count_tokens_positive(self):
        self.assertGreater(count_tokens("hello world"), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
