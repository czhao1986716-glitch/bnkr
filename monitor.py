import requests
import pandas as pd
import datetime
import os
import time

API_KEY = os.getenv('BASESCAN_API_KEY')
TOKEN_ADDRESS = "0x22af33fe49fd1fa80c7149773dde5890d3c76f3b"
BASE_URL = "https://api.etherscan.io/v2/api"
CSV_FILE = "bnkr_holders_history.csv"

def get_balance(address):
    params = {
        "chainid": "8453",
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": TOKEN_ADDRESS,
        "address": address,
        "tag": "latest",
        "apikey": API_KEY
    }
    try:
        res = requests.get(BASE_URL, params=params, timeout=10).json()
        return float(res['result']) / 10**18 if res['status'] == '1' else 0
    except:
        return 0

def main():
    if not os.path.exists(CSV_FILE): return

    # 读取文件，跳过可能存在的 BaseScan 说明行
    try:
        df_old = pd.read_csv(CSV_FILE)
    except:
        print("CSV 读取失败")
        return

    # 自动识别列名：BaseScan 原始列名通常是 'HolderAddress' 和 'Balance' 或 'Quantity'
    addr_col = next((c for c in df_old.columns if 'Address' in c or 'Holder' in c), None)
    
    if not addr_col:
        print("找不到地址列")
        return

    # 提取前 200 个地址进行更新
    top_addresses = df_old[addr_col].unique()[:200]
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    new_records = []
    for addr in top_addresses:
        if str(addr).startswith('0x'):
            bal = get_balance(addr)
            new_records.append({addr_col: addr, 'Balance': bal, 'Date': bj_time})
            time.sleep(0.2)

    df_new = pd.DataFrame(new_records)
    # 关键：将新抓取的余额追加在旧数据后面，而不是覆盖
    df_final = pd.concat([df_old, df_new], ignore_index=True)
    df_final.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    print(f"成功更新 {len(new_records)} 条数据")

if __name__ == "__main__":
    main()
