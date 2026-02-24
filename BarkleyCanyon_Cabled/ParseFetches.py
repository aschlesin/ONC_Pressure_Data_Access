# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 14:32:45 2021
Prse the Fecth logfiles
@author: schlesin
"""

from onc.onc import ONC
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
load_dotenv()


class ParseFetches():
    def __init__(self,SN,deviceCode,startdate,enddate):
        self.start  = startdate
        self.end    = enddate
        self.SN   = SN
        self.deviceCode = deviceCode
        
        # here you need your ONC token obtained from 
        # the website: https://data.oceannetworks.ca/Profile and put it into a .env file with the key/parameter
        # ONC_TOKEN= 'your token'

        self.token = os.getenv('ONC_TOKEN')
        self.onc = ONC(self.token)
        
        
    def getONCRawData(self):
        
        self.data = self.onc.getDirectRawByDevice({
                'deviceCode':self.deviceCode,
                'dateFrom':self.start,
                'dateTo':self.end}, allPages=True)

        tmps = pd.to_datetime(self.data['data']['times'])
        self.df = pd.DataFrame(self.data['data']['readings'],columns=['lines'])
        self.df.set_index(tmps,inplace=True)
        self.df.rename_axis(index='Timestamp',inplace=True)

        return(self.df)

        
    def parseData(self):
        df = self.df
        # Create a temporary DataFrame of columns from the 'lines' string
        # expand=True turns ['a,b,c'] into separate columns
        df_split = self.df['lines'].str.split(',', expand=True)
        # Filter by column 1 (the tag) and grab column 6 (the value)
        tmp_mask = df_split[1] == 'TMP'
        df.loc[tmp_mask, 'TMP_Temp'] = df_split.loc[tmp_mask, 6].str.split('*').str[0].astype(float)

        # --- DQZ Extraction ---
        dqz_mask = df_split[1] == 'DQZ'
        print(df.loc[dqz_mask])
        df.loc[dqz_mask, 'DQZ_Press'] = df_split.loc[dqz_mask, 6].astype(float)*0.1
        df.loc[dqz_mask, 'DQZ_Temp'] = df_split.loc[dqz_mask, 7].str.split('*').str[0].astype(float)

        # --- INC Extraction (Pitch & Roll) ---
        inc_mask = df_split[1] == 'INC'
        df.loc[inc_mask, 'INC_Pitch'] = df_split.loc[inc_mask, 6].astype(float)
        df.loc[inc_mask, 'INC_Roll'] = df_split.loc[inc_mask, 7].str.split('*').str[0].astype(float)

        # --- PIES Extraction (Pressue, TOF,Mag, RMLE_TOF,Halflife,RMS,RMLE_Range,Peak) ---
        pies_mask = df_split[1] == 'PIES'
        df.loc[pies_mask, 'PIES_PRESS'] = df_split.loc[pies_mask, 13].astype(float)*0.1
        df.loc[pies_mask, 'PIES_TOF'] = df_split.loc[pies_mask, 14].astype(float)
        df.loc[pies_mask, 'PIES_Mag'] = df_split.loc[pies_mask, 15].astype(float)
        df.loc[pies_mask, 'PIES_RMLE_TOF'] = df_split.loc[pies_mask, 16].astype(float)
        df.loc[pies_mask, 'PIES_Halflife'] = df_split.loc[pies_mask, 17].astype(float)
        df.loc[pies_mask, 'PIES_RMS'] = df_split.loc[pies_mask, 18].astype(float)
        df.loc[pies_mask, 'PIES_RMLE_Range'] = df_split.loc[pies_mask, 19].astype(float)
        df.loc[pies_mask, 'PIES_Peak'] = df_split.loc[pies_mask, 20].str.split('*').str[0].astype(float)

        # --- KLR Extraction (Temperature & Pressure) ---
        klr_mask = df_split[1] == 'KLR'
        df.loc[klr_mask, 'KLR_PRESS'] = df_split.loc[klr_mask, 6].astype(float)*0.1
        df.loc[klr_mask, 'KLR_Temp'] = df_split.loc[klr_mask, 7].str.split('*').str[0].astype(float)

        # --- AZA Extraction (Temperature & Pressure & RMS, Settiling) ---
        aza_mask = df_split[1] == 'AZA'
        df.loc[aza_mask, 'AZA_PRESS_PRIM'] = df_split.loc[aza_mask, 8].astype(float)*0.1
        df.loc[aza_mask, 'AZA_Temp_PRIM'] = df_split.loc[aza_mask, 9].astype(float)
        df.loc[aza_mask, 'AZA_PRESS_KLR'] = df_split.loc[aza_mask, 10].astype(float)*0.1
        df.loc[aza_mask, 'AZA_Temp_KLR'] = df_split.loc[aza_mask, 11].astype(float)
        df.loc[aza_mask, 'AZA_PRESS_Low'] = df_split.loc[aza_mask, 12].astype(float)*0.1
        df.loc[aza_mask, 'AZA_Temp_Low'] = df_split.loc[aza_mask, 13].astype(float)
        df.loc[aza_mask, 'AZA_RMS_ERROR'] = df_split.loc[aza_mask, 14].astype(float)
        df.loc[aza_mask, 'AZA_Settling'] = df_split.loc[aza_mask, 15].astype(float)
        df.loc[aza_mask, 'AZA_ERROR_REPORT'] = df_split.loc[aza_mask, 16].astype(float)

        # --- AZS Extraction (Temperature & Pressure & RMS, Settiling) ---
        azs_mask = df_split[1] == 'AZS'
        df.loc[azs_mask, 'AZS_PRESS_PRIM'] = df_split.loc[azs_mask, 8].astype(float)*0.1
        df.loc[azs_mask, 'AZS_Temp_PRIM'] = df_split.loc[azs_mask, 9].astype(float)
        df.loc[azs_mask, 'AZS_PRESS_SEC'] = df_split.loc[azs_mask, 10].astype(float)*0.1
        df.loc[azs_mask, 'AZS_Temp_SEC'] = df_split.loc[azs_mask, 11].astype(float)
        df.loc[azs_mask, 'AZS_PRESS_Low'] = df_split.loc[azs_mask, 12].astype(float)*0.1
        df.loc[azs_mask, 'AZS_Temp_Low'] = df_split.loc[azs_mask, 13].astype(float)
            
        # Optional: Fill gaps so every timestamp has the most recent sensor value
        #self.df_continuous = df.ffill()
        
        return(self.df)

    