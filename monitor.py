import requests
import pandas as pd
import datetime
import os

# 从 GitHub Secrets 读取 API Key
API_KEY = os.getenv('BASESCAN_API_KEY')
TOKEN_ADDRESS = "0x22af33fe49fd1fa80c7149773dde5890d3c76f3b"
BASE_URL = "https://api.basescan.org/api"
CSV_FILE = "bnkr_holders_history.csv"

def get_holders():
    params = {
        "module": "token",
        "action": "tokenholderlist",
        "contractaddress": TOKEN_ADDRESS,
        "page": 1,
        "offset": 200,
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params, timeout=20)
    data = response.json()
    if data['status'] == '1':
        return pd.DataFrame(data['result'])
    return None

def main():
    today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    df_new = get_holders()
    
    if df_new is not None:
        # 18位精度处理
        df_new['TokenHolderQuantity'] = df_new['TokenHolderQuantity'].astype(float) / 10**18
        df_new['Date'] = today
        
        # 合并旧数据
        if os.path.exists(CSV_FILE):
            df_old = pd.read_csv(CSV_FILE)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
            
        df_final.to_csv(CSV_FILE, index=False)
        print(f"数据已更新: {today}")

if __name__ == "__main__":
    main()
