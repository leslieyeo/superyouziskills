import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
from szdata.sentiment import grade_rank

def test_grade_rank():
    assert grade_rank(5) == "极热"
    assert grade_rank(50) == "热"
    assert grade_rank(300) == "温"
    assert grade_rank(2000) == "冷"
    assert grade_rank(None) == "未知"

def test_code_match_is_exact_not_substring(monkeypatch, tmp_path):
    import akshare as ak
    import szdata.sentiment as sentiment
    from szdata.cache import Cache
    monkeypatch.setattr(sentiment, "_cache", Cache(root=tmp_path))
    monkeypatch.setattr(
        ak, "stock_hot_rank_em",
        lambda: pd.DataFrame({"代码": ["16005190"], "当前排名": [1]}),
    )
    out = sentiment.fetch_sentiment("600519")
    assert out["ok"] is True
    assert out["data"]["rank"] is None
