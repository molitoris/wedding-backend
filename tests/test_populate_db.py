import sys

sys.path.append('/workspaces/wedding-api/app')
sys.path.append('/workspaces/wedding-api/tests')

from src.config.app_config import load_config

from tests.temporal_setup import setup_db, load_inivation_data


def test_populate_db(setup_db):
    config = load_config()
    invitations = load_inivation_data(config.setup.get_invitation_file_path())
    
    assert len(invitations) == 3

    assert len(list(config.setup.get_qr_code_output_path().glob('*.png'))) == 3

    for keys, invitation in invitations.items():
        assert 'guests' in invitation.keys()

        for guest in invitation['guests']:
            assert 'first_name' in guest.keys()
            assert 'last_name' in guest.keys()
            assert 'role' in guest.keys()
