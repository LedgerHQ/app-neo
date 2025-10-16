/*
 * MIT License, see root folder for full license.
 */

#include "ui.h"
#include "glyphs.h"
#include "crypto_helpers.h"

/** default font */
#define DEFAULT_FONT BAGL_FONT_OPEN_SANS_EXTRABOLD_11px | BAGL_FONT_ALIGNMENT_CENTER

/** text description font. */
#define TX_DESC_FONT BAGL_FONT_OPEN_SANS_REGULAR_11px | BAGL_FONT_ALIGNMENT_CENTER

#define NO_INFO "Info not available"

/** the timer */
int exit_timer;

/** display for the timer */
char timer_desc[MAX_TIMER_TEXT_WIDTH];

/** UI state enum */
enum UI_STATE uiState;

/** UI state flag */
#if defined(TARGET_NANOX) || defined(TARGET_NANOS2)
#include "ux.h"
ux_state_t G_ux;
bolos_ux_params_t G_ux_params;
#elif defined(TARGET_STAX) || defined(TARGET_FLEX)
#include "nbgl_page.h"
#include "nbgl_use_case.h"
#include "ux.h"

ux_state_t ux;
ux_state_t G_ux;
bolos_ux_params_t G_ux_params;

#endif

/** notification to restart the hash */
unsigned char hashTainted;

/** notification to refresh the view, if we are displaying the public key */
unsigned char publicKeyNeedsRefresh;

/** the hash. */
cx_sha256_t tx_hash;

/** index of the current screen. */
unsigned int curr_scr_ix;

/** max index for all screens. */
unsigned int max_scr_ix;

/** raw transaction data. */
unsigned char raw_tx[MAX_TX_RAW_LENGTH];

/** current index into raw transaction. */
unsigned int raw_tx_ix;

/** current length of raw transaction. */
unsigned int raw_tx_len;

/** all text descriptions. */
char tx_desc[MAX_TX_TEXT_SCREENS][MAX_TX_TEXT_LINES][MAX_TX_TEXT_WIDTH];

/** currently displayed text description. */
char curr_tx_desc[MAX_TX_TEXT_LINES][MAX_TX_TEXT_WIDTH];

/** currently displayed address */
char address58[MAX_TX_TEXT_LINES][MAX_TX_TEXT_WIDTH];

/** UI was touched indicating the user wants to deny te signature request */
static const void *reject_tx_and_send_response(void);

/** sets the tx_desc variables to no information */
static void clear_tx_desc(void);

////////////////////////////////////  NANO X //////////////////////////////////////////////////
#if defined(TARGET_NANOX) || defined(TARGET_NANOS2)

UX_STEP_NOCB(ux_confirm_single_flow_1_step, pnn, {&C_icon_eye, "Review", "Transaction"});
UX_STEP_NOCB(ux_confirm_single_flow_2_step, bn, {"Type", tx_desc[0][1]});
UX_STEP_NOCB(ux_confirm_single_flow_3_step,
             bnn,
             {
                 "Amount",
                 tx_desc[1][0],
                 tx_desc[1][1],
             });
UX_STEP_NOCB(ux_confirm_single_flow_4_step,
             bnnn,
             {"Destination Address", tx_desc[2][0], tx_desc[2][1], tx_desc[2][2]});
UX_STEP_VALID(ux_confirm_single_flow_5_step,
              pb,
              sign_tx_and_send_response(),
              {
                  &C_icon_validate_14,
                  "Accept",
              });
UX_STEP_VALID(ux_confirm_single_flow_6_step,
              pb,
              reject_tx_and_send_response(),
              {
                  &C_icon_crossmark,
                  "Reject",
              });
UX_FLOW(ux_confirm_single_flow,
        &ux_confirm_single_flow_1_step,
        &ux_confirm_single_flow_2_step,
        &ux_confirm_single_flow_3_step,
        &ux_confirm_single_flow_4_step,
        &ux_confirm_single_flow_5_step,
        &ux_confirm_single_flow_6_step);

UX_STEP_NOCB(ux_display_public_flow_step,
             bnnn,
             {"Address", address58[0], address58[1], address58[2]});
UX_STEP_VALID(ux_display_public_go_back_step,
              pb,
              ui_idle(),
              {
                  &C_icon_back,
                  "Back",
              });

UX_FLOW(ux_display_public_flow, &ux_display_public_flow_step, &ux_display_public_go_back_step);

void display_account_address() {
    if (G_ux.stack_count == 0) {
        ux_stack_push();
    }
    ux_flow_init(0, ux_display_public_flow, NULL);
}

