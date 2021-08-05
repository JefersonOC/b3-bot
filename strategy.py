import requests


def main():
    """main function"""
    api = "http://159.65.193.229:9090/fetch/greenblatt"
    try:
        data = requests.get(api, timeout=30).json()
        for x in data["data"]:
            if x["final_Score"] > 200:
                api = "http://159.65.193.229:9090/fetch/indicators?stock=" + \
                    x["ticker"] + ".SA"
                try:
                    data = requests.get(api, timeout=30).json()
                    if float(data["data"]["rsi14"]) < 30:
                        print("BUY >> " + data["data"]["stock"])
                    if float(data["data"]["rsi14"]) > 70:
                        print("SELL >> " + data["data"]["stock"])

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
