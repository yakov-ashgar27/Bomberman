"""High score table (FR-13)."""
from bomberman.highscores import HighScoreTable, clean_name


def test_empty_table_when_file_missing(tmp_path):
    table = HighScoreTable(tmp_path / "none.json")
    assert table.entries == []
    assert table.qualifies(1)
    assert not table.qualifies(0)


def test_scores_sorted_and_trimmed(tmp_path):
    table = HighScoreTable(tmp_path / "hs.json", max_entries=3)
    for name, score in [("a", 100), ("b", 300), ("c", 200), ("d", 50)]:
        table.add(name, score)
    assert [e.score for e in table.entries] == [300, 200, 100]
    assert not table.qualifies(100)
    assert table.add("e", 250) == 2
    assert [e.name for e in table.entries] == ["b", "e", "c"]


def test_ties_keep_older_entry_first(tmp_path):
    table = HighScoreTable(tmp_path / "hs.json")
    table.add("first", 100)
    assert table.add("second", 100) == 2


def test_scores_persist_between_runs(tmp_path):
    path = tmp_path / "hs.json"
    HighScoreTable(path).add("yuki", 1234)
    reloaded = HighScoreTable(path)
    assert [(e.name, e.score) for e in reloaded.entries] == [("yuki", 1234)]


def test_corrupted_file_does_not_crash(tmp_path):
    path = tmp_path / "hs.json"
    path.write_text("{not json", encoding="utf-8")
    assert HighScoreTable(path).entries == []


def test_name_cleaning():
    assert clean_name("   ") == "PLAYER"
    assert clean_name("a" * 30) == "a" * 10
    assert clean_name(" Dana\n") == "Dana"
