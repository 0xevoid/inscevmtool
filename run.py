from flask import Flask, render_template, request
from web3 import Web3, Account
import time

app = Flask(__name__)

# Nilai awal
rpc = "Ganti dengan menggunakan RPC"
lim = 5  # Tingkatkan nilai default
data = 'data:,{"p":"asc-20","op":"mint","tick":"aval","amt":"100000000"}'


@app.route("/", methods=["GET", "POST"])
def index():
    global rpc, lim, data

    if request.method == "POST":
        rpc = request.form["rpc"]
        lim = int(request.form["lim"])
        data = request.form["data"]

    return render_template("index.html", rpc=rpc, lim=lim, data=data)


@app.route("/run", methods=["GET"])
def run():
    global rpc, lim, data

    w3 = Web3(Web3.HTTPProvider(rpc))

    # Periksa apakah rpc valid
    if not w3.isConnected():
        return "Error: Unable to connect to RPC node."

    # Dapatkan harga bahan bakar
    gas_price = w3.eth.gas_price
    gas_price_gwei = w3.fromWei(gas_price, "Gwei")

    # Dapatkan semua kunci pribadi
    private_keys = request.form["private_keys"].split("\n")

    # Variabel yang digunakan untuk menyimpan pesan cetak
    output_messages = []

    # Iterasi setiap kunci pribadi
    for idx, private_key in enumerate(private_keys, start=1):
        private_key = private_key.strip()  # Hapus spasi awal dan akhir

        # Kunci pribadi kosong diabaikan
        if not private_key:
            continue

        # Dapatkan alamat yang sesuai
        from_address = Account.from_key(private_key).address
        to_address = from_address  # Gunakan alamat yang sesuai sebagai alamat penerima

        # Kirim transaksi
        for i in range(lim):
            nonce = w3.eth.getTransactionCount(from_address)
            transaction = {
                "from": from_address,
                "to": to_address,
                "value": w3.toWei(0, "ether"),
                "nonce": nonce,
                "gas": 25000,
                "gasPrice": gas_price,
                "data": w3.toHex(text=data),
                "chainId": w3.eth.chain_id,
            }

            # Tandatangani transaksi
            signed = w3.eth.account.sign_transaction(transaction, private_key)

            try:
                # Disiarkan ke blockchain
                tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
                output_messages.append(
                    f"Account {idx} - Hash: {tx_hash.hex()}, noce: {nonce}"
                )
            except Exception as e:
                output_messages.append(f"Account {idx} - kesalahan transaksi: {e}, transaksi data: {data}")

            time.sleep(3)  # Waktu istirahat setiap transaksi, dapat disesuaikan dengan kebutuhan

    # Tampilkan pesan cetak dalam HTML
    return render_template(
        "index.html", rpc=rpc, lim=lim, data=data, output="\n".join(output_messages)
    )


if __name__ == "__main__":
    app.run(debug=True)
