from common.utils_methods.connect_utils import ConnectUtils
from common.models.default_strategy import DefaultStrategy
from common.models.logger import Logger
import os
from datetime import datetime, timezone

LOGGER = Logger(__name__)


MAX_CONTACT_ACTIVE_TIME = 2  # hours
RP_ARN_LIMITS = 100


class AutoCleanUpActiveContacts(DefaultStrategy):
    def __init__(self, event):
        self.event = event
        self.instance_id = os.environ.get("INSTANCE_ID")
        self.region = os.environ.get("REGION")
        self.connect_utils = ConnectUtils(self.region, self.instance_id)
        LOGGER.info(
            f"Initializing AutoCleanUpActiveContacts for instance: {self.instance_id}"
        )

    def do_validate(self):
        LOGGER.info("Starting validation process")

        if not self.instance_id:
            LOGGER.error(
                "Validation failed: INSTANCE_ID environment variable is not set"
            )
            return False, "INSTANCE_ID environment variable is not set"

        if not os.environ.get("REGION"):
            LOGGER.error("Validation failed: REGION environment variable is not set")
            return False, "REGION environment variable is not set"

        LOGGER.info(
            "Validation successful: All required environment variables are present"
        )
        return True, None

    def _routing_profile_arn(self):
        """
        Returns the currently active contact for the given Routing Profile.

        We prefer querying at Routing Profile level instead of Users or Queues,
        because Routing Profiles are significantly fewer in number. This reduces
        total API calls, improves lookup performance, and avoids unnecessary
        iteration over all users / queues.
        """
        LOGGER.info(f"Fetching routing profiles for instance: {self.instance_id}")

        try:
            rp_paginator = self.connect_utils._get_paginator("list_routing_profiles")
            routing_profile_arns = []

            for page in rp_paginator.paginate(InstanceId=self.instance_id):
                arns = [rp["Arn"] for rp in page.get("RoutingProfileSummaryList", [])]
                routing_profile_arns.extend(arns)

            LOGGER.add_tempdata("routing_profile_count", len(routing_profile_arns))
            LOGGER.info(
                f"Successfully retrieved {len(routing_profile_arns)} routing profile ARNs"
            )

            return routing_profile_arns

        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.add_tempdata("instance_id", self.instance_id)
            LOGGER.error(
                f"Failed to retrieve routing profile ARNs for instance {self.instance_id}: {str(e)}"
            )
            raise

    def _active_contact_ids(self, routing_profile_arn: list):
        """
        Returns the currently active contacts for the given Routing Profile.
        """
        LOGGER.info(
            f"Fetching active contacts for {len(routing_profile_arn)} routing profiles"
        )

        try:
            active_contact_ids_list = []
            filter_params = {
                "RoutingProfiles": routing_profile_arn,
                "ContactStates": ["CONNECTED"],
            }

            LOGGER.add_tempdata("filter_params", filter_params)

            response = self.connect_utils.get_current_user_data(filter_params)
            user_data_list = response.get("UserDataList", [])

            LOGGER.info(f"Processing {len(user_data_list)} users for active contacts")

            contacts_checked = 0
            contacts_exceeding_threshold = 0

            for user in user_data_list:
                for contact in user.get("Contacts", []):
                    contacts_checked += 1
                    ts = contact.get("ConnectedToAgentTimestamp")

                    if not ts:
                        LOGGER.warning(
                            f"Contact {contact.get('ContactId')} missing ConnectedToAgentTimestamp"
                        )
                        continue

                    connected_to_agent_timestamp = (
                        datetime.fromisoformat(ts) if isinstance(ts, str) else ts
                    )
                    duration_hours = (
                        datetime.now(timezone.utc) - connected_to_agent_timestamp
                    ).total_seconds() / 3600

                    if (
                        contact.get("AgentContactState") == "CONNECTED"
                        and duration_hours >= MAX_CONTACT_ACTIVE_TIME
                    ):
                        contact_id = contact.get("ContactId")
                        active_contact_ids_list.append(contact_id)
                        contacts_exceeding_threshold += 1
                        LOGGER.info(
                            f"Contact {contact_id} exceeds threshold: {duration_hours:.2f} hours active"
                        )

            LOGGER.add_tempdata("contacts_checked", contacts_checked)
            LOGGER.add_tempdata(
                "contacts_exceeding_threshold", contacts_exceeding_threshold
            )
            LOGGER.add_tempdata("active_contact_ids", active_contact_ids_list)
            LOGGER.info(
                f"Found {len(active_contact_ids_list)} contacts exceeding {MAX_CONTACT_ACTIVE_TIME} hour threshold out of {contacts_checked} checked"
            )

            return active_contact_ids_list

        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.add_tempdata("routing_profile_count", len(routing_profile_arn))
            LOGGER.error(f"Failed to retrieve active contact IDs: {str(e)}")
            raise

    def _process_contact_validation_and_disconnect(self, contact_id):
        """
        Validates and disconnects a contact if it exceeds the active time threshold.
        """
        LOGGER.info(f"Processing contact validation for contact_id: {contact_id}")

        try:
            response = self.connect_utils.describe_contact(contact_id)
            contact = response.get("Contact")

            if not contact:
                LOGGER.warning(f"No contact details found for contact_id: {contact_id}")
                return None

            # Check if already disconnected
            if contact.get("DisconnectTimestamp"):
                disconnect_ts = contact.get("DisconnectTimestamp")
                LOGGER.add_tempdata("already_disconnected_contact_id", contact_id)
                LOGGER.info(
                    f"Contact {contact_id} is already disconnected at {disconnect_ts}"
                )
                return {
                    "status": "Already_Disconnected",
                    "LastUpdateTimestamp": disconnect_ts,
                    "contact_id": contact_id,
                }

            # Process active contact
            ts = contact.get("LastUpdateTimestamp")
            if not ts:
                LOGGER.warning(f"Contact {contact_id} missing LastUpdateTimestamp")
                return None

            last_update_timestamp = (
                datetime.fromisoformat(ts) if isinstance(ts, str) else ts
            )
            duration_hours = (
                datetime.now(timezone.utc) - last_update_timestamp
            ).total_seconds() / 3600

            LOGGER.add_tempdata("contact_duration_hours", f"{duration_hours:.2f}")

            if duration_hours >= MAX_CONTACT_ACTIVE_TIME:
                LOGGER.info(
                    f"Attempting to disconnect contact {contact_id} (active for {duration_hours:.2f} hours)"
                )
                self.connect_utils.stop_contact(contact_id)
                LOGGER.add_tempdata("disconnected_contact_id", contact_id)
                LOGGER.info(f"Successfully disconnected contact {contact_id}")

                return {
                    "status": "Disconnected",
                    "LastUpdateTimestamp": last_update_timestamp,
                    "contact_id": contact_id,
                    "duration_hours": round(duration_hours, 2),
                }
            else:
                LOGGER.add_tempdata("in_progress_contact_id", contact_id)
                LOGGER.info(
                    f"Contact {contact_id} not disconnected: active for {duration_hours:.2f} hours (threshold: {MAX_CONTACT_ACTIVE_TIME} hours)"
                )

                return {
                    "status": "In_Progress",
                    "LastUpdateTimestamp": last_update_timestamp,
                    "contact_id": contact_id,
                    "duration_hours": round(duration_hours, 2),
                }

        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.add_tempdata("failed_contact_id", contact_id)
            LOGGER.error(f"Failed to process contact {contact_id}: {str(e)}")
            raise

    def do_operation(self):
        """
        Main operation to clean up active contacts that exceed the time threshold.
        """
        LOGGER.info(
            f"Starting contact cleanup operation with {MAX_CONTACT_ACTIVE_TIME} hour threshold"
        )

        try:
            contact_result = []
            disconnected_count = 0
            in_progress_count = 0
            already_disconnected_count = 0
            failed_count = 0

            # Get routing profiles
            rp_arn_list = self._routing_profile_arn()
            LOGGER.info(
                f"Processing {len(rp_arn_list)} routing profiles in batches of {RP_ARN_LIMITS}"
            )

            # Get active contacts in batches
            all_active_contacts = []
            for i in range(0, len(rp_arn_list), RP_ARN_LIMITS):
                batch_arns = rp_arn_list[i : i + RP_ARN_LIMITS]
                LOGGER.info(
                    f"Processing batch {i//RP_ARN_LIMITS + 1}: {len(batch_arns)} routing profiles"
                )
                batch_contacts = self._active_contact_ids(batch_arns)
                all_active_contacts.extend(batch_contacts)

            LOGGER.add_tempdata("total_active_contacts", len(all_active_contacts))
            LOGGER.info(f"Total active contacts found: {len(all_active_contacts)}")

            # Process each contact
            for idx, contact_id in enumerate(all_active_contacts, 1):
                LOGGER.info(
                    f"Processing contact {idx}/{len(all_active_contacts)}: {contact_id}"
                )

                try:
                    contact_disconnect_status = (
                        self._process_contact_validation_and_disconnect(contact_id)
                    )

                    if not contact_disconnect_status:
                        failed_count += 1
                        continue

                    status = contact_disconnect_status.get("status")

                    if status == "Disconnected":
                        disconnected_count += 1
                        contact_result.append(
                            {
                                "Contact_status": "Disconnected",
                                "LastUpdateTimestamp": str(
                                    contact_disconnect_status.get("LastUpdateTimestamp")
                                ),
                                "contact_id": contact_id,
                                "duration_hours": contact_disconnect_status.get(
                                    "duration_hours"
                                ),
                            }
                        )
                        LOGGER.add_tempdata("disconnected_contact_id", contact_id)
                        LOGGER.info(f"Contact {contact_id} successfully disconnected")

                    elif status == "In_Progress":
                        in_progress_count += 1
                        contact_result.append(
                            {
                                "Contact_status": "In_Progress",
                                "LastUpdateTimestamp": str(
                                    contact_disconnect_status.get("LastUpdateTimestamp")
                                ),
                                "contact_id": contact_id,
                                "duration_hours": contact_disconnect_status.get(
                                    "duration_hours"
                                ),
                            }
                        )
                        LOGGER.add_tempdata("in_progress_contact_id", contact_id)
                        LOGGER.info(
                            f"Contact {contact_id} still in progress (below threshold)"
                        )

                    elif status == "Already_Disconnected":
                        already_disconnected_count += 1
                        contact_result.append(
                            {
                                "Contact_status": "Already_Disconnected",
                                "LastUpdateTimestamp": str(
                                    contact_disconnect_status.get("LastUpdateTimestamp")
                                ),
                                "contact_id": contact_id,
                            }
                        )

                except Exception as contact_error:
                    failed_count += 1
                    LOGGER.add_tempdata("error", str(contact_error))
                    LOGGER.error(
                        f"Failed to process contact {contact_id}: {str(contact_error)}"
                    )

            # Summary logging
            summary = {
                "total_contacts_processed": len(all_active_contacts),
                "disconnected": disconnected_count,
                "in_progress": in_progress_count,
                "already_disconnected": already_disconnected_count,
                "failed": failed_count,
            }

            LOGGER.add_tempdata("operation_summary", summary)
            LOGGER.info(f"Contact cleanup operation completed: {summary}")

            return {
                "status": "Success",
                "message": "Contact cleanup job completed successfully",
                "summary": summary,
                "contact_details": contact_result,
            }

        except Exception as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.error(f"Contact cleanup operation failed: {str(e)}")
            raise
