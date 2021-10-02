base_url = "https://aa-sandbox.setu.co"
setu_rahasya_url = "https://rahasya.setu.co"

headers = {
    "client_api_key" :"30144173-ab0f-427c-a6b7-935296062686",
    "x-jws-signature" : "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..k67GKH_EnDdvR8yr8Va9teMXJQbRLmP9GMdwT7DHIjPBesLbMBXH_a6bp6QL1d7h6Y0VtcBWScysA9CpgyK23dY1GE8DTnBXGHiiCCSpkRxgPFDSDbfkYHemvl2j4Xpzry1RfMmQOMaWiwROkfGuIEl0k1xqt83_-SyiTt4F_-TPKiOShniLSbJYYUV5R1sy6ZswtXpzh57lpAPXWH7OotYHXaf-9q1T4aT8esGJg_H3Wh3YxPG7TRUzYNBTRfrERwuAS2p2uybn5R4VhobVRCpSFLsf7qAU6Awhc3cZj8qEoXQfIXGBsU7hDtYcpCWu9DkeWSqLIIxB3OYTf31pkA"
    }

Decrpyt_Body = {
    "base64Data": "string",
    "base64RemoteNonce": "string",
    "base64YourNonce": "string",
    "ourPrivateKey": "string",
    "remoteKeyMaterial": {
        "DHPublicKey": {
            "KeyValue": "string",
            "Parameters": "string",
            "expiry": "string"
        },
        "Nonce": "string",
        "cryptoAlg": "string",
        "curve": "string",
        "params": "string"
    }
}

consent_obj = {
    "ver": "1.0",
    "timestamp": "2021-09-25T06:59:19.850Z",
    "txnid": "f489b345-3bb0-4064-9496-e23d9898k74z",
    "ConsentDetail": {
        "consentStart": "2021-09-25T06:59:19.850Z",
        "consentExpiry": "2021-12-31T11:39:57.153Z",
        "consentMode": "VIEW",
        "fetchType": "ONETIME",
        "consentTypes": [
            "TRANSACTIONS",
            "PROFILE",
            "SUMMARY"
        ],
        "fiTypes": [
            "DEPOSIT",
            "EQUITIES"
        ],
        "DataConsumer": {
            "id": "FIU"
        },
        "Customer": {
            "id": "8169840285@setu-aa"
        },
        "Purpose": {
            "code": "101",
            "refUri": "https://api.rebit.org.in/aa/purpose/101.xml",
            "text": "Wealth management service",
            "Category": {
                "type": "string"
            }
        },
        "FIDataRange": {
            "from": "2019-04-11T11:39:57.153Z",
            "to": "2021-10-17T14:25:33.440Z"
        },
        "DataLife": {
            "unit": "MONTH",
            "value": 0
        },
        "Frequency": {
            "unit": "MONTH",
            "value": 1000
        },
        "DataFilter": [
            {
                "type": "TRANSACTIONAMOUNT",
                "operator": ">=",
                "value": "10"
            }
        ]
    }
}

Request_FI_Data = {
    "ver": "1.0",
    "timestamp": "2021-09-27T19:08:43.830Z",
    "txnid": "{{txn_id}}",
    "FIDataRange": {
        "from": "2021-01-11T11:39:57.153Z",
        "to": "2021-06-17T14:25:33.440Z"
    },
    "Consent": {
        "id": "{{consent_id}}",
        "digitalSignature": "{{digital_signature}}"
    },
    "KeyMaterial": {
        "cryptoAlg": "ECDH",
        "curve": "Curve25519",
        "params": "",
        "DHPublicKey": {
            "expiry": "2021-09-28T19:03:25.866Z",
            "Parameters": "",
            "KeyValue": "-----BEGIN PUBLIC KEY-----MIIBMTCB6gYHKoZIzj0CATCB3gIBATArBgcqhkjOPQEBAiB/////////////////////////////////////////7TBEBCAqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqYSRShRAQge0Je0Je0Je0Je0Je0Je0Je0Je0Je0Je0JgtenHcQyGQEQQQqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq0kWiCuGaG4oIa04B7dLHdI0UySPU1+bXxhsinpxaJ+ztPZAiAQAAAAAAAAAAAAAAAAAAAAFN753qL3nNZYEmMaXPXT7QIBCANCAARdsn2VUONjG9ZdtR625iUIJKY7bAkdnQ2F5oh4yei1hmLLKCE+cO7gAL8IEtd32q8MH3SjxsggQuZI9RLDRNQo-----END PUBLIC KEY-----"
        },
        "Nonce": "NTE3MGZlMDliNmFiNGFlMjFmNWU5Y2Y2NzliOGU1NTc="
    }
}