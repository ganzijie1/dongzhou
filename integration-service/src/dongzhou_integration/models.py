from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class GuestSessionRequest(StrictModel):
    installation_id: UUID = Field(strict=False)


class SaveWriteRequest(StrictModel):
    expected_version: int = Field(ge=1)
    payload: dict[str, Any]


class GameClockQuery(StrictModel):
    server_id: str = Field(alias="serverID", min_length=1, max_length=128)


class AinpcLoginReadyRequest(StrictModel):
    game_server_id: str = Field(alias="gameServerId", min_length=1, max_length=128)
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    login_request_id: str = Field(alias="loginRequestId", min_length=1, max_length=256)
    instance_id: int | None = Field(default=None, alias="instanceId", ge=0)
    instance_count: int | None = Field(default=None, alias="instanceCount", ge=1)
    startup_id: str | None = Field(default=None, alias="startupId", min_length=1, max_length=128)


class AinpcAliveQuery(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)


class AinpcTaskStatusQuery(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    query_task_status: Literal["TASK_STATUS_RUNNING"] = Field(alias="queryTaskStatus")


class AinpcBehaviorParamsValidationRequest(StrictModel):
    tree_name: str = Field(alias="treeName", min_length=1, max_length=128)
    params: str = Field(min_length=2, max_length=20_000)


class AinpcBehaviorExecutionRequest(BaseModel):
    # AINPC may add immutable execution context fields as its protocol evolves.
    # The Dongzhou adapter validates all fields it consumes and preserves the rest.
    model_config = ConfigDict(extra="allow", strict=True)

    game_server_id: str = Field(alias="gameServerId", min_length=1, max_length=128)
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    uid: str = Field(min_length=1, max_length=256)
    action_id: str = Field(alias="actionId", min_length=1, max_length=128)
    action_name: str = Field(alias="actionName", min_length=1, max_length=128)
    action_params: str = Field(alias="actionParams", min_length=2, max_length=20_000)
    duration: int = Field(ge=1, le=604_800)
    schedule_id: int | str | None = Field(default=None, alias="scheduleId")
    schedule_name: str | None = Field(default=None, alias="scheduleName", min_length=1, max_length=128)
    plan_id: str | None = Field(default=None, alias="planId", min_length=1, max_length=256)
    action_chain_id: str | None = Field(default=None, alias="actionChainId", min_length=1, max_length=256)


class AinpcPrivateChatRuntimeQuery(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    reveal_pii: Literal[False] = Field(default=False, alias="revealPii")


class AinpcPrivateChatRuntimeResetRequest(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    target_id: str = Field(alias="targetId", min_length=1, max_length=128)
    action: Literal[
        "EPrivateChatRuntimeResetActionEndWaitingReply",
        "EPrivateChatRuntimeResetActionClearPending",
    ]
    confirm_reset: Literal[True] = Field(alias="confirmReset")


class AinpcAllLoginRequest(StrictModel):
    instance_id: int | None = Field(default=None, alias="instanceId", ge=0)
    instance_count: int | None = Field(default=None, alias="instanceCount", ge=1)
    startup_id: str | None = Field(default=None, alias="startupId", min_length=1, max_length=128)


class AinpcSingleLoginRequest(StrictModel):
    game_server_id: str = Field(alias="gameServerId", min_length=1, max_length=128)
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    request_id: str = Field(alias="requestId", min_length=1, max_length=256)


class AinpcNpcDirectoryQuery(StrictModel):
    server_id: str = Field(alias="serverId", min_length=1, max_length=128)
    include_offline: bool = Field(default=False, alias="includeOffline")


class AinpcNearbyFilter(StrictModel):
    filter_type: Literal["FILTER_ONLY_PLAYER", "FILTER_ONLY_SMART_NPC"] = Field(
        alias="filterType"
    )


class AinpcNearbyQuery(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    filters: list[AinpcNearbyFilter] = Field(min_length=1, max_length=4)


class AinpcTargetPlayerQuery(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    target_player_id: int = Field(alias="targetPlayerId", ge=1)


class AinpcPlayerInfo(StrictModel):
    # AINPC forwards the complete V1 playerInfo object. Dongzhou only consumes
    # identity and display name, but must not reject fleet/guild/position fields.
    model_config = ConfigDict(extra="allow", strict=True)

    player_id: int | str = Field(
        validation_alias=AliasChoices("playerId", "id"),
        serialization_alias="playerId",
    )
    player_name: str = Field(
        validation_alias=AliasChoices("playerName", "name"),
        serialization_alias="playerName",
        min_length=1,
        max_length=200,
    )


class AinpcChatStartRequest(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    player_info: AinpcPlayerInfo = Field(alias="playerInfo")
    topic: str = Field(min_length=1, max_length=1000)
    login_request_id: str = Field(alias="loginRequestId", min_length=1, max_length=256)
    is_npc: bool = Field(default=False, alias="isNpc")


class AinpcPrivateMessageRequest(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    login_request_id: str = Field(alias="loginRequestId", min_length=1, max_length=256)
    chat_id: str = Field(alias="chatId", min_length=1, max_length=256)
    data: dict[str, Any]
    task_id: str = Field(alias="taskId", min_length=1, max_length=256)
    delivery_attempt_id: str | None = Field(
        default=None, alias="deliveryAttemptId", min_length=1, max_length=128
    )
    attempt: int = Field(default=1, ge=1)
    is_minor: bool = Field(default=False, alias="isMinor")
    need_manual_takeover: bool = Field(
        default=False,
        validation_alias=AliasChoices("needManualTakeover", "need_manual_takeover"),
        serialization_alias="needManualTakeover",
    )
    is_npc: bool = Field(default=False, alias="isNpc")
    player_info: AinpcPlayerInfo | None = Field(default=None, alias="playerInfo")


class AinpcPublicMessageRequest(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=500)
    login_request_id: str = Field(alias="loginRequestId", min_length=1, max_length=256)


class AinpcPrivateMessageDeliveryQuery(StrictModel):
    ai_id: str = Field(alias="aiId", min_length=1, max_length=128)
    chat_id: str = Field(alias="chatId", min_length=1, max_length=256)
    task_id: str = Field(alias="taskId", min_length=1, max_length=256)
    message_id: str = Field(alias="messageId", min_length=1, max_length=256)
    delivery_attempt_id: str = Field(
        alias="deliveryAttemptId", min_length=1, max_length=128
    )
    attempt: int = Field(ge=1)


class AinpcLittleElfMessageRequest(StrictModel):
    game_server_id: int | str
    player_id: int | str
    answer: str = Field(min_length=1, max_length=20_000)
    task_id: str = Field(min_length=1, max_length=256)
    chat_id: str = Field(min_length=1, max_length=256)
    intent_type: str = Field(default="unknown", max_length=64)
    guide_session_id: str = Field(default="", max_length=256)
    guide_started: bool = False
    reason: str = Field(default="", max_length=1000)


class AdviserQuestionRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    question: str = Field(min_length=1, max_length=500)
    stage_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    stage_title: str = Field(min_length=1, max_length=200)
    stage_index: int = Field(ge=1, le=172)


class AdviserFeedbackRequest(StrictModel):
    action_id: UUID = Field(strict=False)
    rating: Literal["accurate", "inaccurate"]
    reason: str = Field(default="", max_length=500)


class KnowledgeSearchRequest(StrictModel):
    client_request_id: UUID | None = Field(default=None, strict=False)
    stage_id: str | None = Field(default=None, min_length=1, max_length=64)
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=6, ge=1, le=20)


class KnowledgeQuizStartRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    stage_id: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_.:-]+$",
    )


class KnowledgeQuizAnswerRequest(StrictModel):
    action_id: UUID = Field(strict=False)
    answer_index: int = Field(ge=0, le=3)


class CampaignRouteRequest(StrictModel):
    from_stage_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    from_stage_index: int = Field(ge=1, le=172)
    to_stage_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    to_stage_index: int = Field(ge=2, le=172)
    route_method: Literal["campaign_progression", "fixed_point", "npc_dialog"] = "campaign_progression"

    @model_validator(mode="after")
    def validate_adjacent_stages(self) -> CampaignRouteRequest:
        if self.to_stage_index != self.from_stage_index + 1:
            raise ValueError("campaign route stages must be adjacent")
        if self.to_stage_id == self.from_stage_id:
            raise ValueError("campaign route stage IDs must differ")
        return self


class NpcInput(StrictModel):
    hero_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")
    name: str = Field(min_length=1, max_length=100)


class NpcSyncRequest(StrictModel):
    npcs: list[NpcInput] = Field(min_length=1, max_length=50)


class NpcInteractionPreferenceRequest(StrictModel):
    enabled: bool


class NpcCommendationRequest(StrictModel):
    stage_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    knowledge_id: str = Field(min_length=1, max_length=256)


class NpcMeritCommendationRequest(StrictModel):
    contribution_entry_id: UUID = Field(strict=False)
    contribution_entry_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    contribution_dossier_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class NpcRecollectionRequest(StrictModel):
    stage_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    knowledge_id: str = Field(min_length=1, max_length=256)


class NpcDecisionOption(StrictModel):
    index: int = Field(ge=0, le=20)
    text: str = Field(min_length=1, max_length=500)


class NpcDecisionRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    stage_id: str | None = Field(default=None, min_length=1, max_length=64)
    question: str = Field(min_length=1, max_length=2000)
    options: list[NpcDecisionOption] = Field(min_length=2, max_length=8)
    topic: str = Field(default="court_decision", min_length=1, max_length=100)
    memory_idempotency_key: str | None = Field(default=None, min_length=1, max_length=256)
    memory_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    public_notice_id: str | None = Field(default=None, min_length=1, max_length=128)
    public_notice_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    contribution_entry_id: UUID | None = Field(default=None, strict=False)
    contribution_entry_digest: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    contribution_dossier_digest: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )

    @model_validator(mode="after")
    def memory_reference_is_complete(self) -> "NpcDecisionRequest":
        if bool(self.memory_idempotency_key) != bool(self.memory_digest):
            raise ValueError("NPC memory reference is incomplete")
        if bool(self.public_notice_id) != bool(self.public_notice_digest):
            raise ValueError("NPC public notice reference is incomplete")
        if bool(self.contribution_entry_id) != bool(self.contribution_entry_digest):
            raise ValueError("organization contribution reference is incomplete")
        if self.contribution_dossier_digest and not self.contribution_entry_id:
            raise ValueError("organization contribution dossier has no ledger entry")
        return self


class NpcMessageRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    content: str = Field(min_length=1, max_length=2000)


class NpcScheduleGenerateRequest(StrictModel):
    force_regenerate: bool = False


OrganizationTaskType = Literal["diplomacy", "drill", "intelligence", "patrol", "supply"]


class NpcThoughtRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    stage_id: str = Field(min_length=1, max_length=64)
    stage_title: str = Field(min_length=1, max_length=200)
    knowledge_id: str = Field(min_length=1, max_length=200)
    evidence_source_index: int = Field(default=0, ge=0, le=20)
    task_type: OrganizationTaskType
    logistics_briefing_request_id: UUID | None = Field(default=None, strict=False)
    logistics_briefing_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def logistics_reference_is_complete(self) -> "NpcThoughtRequest":
        if bool(self.logistics_briefing_request_id) != bool(
            self.logistics_briefing_digest
        ):
            raise ValueError("NPC thought logistics reference is incomplete")
        return self


class LogisticsBriefingRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    stage_id: str = Field(min_length=1, max_length=64)
    stage_title: str = Field(min_length=1, max_length=200)


class CourtMandateOperation(StrictModel):
    kind: Literal["diplomacy"]
    target_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.:-]+$")
    target_name: str = Field(min_length=1, max_length=100)
    proposal: str = Field(min_length=1, max_length=500)


class CourtMandateRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    stage_id: str = Field(min_length=1, max_length=64)
    stage_title: str = Field(min_length=1, max_length=200)
    hero_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")
    support_hero_id: str | None = Field(
        default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$"
    )
    knowledge_id: str = Field(min_length=1, max_length=200)
    evidence_source_index: int = Field(default=0, ge=0, le=20)
    schedule_plan_id: str = Field(min_length=1, max_length=128)
    schedule_event_id: str = Field(min_length=1, max_length=256)
    council_request_id: UUID = Field(strict=False)
    decision_index: int = Field(ge=0, le=20)
    task_type: OrganizationTaskType
    knowledge_search_receipt_id: str | None = Field(default=None, min_length=1, max_length=256)
    knowledge_search_receipt_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    correspondence_message_id: str | None = Field(default=None, min_length=1, max_length=256)
    correspondence_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    thought_request_id: UUID | None = Field(default=None, strict=False)
    thought_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    knowledge_quiz_question_id: UUID | None = Field(default=None, strict=False)
    knowledge_quiz_result_digest: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    supersedes_mandate_id: str | None = Field(default=None, min_length=1, max_length=256)
    supersedes_mandate_digest: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    operation: CourtMandateOperation | None = None

    @model_validator(mode="after")
    def operation_matches_task(self) -> "CourtMandateRequest":
        if self.support_hero_id == self.hero_id:
            raise ValueError("court mandate support officer must differ from assignee")
        if self.operation is not None and self.task_type != "diplomacy":
            raise ValueError("court mandate operation does not match task type")
        if bool(self.correspondence_message_id) != bool(self.correspondence_digest):
            raise ValueError("court mandate correspondence reference is incomplete")
        if bool(self.thought_request_id) != bool(self.thought_digest):
            raise ValueError("court mandate thought reference is incomplete")
        if bool(self.knowledge_quiz_question_id) != bool(
            self.knowledge_quiz_result_digest
        ):
            raise ValueError("court mandate knowledge quiz reference is incomplete")
        if bool(self.supersedes_mandate_id) != bool(self.supersedes_mandate_digest):
            raise ValueError("court mandate revision reference is incomplete")
        return self


class CourtMandateResumeRequest(StrictModel):
    action_id: UUID = Field(strict=False)
    decision: Literal["APPROVE", "REJECT", "REVISE"]


class CourtMandateScheduleRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    mandate_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class OrganizationTaskReviewRequest(StrictModel):
    action_id: UUID = Field(strict=False)
    decision: Literal["ACCEPT", "CENSURE"]


class OrganizationInventoryRequisitionRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    units: int = Field(ge=20, le=100)
    stage_id: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def units_are_full_lots(self) -> "OrganizationInventoryRequisitionRequest":
        if self.units % 20:
            raise ValueError("inventory requisition units must be a multiple of 20")
        return self


class OrganizationTaskParameters(StrictModel):
    resource_units: int = Field(ge=0, le=200)
    assignee_name: str = Field(min_length=1, max_length=100)
    mandate_id: str | None = Field(default=None, min_length=1, max_length=256)
    mandate_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class OrganizationTaskRequest(StrictModel):
    client_request_id: UUID = Field(strict=False)
    task_type: OrganizationTaskType
    assignee_hero_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")
    stage_id: str = Field(min_length=1, max_length=64)
    stage_title: str = Field(min_length=1, max_length=200)
    brief: str = Field(min_length=1, max_length=1000)
    parameters: OrganizationTaskParameters
