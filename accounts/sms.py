import logging
import uuid

import requests
from django.conf import settings

logger = logging.getLogger("accounts.sms")

TURATEL_SEND_SMS_URL = "https://api.turatel.com/AllInOneWebService/json-api/api/SmsProxy/sendSMS"

# https://api.turatel.com SendSms hata kodları (dokümandan).
TURATEL_ERROR_MESSAGES = {
    "-1": "Girilen bilgilere sahip bir kullanıcı bulunamadı.",
    "-2": "Kullanıcı pasif durumda.",
    "-3": "Kullanıcı bloke durumda.",
    "-4": "Kullanıcı hesabı bulunamadı.",
    "-5": "Kullanıcı hesabı pasif durumda.",
    "-8": "Alınan parametrelerden biri veya birkaçı hatalı.",
    "-13": "Geçersiz gönderici bilgisi.",
    "-14": "Hesaba ait SMS gönderim yetkisi bulunmuyor.",
    "-15": "Mesaj içeriği boş veya limit olan karakter sayısını aşıyor.",
    "-16": "Geçersiz alıcı bilgisi.",
    "-19": "Mükerrer gönderim isteği.",
    "-21": "Numara kara listede.",
    "-22": "Yetkisiz IP adresi.",
    "-28": "Kullanıcı gönderim limiti aşıldı.",
}


class SmsSendError(Exception):
    pass


def _to_turatel_receiver(phone_number: str) -> str:
    # "+905555555555" -> "905555555555"
    return phone_number.lstrip("+")


def send_sms(phone_number: str, message: str) -> None:
    payload = {
        "username": settings.TURATEL_USERNAME,
        "password": settings.TURATEL_PASSWORD,
        "userCode": settings.TURATEL_USER_CODE,
        "accountId": settings.TURATEL_ACCOUNT_ID,
        "originator": settings.TURATEL_ORIGINATOR,
        "validityPeriod": 300,  # OTP hesaplarda saniye cinsinden, max 300.
        "isCheckBlackList": True,
        "isEncryptedParameter": True,
        "referenceId": str(uuid.uuid4()),
        "sendDate": "",
        "messageText": message,
        "receiverList": [_to_turatel_receiver(phone_number)],
        "personalMessages": [],
    }

    try:
        response = requests.post(TURATEL_SEND_SMS_URL, json=payload, timeout=10)
    except requests.RequestException:
        logger.exception("Turatel SMS isteği başarısız (%s)", phone_number)
        raise SmsSendError("SMS sağlayıcısına ulaşılamadı.")

    if response.status_code != 200:
        logger.error("Turatel SMS HTTP %s: %s", response.status_code, response.text)
        raise SmsSendError("SMS gönderilemedi.")

    result = response.json().get("sendSmsResult", {})
    error_code = str(result.get("ErrorCode", ""))
    if error_code != "0":
        detail = TURATEL_ERROR_MESSAGES.get(error_code, f"Bilinmeyen hata (kod: {error_code}).")
        logger.error("Turatel SMS hata kodu %s (%s): %s", error_code, phone_number, detail)
        raise SmsSendError(detail)
