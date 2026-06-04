"""Tilannekuva-aggregaattori: kokoaa iteraatioiden metriikat yhdeksi nakymaksi.

Punaisena ensin (summary-moduulia ei viela ole), sitten vihreaksi.
"""
import summary


def _iter(name, size, pf, hy):
    return {
        "iter": name,
        "size": size,
        "runs": {
            "Privacy Filter only": pf,
            "Regex only": {"typed_recall": 0.8, "redaction_recall": 0.8, "n_leaks": 5},
            "Hybrid": hy,
        },
    }


def test_overview_extracts_hybrid_and_pf_metrics():
    its = [_iter("1", 51,
                 pf={"typed_recall": 0.51, "redaction_recall": 0.78, "n_leaks": 11},
                 hy={"typed_recall": 0.96, "redaction_recall": 0.98, "n_leaks": 1})]
    rows = summary.iteration_overview(its)
    assert len(rows) == 1
    r = rows[0]
    assert r["iter"] == "1"
    assert r["size"] == 51
    assert r["pf_redaction"] == 0.78
    assert r["hybrid_redaction"] == 0.98
    assert r["hybrid_typed"] == 0.96
    assert r["hybrid_leaks"] == 1


def test_overview_preserves_iteration_order():
    its = [
        _iter("0", 15, {"typed_recall": 0.5, "redaction_recall": 0.88, "n_leaks": 2},
              {"typed_recall": 0.88, "redaction_recall": 0.94, "n_leaks": 1}),
        _iter("1", 51, {"typed_recall": 0.51, "redaction_recall": 0.78, "n_leaks": 11},
              {"typed_recall": 0.96, "redaction_recall": 0.98, "n_leaks": 1}),
    ]
    rows = summary.iteration_overview(its)
    assert [r["iter"] for r in rows] == ["0", "1"]


def test_build_summary_renders_markdown_with_key_numbers():
    its = [_iter("1", 51,
                 pf={"typed_recall": 0.51, "redaction_recall": 0.78, "n_leaks": 11},
                 hy={"typed_recall": 0.96, "redaction_recall": 0.98, "n_leaks": 1})]
    md = summary.build_summary(its)
    assert isinstance(md, str)
    assert "Hybrid" in md
    assert "51" in md          # aineiston koko nakyy
    assert "98 %" in md        # hybridin maskaus-recall
