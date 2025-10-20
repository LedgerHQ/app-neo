# Neo Application

## error codes

any response that doesn not end with `0x9000` is an error.
Some errors are standard errors from the APDU (Application Protocol Data Unit).
See [list](https://www.eftlab.com/knowledge-base/complete-list-of-apdu-responses)

All errors on NEO 1.1 start with 0x6D (because I read the spec wrong).

- `0x6D00` unknown command.
  (this is to spec, the rest are enoded as 'unknown command' `0x6D` but should be 'unknown parameter' `0x6B`)
- `0x6D01` error, unknown user interface screen, up button was pressed.
- `0x6D02` error, unknown user interface screen, down button was pressed.
- `0x6D03` buffer underflow in transaction parsing while skipping over bytes.
- `0x6D04` variable length byte array decoding error.
- `0x6D05` buffer underflow in transaction parsing while reading bytes.
- `0x6D06` transaction type decoding error.
- `0x6D07` transaction attribute usage type decoding error.
- `0x6D08` signing message too short, bip44 path unreadable.
- `0x6D09` public key message too short, bip44 path unreadable.
- `0x6D10` signed public key message too short, bip44 path unreadable.
- `0x6D11` base_x encoded string is too long for available encoding memory.
- `0x6D12` base_x encoded string is too long for available decoding memory.
- `0x6D14` base_x encoding error.

This will be fixed to use the correct codes (0x9210 No more storage available, 0x6B00 wrong parameter)
in 1.2 sometime in 2018.

## blue-app-neo CE

This is the community edition of the Ledger Nano S app for the NEO Cryptocoin.

Documentation on how it works is here:
[sequence diagrams](https://coranos.github.io/blue-app-neo/docs/index.html)

Run `make load` to build and load the application onto the device.

After installing and running the application, you can run `demo.py` to test signing several transactions over USB.

Each transaction should display correctly in the UI.
Use the buttons individually to scroll up and down to view the transaction details.
Either Sign or Deny the transaction by clicking both top buttons on the 'Sign Tx Now', 'Sign Tx' and 'Deny Tx' screens.
The only difference between 'Sign Tx Now' and 'Sign Tx' is their placement order in the screen list, both sign the transaction.

Note that in order to run `demo-GAS-NEO.py`, you must install the `fastecdsa` Python package:

```bash
pip install ecdsa
```

also install [GMP](https://gmplib.org/)

========

See [Ledger's documentation](https://developers.ledger.com/) to get started.

=======

## blue-app-neo

todo: key screen does not refresh, have to go in and out to see a refresh.
