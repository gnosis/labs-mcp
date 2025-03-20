import pytest

from server.app import answer_binary_question


@pytest.skip("Deactivated to avoid wasting OpenAI credits")
def test_answer_binary_question():
    test_question = "Will Mirra Andreeva win a Grand Slam title on or before March 22, 2025?"
    answer = answer_binary_question(test_question)
    print(answer)
