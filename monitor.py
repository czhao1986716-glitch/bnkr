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
    except Exception as e:
        return 0

def main():
    if not os.path.exists(CSV_FILE):
        return

    try:
        # 读取时强制处理：去掉数值列可能的逗号
        df_history = pd.read_csv(CSV_FILE)
        df_history.columns = df_history.columns.str.strip()
        
        # 核心修复：清理 Balance 列，确保它是纯数字
        if 'Balance' in df_history.columns:
            df_history['Balance'] = df_history['Balance'].astype(str).str.replace(',', '').astype(float)
    except Exception as e:
        print(f"读取或清理CSV失败: {e}")
        return

    addr_col = next((c for c in df_history.columns if 'Address' in c or 'Holder' in c), 'HolderAddress')
    unique_addresses = df_history[addr_col].dropna().unique().tolist()[:200]
    
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
    print(f"开始更新 {len(unique_addresses)} 个大户的数据...")

    new_records = []
    for addr in unique_addresses:
        if not str(addr).startswith('0x'): continue
        
        curr_bal = get_balance(addr)
        
        # 寻找该地址上一次的记录
        addr_hist = df_history[df_history[addr_col] == addr]
        
        # 核心修复：确保参与减法运算的两个值都是 float 类型
        if not addr_hist.empty and 'Balance' in df_history.columns:
            last_bal = float(addr_hist['Balance'].iloc[-1])
        else:
            last_bal = curr_bal
        
        change = curr_bal - last_bal
        
        new_records.append({
            addr_col: addr,
            'Balance': curr_bal,
            'Change': change,
            'Date': bj_time
        })
        time.sleep(0.21)

    df_new = pd.DataFrame(new_records)
    df_final = pd.concat([df_history, df_new], ignore_index=True)
    
    # 限制文件大小
    if len(df_final) > 10000:
        df_final = df_final.tail(10000)

    df_final.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ 更新成功！")

if __name__ == "__main__":
    main()
