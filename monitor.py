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
    """查询指定地址的代币余额 (免费接口)"""
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
        if res['status'] == '1':
            return float(res['result']) / 10**18
        return 0
    except:
        return 0

def main():
    if not os.path.exists(CSV_FILE):
        print("请先手动上传初始的 CSV 文件！")
        return

    # 读取旧名单
    df = pd.read_csv(CSV_FILE)
    # 假设 CSV 里有 'Address' 或 'TokenHolderAddress' 这一列
    address_col = 'TokenHolderAddress' if 'TokenHolderAddress' in df.columns else 'Address'
    
    addresses = df[address_col].unique().tolist()[:200] # 只取前200个
    
    results = []
    bj_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d')

    print(f"开始更新 {len(addresses)} 个大户的余额...")
    
    for addr in addresses:
        balance = get_balance(addr)
        results.append({"Address": addr, "Balance": balance, "Date": bj_time})
        time.sleep(0.2) # 免费版限速 5次/秒

    df_new = pd.DataFrame(results)
    
    # 进行简单对比（示例：对比上一次的数据）
    # 这里你可以加入逻辑：如果 Balance 变为 0，标记为“清仓离场”
    # 如果有新数据，可以追加到历史记录中
    
    df_new.to_csv(f"report_{bj_time}.csv", index=False)
    print("今日余额变动报告已生成。")

if __name__ == "__main__":
    main()
