import sys
import pathlib as _pathlib
sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parents[1]))

from make_app import landing_config


def test_landing_config_present():
    # Ensure example landing_config is present and has options
    assert isinstance(landing_config, dict)
    opts = landing_config.get('options', [])
    assert isinstance(opts, list)

# More detailed endpoint tests should use a test client or run the app and issue GET requests to /landing/cards
