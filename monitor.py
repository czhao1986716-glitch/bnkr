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
    try:
        response = requests.get(BASE_URL, params=params, timeout=20)
        data = response.json()
        if data['status'] == '1':
            return pd.DataFrame(data['result'])
        else:
            print(f"API Error: {data.get('message')}")
            return None
    except Exception as e:
        print(f"Request Failed: {e}")
        return None

def main():
    # 获取北京时间 (UTC+8)
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    df_new = get_holders()
    
    if df_new is not None:
        # 18位精度处理
        df_new['TokenHolderQuantity'] = df_new['TokenHolderQuantity'].astype(float) / 10**18
        df_new['Date'] = bj_time
        
        # 合并旧数据
        if os.path.exists(CSV_FILE):
            try:
                df_old = pd.read_csv(CSV_FILE)
                df_final = pd.concat([df_old, df_new], ignore_index=True)
            except:
                df_final = df_new
        else:
            df_final = df_new
            
        # 增加 encoding='utf-8-sig' 确保 Excel 打开不乱码
        df_final.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        print(f"数据更新成功: {bj_time}")
    else:
        print("未能获取到数据，请检查 API Key 或网络。")

if __name__ == "__main__":
    main()
