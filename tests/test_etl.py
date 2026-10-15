import pytest
from banxico_etl.extract import BanxicoExtractor
from banxico_etl.transform import MacroTransformer
from banxico_etl.load import MacroStorage
from banxico_etl.analytics import MacroAnalytics

def test_extract_sample_data():
    extractor = BanxicoExtractor()
    dataset = extractor.get_sample_historical_dataset()
    
    assert "SF43718" in dataset
    assert "SF43783" in dataset
    assert "SP68257" in dataset
    assert "SP1" in dataset
    assert len(dataset["SF43718"]) > 300

def test_transform_and_align():
    extractor = BanxicoExtractor()
    dataset = extractor.get_sample_historical_dataset()
    indicators = MacroTransformer.align_and_harmonize_series(dataset)
    
    assert len(indicators) > 300
    first = indicators[0]
    assert first.usd_mxn_fix is not None
    assert first.tiie_28d is not None
    assert first.tasa_real is not None

def test_load_and_analytics(tmp_path):
    storage = MacroStorage(base_dir=str(tmp_path / "lake"))
    extractor = BanxicoExtractor()
    dataset = extractor.get_sample_historical_dataset()
    indicators = MacroTransformer.align_and_harmonize_series(dataset)
    
    count = storage.save_indicators(indicators)
    assert count == len(indicators)

    analytics = MacroAnalytics(storage.con)
    latest = analytics.get_latest_indicators()
    assert latest["usd_mxn_fix"] is not None
    assert latest["tiie_28d"] is not None
    assert latest["tasa_real"] is not None

    stats = analytics.get_summary_statistics()
    assert stats["num_observaciones"] == count
    assert stats["usd_min"] < stats["usd_max"]

    storage.close()
