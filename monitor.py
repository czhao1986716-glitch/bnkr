import requests
import pandas as pd
import datetime
import os

# 从 GitHub Secrets 读取 API Key (建议使用 Etherscan 官网申请的新 Key)
API_KEY = os.getenv('BASESCAN_API_KEY')
TOKEN_ADDRESS = "0x22af33fe49fd1fa80c7149773dde5890d3c76f3b"
# 关键修改：使用 V2 统一入口
BASE_URL = "https://api.etherscan.io/v2/api"
CSV_FILE = "bnkr_holders_history.csv"

def get_holders():
    params = {
        "chainid": "8453",      # 关键修改：增加 Base 链的 ChainID
        "module": "token",
        "action": "tokenholderlist",
        "contractaddress": TOKEN_ADDRESS,
        "page": 1,
        "offset": 200,
        "apikey": API_KEY
    }
    try:
        # V2 接口请求
        response = requests.get(BASE_URL, params=params, timeout=20)
        data = response.json()
        
        # 如果报错提示 V1 废弃，这里会打印出来
        if data['status'] == '1':
            return pd.DataFrame(data['result'])
        else:
            print(f"API 提示: {data.get('message')}")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def main():
    # 获取北京时间 (UTC+8)
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    df_new = get_holders()
    
    if df_new is not None:
        # 18位精度处理
        df_new['TokenHolderQuantity'] = df_new['TokenHolderQuantity'].astype(float) / 10**18
        df_new['Date'] = bj_time
        
        if os.path.exists(CSV_FILE):
            try:
                df_old = pd.read_csv(CSV_FILE)
                df_final = pd.concat([df_old, df_new], ignore_index=True)
            except:
                df_final = df_new
        else:
            df_final = df_new
            
        df_final.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        print(f"数据更新成功: {bj_time}")
    else:
        print("未能获取到数据，请检查 API 是否已升级至 V2 格式。")

if __name__ == "__main__":
    main()
