/*******************************************************************************
 *   Ledger Blue
 *   (c) 2016 Ledger
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 ********************************************************************************/

#include "os.h"
#include "cx.h"
#include <stdbool.h>
#include "os_io_seproxyhal.h"
#include "crypto_helpers.h"
#include "parser.h"
#include "status_words.h"
#include "io.h"
#include "ui.h"
#include "neo.h"
#ifdef HAVE_BAGL
#include "bagl.h"
#endif

/** start of the buffer, reject any transmission that doesn't start with this, as it's invalid. */
#define CLA 0x80

/** #### instructions start #### **/
/** instruction to sign transaction and send back the signature. */
#define INS_SIGN 0x02

/** instruction to send back the public key. */
#define INS_GET_PUBLIC_KEY 0x04

/** instruction to send back the public key, and a signature of the private key signing the public
 * key. */
#define INS_GET_SIGNED_PUBLIC_KEY 0x08
/** #### instructions end #### */

int apdu_dispatcher(const command_t *cmd) {
    LEDGER_ASSERT(cmd != NULL, "NULL cmd");
    unsigned int tx = 0;
    unsigned char *in = NULL;
    uint8_t raw_pubkey[65] = {0};
    unsigned int bip44_path[BIP44_PATH_LEN] = {0};
    unsigned char result[32] = {0};
    uint32_t i = 0;
    size_t sig_len = 0;
    cx_ecfp_public_key_t publicKey;
    cx_ecfp_private_key_t privateKey;
    cx_sha256_t pubKeyHash;
    int ret = -1;

    if (cmd->cla != CLA) {
        return io_send_sw(SWO_INVALID_CLA);
    }

    // check the second byte (0x01) for the instruction.
    switch (cmd->ins) {
        // we're getting a transaction to sign, in parts.
        case INS_SIGN:
            // check the third byte (0x02) for the instruction subtype.
            if ((cmd->p1 != P1_MORE) && (cmd->p1 != P1_LAST)) {
                hashTainted = 1;
                ret = io_send_sw(SWO_INCORRECT_P1_P2);
                break;
            }

            // if this is the first transaction part, reset the hash and all the other
            // temporary variables.
            if (hashTainted) {
                cx_sha256_init(&tx_hash);
                hashTainted = 0;
                raw_tx_ix = 0;
                raw_tx_len = 0;
            }

            // move the contents of the buffer into raw_tx, and update raw_tx_ix to the
            // end of the buffer, to be ready for the next part of the tx.
            if (raw_tx_ix + cmd->lc > MAX_TX_RAW_LENGTH) {
                hashTainted = 1;
                ret = io_send_sw(0x6D08);
                break;
            }
            memmove(raw_tx + raw_tx_ix, cmd->data, cmd->lc);
            raw_tx_ix += cmd->lc;

            // set the screen to be the first screen.
            curr_scr_ix = 0;

            // if this is the last part of the transaction, parse the transaction into
            // human readable text, and display it.
            if (cmd->p1 == P1_LAST) {
                raw_tx_len = raw_tx_ix;
                raw_tx_ix = 0;

                // parse the transaction into human readable text.
                ret = display_tx_desc();
                if (ret != 0) {
                    break;
                }

                // display the UI, starting at the top screen which is "Sign Tx Now".
                ui_top_sign();
            }

            // if this is not the last part of the transaction, do not display the UI,
            // and approve the partial transaction. this adds the TX to the hash.
            if (cmd->p1 == P1_MORE) {
                ret = sign_tx_and_send_response();
            } else {
                ret = 0;
            }
            break;

            // we're asked for the public key.
        case INS_GET_PUBLIC_KEY:
            if (cmd->lc < BIP44_BYTE_LENGTH) {
                hashTainted = 1;
                ret = io_send_sw(0x6D09);
                break;
            }

            /** BIP44 path, used to derive the private key from the mnemonic by calling
             * os_perso_derive_node_bip32. */
            in = cmd->data;
            for (i = 0; i < BIP44_PATH_LEN; i++) {
                bip44_path[i] = U4BE(in, 0);
                in += 4;
            }

            if (bip32_derive_get_pubkey_256(CX_CURVE_256R1,
                                            bip44_path,
                                            BIP44_PATH_LEN,
                                            raw_pubkey,
                                            NULL,
                                            CX_SHA512) != CX_OK) {
                ret = io_send_sw(0x6D00);
                break;
            }

            // push the public key onto the response buffer.
            memmove(G_io_apdu_buffer, raw_pubkey, sizeof(raw_pubkey));
            ret = display_public_key(raw_pubkey);
            if (ret != 0) {
                break;
            }
            ret = io_send_response_pointer(G_io_apdu_buffer, sizeof(raw_pubkey), SWO_SUCCESS);
            break;

            // we're asking for the signed public key.
        case INS_GET_SIGNED_PUBLIC_KEY:
            if (cmd->lc < BIP44_BYTE_LENGTH) {
                hashTainted = 1;
                ret = io_send_sw(0x6D10);
                break;
            }

            /** BIP44 path, used to derive the private key from the mnemonic by calling
             * os_perso_derive_node_bip32. */
            in = cmd->data;
            for (i = 0; i < BIP44_PATH_LEN; i++) {
                bip44_path[i] = U4BE(in, 0);
                in += 4;
            }

            if (bip32_derive_init_privkey_256(CX_CURVE_256R1,
                                              bip44_path,
                                              BIP44_PATH_LEN,
                                              &privateKey,
                                              NULL) != CX_OK) {
                ret = io_send_sw(0x6D00);
                break;
            }

            // generate the public key.
            CX_ASSERT(cx_ecdsa_init_public_key(CX_CURVE_256R1, NULL, 0, &publicKey));
            CX_ASSERT(cx_ecfp_generate_pair_no_throw(CX_CURVE_256R1, &publicKey, &privateKey, 1));

            // push the public key onto the response buffer.
            memmove(G_io_apdu_buffer, publicKey.W, sizeof(publicKey.W));
            tx = sizeof(publicKey.W);

            ret = display_public_key(publicKey.W);
            if (ret != 0) {
                break;
            }
            G_io_apdu_buffer[tx++] = 0xFF;
            G_io_apdu_buffer[tx++] = 0xFF;

            cx_sha256_init(&pubKeyHash);
            CX_ASSERT(cx_hash_no_throw(&pubKeyHash.header,
                                       CX_LAST,
                                       publicKey.W,
                                       sizeof(publicKey.W),
                                       result,
                                       sizeof(result)));
            sig_len = sizeof(G_io_apdu_buffer) - tx;
            if (cx_ecdsa_sign_no_throw((void *) &privateKey,
                                       CX_RND_RFC6979 | CX_LAST,
                                       CX_SHA256,
                                       result,
                                       sizeof(result),
                                       G_io_apdu_buffer + tx,
                                       &sig_len,
                                       NULL) != CX_OK) {
                ret = io_send_sw(0x6D00);
                break;
            }

            tx += sig_len;
            ret = io_send_response_pointer(G_io_apdu_buffer, tx, SWO_SUCCESS);
            break;

        case 0xFF:  // return to dashboard
            ret = 0;
            break;

            // we're asked to do an unknown command
        default:
            // return an error.
            hashTainted = 1;
            ret = io_send_sw(SWO_INVALID_INS);
            break;
    }
    return ret;
}

