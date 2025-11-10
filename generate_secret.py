import pyotp
import qrcode

secret = pyotp.random_base32()
print("Ta clé secrète à mettre dans .env :", secret)

uri = pyotp.totp.TOTP(secret).provisioning_uri(
    name="blackcoin-validator",
    issuer_name="BlackCoin Admin"
)

qrcode.make(uri).show()
