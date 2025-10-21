import struct
from hashlib import sha256
from ecdsa.curves import NIST256p
from ecdsa.keys import VerifyingKey
from ecdsa.util import sigdecode_der

from ragger.bip import pack_derivation_path
from ragger.backend.interface import BackendInterface, RAPDU
from ragger.navigator.navigation_scenario import NavigateWithScenario

CLA: int = 0x80
INS_SIGN: int = 0x02
INS_GET_PUBLIC_KEY: int = 0x04
INS_GET_SIGNED_PUBLIC_KEY: int = 0x08
P1_LAST: int = 0x80
P1_MORE: int = 0x00
DEFAULT_PATH: str = "m/44'/888'/0'/0/0"
MAX_APDU_SIZE: int = 0xFF
SIGDER_LEN_OFFSET: int = 1
SIGNED_KEY_SIG_OFFSET: int = 65
PATH_LEN: int = 20


def check_tx_nist256(transaction: bytes, der_signature: bytes,
                     public_key: bytes) -> None:

    pk: VerifyingKey = VerifyingKey.from_string(public_key, NIST256p, sha256)

    assert pk.verify(signature=der_signature,
                     data=transaction,
                     hashfunc=sha256,
                     sigdecode=sigdecode_der) is True


def serialize(cla: int,
              ins: int,
              p1: int = 0,
              p2: int = 0,
              cdata: bytes = b"") -> bytes:
    header: bytes = struct.pack("BBBBB", cla, ins, p1, p2,
                                len(cdata))  # add Lc to APDU header

    return header + cdata


def get_public_key(backend: BackendInterface, bip44_path: str) -> bytes:
    packed = serialize(
        cla=CLA,
        ins=INS_GET_PUBLIC_KEY,
        p1=0x00,
        p2=0x00,
        cdata=pack_derivation_path(bip44_path)[1:])  # No length prefix

    return backend.exchange_raw(packed).data


def get_signed_public_key_and_validate(backend: BackendInterface,
                                       bip44_path: str) -> bytes:
    packed = serialize(
        cla=CLA,
        ins=INS_GET_SIGNED_PUBLIC_KEY,
        p1=0x00,
        p2=0x00,
        cdata=pack_derivation_path(bip44_path)[1:])  # No length prefix

    key_and_signature = backend.exchange_raw(packed).data

    # Extract key and its signature
    signed_key = key_and_signature[:SIGNED_KEY_SIG_OFFSET]
    signature_ = key_and_signature[SIGNED_KEY_SIG_OFFSET + 2:]

    # Validate key signature
    check_tx_nist256(signed_key, signature_, signed_key)

    return signed_key[:65]


def get_packed_path() -> bytes:
    return pack_derivation_path(DEFAULT_PATH)[1:]


def sign_tx(scenario_navigator: NavigateWithScenario, tx: bytes,
            do_navigate: bool) -> RAPDU:
    offset = 0
    backend = scenario_navigator.backend
    custom_text = "Hold to" if backend.device.touchable else "Accept"
    while offset != len(tx):
        if (len(tx) - offset) > MAX_APDU_SIZE:
            chunk = tx[offset:offset + MAX_APDU_SIZE]
        else:
            chunk = tx[offset:]
        if (offset + len(chunk)) == len(tx):
            with backend.exchange_async(CLA, INS_SIGN, P1_LAST, 0x00, chunk):
                if do_navigate:
                    scenario_navigator.review_approve(
                        custom_screen_text=custom_text)
                pass
            response = backend.last_async_response
        else:
            backend.exchange(CLA, INS_SIGN, P1_MORE, 0x00, chunk)
        offset += len(chunk)
    return response


def sign_and_validate(scenario_navigator: NavigateWithScenario,
                      tx: bytes) -> None:
    # Get public key
    backend = scenario_navigator.backend
    publicKey = get_public_key(backend, DEFAULT_PATH)[1:]
    # Sign Tx
    sigDer = sign_tx(scenario_navigator, tx, True)
    sigLen = sigDer.data[SIGDER_LEN_OFFSET]
    # Validate signature
    check_tx_nist256(tx[:-PATH_LEN], sigDer.data[:sigLen + 2], publicKey)
