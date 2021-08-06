import requests


def main():
    """main function"""
    api = "http://159.65.193.229:9090/fetch/greenblatt"
    try:
        data = requests.get(api, timeout=30).json()
        for x in data["data"]:
            api = "http://159.65.193.229:9090/fetch/indicators?stock=" + \
                x["ticker"] + ".SA"
            try:
                response = requests.get(api, timeout=30).json()
                if float(response["data"]["rsi14"]) < 30:
                    print("===============================")
                    print("COMPANY  >> " + str(x["companyName"]))
                    print("SCORE    >> " + str(x["final_Score"]))
                    print("BUY      >> " + response["data"]["stock"])
                    print("RSI      >> " + response["data"]["rsi14"])
                    print("EMA      >> " + response["data"]["ema56"])

            except requests.exceptions.RequestException:
                return False
            except (ValueError):
                return False
    except requests.exceptions.RequestException:
        return False
    except (ValueError):
        return False


if __name__ == '__main__':
    main()
