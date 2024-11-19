# kgcontroller module
import pandas as pd
import numpy as np
from dbexcel import *
from kgmodel import *

def insert_foresatt(f):
    global forelder
    new_id = 0
    if forelder.empty:
        new_id = 1
    else:
        new_id = forelder['foresatt_id'].max() + 1

    forelder = pd.concat([pd.DataFrame([[new_id,
                                         f.foresatt_navn,
                                         f.foresatt_adresse,
                                         f.foresatt_tlfnr,
                                         f.foresatt_pnr]],
                                       columns=forelder.columns), forelder], ignore_index=True)

    return forelder

def insert_barn(b):
    global barn
    new_id = 0
    if barn.empty:
        new_id = 1
    else:
        new_id = barn['barn_id'].max() + 1

    barn = pd.concat([pd.DataFrame([[new_id,
                                    b.barn_pnr]],
                                   columns=barn.columns), barn], ignore_index=True)

    return barn

def insert_soknad(s):
    global soknad
    new_id = 0
    if soknad.empty:
        new_id = 1
    else:
        new_id = soknad['sok_id'].max() + 1

    soknad = pd.concat([pd.DataFrame([[new_id,
                                      s.foresatt_1.foresatt_id,
                                      s.foresatt_2.foresatt_id,
                                      s.barn_1.barn_id,
                                      s.fr_barnevern,
                                      s.fr_sykd_familie,
                                      s.fr_sykd_barn,
                                      s.fr_annet,
                                      s.barnehager_prioritert,
                                      s.sosken__i_barnehagen,
                                      s.tidspunkt_oppstart,
                                      s.brutto_inntekt]], 
                                      columns=soknad.columns), soknad], ignore_index=True)

    return soknad

def select_alle_barnehager():
    """Returnerer en liste med alle barnehager definert i databasen dbexcel."""
    return barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                                               r['barnehage_navn'],
                                               r['barnehage_antall_plasser'],
                                               r['barnehage_ledige_plasser']),
                           axis=1).to_list()


def select_foresatt(f_navn):
    """OBS! Ignorerer duplikater"""
    series = forelder[forelder['foresatt_navn'] == f_navn]['foresatt_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0]


def select_barn(b_pnr):
    """OBS! Ignorerer duplikater"""
    series = barn[barn['barn_pnr'] == b_pnr]['barn_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0]

def select_alle_soknader():
    enriched_soknad_list = []
    for _, r in soknad.iterrows():
        fos1 = forelder.loc[forelder['foresatt_id'] == r['foresatt_1']].iloc[0] if not forelder[forelder['foresatt_id'] == r['foresatt_1']].empty else None
        fos2 = forelder.loc[forelder['foresatt_id'] == r['foresatt_2']].iloc[0] if not forelder[forelder['foresatt_id'] == r['foresatt_2']].empty else None
        barn1 = barn.loc[barn['barn_id'] == r['barn_1']].iloc[0] if not barn[barn['barn_id'] == r['barn_1']].empty else None

        enriched_soknad = Soknad(
            r['sok_id'], 
            fos1 if fos1 is not None else Foresatt(0, 'Unknown', '', '', ''),
            fos2 if fos2 is not None else Foresatt(0, 'Unknown', '', '', ''),
            barn1 if barn1 is not None else Barn(0, 'Unknown'),
            r['fr_barnevern'], 
            r['fr_sykd_familie'] if 'fr_sykd_familie' in r else '',
            r['fr_sykd_barn'] if 'fr_sykd_barn' in r else '',
            r['fr_annet'] if 'fr_annet' in r else '',
            r['barnehager_prioritert'] if 'barnehager_prioritert' in r else '',
            r['sosken__i_barnehagen'] if 'sosken__i_barnehagen' in r else '',
            r['tidspunkt_oppstart'] if 'tidspunkt_oppstart' in r else '',
            r['brutto_inntekt'] if 'brutto_inntekt' in r else 0
        )
        enriched_soknad_list.append(enriched_soknad)
    return enriched_soknad_list

def commit_all():
    """Writes all DataFrames to Excel, replacing sheets if they already exist."""
    with pd.ExcelWriter('kgdata.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        forelder.to_excel(writer, sheet_name='foresatt')
        barnehage.to_excel(writer, sheet_name='barnehage')
        barn.to_excel(writer, sheet_name='barn')
        soknad.to_excel(writer, sheet_name='soknad')


excel_data = pd.read_excel("kgdata.xlsx", sheet_name=None)


def get_all_data():
    data = {sheet_name: sheet_df.to_dict(
        orient='records') for sheet_name, sheet_df in excel_data.items()}
    return data

def form_to_object_soknad(sd):
    foresatt_1 = Foresatt(0, sd.get('navn_forelder_1'), sd.get('adresse_forelder_1'), sd.get('tlf_nr_forelder_1'), sd.get('personnummer_forelder_1'))
    foresatt_2 = Foresatt(0, sd.get('navn_forelder_2'), sd.get('adresse_forelder_2'), sd.get('tlf_nr_forelder_2'), sd.get('personnummer_forelder_2'))
    barn_1 = Barn(0, sd.get('personnummer_barnet_1'))

    insert_foresatt(foresatt_1)
    insert_foresatt(foresatt_2)
    insert_barn(barn_1)

    foresatt_1.foresatt_id = select_foresatt(sd.get('navn_forelder_1'))
    foresatt_2.foresatt_id = select_foresatt(sd.get('navn_forelder_2'))
    barn_1.barn_id = select_barn(sd.get('personnummer_barnet_1'))

    sok_1 = Soknad(0, foresatt_1, foresatt_2, barn_1, sd.get('fortrinnsrett_barnevern'), sd.get('fortrinnsrett_sykdom_i_familien'), sd.get('fortrinnsrett_sykdome_paa_barnet'), sd.get('fortrinssrett_annet'), sd.get('liste_over_barnehager_prioritert_5'), sd.get('har_sosken_som_gaar_i_barnehagen'), sd.get('tidspunkt_for_oppstart'), sd.get('brutto_inntekt_husholdning'))

    return sok_1

def test_df_to_object_list():
    assert barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                                               r['barnehage_navn'],
                                               r['barnehage_antall_plasser'],
                                               r['barnehage_ledige_plasser']),
                           axis=1).to_list()[0].barnehage_navn == "Sunshine Preschool"
