
room/v1/vault.protoroom.v1"ç
VaultItemStack
item_id (	RitemId
count (Rcount#
upgrade_level (RupgradeLevel'
enchantment_ids (	RenchantmentIds"i
VaultStartCommand!
operation_id (	RoperationId1
deposit (2.room.v1.VaultItemStackRdeposit"R
VaultPlaceCommand!
operation_id (	RoperationId
x (Rx
y (Ry"S
VaultKnockCommand!
operation_id (	RoperationId
	ledger_id (	RledgerId"û
VaultPassCommand!
operation_id (	RoperationId
	ledger_id (	RledgerId
nonce (	Rnonce
bearer (	Rbearer
	signature (	R	signature"I
VaultRackCommand!
operation_id (	RoperationId
page (Rpage"4
VaultBagCommand!
operation_id (	RoperationId"T
VaultUnlockCommand!
operation_id (	RoperationId
	ledger_id (	RledgerId"U
VaultCollectCommand!
operation_id (	RoperationId
	ledger_id (	RledgerId"'
	VaultCell
x (Rx
y (Ry"M
	VaultText
en (	Ren
zh_hant (	RzhHant
zh_hans (	RzhHans"t
VaultAchievementText&
name (2.room.v1.VaultTextRname4
description (2.room.v1.VaultTextRdescription"∫
VaultLedgerSummary
	ledger_id (	RledgerId
	sealed_at (	RsealedAt
	locked_by (	RlockedBy1
deposit (2.room.v1.VaultItemStackRdeposit
contents (	Rcontents"Î
VaultReadyEvent
stage (Rstage

forge_code (	R	forgeCode

board_size (R	boardSize
	threshold (R	threshold5
ledgers (2.room.v1.VaultLedgerSummaryRledgers
forging (	Rforging$
start_fee_gold (RstartFeeGold#
fee_available (RfeeAvailable"
retry_after_s	 (RretryAfterS&
unlock_fee_gold
 (RunlockFeeGold" 
VaultRequestRejectedEvent!
operation_id (	RoperationId

error_code (	R	errorCode"
retry_after_s (RretryAfterS$
start_fee_gold (RstartFeeGold!
gold_balance (RgoldBalance"À
VaultStateEvent!
operation_id (	RoperationId
game_id (	RgameId
stage (Rstage
board (	Rboard
to_move (	RtoMove,
blocked (2.room.v1.VaultCellRblocked/
	last_move (2.room.v1.VaultCellRlastMove

move_count (R	moveCount
outcome	 (	Routcome%
achievement_id
 (	RachievementId"
fee_paid_gold (RfeePaidGold!
gold_balance (RgoldBalance1
deposit (2.room.v1.VaultItemStackRdeposit"Ã
VaultSealedEvent
game_id (	RgameId
	ledger_id (	RledgerId
n1 (	Rn1
n2 (	Rn2
e (Re
game_record (	R
gameRecord
seal_sig (	RsealSig
counter (Rcounter"G
VaultIssuedPass
bearer (	Rbearer
	signature (	R	signature"·
VaultNonceEvent!
operation_id (	RoperationId
	ledger_id (	RledgerId
nonce (	Rnonce
	nonce_sig (	RnonceSig 
expires_in_s (R
expiresInS9
issued_pass (2.room.v1.VaultIssuedPassR
issuedPass"Ó
VaultDoorEvent!
operation_id (	RoperationId
	ledger_id (	RledgerId
result (	Rresult
owner_id (	RownerId
n1 (	Rn1
n2 (	Rn2
e (Re
game_record (	R
gameRecord
seal_sig	 (	RsealSig
counter
 (Rcounter
	locked_by (	RlockedBy,
message (2.room.v1.VaultTextRmessage%
achievement_id (	RachievementIdH
achievement_text (2.room.v1.VaultAchievementTextRachievementTextJRnonceR	nonce_sigRbearerR	signature"„
VaultRackBox
	ledger_id (	RledgerId
owner_id (	RownerId
	sealed_at (	RsealedAt
	locked_by (	RlockedBy
mine (Rmine1
deposit (2.room.v1.VaultItemStackRdeposit
contents (	Rcontents"ß
VaultRackEvent!
operation_id (	RoperationId
page (Rpage
	page_size (RpageSize
total (Rtotal+
boxes (2.room.v1.VaultRackBoxRboxes"©
VaultBagStack
item_id (	RitemId
count (Rcount
	max_stack (RmaxStack#
upgrade_level (RupgradeLevel'
enchantment_ids (	RenchantmentIds"í
VaultBagEvent!
operation_id (	RoperationId
	available (R	available
gold (Rgold,
items (2.room.v1.VaultBagStackRitems"˚
VaultUnlockEvent!
operation_id (	RoperationId
	ledger_id (	RledgerId
nonce (	Rnonce
	nonce_sig (	RnonceSig
bearer (	Rbearer
	signature (	R	signature
	gold_paid (RgoldPaid!
gold_balance (RgoldBalance"û
VaultBoxEvent!
operation_id (	RoperationId
	ledger_id (	RledgerId1
deposit (2.room.v1.VaultItemStackRdeposit
contents (	RcontentsBl
com.room.v1B
VaultProtoP¢RXX™CTFGame.Networking.Wire.Proto Room\V1‚Room\V1\GPBMetadataÍRoom::V1bproto3