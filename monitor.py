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
    params = {"chainid": "8453", "module": "account", "action": "tokenbalance", 
              "contractaddress": TOKEN_ADDRESS, "address": address, "tag": "latest", "apikey": API_KEY}
    try:
        res = requests.get(BASE_URL, params=params, timeout=10).json()
        return float(res['result']) / 10**18 if res['status'] == '1' else 0
    except: return 0

def main():
    if not os.path.exists(CSV_FILE): return
    df_history = pd.read_csv(CSV_FILE)
    
    # 统一列名
    addr_col = 'HolderAddress'
    if 'Address' in df_history.columns: df_history.rename(columns={'Address': addr_col}, inplace=True)
    
    # 获取需要监控的地址列表（前200名）
    unique_addresses = df_history[addr_col].unique()[:200]
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    
    new_data = []
    for addr in unique_addresses:
        if not str(addr).startswith('0x'): continue
        curr_bal = get_balance(addr)
        
        # 寻找该地址上一次的余额记录
        addr_history = df_history[df_history[addr_col] == addr]
        last_bal = addr_history['Balance'].iloc[-1] if not addr_history.empty else curr_bal
        
        diff = curr_bal - last_bal
        
        new_data.append({
            'HolderAddress': addr,
            'Balance': curr_bal,
            'Change': diff,
            'Date': bj_time
        })
        time.sleep(0.2)

    df_new = pd.DataFrame(new_data)
    df_final = pd.concat([df_history, df_new], ignore_index=True)
    df_final.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    main()
