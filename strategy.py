import requests


def main():
    """main function"""
    #api = "http://159.65.193.229:9090/fetch/graham"
    api = "http://159.65.193.229:9090/fetch/greenblatt"
    try:
        data = requests.get(api).json()
        for x in data["data"][:20]:
            api = "http://159.65.193.229:9090/fetch/indicators?stock=" + \
                x["ticker"] + ".SA"
            try:
                response = requests.get(api).json()
                if float(response["data"]["rsi14"]) < 30:
                    print("==================================")
                    print("COMPANY  >> " + str(x["companyName"]))
                    print("TIKER    >> " + response["data"]["stock"])
                    print("PRICE    >> " + str(x["price"]))
                    # print("DISCOUNT         >> " + str(x["desconto"]))
                    # print("INTRINSIC PRICE  >> " + str(x["val_Intrinseco"]))
                    print("SCORE    >> " + str(x["final_Score"]))
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
