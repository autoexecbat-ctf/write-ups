
room/v1/commands.protoroom.v1common/v1/common.proto"
InitRoomCommand"r
MoveCommand-
	direction (2.common.v1.Vec2R	direction4
aim_direction (2.common.v1.Vec2RaimDirection"B

AimCommand4
aim_direction (2.common.v1.Vec2RaimDirection"C
FireCommand4
aim_direction (2.common.v1.Vec2RaimDirection"
ReloadCommand"—
UseAbilityCommand

ability_id (	R	abilityId-
	direction (2.common.v1.Vec2R	direction4
aim_direction (2.common.v1.Vec2RaimDirection"h
SwapSlotsCommand)
slot_a (2.common.v1.SlotRefRslotA)
slot_b (2.common.v1.SlotRefRslotB"Q
SplitStackCommand&
slot (2.common.v1.SlotRefRslot
count (Rcount"`
MergeStacksCommand&
from (2.common.v1.SlotRefRfrom"
to (2.common.v1.SlotRefRto">
DiscardItemCommand(
item_instance_id (	RitemInstanceId"@
UseConsumableCommand(
item_instance_id (	RitemInstanceId"
ConfirmRunEndCommand"
FleeRunCommand";
InteractCommand(
interact_host_id (	RinteractHostId"8
DescendFloorCommand!
target_floor (RtargetFloor"O
BuyAttributeRankCommand4
	attribute (2.common.v1.AttributeIdR	attribute"Z
SellItemCommand
slot (Rslot
quantity (Rquantity
shop_id (	RshopId"”
BuyItemCommand&
item_listing_id (	RitemListingId
quantity (Rquantity%
expected_price (RexpectedPrice
shop_id (	RshopId"T
RefreshShopCommand%
expected_price (RexpectedPrice
shop_id (	RshopId"„
EnchantItemCommand(
item_instance_id (	RitemInstanceId%
enchantment_id (	RenchantmentId

slot_index (R	slotIndex"
ClaimStarterPistolCommand"K
UnlockSkillNodeCommand
node_id (	RnodeId
variant (Rvariant"K
SetSkillVariantCommand
node_id (	RnodeId
variant (Rvariant"2
UpgradeSkillNodeCommand
node_id (	RnodeId"
RespecSkillsCommand"e
UpgradeItemCommand(
item_instance_id (	RitemInstanceId%
expected_level (RexpectedLevel"<
HeartbeatEchoCommand$
server_time_ms (RserverTimeMs"0
StartCraftCommand
	recipe_id (	RrecipeId",
CollectCraftCommand
job_id (	RjobId"
EnterKonamiCodeCommandBo
com.room.v1BCommandsProtoP¢RXXªCTFGame.Networking.Wire.ProtoÊRoom\V1âRoom\V1\GPBMetadataêRoom::V1bproto3