
# Лабораторна робота 3
# Виконав ФБ-33 Терещенко Микола


import os
import pandas as pd
from spyre import server
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.request
from datetime import datetime


state_id_name = {1: "Cherkasy", 2: "Chernihiv", 3: "Chernivtsi", 4: "Crimea", 5: "Dnipro", 6: "Donets'k", 
            7: "Ivano-Frankivs'k", 8: "Kharkiv", 9: "Kherson", 10: "Khmel'nyts'kyy", 11: "Kyiv", 12: "Kyiv City", 
            13: "Kropyvnyts'kyi", 14: "Luhans'k", 15: "L'viv", 16: "Mykolayiv", 17: "Odesa", 18: "Poltava", 19: "Rivne",
            20: "Sevastopol'", 21: "Sumy", 22: "Ternopil'", 23: "Transcarpathia", 24: "Vinnytsya", 25: "Volyn", 
            26: "Zaporizhzhya", 27: "Zhytomyr"}



def check_if_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)

    dir = os.listdir(path) 
  
    if len(dir) == 0:
        for i in range(1,28):
            get_data(i, path)  


def get_data(province_id, path):

    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={province_id}&year1=1981&year2=2024&type=Mean"
    vhi_url = urllib.request.urlopen(url)
    

    now = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f'vhi_id_{province_id}_{now}.csv'
    filepath = f'{path}/{filename}'
    with open(filepath, 'wb') as out:
        out.write(vhi_url.read())
    print(f"VHI was downloaded in {filepath}")



def read_and_create_data_frame(path):
    
    out_df = pd.DataFrame()

    csv_files = os.listdir('/home/kali/Downloads/csv')  #change with your pathfolder

    frames = []

    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']


    for file in range(len(csv_files)):
        file_path = os.path.join(path, csv_files[file])
        df = pd.read_csv(file_path , header = 1, names = headers)
        
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df['Year'] = df['Year'].str.replace('<tt><pre>', '')
        df = df[~df['Year'].str.contains('</pre></tt>')]
        df['area'] = file + 1
        df.drop('empty', axis=1, inplace=True)
        df['Year'] = df['Year'].astype(int)
        df['Week'] = df['Week'].astype(int)
        frames.append(df)
    
    out_df = pd.concat(frames).drop_duplicates().reset_index(drop=True)
    out_df.drop([22, 12])
    out_df = out_df.loc[(out_df.area != 12) & (out_df.area != 20)]  
    return out_df
 






class APA(server.App):
    title = "LAB 3"
    
    inputs = [
        {
            "type": 'dropdown',
            "label": 'Index',
            "options": [
                {"label": "VCI", "value": "VCI"},
                {"label": "TCI", "value": "TCI"},
                {"label": "VHI", "value": "VHI"}
            ],
            "key": 'index',
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "label": 'Region',
            "options": [
                {"label": state_id_name[i], "value": i} for i in range(1, 28)
            ],
            "key": 'region',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": 'Week range',
            "value": "1-52",
            "key": 'week_interval',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": 'Date [yyyy-yyyy]',
            "value": '2000-2021',
            "key": 'date_range',
            "action_id": "update_data"
        }
    ]

    controls = [{"type": "button", "label": "Update", "id": "update_data"}]

    tabs = ["Table", "Plot"]

    outputs = [
        {"type": "table", "id": "table", "control_id": "update_data", "tab": "Table"},
        {"type": "plot", "id": "plot", "control_id": "update_data", "tab": "Plot"}
    ]

    def getData(self, params):
        index = params['index']
        region = int(params['region'])
        week_interval = params['week_interval'].split('-')
        date_range = params['date_range'].split('-')


                                                                                
        df = read_and_create_data_frame('/home/kali/Downloads/csv')   #change with your pathfolder 

        processed_data = df[(df['area'] == region) & 
                                (df['Year'].between(int(date_range[0]), int(date_range[1]))) &
                                (df['Week'].between(int(week_interval[0]), int(week_interval[1])))]
        
        processed_data = processed_data[['Year', 'Week', index]]

        return processed_data

    def getPlot(self, params):
        index = params['index']
        region = int(params['region'])
        week_interval = params['week_interval'].split('-')
        date_range = params['date_range'].split('-')

        processed_data = self.getData(params)


        pivot_data = processed_data.pivot(index='Year', columns='Week', values=index)
        plt.figure(figsize=(25, 20))
        sns.heatmap(pivot_data, cmap="inferno", annot=True)
        plt.title(f'Heatmap {index} for region: {state_id_name[region]}')
        plt.xlabel('Week')
        plt.ylabel('Year')

        plot = plt.gcf()
        return plot

def main():

   

    check_if_exist('/home/kali/Downloads/csv') #change with your pathfolder 
    app = APA()
    app.launch()

if __name__ == "__main__":
    main()
