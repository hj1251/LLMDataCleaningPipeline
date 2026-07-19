from pipeline.validation import validate


def test_valid_description_passes():
    result = validate("BMW X2 18-24 Carpet")
    assert result["is_valid"] is True
    assert result["issues"] == []


def test_too_short_is_flagged():
    result = validate("BMW")
    assert result["is_valid"] is False
    assert "Too short - missing brand or product type" in result["issues"]


def test_too_long_is_flagged():
    result = validate("BMW X2 18-24 Premium Leather Boot Mat Carpet Set")
    assert result["is_valid"] is False
    assert "Too long - contains extra details" in result["issues"]


def test_noise_word_is_flagged():
    result = validate("BMW Carpet for X2")
    assert result["is_valid"] is False
    assert "Contains noise words" in result["issues"]