UX_STEP_NOCB(ux_idle_flow_1_step,
             nn,
             {
                 "Application",
                 "is ready",
             });
UX_STEP_VALID(ux_idle_flow_2_step,
              pbb,
              display_account_address(),
              {&C_icon_eye, "Display", "Account"});
UX_STEP_NOCB(ux_idle_flow_3_step,
             bn,
             {
                 "Version",
                 APPVERSION,
             });
UX_STEP_VALID(ux_idle_flow_4_step,
              pb,
              os_sched_exit(-1),
              {
                  &C_icon_dashboard,
                  "Quit",
              });

UX_FLOW(ux_idle_flow,
        &ux_idle_flow_1_step,
        &ux_idle_flow_2_step,
        &ux_idle_flow_3_step,
        &ux_idle_flow_4_step);

#endif
////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////  STAX //////////////////////////////////////////////////
#if defined(TARGET_STAX) || defined(TARGET_FLEX)

#define NB_INFO_FIELDS 2
static const char *const infoTypes[] = {"Version", "Developer"};
static const char *const infoContents[] = {APPVERSION, "Ledger"};

static nbgl_contentTagValue_t fields[3];
static nbgl_contentTagValueList_t pairList;

static void reviewChoice(bool confirm);
static void reviewStart(void);
static void pageCallback(int token, uint8_t index);

static nbgl_homeAction_t homeAction;
static nbgl_contentInfoList_t infoList;

void onQuitCallback(void) {
    os_sched_exit(-1);
}

static void displayAddress(void) {
    nbgl_pageInfoDescription_t info = {.centeredInfo.icon = &C_wallet_64px,
                                       .centeredInfo.text1 = "Address",
                                       .centeredInfo.text2 = address58[0],
                                       .centeredInfo.style = LARGE_CASE_INFO,
                                       .centeredInfo.offsetY = -16,
                                       .footerText = NULL,
                                       .bottomButtonStyle = QUIT_ICON,
                                       .tapActionText = NULL,
                                       .tuneId = TUNE_TAP_CASUAL,
                                       .bottomButtonsToken = 0};

    nbgl_pageDrawInfo(&pageCallback, NULL, &info);
}

static void pageCallback(int token, uint8_t index) {
    UNUSED(index);
    if (token == 0) {
        ui_idle();
    }
}

static void reviewChoice(bool confirm) {
    if (confirm) {
        sign_tx_and_send_response();
        nbgl_useCaseReviewStatus(STATUS_TYPE_TRANSACTION_SIGNED, ui_idle);
    } else {
        reject_tx_and_send_response();
        nbgl_useCaseReviewStatus(STATUS_TYPE_TRANSACTION_REJECTED, ui_idle);
    }
}

static void reviewStart(void) {
    memset(&fields, 0, sizeof(fields));

    pairList.pairs = fields;
    pairList.nbPairs = 3;

    fields[0].item = "Type";
    fields[0].value = tx_desc[0][1];
    fields[1].item = "Amount";
    fields[1].value = tx_desc[1][2];
    fields[2].item = "Destination Address";
    fields[2].value = tx_desc[2][0];

    nbgl_useCaseReview(TYPE_TRANSACTION,
                       &pairList,
                       &C_icon_64px,
                       "Review transaction",
                       NULL,
                       "Sign transaction",
                       reviewChoice);
}
#endif
////////////////////////////////////////////////////////////////////////////////////////////////

/** processes the transaction approval. the UI is only displayed when all of the TX has been sent
 * over for signing. */
