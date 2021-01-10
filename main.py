import requests
import pandas as pd
import numpy as np
from email.message import EmailMessage
import smtplib
import email.message
from config import steamid, mail_subject, mail_from, mail_to, mail_password, watchlist

def get_inventory() -> dict:
    currency = "3"
    URL = f"https://csgobackpack.net/?nick={steamid}&currency={currency}"

    page = requests.get(URL, headers={})
    table = pd.read_html(page.text)
    
    table_df = pd.DataFrame(table[0])
    data = table[0]
    np_objects = data.to_numpy()
    data_objects = {}
    for item_np in np_objects:
        item_array = list(item_np)
        data_objects[item_array[2]] = {"amount": item_array[3],"price": item_array[4], "classid": item_array[7], "total_price": str(float(item_array[3]) * float(item_array[4].split("€")[0]))+"€"}
    data_objects["total_items"] = sum(data["Amount"])
    data_objects["total_value"] = str(round(sum([float(price.split("€")[0]) for price in data["In Total"]]), 2))+"€"

    return data_objects

def send_mail():
    items = get_inventory()

    tds = ""
    welements = ""
    _watchlist = {}

    for item in items:
        
        if item == "total_items" or item == "total_value": 
            pass
        else:
            amount = items[item]["amount"]
            price = items[item]["price"]
            total_price = items[item]["total_price"]
            tds+=f"<tr><td>{item}</td><td>{amount}</td><td>{price}</td><td>{total_price}</td></tr>"

    for witem in watchlist:
        _watchlist[witem] = requests.get(f"https://steamcommunity.com/market/priceoverview/?appid=730&market_hash_name={witem}&currency=3").json()

    for _witem in _watchlist:
        welements += f"<h4>{_witem} : {_watchlist[_witem]['lowest_price']}</h4>"

        html = f"""
        <h1>See your daily inventory!</h1>
        <hr>
        <h3>Total items: {items['total_items']}</h3>
        <h3>Total inventory value: {items['total_value']}</h3>
        <table>
            <tr>
                <th>Name</th>
                <th>Amount</th>
                <th>Price</th>
                <th>Total Price</th>
            </tr>
            {tds}
        </table>
        <br>
        <h1>Watchlist</h1>
        <hr>
        {welements}
        """
    
    msg = email.message.Message()
    msg["Subject"] = mail_subject
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg.add_header('Content-Type','text/html')
    msg.set_payload(html, charset="utf-8")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(mail_from, mail_password)
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    server.quit()

    return

if __name__ == "__main__":
    send_mail()