/** main loop. */
void app_main(void) {
    // Length of APDU command received in G_io_apdu_buffer
    int input_len = 0;
    // Structured APDU command
    command_t cmd;

    curr_scr_ix = 0;
    max_scr_ix = 0;
    raw_tx_ix = 0;
    hashTainted = 1;

    io_init();

    // init the public key display to "no public key".
    display_no_public_key();

    // show idle screen.
    ui_idle();

    for (;;) {
        // Receive command bytes in G_io_apdu_buffer
        if ((input_len = io_recv_command()) < 0) {
            PRINTF("=> io_recv_command failure\n");
            return;
        }

        // Parse APDU command from G_io_apdu_buffer
        if (!apdu_parser(&cmd, G_io_apdu_buffer, input_len)) {
            PRINTF("=> /!\\ BAD LENGTH: %.*H\n", input_len, G_io_apdu_buffer);
            io_send_sw(SWO_WRONG_DATA_LENGTH);
            continue;
        }

        PRINTF("=> CLA=%02X | INS=%02X | P1=%02X | P2=%02X | Lc=%02X | CData=%.*H\n",
               cmd.cla,
               cmd.ins,
               cmd.p1,
               cmd.p2,
               cmd.lc,
               cmd.lc,
               cmd.data);

        // Dispatch structured APDU command to handler
        if (apdu_dispatcher(&cmd) < 0) {
            PRINTF("=> apdu_dispatcher failure\n");
            return;
        }
    }
}
