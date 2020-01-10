import unittest
from hermes.session import Session


class TestSession(unittest.TestCase):

    SESSION_LOCALE = None  # type: Session

    @classmethod
    def setUpClass(cls):

        TestSession.SESSION_LOCALE = Session()

        Session.UNIVERSELLE.sauver('licorne', 'mdp_ultra_secret')
        Session.UNIVERSELLE.sauver('montagne', 'utilisateur_ldap')

        Session.UNIVERSELLE.sauver('mm', 'licorne')

        Session.UNIVERSELLE.sauver('mmm', 'hello.0')

        Session.UNIVERSELLE.sauver('http_requete_0', {'status': 200, 'json_data': {}, 'hello': [0, 1, 2, 'b']})

        TestSession.SESSION_LOCALE.sauver('hello_world', 'you are most welcome')

        Session.UNIVERSELLE.sauver('identifiant_itop', 'ITOP-C-000941')

        Session.UNIVERSELLE.sauver('test_boolean', True)
        Session.UNIVERSELLE.sauver('test_boolean_2', False)

        Session.UNIVERSELLE.sauver('anniversaire', '1994-02-06')

        TestSession.SESSION_LOCALE.sauver(
            'ma_liste',
            [
                {
                    'a': 'n',
                    'b': 'p'
                },
                {
                    'a': 'yu',
                    'b': 'po'
                },
            ]
        )

        TestSession.SESSION_LOCALE.sauver(
            'requete_itop_0',
            {
                'objects': {
                    'NormalChange::1515': {
                        'fields':
                            {
                                'caller_mail': 'toto@zero.fr'
                            }
                    }
                }
            }
        )

        TestSession.SESSION_LOCALE.sauver('Class', 'NormalChange')
        TestSession.SESSION_LOCALE.sauver('RefITOP', '1515')

    def test_remplacement_obj_vers_str(self):

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire('{{ ma_liste }}'),
            '[{"a": "n", "b": "p"}, {"a": "yu", "b": "po"}]'
        )

    def test_boolean(self):

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire('{{ test_boolean }}'),
            'True'
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire('{{ test_boolean_2 }}'),
            'False'
        )

    def test_remplacement_nested(self):

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire("{{ mm }}"),
            "licorne"
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire("{{ {{ mm }} }}"),
            'mdp_ultra_secret'
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire("{{ http_requete_0.{{ mmm }} }}"),
            '0'
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire(
                '{{ requete_itop_0.objects.{{ Class }}::{{ RefITOP }}.fields.caller_mail }}'),
            'toto@zero.fr'
        )

    def test_remplacement_simple(self):

        self.assertEqual(
            "J'aime les mdp_ultra_secret ! Et aussi les utilisateur_ldap !!",
            TestSession.SESSION_LOCALE.retranscrire(
                "J'aime les {{ licorne }} ! Et aussi les {{montagne}} !!"
            )
        )

    def test_remplacement_sous_niveau(self):

        self.assertEqual(
            "Je souhaite arriver au status 200 sachant la lettre b",
            TestSession.SESSION_LOCALE.retranscrire("Je souhaite arriver au status {{ http_requete_0.status }} sachant la lettre {{ http_requete_0.hello.3 }}")
        )

        self.assertEqual(
            "Je souhaite arriver au status 200",
            TestSession.SESSION_LOCALE.retranscrire("Je souhaite arriver au status {{ http_requete_0.status }}")
        )

    def test_remplacement_dict(self):

        self.assertEqual(
            {
                'auth_user': 'mdp_ultra_secret',
                'auth_pass': 'utilisateur_ldap',
                'json_data': '0'
            },
            TestSession.SESSION_LOCALE.retranscrire(
                {
                    'auth_user': '{{licorne}}',
                    'auth_pass': '{{montagne}}',
                    'json_data': '{{http_requete_0.hello.0}}'
                }
            )
        )

    def test_filtre(self):

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire(
                '{{identifiant_itop|int}}'
            ),
            '941'
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire(
                '{{identifiant_itop|int|remplissageSixZero}}'
            ),
            '000941'
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire(
                '{{anniversaire|dateAjouterUnJour}}'
            ),
            '1994-02-07'
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire(
                '{{anniversaire|dateRetirerUnJour}}'
            ),
            '1994-02-05'
        )

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire(
                '{{anniversaire|dateAjouterUnJour|dateFormatFrance}}'
            ),
            '07/02/1994'
        )

    def test_key_error(self):

        with self.assertRaises(KeyError):
            TestSession.SESSION_LOCALE.retranscrire('{{ cle_inexistante }}')

        with self.assertRaises(KeyError):
            Session.UNIVERSELLE.retranscrire('{{ cle_n_existe_toujours_pas }}')

    def test_key_dict_int(self):

        self.assertEqual(
            TestSession.SESSION_LOCALE.retranscrire('{{ http_requete_0.0 }}'),
            TestSession.SESSION_LOCALE.retranscrire('{{ http_requete_0.status }}')
        )


if __name__ == '__main__':
    unittest.main()
