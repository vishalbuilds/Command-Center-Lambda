import phonenumbers
from phonenumbers import ValidationResult
from common.models.default_strategy import DefaultStrategy
from common.models.logger import Logger

LOGGER = Logger(__name__)

PLUS_SIGN = "+"


class PhoneNumberFormat(DefaultStrategy):
    def __init__(self, event):
        self.event = event
        self.phone_number = event.get("phone_number", None)

    def do_validate(self):
        if not self.phone_number:
            LOGGER.error("Phone number is required in event")
            return False, "Phone number is required in event"
        else:
            return True, None

    def do_operation(self):
        phone_number = str(self.phone_number)
        if not phone_number.startswith(PLUS_SIGN):
            phone_number = PLUS_SIGN + phone_number
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            is_possible_number_response = phonenumbers.is_possible_number_with_reason(
                parsed_number
            )
            if is_possible_number_response in [
                ValidationResult.IS_POSSIBLE,
                ValidationResult.IS_POSSIBLE_LOCAL_ONLY,
            ]:
                if phonenumbers.is_valid_number(parsed_number):
                    return {
                        "validationResult": "Valid",
                        "countryCode": parsed_number.country_code,
                        "regionCode": phonenumbers.region_code_for_number(
                            parsed_number
                        ),
                        "phoneNumber": parsed_number.national_number,
                    }
                else:
                    return {
                        "validationResult": "Invalid",
                        "countryCode": parsed_number.country_code,
                        "regionCode": phonenumbers.region_code_for_number(
                            parsed_number
                        ),
                        "phoneNumber": parsed_number.national_number,
                    }
            else:
                return {
                    "validationResult": "Invalid",
                    "failedReason": ValidationResult.to_string(
                        is_possible_number_response
                    ),
                }
        except phonenumbers.NumberParseException as e:
            LOGGER.add_tempdata("error", str(e))
            LOGGER.error(f"Error in processing phone number format request: {e}")
            return {"validationResult": "Error", "failedReason": str(e)}
