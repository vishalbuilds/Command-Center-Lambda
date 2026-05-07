from common.utils_methods.connect_utils import ConnectUtils
from common.models.default_strategy import DefaultStrategy
from aws_lambda_powertools import Logger
import os
from datetime import datetime, timezone

logger = Logger(child=True)


MAX_CONTACT_ACTIVE_TIME = 2  # hours
RP_ARN_LIMITS = 100


class AutoCleanUpActiveContacts(DefaultStrategy):

    def __init__(self, event):
        self.event = event
        self.instance_id = os.environ.get("INSTANCE_ID")
        self.region = os.environ.get("REGION")
        self.connect_utils = ConnectUtils(self.region, self.instance_id)
        logger.info(
            f"Initializing AutoCleanUpActiveContacts for instance: {self.instance_id}",
            extra={"instance_id": self.instance_id, "region": self.region},
        )

    def do_validate(self):
        logger.info(
            "Starting validation process",
            extra={"instance_id": self.instance_id, "region": self.region},
        )

        if not self.instance_id:
            logger.error(
                "Validation failed: INSTANCE_ID environment variable is not set",
                extra={"instance_id": self.instance_id, "region": self.region},
            )
            return False, "INSTANCE_ID environment variable is not set"

        if not os.environ.get("REGION"):
            logger.error(
                "Validation failed: REGION environment variable is not set",
                extra={"instance_id": self.instance_id, "region": self.region},
            )
            return False, "REGION environment variable is not set"

        logger.info(
            "Validation successful: All required environment variables are present",
            extra={"instance_id": self.instance_id, "region": self.region},
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
        logger.info(
            f"Fetching routing profiles for instance: {self.instance_id}",
            extra={"instance_id": self.instance_id, "region": self.region},
        )

        try:
            routing_profiles = self.connect_utils.list_routing_profile()
            routing_profile_arns = [rp["Arn"] for rp in routing_profiles]

            logger.info(
                f"Successfully retrieved {len(routing_profile_arns)} routing profile ARNs",
                extra={
                    "routing_profile_count": len(routing_profile_arns),
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            return routing_profile_arns

        except Exception as e:
            logger.exception(
                f"Failed to retrieve routing profile ARNs for instance {self.instance_id}: {str(e)}",
                extra={
                    "error": str(e),
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )
            raise

    def _active_contact_ids(self, routing_profile_arn: list):
        """
        Returns the currently active contacts for the given Routing Profile.
        """
        logger.info(
            f"Fetching active contacts for {len(routing_profile_arn)} routing profiles",
            extra={
                "routing_profile_arn_count": len(routing_profile_arn),
                "instance_id": self.instance_id,
                "region": self.region,
            },
        )

        try:
            active_contact_ids_list = []
            filter_params = {
                "RoutingProfiles": routing_profile_arn,
                "ContactStates": ["CONNECTED"],
            }

            logger.info(
                "Active contact filter params",
                extra={
                    "filter_params": filter_params,
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            response = self.connect_utils.get_current_user_data(filter_params)
            user_data_list = response.get("UserDataList", [])

            logger.info(
                f"Processing {len(user_data_list)} users for active contacts",
                extra={
                    "user_count": len(user_data_list),
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            contacts_checked = 0
            contacts_exceeding_threshold = 0

            for user in user_data_list:
                for contact in user.get("Contacts", []):
                    contacts_checked += 1
                    ts = contact.get("ConnectedToAgentTimestamp")

                    if not ts:
                        logger.info(
                            f"Contact {contact.get('ContactId')} missing ConnectedToAgentTimestamp",
                            extra={
                                "missing_contact_id": contact,
                                "instance_id": self.instance_id,
                                "region": self.region,
                            },
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
                        logger.info(
                            f"Contact {contact_id} exceeds threshold: {duration_hours:.2f} hours active",
                            extra={
                                "contact_id": contact_id,
                                "duration_hours": duration_hours,
                                "instance_id": self.instance_id,
                                "region": self.region,
                            },
                        )

            logger.info(
                f"Found {len(active_contact_ids_list)} contacts exceeding {MAX_CONTACT_ACTIVE_TIME} hour threshold out of {contacts_checked} checked",
                extra={
                    "contacts_checked": contacts_checked,
                    "contacts_exceeding_threshold": contacts_exceeding_threshold,
                    "active_contact_ids": active_contact_ids_list,
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            return active_contact_ids_list

        except Exception as e:
            logger.exception(
                f"Failed to retrieve active contact IDs: {str(e)}",
                extra={
                    "error": str(e),
                    "routing_profile_count": len(routing_profile_arn),
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )
            raise

    def _process_contact_validation_and_disconnect(self, contact_id):
        """
        Validates and disconnects a contact if it exceeds the active time threshold.
        """
        logger.info(
            f"Processing contact validation for contact_id: {contact_id}",
            extra={
                "contact_id": contact_id,
                "instance_id": self.instance_id,
                "region": self.region,
            },
        )

        try:
            response = self.connect_utils.describe_contact(contact_id)
            contact = response.get("Contact")

            if not contact:
                logger.info(
                    f"No contact details found for contact_id: {contact_id}",
                    extra={
                        "contact_id": contact_id,
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
                )
                return None

            # Check if already disconnected
            if contact.get("DisconnectTimestamp"):
                disconnect_ts = contact.get("DisconnectTimestamp")
                logger.info(
                    f"Contact {contact_id} is already disconnected at {disconnect_ts}",
                    extra={
                        "already_disconnected_contact_id": contact_id,
                        "disconnect_ts": disconnect_ts,
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
                )
                return {
                    "status": "Already_Disconnected",
                    "LastUpdateTimestamp": disconnect_ts,
                    "contact_id": contact_id,
                }

            # Process active contact
            ts = contact.get("LastUpdateTimestamp")
            if not ts:
                logger.info(
                    f"Contact {contact_id} missing LastUpdateTimestamp",
                    extra={
                        "contact_id": contact_id,
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
                )
                return None

            last_update_timestamp = (
                datetime.fromisoformat(ts) if isinstance(ts, str) else ts
            )
            duration_hours = (
                datetime.now(timezone.utc) - last_update_timestamp
            ).total_seconds() / 3600

            logger.info(
                "Contact duration hours",
                extra={
                    "contact_duration_hours": f"{duration_hours:.2f}",
                    "contact_id": contact_id,
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            if duration_hours >= MAX_CONTACT_ACTIVE_TIME:
                logger.info(
                    f"Attempting to disconnect contact {contact_id} (active for {duration_hours:.2f} hours)",
                    extra={
                        "contact_id": contact_id,
                        "duration_hours": duration_hours,
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
                )
                self.connect_utils.stop_contact(contact_id)
                logger.info(
                    f"Successfully disconnected contact {contact_id}",
                    extra={
                        "disconnected_contact_id": contact_id,
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
                )

                return {
                    "status": "Disconnected",
                    "LastUpdateTimestamp": last_update_timestamp,
                    "contact_id": contact_id,
                    "duration_hours": round(duration_hours, 2),
                }
            else:
                logger.info(
                    f"Contact {contact_id} not disconnected: active for {duration_hours:.2f} hours (threshold: {MAX_CONTACT_ACTIVE_TIME} hours)",
                    extra={
                        "in_progress_contact_id": contact_id,
                        "duration_hours": duration_hours,
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
                )

                return {
                    "status": "In_Progress",
                    "LastUpdateTimestamp": last_update_timestamp,
                    "contact_id": contact_id,
                    "duration_hours": round(duration_hours, 2),
                }

        except Exception as e:
            logger.exception(
                f"Failed to process contact {contact_id}: {str(e)}",
                extra={
                    "error": str(e),
                    "failed_contact_id": contact_id,
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )
            raise

    def do_operation(self):
        """
        Main operation to clean up active contacts that exceed the time threshold.
        """
        logger.info(
            f"Starting contact cleanup operation with {MAX_CONTACT_ACTIVE_TIME} hour threshold",
            extra={
                "MAX_CONTACT_ACTIVE_TIME": MAX_CONTACT_ACTIVE_TIME,
                "instance_id": self.instance_id,
                "region": self.region,
            },
        )

        try:
            contact_result = []
            disconnected_count = 0
            in_progress_count = 0
            already_disconnected_count = 0
            failed_count = 0

            # Get routing profiles
            rp_arn_list = self._routing_profile_arn()
            logger.info(
                f"Processing {len(rp_arn_list)} routing profiles in batches of {RP_ARN_LIMITS}",
                extra={
                    "routing_profile_count": len(rp_arn_list),
                    "RP_ARN_LIMITS": RP_ARN_LIMITS,
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            # Get active contacts in batches
            all_active_contacts = []
            for i in range(0, len(rp_arn_list), RP_ARN_LIMITS):
                batch_arns = rp_arn_list[i : i + RP_ARN_LIMITS]
                logger.info(
                    f"Processing batch {i//RP_ARN_LIMITS + 1}: {len(batch_arns)} routing profiles",
                    extra={
                        "batch_number": i // RP_ARN_LIMITS + 1,
                        "batch_size": len(batch_arns),
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
                )
                batch_contacts = self._active_contact_ids(batch_arns)
                all_active_contacts.extend(batch_contacts)

            logger.info(
                f"Total active contacts found: {len(all_active_contacts)}",
                extra={
                    "total_active_contacts": len(all_active_contacts),
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            # Process each contact
            for idx, contact_id in enumerate(all_active_contacts, 1):
                logger.info(
                    f"Processing contact {idx}/{len(all_active_contacts)}: {contact_id}",
                    extra={
                        "contact_index": idx,
                        "total_contacts": len(all_active_contacts),
                        "contact_id": contact_id,
                        "instance_id": self.instance_id,
                        "region": self.region,
                    },
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
                        logger.info(
                            f"Contact {contact_id} successfully disconnected",
                            extra={
                                "disconnected_contact_id": contact_id,
                                "contact_index": idx,
                                "instance_id": self.instance_id,
                                "region": self.region,
                            },
                        )

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
                        logger.info(
                            f"Contact {contact_id} still in progress (below threshold)",
                            extra={
                                "in_progress_contact_id": contact_id,
                                "contact_index": idx,
                                "instance_id": self.instance_id,
                                "region": self.region,
                            },
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
                    logger.exception(
                        f"Failed to process contact {contact_id}: {str(contact_error)}",
                        extra={
                            "error": str(contact_error),
                            "contact_id": contact_id,
                            "instance_id": self.instance_id,
                            "region": self.region,
                        },
                    )

            # Summary logging
            summary = {
                "total_contacts_processed": len(all_active_contacts),
                "disconnected": disconnected_count,
                "in_progress": in_progress_count,
                "already_disconnected": already_disconnected_count,
                "failed": failed_count,
            }

            logger.info(
                f"Contact cleanup operation completed: {summary}",
                extra={
                    "operation_summary": summary,
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )

            return {
                "status": "Success",
                "message": "Contact cleanup job completed successfully",
                "summary": summary,
                "contact_details": contact_result,
            }

        except Exception as e:
            logger.exception(
                f"Contact cleanup operation failed: {str(e)}",
                extra={
                    "error": str(e),
                    "instance_id": self.instance_id,
                    "region": self.region,
                },
            )
            raise
