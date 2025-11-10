import pyotp
import qrcode

# === INFORMATIONS DU VALIDATEUR ===
secret = "JZN6TBJ2WRVFRGOD5JJA7C6IK26NVV3B"
email = "fawilfried@gmail.com"
app_name = "BlackCoin Validator"

# === CRÉATION DU LIEN COMPATIBLE GOOGLE AUTHENTICATOR ===
uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=app_name)

# === GÉNÉRATION DU QR CODE ===
qr = qrcode.make(uri)
qr.save("validator_qr.png")

print("✅ QR code généré avec succès : validator_qr.png")
print(f"URI Google Authenticator : {uri}")
