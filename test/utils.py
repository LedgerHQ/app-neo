import struct
from pathlib import Path
from hashlib import sha256
from inspect import currentframe
from ecdsa.curves import NIST256p
from ecdsa.keys import VerifyingKey
from ecdsa.util import sigdecode_der
from ragger.bip import pack_derivation_path
from ragger.navigator import NavInsID

CLA: int = 0x80
INS_SIGN: int = 0x02
INS_GET_PUBLIC_KEY: int = 0x04
P1_LAST: int = 0x80
P1_MORE: int = 0x00
DEFAULT_PATH: str = "m/44'/888'/0'/0/0"
MAX_APDU_SIZE: int = 0xFF
SIGDER_LEN_OFFSET: int = 1
PATH_LEN: int = 20

ROOT_SCREENSHOT_PATH = Path(__file__).parent.resolve()


def check_tx_nist256(transaction, der_signature, public_key):

    pk: VerifyingKey = VerifyingKey.from_string(public_key,
                                                curve=NIST256p,
                                                hashfunc=sha256)

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


def get_public_key(backend, bip44_path: str) -> bytes:
    packed = serialize(
        cla=CLA,
        ins=INS_GET_PUBLIC_KEY,
        p1=0x00,
        p2=0x00,
        cdata=pack_derivation_path(bip44_path)[1:])  # No length prefix

    return backend.exchange_raw(packed).data


def get_packed_path():
    return pack_derivation_path(DEFAULT_PATH)[1:]


def navigate(firmware, navigator, snappath: Path = None):
    if firmware.device == "stax":
        navigator.navigate_until_text_and_compare(
            # Use custom touch coordinates to account for warning approve
            # button position.
            NavInsID.USE_CASE_REVIEW_TAP,
            [
                NavInsID.USE_CASE_REVIEW_CONFIRM,
                NavInsID.USE_CASE_STATUS_DISMISS, NavInsID.WAIT_FOR_HOME_SCREEN
            ],
            "Hold to",
            ROOT_SCREENSHOT_PATH,
            snappath)
    else:
        navigator.navigate_until_text_and_compare(NavInsID.RIGHT_CLICK,
                                                  [NavInsID.BOTH_CLICK],
                                                  "Accept",
                                                  ROOT_SCREENSHOT_PATH,
                                                  snappath)


def sign_tx(backend, firmware, navigator, tx, path, do_navigate):
    offset = 0
    while offset != len(tx):
        if (len(tx) - offset) > MAX_APDU_SIZE:
            chunk = tx[offset:offset + MAX_APDU_SIZE]
        else:
            chunk = tx[offset:]
        if (offset + len(chunk)) == len(tx):
            with backend.exchange_async(CLA, INS_SIGN, P1_LAST, 0x00, chunk):
                if do_navigate:
                    navigate(firmware, navigator, path)
                pass
            response = backend.last_async_response
        else:
            backend.exchange(CLA, INS_SIGN, P1_MORE, 0x00, chunk)
        offset += len(chunk)
    return response


def sign_and_validate(backend, firmware, navigator, tx):
    path = Path(currentframe().f_back.f_code.co_name)
    # Get public key
    publicKey = get_public_key(backend, DEFAULT_PATH)[1:]
    # Sign Tx
    sigDer = sign_tx(backend, firmware, navigator, tx, path, True)
    sigLen = sigDer.data[SIGDER_LEN_OFFSET]
    # Validate signature
    check_tx_nist256(tx[:-PATH_LEN], sigDer.data[:sigLen + 2], publicKey)
