import os
from pathlib import Path

import pandas
from pandas.errors import ParserError

from pydispatch import dispatcher
from models.base import ObservableModel
from paths import path_dict_folder

UPDATE_TEXT_SIGNAL = 'update_text'


def cols_mapping(row, column_to_map, col1_to_fill, col2_to_fill, col3_to_fill, mapping_dict):
    key = row[column_to_map]
    if key in mapping_dict:
        values = mapping_dict[key]
        try:
            row[col1_to_fill] = values[0]
            row[col2_to_fill] = values[1]
            row[col3_to_fill] = values[2]
        except IndexError:
            row[col1_to_fill] = values[0]
            row[col2_to_fill] = values[1]
    elif key is None:
        pass
    else:
        row[col1_to_fill] = '-'
        row[col2_to_fill] = '-'
        if col3_to_fill is not None:
            row[col3_to_fill] = '-'
    return row


class DictUpdate(ObservableModel):
    def __init__(self):
        super().__init__()
        self._path_dict_folder = os.path.join(os.getcwd(), 'slowniki')
        self.file_paths_list = []
        self.progress_value = 0
        self.dict_gielda_depozyt = []
        self.dict_rachunki = []
        self.dict_klasa_konta_status_aktyw = []

    def set_path(self, path: str) -> None:
        print(f'set_path(): {path}')
        self._path_dict_folder = path

    def check_files_in_folder(self, file_list):
        folder = Path(self._path_dict_folder)

        if not folder.exists():
            return 'FolderNotExists'

        missing_files = []

        for file_name in file_list:
            file_path = folder / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        return missing_files

    def update_KSFIN_dict(self) -> None:
        self.get_dict_konto_fin()
        self.get_dict_konto_subkonto()
        self.get_dict_spwr_konto_subkonto()
        return

    def update_KSGPW_dict(self):
        self.get_dict_gielda_depozyt()
        self.get_dict_rachunki()
        self.get_dict_klasa_konta_status_aktyw()
        self.get_dict_rachunek_klasa_konta_status_aktyw()
        return

    def get_dict_gielda_depozyt(self) -> dict:
        try:
            path = os.path.join(self._path_dict_folder, 'out_dic_gielda_id_depozyt.unl')
            dict_gielda_depozyt_df = pandas.read_csv(path, sep='|', header=None)
            dict_gielda_depozyt = {}
            for index, row in dict_gielda_depozyt_df.iterrows():
                key = row[0]
                values = (row[1], row[2])
                dict_gielda_depozyt[key] = values
            self.dict_gielda_depozyt = dict_gielda_depozyt
        except FileNotFoundError or ParserError:
            dict_gielda_depozyt = {1: ('WWA', 'KDPW'), 2: ('WWA', 'KDPW'), 3: ('WWA', 'KDPW'), 4: ('WWA', 'KDPW'),
                                   5: ('WWA', 'KDPW'), 6: ('WWA', 'KDPW'), 7: ('WWA', 'KDPW'), 8: ('WWA', 'KDPW'),
                                   9: ('WWA', 'KDPW'), 10: ('WWA', 'KDPW'), 11: ('VSE', 'KBCD'), 12: ('EUN', 'KBCD'),
                                   13: ('HEX', 'KBCD'), 14: ('GXE', 'KBCD'), 15: ('BME', 'KBCD'), 16: ('SSX', 'KBCD'),
                                   17: ('NYS', 'KBCD'), 18: ('LSE', 'KBCD'), 19: ('BIT', 'KBCD'), 20: ('NSD', 'KBCD'),
                                   21: ('SSE', 'KBCD'), 22: ('CME', 'KBCD'), 23: ('NYS', 'KBCD'), 24: ('LSE', 'KBCD'),
                                   25: ('MON', 'KBCD'), 26: ('WWA', 'KDPW'), 27: ('WWA', 'KDPW'), 28: ('WWA', 'KDPW'),
                                   29: ('WWA', 'KDPW'), 30: ('WWA', 'KDPW'), 31: ('WWA', 'KDPW'), 32: ('WWA', 'KDPW'),
                                   33: ('WWA', 'KDPW'), 34: ('WWA', 'KDPW'), 35: ('WWA', 'KDPW'), 36: ('WWA', 'KDPW'),
                                   37: ('OTC', 'KBCD'), 38: ('OTC', 'BASA'), 39: ('WAS', 'BNYM'), 40: ('NSD', 'KBCD'),
                                   41: ('EFR', 'KBCD'), 42: ('EUB', 'KBCD'), 43: ('EUN', 'KBCD'), 44: ('EUP', 'KBCD'),
                                   45: ('BON', 'KBCD')}
        return dict_gielda_depozyt

    def get_dict_rachunki(self) -> dict:
        try:
            df = pandas.read_csv(f'{self._path_dict_folder}\out_dic_rachunek_klasa_konta_status_aktyw.unl', sep='|',
                                 on_bad_lines='warn')
            dict_rachunki = df.iloc[:, 0].tolist()
            print(f'   PW: Załadowano słownik out_dic_klasa_konta_status_aktyw na podstawie pliku. ')
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Załadowano słownik out_dic_klasa_konta_status_aktyw na podstawie pliku. ",
                            head='dict')
        except FileNotFoundError or ParserError:
            dict_rachunki = [855, 320, 91501, 818, 979, 924, 915, 311, 400, 91501, 91501, 338, 13, 91501, 986, 855, 308,
                             818, 986, 91501, 13, 936, 91501, 327, 980, 980, 400, 945, 10, 924, 311, 325, 339, 945, 906,
                             912, 979, 91511, 91506, 91506, 91511, 91511, 91501, 91512, 91506, 91512, 91536, 91536, 936,
                             906, 817, 308, 974, 91506, 91201, 91501, 974]

        self.dict_rachunki = dict_rachunki
        return dict_rachunki

    def get_dict_klasa_konta_status_aktyw(self) -> None:
        try:
            dict_klasa_konta_status_aktyw = self.create_dic('out_dic_klasa_konta_status_aktyw.unl',
                                                            ['konto_src', 'kod_src', 'konto_tgt', 'status_aktyw'],
                                                            len_src_cols=2)
            print(f'   PW: Załadowano słownik out_dic_klasa_konta_status_aktyw na podstawie pliku. ')
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Załadowano słownik out_dic_klasa_konta_status_aktyw na podstawie pliku.",
                            head='dict')
        except FileNotFoundError:
            dict_klasa_konta_status_aktyw = {'1010000': ('1', 'poz'), '110tech': ('1', 'pdst_tech'),
                                             '1100000': ('1', 'pdst'),
                                             '1120000': ('1', 'zob_poz_bezkdpw'), '1200000': ('1', 'blk_sprz'),
                                             '124blca': ('1', 'wykpraw_dwpw'), '124tech': ('1', 'blk_tech'),
                                             '1240000': ('1', 'blk'), '1260000': ('1', 'blk_kom_inne'),
                                             '126tech': ('1', 'blk_kom_inne_tech'), '1270000': ('1', 'blk_cel'),
                                             '1280000': ('1', 'blk_profit'), '127blte': ('1', 'wykpraw_blte'),
                                             '127blca': ('1', 'wykpraw'), '1300000': ('1', 'zab_inne'),
                                             '1330000': ('1', 'zab_wdz'), '1400000': ('1', 'pdst'),
                                             '1600000': ('1e', 'trans_kzw'), '210avai': ('2', 'avai'),
                                             '210tech': ('2', 'tech'),
                                             '210blca': ('2', 'blca'), '210blco': ('2', 'blco'),
                                             '210blrd': ('2', 'blrd'),
                                             '210blte': ('2', 'blte'), '210blwy': ('2', 'blwy'),
                                             '2210000': ('3i', 'avai'),
                                             '2230000': ('3', 'avai'), '2240000': ('3o', 'avai'),
                                             '311tech': ('1e', 'weryf_tech'), '3110000': ('1e', 'weryf'),
                                             '3300000': ('1', 'trns_kzw'), '3310000': ('1e', 'tech'),
                                             '2220000': ('3o', 'tech'),
                                             '1480000': ('1', 'blk_kom_inne')}
        return dict_klasa_konta_status_aktyw

    def get_dict_rachunek_klasa_konta_status_aktyw(self) -> dict:
        try:
            dict_rachunek_klasa_konta_status_aktyw = self.create_dic('out_dic_rachunek_klasa_konta_status_aktyw.unl',
                                                                     ['rachunek_src', 'konto_src', 'kod_src',
                                                                      'rachunek_tgt',
                                                                      'konto_tgt', 'status_aktyw'], len_src_cols=3)
            print(f'   PW: Załadowano słownik out_dic_rachunek_klasa_konta_status_aktyw na podstawie pliku. ')
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Załadowano słownik out_dic_rachunek_klasa_konta_status_aktyw na podstawie pliku",
                            head='dict')
        except FileNotFoundError:
            dict_rachunek_klasa_konta_status_aktyw = {'8172210000': ('13', '3i', 'avai0817'),
                                                      '8552210000': ('13', '3i', 'avai0855'),
                                                      '320210avai': ('13', '2e', 'avaibld_trns'),
                                                      '915013110000': ('13', '1e', 'weryf'),
                                                      '8182210000': ('13', '3i', 'avai0818'),
                                                      '9792210000': ('13', '3i', 'avai0979'),
                                                      '9242210000': ('13', '3i', 'avai0924'),
                                                      '9152210000': ('13', '3i', 'avai0915'),
                                                      '311210tech': ('13', '2e', 'techweryf'),
                                                      '4002210000': ('13', '3i', 'avai0400'),
                                                      '915013310000': ('13', '1e', 'tech'),
                                                      '915013300000': ('13', '1', 'trns_kzw'),
                                                      '3382240000': ('13', '3o', 'avai0338'),
                                                      '132240000': ('13', '3o', 'avai0013'),
                                                      '915011600000': ('13', '1e', 'trans_kzw'),
                                                      '9862210000': ('13', '3i', 'avai0986'),
                                                      '8552240000': ('13', '3o', 'avai0855'),
                                                      '3082210000': ('13', '3i', 'avai0308'),
                                                      '8182240000': ('13', '3o', 'avai0818'),
                                                      '9862240000': ('13', '3o', 'avai0986'),
                                                      '91501311tech': ('13', '1e', 'weryf_tech'),
                                                      '132210000': ('13', '3i', 'avai0013'),
                                                      '9362210000': ('13', '3i', 'avai0936'),
                                                      '915013200000': ('13', '1e', 'bld_trns'),
                                                      '3272240000': ('13', '3o', 'avai0327'),
                                                      '9802210000': ('13', '3i', 'avai0980'),
                                                      '9802240000': ('13', '3o', 'avai0980'),
                                                      '4002240000': ('13', '3o', 'avai0400'),
                                                      '9452240000': ('13', '3o', 'avai0945'),
                                                      '102230000': ('13', '3', 'avai0010'),
                                                      '9242240000': ('13', '3o', 'avai0924'),
                                                      '311210avai': ('13', '2e', 'avaiweryf'),
                                                      '3252240000': ('13', '3o', 'avai0325'),
                                                      '3392240000': ('13', '3o', 'avai0339'),
                                                      '9452210000': ('13', '3i', 'avai0945'),
                                                      '9062210000': ('13', '3i', 'avai0906'),
                                                      '9122240000': ('13', '3o', 'avai0912'),
                                                      '9792240000': ('13', '3o', 'avai0979'),
                                                      '915111110000': ('13', '1', '000091511'),
                                                      '915061400000': ('13', '1', '000091506'),
                                                      '91506210avai': ('13', '2', 'avai91506'),
                                                      '915111280000': ('13', '1', '000091511'),
                                                      '91511210avai': ('13', '2', 'avai91511'),
                                                      '91501210avai': ('13', '2', 'avai'),
                                                      '91512210avai': ('13', '2', 'avai91512'),
                                                      '915061260000': ('13', '1', '000091506'),
                                                      '915121110000': ('13', '1', '000091512'),
                                                      '915361110000': ('13', '1', '000091536'),
                                                      '91536210avai': ('13', '2', 'avai91536'),
                                                      '9362240000': ('13', '3o', 'avai0936'),
                                                      '9062240000': ('13', '3o', 'avai0906'),
                                                      '8172240000': ('13', '3o', 'avai0817'),
                                                      '3082240000': ('13', '3o', 'avai0308'),
                                                      '9742240000': ('13', '3o', 'avai0974'),
                                                      '91506210blca': ('13', '2', 'blca91506'),
                                                      '912012240000': ('13', '3o', 'avai0912'),
                                                      '915012220000': ('13', '3o', 'avai0915'),
                                                      '9742210000': ('13', '3i', 'avai0974')}
        return dict_rachunek_klasa_konta_status_aktyw

    def get_dict_konto_fin(self):
        try:
            path = os.path.join(self._path_dict_folder, "out_dic_spwr_konto_subkonto.unl")
            dataframe = pandas.read_csv(path, sep='|')
            dict_konto_fin = list(set(dataframe.iloc[:, 0].tolist()))
        except Exception as e:
            dict_konto_fin = [128, 170, 139, 142]
        return dict_konto_fin

    def get_dict_konto_subkonto(self):
        try:
            dict_konto_subkonto = self.create_dic_fin('out_dic_konto_subkonto.unl',
                                                      ['konto_src', 'subkonto_src', 'subkonto_pdst_src', 'konto_tgt',
                                                       'subkonto_tgt'], len_src_cols=3)
            print(f'  FIN: Załadowano słownik out_dic_konto_subkonto na podstawie pliku. ')
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Załadowano słownik out_dic_konto_subkonto na podstawie pliku. ", head='dict')
        except FileNotFoundError:
            dict_konto_subkonto = {'10911': ('10901', '100001621'), '1097871': ('10901', '100001520'),
                                   '1097891': ('10901', '100001520'), '1097971': ('10901', '100001520'),
                                   '1097981': ('10901', '100001520'), '1099781': ('10901', '100001520'),
                                   '1097873': ('10901', '100006000'), '1099783': ('10901', '100006000'),
                                   '1097893': ('10901', '100006000'), '12733': ('12703', '3'),
                                   '13816211070': ('13802', '200001621'), '13878770': ('13802', '200001621'),
                                   '13878970': ('13802', '200001621'), '13879770': ('13802', '200001621'),
                                   '13879870': ('13802', '200001621'), '13897870': ('13802', '200001621'),
                                   '1381118': ('13802', '300001521'), '1387878': ('13802', '300001521'),
                                   '138174': ('13803', '100001521'), '138274': ('13803', '200001521'),
                                   '138374': ('13803', '300001521'), '138474': ('13803', '400001521'),
                                   '138574': ('13803', '500001521'), '138674': ('13803', '600001621'),
                                   '138774': ('13803', '700001521'), '138874': ('13803', '800001521'),
                                   '1381174': ('13803', '900001521'), '1381374': ('13803', '1000001621'),
                                   '1381274': ('13803', '1100001521'), '1381474': ('13803', '1200001521'),
                                   '1381674': ('13803', '1300001521'), '1381774': ('13803', '1400001521'),
                                   '1381974': ('13803', '1500001521'), '162303': ('16201', '100001520'),
                                   '162313': ('16201', '100001520'), '162323': ('16201', '100001520'),
                                   '162333': ('16201', '100001520'), '162343': ('16201', '100001520'),
                                   '162353': ('16201', '100001520'), '162404': ('16202', '4000006000'),
                                   '162414': ('16202', '4100006000'), '162444': ('16202', '4200006000'),
                                   '162434': ('16202', '4300006000'), '17055': ('17000', '1'), '17077': ('17000', '2'),
                                   '12833': ('17000', '3'), '14266': ('17000', '4'), '1392323': ('17000', '80100'),
                                   '1392424': ('17000', '900'), '1392525': ('17000', '11'), '1392626': ('17000', '12'),
                                   '1392727': ('17000', '13'), '1392222': ('17000', '14'),
                                   '1731021104': ('17301', '1021'),
                                   '1731351104': ('17301', '1351'), '1731520104': ('17301', '1520'),
                                   '1731521104': ('17301', '1521'), '1731891104': ('17301', '1891'),
                                   '1731941104': ('17301', '1941'), '1732120104': ('17301', '2120'),
                                   '1732121104': ('17301', '2121'), '1732421104': ('17301', '2421'),
                                   '1732520104': ('17301', '2520'), '1732521104': ('17301', '2521'),
                                   '1732721104': ('17301', '2721'), '1733121104': ('17301', '3121'),
                                   '1736000104': ('17301', '6000'), '1736340104': ('17301', '6340'),
                                   '229': ('22900', '1621'),
                                   '2291': ('22900', '100001621'), '22911': ('22901', '1000001621'),
                                   '229111': ('22901', '1100001621'), '2292121': ('22902', '2100001621'),
                                   '2292222': ('22902', '2200001621'), '2292323': ('22902', '2300001621'),
                                   '22933': ('22903', '3000001621'), '229313': ('22903', '3100001621'),
                                   '22966': ('22905', '5000001621'), '229616': ('22905', '5100001621'),
                                   '22999': ('22906', '6000001621'), '22977': ('22907', '7000001621'),
                                   '245': ('24500', '1621'), '24522': ('24513', '1300001621'),
                                   '2457871': ('24501', '100001621'), '2457891': ('24501', '100001621'),
                                   '2457971': ('24501', '100001621'), '2459781': ('24501', '100001621'),
                                   '2451': ('24509', '900001621'), '2452': ('24510', '1000001621'),
                                   '2453': ('24511', '1100001621'), '2454': ('24512', '1200001621'),
                                   '2491212': ('24901', '2521'), '249697227': ('24902', '1621'),
                                   '2492929': ('24903', '1621'), '24929129': ('24904', '1621'),
                                   '2493131': ('24905', '1621'), '2493232': ('24906', '1621'),
                                   '2493939': ('24907', '1621'), '24940140': ('24909', '1621'),
                                   '2499191': ('24910', '1621'), '2499393': ('24911', '1621'),
                                   '24926126': ('24920', '2000001621'),
                                   '249261026': ('24920', '2010001621'), '2492630126': ('24920', '2020101621'),
                                   '2492630226': ('24920', '2030001621'), '24926526': ('24920', '2040001621'),
                                   '249261926': ('24921', '2100001621'), '24926326': ('24930', '3000001961'),
                                   '249263126': ('24930', '3010001961'), '2492121': ('24930', '3020001961'),
                                   '24920020': ('24931', '3100001961'), '24920120': ('24931', '3110001961'),
                                   '249340340': ('24931', '3120001961'), '2493400340': ('24931', '3130001961'),
                                   '2493401340': ('24931', '3140001961'), '2493403343': ('24931', '3150001961'),
                                   '249787341': ('24934', '3400006000'), '249978341': ('24934', '3400006000'),
                                   '249613342': ('24935', '3500006000'), '249633342': ('24935', '3500006000'),
                                   '249781342': ('24935', '3500006000'), '249788342': ('24935', '3500006000'),
                                   '249784342': ('24935', '3500006000'), '249787342': ('24935', '3500006000'),
                                   '249789342': ('24935', '3500006000'), '249797342': ('24935', '3500006000'),
                                   '249978342': ('24935', '3500006000'), '2495353': ('24950', '10'),
                                   '2495454': ('24950', '20'), '2495555': ('24950', '30'), '2495656': ('24950', '40'),
                                   '259787': ('25900', '7870001621'), '259789': ('25900', '7890001621'),
                                   '259797': ('25900', '7970001621'), '259798': ('25900', '7980001621'),
                                   '259978': ('25900', '9780001621'), '2597871': ('25901', '1621'),
                                   '2597891': ('25901', '1621'), '2597971': ('25901', '1621'),
                                   '2597981': ('25901', '1621'), '2599781': ('25901', '1621'),
                                   '263200200': ('26301', '2000001621'),
                                   '2632001200': ('26301', '2100001621'), '441212': ('44102', '2100011621'),
                                   '441222': ('44102', '2200011621'), '441232': ('44102', '2300011621'),
                                   '44188': ('44108', '800011621'), '441313': ('44103', '3100011621'),
                                   '441323': ('44103', '3200011621'), '441333': ('44103', '3300011621'),
                                   '4621521103': ('46201', '100011521'), '46915201010': ('46202', '100011520'),
                                   '46919201010': ('46202', '200011920'), '46960001010': ('46202', '400016000'),
                                   '4631021104': ('46301', '11021'), '4631351104': ('46301', '11351'),
                                   '4631520104': ('46301', '11520'), '4631521104': ('46301', '11521'),
                                   '4631891104': ('46301', '11891'), '4631941104': ('46301', '11941'),
                                   '4632120104': ('46301', '12120'), '4632121104': ('46301', '12121'),
                                   '4632421104': ('46301', '12421'), '4632520104': ('46301', '12520'),
                                   '4632521104': ('46301', '12521'), '4632721104': ('46301', '12721'),
                                   '4633121104': ('46301', '13121'), '4636000104': ('46301', '16000'),
                                   '4636340104': ('46301', '16340'), '4693434': ('46501', '200011520'),
                                   '46931231': ('46501', '300011621'), '46511': ('46502', '100011520'),
                                   '46919201019': ('46601', '100001621'), '46966': ('47001', '100011621'),
                                   '4691818': ('47002', '100021621'), '4691919': ('47002', '200021621'),
                                   '470303': ('47003', '3000021621'), '470313': ('47003', '3100021621'),
                                   '470323': ('47003', '3200021621'), '470333': ('47003', '3300021621'),
                                   '470404': ('47004', '4000021621'), '470414': ('47004', '4100021621'),
                                   '470424': ('47004', '4200021621'), '470434': ('47004', '4300021621'),
                                   '5707871': ('57001', '1621'), '5709781': ('57001', '1621'),
                                   '5707891': ('57001', '1621'), '5707971': ('57001', '1621'),
                                   '5707981': ('57001', '1621'),
                                   '5717871': ('57101', '7870001621'), '5719781': ('57101', '9780001621'),
                                   '5717891': ('57101', '7890001621'), '5717971': ('57101', '7970001621'),
                                   '5717981': ('57101', '7980001621'), '7005656': ('70001', '100011621'),
                                   '72216951695': ('70002', '200011621'), '723313': ('72303', '310011621'),
                                   '7231351103': ('72303', '310011351'), '7231920103': ('72303', '310011920'),
                                   '7231941103': ('72303', '310011941'), '7236000103': ('72303', '310016000'),
                                   '7236340103': ('72303', '310016340'), '723323': ('72303', '320011621'),
                                   '7231761103': ('72303', '320011761'), '723333': ('72303', '330011621'),
                                   '72319201013': ('72303', '330011920'), '723353': ('72303', '350011621'),
                                   '7233003': ('72303', '360011621'), '72355': ('72305', '500011621'),
                                   '723505': ('72306', '600011621'), '723515': ('72307', '700011621'),
                                   '723606': ('72308', '800011621'), '723616': ('72309', '900011621'),
                                   '741212': ('74102', '2100011621'), '741222': ('74102', '2200011621'),
                                   '741232': ('74102', '2300011621'), '74188': ('74108', '800011621'),
                                   '741313': ('74103', '3100011621'), '741323': ('74103', '3200011621'),
                                   '741333': ('74103', '3300011621'), '768626': ('72500', '100011621'),
                                   '768616': ('72700', '300011621'), '7507871': ('75001', '7870011621'),
                                   '7507891': ('75001', '7890011621'), '7507971': ('75001', '7970011621'),
                                   '7507981': ('75001', '7980011621'), '7509781': ('75001', '9780011621'),
                                   '7507872': ('75002', '7870011621'), '7507892': ('75002', '7890011621'),
                                   '7507972': ('75002', '7970011621'), '7507982': ('75002', '7980011621'),
                                   '7509782': ('75002', '9780011621'), '7507812': ('75002', '7810011621'),
                                   '7501114': ('75003', '11621'), '762152010322': ('76200', '11520'),
                                   '762212010322': ('76200', '12121'), '762600010322': ('76200', '16000'),
                                   '76919201099': ('76600', '11621'), '7681010': ('76801', '100011621'),
                                   '7681111': ('76802', '100011621'), '7681212': ('76803', '100011621'),
                                   '76813511012': ('76803', '100011351'), '76817611012': ('76803', '100011941'),
                                   '7681313': ('76804', '100011621'), '7681717': ('76805', '100011621'),
                                   '7681818': ('76806', '100011621'), '7681919': ('76807', '100011621'),
                                   '768828': ('76808', '100011621'), '7681351108': ('76808', '100011351'),
                                   '7681761108': ('76808', '100011761'), '7681941108': ('76808', '100011941'),
                                   '7686000108': ('76808', '100016000'), '7686340108': ('76808', '100016340'),
                                   '7682020': ('76809', '100011621'), '76813511020': ('76809', '100011351'),
                                   '7682121': ('76810', '100011621'), '7682222': ('76811', '100011621'),
                                   '7682323': ('76812', '100011621'), '7682424': ('76813', '100011621'),
                                   '7682525': ('76814', '100011621'), '76813511025': ('76814', '100011351'),
                                   '76863401025': ('76814', '100016340'), '7687171': ('76815', '100011621'),
                                   '76844': ('76815', '200011621'), '76888': ('76816', '100011621'),
                                   '768858': ('76817', '100011621'), '7681616': ('76818', '100011621'),
                                   '7683131': ('76819', '100011621'), '7691414': ('77001', '11621'),
                                   '7691818': ('77002', '100011621'), '7699999': ('77002', '200011621'),
                                   '2492727': ('24902', '200001621'), '4631341104': ('46301', '11341')}
        return dict_konto_subkonto

    def get_dict_spwr_konto_subkonto(self):
        try:
            dict_spwr_konto_subkonto = self.create_dic_fin('out_dic_spwr_konto_subkonto.unl',
                                                           ['konto_src', 'subkonto_src', 'subkonto_pdst_src',
                                                            'spw_r_src',
                                                            'konto_tgt', 'subkonto_tgt'], len_src_cols=4)
            print(f'  FIN: Załadowano słownik out_dic_spwr_konto_subkonto na podstawie pliku. ')
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Załadowano słownik out_dic_spwr_konto_subkonto na podstawie pliku. ", head='dict')
        except FileNotFoundError:
            dict_spwr_konto_subkonto = {'170552521': ('17000', '1'), '170552520': ('17000', '2'),
                                        '170552421': ('17000', '1'), '170552121': ('17000', '3'),
                                        '142666340': ('17000', '4'), '142666000': ('17000', '4'),
                                        '142662521': ('17000', '1'), '142662520': ('17000', '2'),
                                        '142662121': ('17000', '3'), '142662120': ('17000', '4'),
                                        '128333211': ('17000', '3'), '128333111': ('17000', '3'),
                                        '128332721': ('17000', '3'), '128332621': ('17000', '3'),
                                        '128332611': ('17000', '3'), '128332521': ('17000', '1'),
                                        '128332421': ('17000', '1'), '128332121': ('17000', '3'),
                                        '128332111': ('17000', '3'), '128331891': ('17000', '3'),
                                        '128331941': ('17000', '3'), '128331761': ('17000', '3'),
                                        '128331621': ('17000', '3'), '128331521': ('17000', '3'),
                                        '128331351': ('17000', '3'), '128331341': ('17000', '3'),
                                        '128331021': ('17000', '3'), '128333121': ('17000', '3'),
                                        '170772521': ('17000', '1'), '170772520': ('17000', '2'),
                                        '13922221021': ('17000', '15'), '13922221521': ('17000', '15')
                                        }
        return dict_spwr_konto_subkonto

    def get_dic_gielda_id_depozyt(self):
        try:
            out_dic_gielda_id_depozyt = pandas.read_csv(fr'{self._path_dict_folder}\out_dic_gielda_id_depozyt.unl',
                                                        sep='|', header=None, low_memory=False)
            print('   Załadowano słownik out_dic_gielda_id_depozyt na podstawie pliku. ')
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Załadowano słownik out_dic_gielda_id_depozyt na podstawie pliku.", head='dict')
            out_dic_gielda_id_depozyt = out_dic_gielda_id_depozyt.rename(columns={0: 'kod_rynku', 1: 'gielda',
                                                                                  2: 'id_depozyt', 3: 'rynekzlecen',
                                                                                  4: 'zlc_rodzaj_znak_1',
                                                                                  5: 'przedrostek', 6: 'wyroznik'})
            return out_dic_gielda_id_depozyt[
                ['kod_rynku', 'gielda', 'id_depozyt', 'rynekzlecen', 'zlc_rodzaj_znak_1', 'przedrostek', 'wyroznik']]
        except FileNotFoundError:
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Brak słownika out_dic_gielda_id_depozyt w folderze \n{self._path_dict_folder}.",
                            head='dict')

    def get_dic_kody_operacji(self):
        try:
            out_dict_kody_operacji = pandas.read_csv(fr'{self._path_dict_folder}\out_dic_kody_operacji.unl', sep='|',
                                                     header=None, low_memory=False)
            print('   Załadowano słownik out_dict_kody_operacji na podstawie pliku. ')
            out_dict_kody_operacji = out_dict_kody_operacji.rename(columns={0: 'kod_operacji_lp', 2: 'kdpw_tryb_obr',
                                                                            3: 'kdpw_kod_rnk'})
            return out_dict_kody_operacji[['kod_operacji_lp', 'kdpw_tryb_obr', 'kdpw_kod_rnk']]
        except FileNotFoundError:
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Brak słownika out_dic_kody_operacji w folderze \n{self._path_dict_folder}.",
                            head='dict')

    @staticmethod
    def map_values_to_columns(dataframe, column_to_map, col1_to_fill, col2_to_fill, map_dict, col3_to_fill=None):
        return dataframe.apply(cols_mapping, args=(column_to_map, col1_to_fill, col2_to_fill, col3_to_fill), axis=1,
                               mapping_dict=map_dict)

    def create_dic(self, file_path, names, len_src_cols, usecols=None) -> dict:
        dict = {}
        if usecols is None:
            usecols = names

        path = os.path.join(self._path_dict_folder, file_path)
        data = pandas.read_csv(path, header=None, sep="|", names=names, usecols=usecols, dtype=str)

        for row in data.itertuples(index=False):
            if len_src_cols == 2:
                key = row[0].lower() + row[1].lower()
                values = (row[2].lower(), row[3].lower())
                dict[key] = values
            if len_src_cols == 3:
                key = str(int(row[0])) + row[1] + row[2].lower()
                values = (str(row[3]), row[4].lower(), row[5].lower())
                dict[key] = values
        return dict

    def create_dic_fin(self, file_path, names, len_src_cols, usecols=None):
        dict = {}
        if usecols is None:
            usecols = names

        path = os.path.join(self._path_dict_folder, file_path)
        data = pandas.read_csv(path, header=None, sep="|", names=names, usecols=usecols, dtype=str)

        data.loc[:, 'subkonto_src'] = data.loc[:, 'subkonto_src'].astype(str).str.lstrip('0')
        data.loc[:, 'subkonto_tgt'] = data.loc[:, 'subkonto_tgt'].astype(str).str.lstrip('0')
        data.loc[:, 'subkonto_pdst_src'] = data.loc[:, 'subkonto_pdst_src'].astype(str).str.lstrip('0')

        for row in data.itertuples(index=False):
            if len_src_cols == 4:
                key = row[0] + row[1] + row[2] + row[3]
                values = (row[4], row[5])
                dict[key] = values
            if len_src_cols == 3:
                key = row[0] + row[1] + row[2]
                values = (row[3], row[4])
                dict[key] = values
        return dict
