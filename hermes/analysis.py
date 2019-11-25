import re

from requests_html import HTML
from slugify import slugify
from unidecode import unidecode

import pandas as pd


class ExtractionInteret(object):

    REGEX_HTML_TAGS = re.compile(
        r'<(br|basefont|hr|input|source|frame|param|area|meta|!--|col|link|option|base|img|wbr|!DOCTYPE|html|head).*?>|<(a|abbr|acronym|address|applet|article|aside|audio|b|bdi|bdo|big|blockquote|body|button|canvas|caption|center|cite|code|colgroup|command|datalist|dd|del|details|dfn|dialog|dir|div|dl|dt|em|embed|fieldset|figcaption|figure|font|footer|form|frameset|head|header|hgroup|h1|h2|h3|h4|h5|h6|html|i|iframe|ins|kbd|keygen|label|legend|li|map|mark|menu|meter|nav|noframes|noscript|object|ol|optgroup|output|p|pre|progress|q|rp|rt|ruby|s|samp|script|section|select|small|span|strike|strong|style|sub|summary|sup|table|tbody|td|textarea|tfoot|th|thead|time|title|tr|track|tt|u|ul|var|video).*?</\2>'
    )

    def __init__(self, titre, source):
        """
        :param string source:
        """
        self._titre = titre.replace('\r', '').replace('\n', '')
        self._source = source.lstrip().strip('\r')
        self._interets = {'informations': list(), 'titre': self._titre, 'hyperliens': list(), 'identifiants': list()}
        self._recyles = list()

        self._may_html = re.search(ExtractionInteret.REGEX_HTML_TAGS, self._source) is not None
        self._dom = HTML(html=source.replace('<br>', '<br>\n').replace('<br/>', '<br/>\n')) if self._may_html else None

        nb_interet_pre = len(self._interets.keys())

        if self._may_html:

            for table in self._dom.find('table'):

                if table.attrs.get('class') is not None and 'MsoNormalTable' in table.attrs.get('class'):
                    continue

                df = pd.read_html(table.raw_html)

                for el in df[0].to_dict(orient='records'):
                    keys = el.keys()

                    if 0 in keys and 1 in keys:
                        possible_key = str(el[0]).lstrip().rstrip()
                        possible_value = str(el[1]).lstrip().rstrip()

                        self[possible_key] = possible_value
                        self._recyles.append(possible_value)

                    elif 1 not in keys:
                        possible_line = str(el[0])
                        self._recyles.append(possible_line)

            self._interets['hyperliens'] = list(self._dom.links)

            if self._may_html is True and len(self._interets.keys()) == nb_interet_pre:
                self._source = self._dom.full_text.replace('\r', '\n')
                self._may_html = False

        self._sentences = ExtractionInteret.extract_sentences(self._source.replace('\n', '\n '))

        if self._may_html is False:
            for line in self._source.split('\n') + [self._titre]:

                self._recyles.append(line)

                mes_associations = re.findall(r'(([^\w])|^)([a-zA-Z $\u00C0-\u017F\'_]{3,})(:|→|⟶|-->|->)(.+?(?=[\n\"><\]\[]))', line+'\n')
                mes_hyperliens = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)

                self._interets['hyperliens'] += [el.strip('<>') for el in mes_hyperliens if el.strip('<>') not in self._interets['hyperliens']]

                for association in mes_associations:  # type: tuple[str, str, str, str, str]

                    a, b, c, e, d = association

                    partie_possible_cle, partie_possible_valeur = c.rstrip().lstrip(), d.rstrip().lstrip()

                    if not partie_possible_valeur.startswith('//') and (self[partie_possible_cle] is None or self[partie_possible_cle] != partie_possible_valeur):
                        self[partie_possible_cle] = partie_possible_valeur

        self._interets['informations'] = self.retrive_informations_balisees()
        self._interets['identifiants'] = self.retrieve_identifer(None, multiple=True)

    @property
    def recycles(self):
        return self._recyles

    def __contains__(self, item):
        return slugify(item) in self._interets.keys()

    def __getitem__(self, key):
        key = slugify(key)
        return self._interets[key] if key in self._interets.keys() else None

    def __setitem__(self, key, value):
        key = slugify(key)

        if self[key] is not None:
            self[key+'-0'] = value
            return

        self._interets[key] = value

    def injecter_interet(self, cle, donnee):
        """
        :param str cle:
        :param str donnee:
        :return:
        """
        cle = slugify(cle)
        if cle in self._interets.keys():
            raise KeyError
        self._interets[cle] = donnee

    @property
    def interets(self):
        return self._interets

    @property
    def source(self):
        return self._source

    @property
    def sentences(self):
        return self._sentences

    def retrieve_xpath(self, expression_xpath):
        """
        Découverte d'un chemin xpath
        :param str expression_xpath:
        :return:
        """
        if self._may_html is None:
            return None

        r = self._dom.xpath(expression_xpath, first=True)

        return r.full_text if r is not None else None

    def retrive_informations_balisees(self, focus=None):

        def extract(my_string):
            mes_informations = [el[1:-1] for el in re.findall(r'\[[a-zA-Z0-9:\-# _\'\u00C0-\u017F]{1,36}\]', my_string)] + \
                               [''.join(el)[1:] for el in re.findall(r'(([^\w#])|^)#(\w*[0-9a-zA-Z]+\w*[0-9a-zA-Z])', my_string)]
            return mes_informations

        informations = list()

        if focus is None:
            cts_listes = self._recyles + self._sentences + [self._interets[el] for el in self._interets.keys() if isinstance(self._interets[el], str)]
        elif focus == 'corpus':
            cts_listes = self._recyles + self._sentences
        else:
            cts_listes = [self._interets[focus] if isinstance(self._interets[focus], str) else str(self._interets[focus])]

        for my_str in cts_listes:
            informations += extract(my_str)

        return list(set(informations))

    def retrieve_expression_reguliere(self, expression_reguliere, focus=None):

        expression_reguliere = re.compile(expression_reguliere)

        if focus is None:
            cts_listes = self._recyles + self._sentences + [self._interets[el] for el in self._interets.keys() if isinstance(self._interets[el], str)]
        elif focus == 'corpus':
            cts_listes = self._recyles + self._sentences
        else:
            cts_listes = [self._interets[focus] if isinstance(self._interets[focus], str) else str(self._interets[focus])]

        for my_str in cts_listes:

            my_extract = re.findall(expression_reguliere, my_str)

            if len(my_extract) > 0:
                return str(my_extract[0]) if isinstance(my_extract, list) else ''.join(my_extract)

        return None

    def retrieve_date(self, prefix, focus=None, multiple=False):
        """
        :param str prefix:
        :param bool multiple:
        :return:
        """

        def extract(my_string):
            """
            :param str my_string:
            :return:
            :rtype: str
            """

            date_fr_regex = re.compile(
                r'{}'.format(re.escape(prefix+' '))+r'([0-2 ][0-9]|(3)[0-1])([\/-])(((0)[0-9])|((1)[0-2]))([\/-])\d{2,4}'
            )

            date_us_regex = re.compile(
                r'{}'.format(re.escape(prefix+' '))+r'\d{4}([\/-])(((0)[0-9])|((1)[0-2]))([\/-])([0-2][0-9]|(3)[0-1])'
            )

            date_rfc_3339 = re.compile(
                r'{}'.format(re.escape(prefix+' '))+r'((?:(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[+-]\d{2}:\d{2})?)'
            )

            date_rfc_2822 = re.compile(
                r'{}'.format(re.escape(prefix+' '))+r'(?:(Sun|Mon|Tue|Wed|Thu|Fri|Sat),\s+)?(0[1-9]|[1-2]?[0-9]|3[01])\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(19[0-9]{2}|[2-9][0-9]{3})\s+(2[0-3]|[0-1][0-9]):([0-5][0-9])(?::(60|[0-5][0-9]))?\s+([-\+][0-9]{2}[0-5][0-9]|(?:UT|GMT|(?:E|C|M|P)(?:ST|DT)|[A-IK-Z]))(\s+|\(([^\(\)]+|\\\(|\\\))*\))*'
            )

            date_fr_reduite_regex = re.compile(
                r'{}'.format(re.escape(prefix+' '))+r'(((0)[0-9])|((1)[0-2]))([\/-])\d{4}'
            )

            date_us_reduite_regex = re.compile(
                r'{}'.format(re.escape(prefix+' '))+r'\d{4}([\/-])(((0)[0-9])|((1)[0-2]))'
            )

            dates_expressions_regulieres = [
                date_rfc_3339,
                date_rfc_2822,
                date_fr_regex,
                date_us_regex,
                date_fr_reduite_regex,
                date_us_reduite_regex
            ]

            for el in dates_expressions_regulieres:
                mt = re.search(el, my_string)

                if mt is not None:
                    return mt.group().replace(prefix, '')

            return None

        dates = list()

        if focus is None:
            cts_listes = self._interets['informations'] + self._recyles + self._sentences + [self._interets[el] for el in self._interets.keys() if isinstance(self._interets[el], str)]
        elif focus == 'corpus':
            cts_listes = self._recyles + self._sentences
        else:
            cts_listes = [self._interets[focus] if isinstance(self._interets[focus], str) else str(self._interets[focus])]

        for my_str in cts_listes:
            ma_date = extract(my_str)
            if ma_date:
                if multiple is False:
                    return ma_date
                dates.append(ma_date)

        return None if multiple is False else dates

    def retrieve_inner_expression(self, expr_left, expr_right, focus=None, multiple=False):
        """
        :param str focus:
        :param str expr_left:
        :param str expr_right:
        :param bool multiple:
        :return:
        """
        expr_left = unidecode(expr_left).lower() if expr_left is not None else ''
        expr_right = unidecode(expr_right).lower() if expr_right is not None else ''

        def extract(ma_chaine):
            """
            :param str ma_chaine:
            :return:
            """
            ma_chaine_unidecoded = unidecode(ma_chaine).lower()

            if expr_left is not None and len(expr_left) > 0 and expr_left in ma_chaine_unidecoded:

                if expr_right is None or len(expr_right) == 0:
                    return ma_chaine[ma_chaine_unidecoded.index(expr_left) + len(expr_left):].lstrip().rstrip()

                if expr_right in ma_chaine_unidecoded[ma_chaine_unidecoded.index(expr_left) + len(expr_left) - 1:]:
                    return ma_chaine[ma_chaine_unidecoded.index(expr_left) + len(expr_left):ma_chaine_unidecoded.index(expr_right)].lstrip().rstrip()

            elif (expr_left is None or len(expr_left) == 0) and expr_right is not None and expr_right in ma_chaine_unidecoded:
                return ma_chaine[:ma_chaine_unidecoded.index(expr_right)-1].lstrip().rstrip()

            return None

        expressions = list()

        if focus is None:
            cts_listes = self._interets['informations'] + self._recyles + self._sentences + [self._interets[el] for el in self._interets.keys() if isinstance(self._interets[el], str)]
        elif focus == 'corpus':
            cts_listes = self._recyles + self._sentences
        else:
            cts_listes = [self._interets[focus] if isinstance(self._interets[focus], str) else str(self._interets[focus])]

        for my_str in cts_listes:
            k = extract(my_str)
            if k is not None:
                if multiple is False:
                    return k
                expressions.append(k)

        return None if multiple is False else expressions

    def retrieve_identifer(self, prefix, focus=None, exclude_prefix=False, cast_integer=False, multiple=False):
        """
        Récupération d'un identifiant
        :param str prefix:
        :param bool exclude_prefix:
        :param bool cast_integer:
        :param bool multiple:
        :return:
        """

        def extract(ma_chaine):
            matchs = re.search(r'(([^\w-])|^){prefix}([^\W\n]+[\d]+)'.format(prefix=prefix.replace(' ', '\\ ')), ma_chaine)
            if matchs:
                digits = ExtractionInteret.extract_digits(matchs.group())

                if digits is not None:
                    return (int(digits) if cast_integer is True else digits) if exclude_prefix is True else matchs.group().replace(matchs.group(1), '')

            return None

        if prefix is None or len(prefix) == 0:
            prefix = '[A-Za-z-°]+'

        identifiants = list()

        if focus is None:
            cts_listes = self._interets['informations'] + self._recyles + self._sentences + [self._interets[el] for el in self._interets.keys() if isinstance(self._interets[el], str)]
        elif focus == 'corpus':
            cts_listes = self._recyles + self._sentences
        else:
            cts_listes = [self._interets[focus] if isinstance(self._interets[focus], str) else str(self._interets[focus])]

        for my_str in cts_listes:
            identifiant = extract(my_str)
            if identifiant is not None:
                if multiple is False:
                    return identifiant
                if identifiant not in identifiants:
                    identifiants.append(identifiant)

        return None if multiple is False else identifiants

    def has_expression_cle(self, expression_cle, focus=None):
        """
        :param str expression_cle:
        :return:
        """

        expression_cle = unidecode(expression_cle).lower()

        if focus is None:
            cts_listes = self._recyles+self._sentences+self.interets['informations']+[self.interets['titre']]
        elif focus == 'corpus':
            cts_listes = self._recyles + self._sentences
        else:
            cts_listes = [self._interets[focus] if isinstance(self._interets[focus], str) else str(self._interets[focus])]

        for el in cts_listes:
            if not isinstance(el, str):
                continue
            if expression_cle in unidecode(el).lower():
                return True

        return False

    def has_expression_dans_cle(self, ma_cle, mon_expression):
        mon_expression = unidecode(mon_expression).lower()

        if self.has_interet(ma_cle) is True:
            el = self[ma_cle]
            if isinstance(el, str):
                return mon_expression in unidecode(el).lower()
            elif isinstance(el, list):
                for el_l in el:
                    if isinstance(el_l, str):
                        if mon_expression in unidecode(el_l).lower():
                            return True

        return False

    def has_information(self, information_cible, focus=None):
        """
        :param focus:
        :param str information_cible:
        :return:
        """
        information_cible = unidecode(information_cible).lower()

        for el in self.interets['informations'] if focus is None else self.retrive_informations_balisees(focus):
            if information_cible in unidecode(el).lower():
                return True
        return False

    def has_interet(self, interet_cible):
        """
        :param str interet_cible:
        :return:
        """
        return slugify(interet_cible) in self.interets.keys()

    def get_interet(self, interet_cible):
        return self.interets[slugify(interet_cible)] if self.has_interet(interet_cible) else None

    @staticmethod
    def extract_digits(string):
        """

        :param str string:
        :return:
        """
        final_str = ''
        first_digit_mt = False

        for c in string:
            if c.isdigit():
                first_digit_mt = True
                final_str += c
            elif first_digit_mt is True and c.isdigit() is False:
                break

        return final_str if final_str != '' else None

    @staticmethod
    def alnum_percentage(source):
        """

        :param string source:
        :return:
        """
        o_len = len(source)
        f_len = 0

        for el in source:
            if el.isalnum():
                f_len += 1

        return f_len / o_len

    @staticmethod
    def extract_sentences(source):
        """
        :param str source:
        :return:
        """

        source_splitted = source.split(' ')
        sentences = ['']

        for possible_word in source_splitted:
            if len(possible_word) == 0:
                continue
            if re.fullmatch(r'[\w\'’/.,!?;\-\u00C0-\u017F\n]{1,26}', possible_word):
                sentences[-1] += ' ' + possible_word if len(sentences[-1]) > 0 else possible_word
                if possible_word in ['.', '?', '!', '\n'] or sentences[-1][-1] in ['.', '?', '!', '\n']:
                    sentences.append('')
            elif sentences[-1] != '':
                if len(sentences[-1].split(' ')) > 3:
                    sentences.append('')
                else:
                    sentences[-1] = ''

        return sentences
