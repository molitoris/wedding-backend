from src.config.app_config import load_config

from tests.temporal_setup import setup_db, load_invitation_data, get_guest_list


def test_populate_db(setup_db):
    config = load_config()
    invitations = load_invitation_data(config.setup.get_invitation_file_path())

    act_guest_list = get_guest_list()

    assert len(invitations) == len(act_guest_list['group'].unique())

    qr_code_files = list(config.setup.get_qr_code_output_path().glob('*.png'))
    assert len(qr_code_files) == len(act_guest_list['group'].unique())

    for _, invitation in invitations.items():
        assert 'guests' in invitation.keys()

        for guest in invitation['guests']:
            assert 'first_name' in guest.keys()
            assert 'last_name' in guest.keys()
            assert 'role' in guest.keys()
