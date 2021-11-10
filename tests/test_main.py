from platon_aide.main import PlatonAide

uri = 'http://127.0.0.1:8888'
aide = PlatonAide(uri)


def test_main():
    print(aide.staking.get_verifier_list())