const void *sign_tx_and_send_response(void) {
    unsigned int tx = 0;

    if (G_io_apdu_buffer[2] == P1_LAST) {
        unsigned int raw_tx_len_except_bip44 = raw_tx_len - BIP44_BYTE_LENGTH;
        // Update and sign the hash
        CX_ASSERT(cx_hash_no_throw(&tx_hash.header, 0, raw_tx, raw_tx_len_except_bip44, NULL, 0));

        unsigned char *bip44_in = raw_tx + raw_tx_len_except_bip44;

        /** BIP44 path, used to derive the private key from the mnemonic by calling
         * os_perso_derive_node_bip32. */
        unsigned int bip44_path[BIP44_PATH_LEN];
        uint32_t i;
        for (i = 0; i < BIP44_PATH_LEN; i++) {
            bip44_path[i] =
                (bip44_in[0] << 24) | (bip44_in[1] << 16) | (bip44_in[2] << 8) | (bip44_in[3]);
            bip44_in += 4;
        }

        cx_ecfp_private_key_t privateKey;
        if (bip32_derive_init_privkey_256(CX_CURVE_256R1,
                                          bip44_path,
                                          BIP44_PATH_LEN,
                                          &privateKey,
                                          NULL) != CX_OK) {
            THROW(0x6D00);
        }

        // Hash is finalized, send back the signature
        unsigned char result[32];

        CX_ASSERT(cx_hash_no_throw(&tx_hash.header, CX_LAST, G_io_apdu_buffer, 0, result, 32));

        size_t sig_len = sizeof(G_io_apdu_buffer);
        if (cx_ecdsa_sign_no_throw((void *) &privateKey,
                                   CX_RND_RFC6979 | CX_LAST,
                                   CX_SHA256,
                                   result,
                                   sizeof(result),
                                   G_io_apdu_buffer,
                                   &sig_len,
                                   NULL) != CX_OK) {
            THROW(0x6D00);
        }
        tx = sig_len;

        // G_io_apdu_buffer[0] &= 0xF0; // discard the parity information
        hashTainted = 1;
        clear_tx_desc();
        raw_tx_ix = 0;
        raw_tx_len = 0;

        // add hash to the response, so we can see where the bug is.
        G_io_apdu_buffer[tx++] = 0xFF;
        G_io_apdu_buffer[tx++] = 0xFF;
        for (int ix = 0; ix < 32; ix++) {
            G_io_apdu_buffer[tx++] = result[ix];
        }
    }
    G_io_apdu_buffer[tx++] = 0x90;
    G_io_apdu_buffer[tx++] = 0x00;
    // Send back the response, do not restart the event loop
    io_exchange(CHANNEL_APDU | IO_RETURN_AFTER_TX, tx);
    // Display back the original UX
#ifdef HAVE_BAGL
    ui_idle();
#endif
    return 0;  // do not redraw the widget
}

/** deny signing. */
static const void *reject_tx_and_send_response(void) {
    hashTainted = 1;
    clear_tx_desc();
    raw_tx_ix = 0;
    raw_tx_len = 0;
    G_io_apdu_buffer[0] = 0x69;
    G_io_apdu_buffer[1] = 0x85;
    // Send back the response, do not restart the event loop
    io_exchange(CHANNEL_APDU | IO_RETURN_AFTER_TX, 2);
    // Display back the original UX
#ifdef HAVE_BAGL
    ui_idle();
#endif
    return 0;  // do not redraw the widget
}

/** show the idle screen. */
void ui_idle(void) {
    uiState = UI_IDLE;

#if defined(TARGET_NANOX) || defined(TARGET_NANOS2)
    // reserve a display stack slot if none yet
    if (G_ux.stack_count == 0) {
        ux_stack_push();
    }
    ux_flow_init(0, ux_idle_flow, NULL);
#elif defined(TARGET_STAX) || defined(TARGET_FLEX)
    infoList.nbInfos = NB_INFO_FIELDS;
    infoList.infoTypes = infoTypes;
    infoList.infoContents = infoContents;

    homeAction.text = "Display account";
    homeAction.icon = NULL;
    homeAction.callback = displayAddress;

    nbgl_useCaseHomeAndSettings(APPNAME,
                                &C_icon_64px,
                                NULL,
                                INIT_HOME_PAGE,
                                NULL,
                                &infoList,
                                &homeAction,
                                onQuitCallback);
#endif  // #if TARGET_ID
}

/** show the top "Sign Transaction" screen. */
void ui_top_sign(void) {
    uiState = UI_TOP_SIGN;

#if defined(TARGET_NANOX) || defined(TARGET_NANOS2)
    // reserve a display stack slot if none yet
    if (G_ux.stack_count == 0) {
        ux_stack_push();
    }
    ux_flow_init(0, ux_confirm_single_flow, NULL);
#elif defined(TARGET_STAX) || defined(TARGET_FLEX)
    reviewStart();
#endif  // #if TARGET_ID
}

/** returns the length of the transaction in the buffer. */
unsigned int get_apdu_buffer_length() {
    unsigned int len0 = G_io_apdu_buffer[APDU_BODY_LENGTH_OFFSET];
    return len0;
}

/** sets the tx_desc variables to no information */
static void clear_tx_desc(void) {
    for (uint8_t i = 0; i < MAX_TX_TEXT_SCREENS; i++) {
        for (uint8_t j = 0; j < MAX_TX_TEXT_LINES; j++) {
            tx_desc[i][j][0] = '\0';
            tx_desc[i][j][MAX_TX_TEXT_WIDTH - 1] = '\0';
        }
    }

    strncpy(tx_desc[1][0], NO_INFO, sizeof(NO_INFO));
    strncpy(tx_desc[2][0], NO_INFO, sizeof(NO_INFO));
}
