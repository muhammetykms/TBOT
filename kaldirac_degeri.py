# import requests

# def get_leverage_brackets(symbol, api_key):
#     url = "https://fapi.binance.com/fapi/v1/leverageBracket"
#     headers = {
#         'X-MBX-APIKEY': api_key
#     }
#     params = {
#         'symbol': symbol
#     }
#     response = requests.get(url, headers=headers, params=params)
#     data = response.json()

#     # Burada data liste mi kontrol edeceğiz
#     if isinstance(data, list) and len(data) > 0:
#         brackets = data[0]['brackets']
#     else:
#         raise Exception(f"API yanıtı beklenmedik formatta: {data}")

#     leverages = sorted(set(b['initialLeverage'] for b in brackets), reverse=True)
#     return leverages

# # Kullanım örneği
# api_key = "SENIN_BINANCE_API_KEYIN"
# symbol = "BNBUSDT"
# allowed_leverages = get_leverage_brackets(symbol, api_key)
# print(f"{symbol} için izin verilen kaldıraçlar: {allowed_leverages}")




import requests

def get_bnbusdt_exchange_info():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()

    for symbol_info in data['symbols']:
        if symbol_info['symbol'] == 'BNBUSDT':
            return symbol_info

    return None

# Kullanım
bnb_info = get_bnbusdt_exchange_info()
if bnb_info:
    print("BNBUSDT Bilgileri:")
    for key, value in bnb_info.items():
        print(f"{key}: {value}")
else:
    print("BNBUSDT bilgisi bulunamadı.")
