from unittest import TestCase

from core.action_response import ActionResponse


class TestActionResponse(TestCase):
    """Test cases for ActionResponse class."""

    def test_action_response_creation_with_required_fields(self) -> None:
        """
        Test creating ActionResponse with required fields only.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(status_code = 200)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.message)
        self.assertIsNone(response.fields)

    def test_action_response_creation_with_all_fields(self) -> None:
        """
        Test creating ActionResponse with all fields.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(
            status_code = 201,
            message = "Created successfully",
            fields = {"id": 123, "name": "test"}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.message, "Created successfully")
        self.assertEqual(response.fields, {"id": 123, "name": "test"})

    def test_action_response_with_string_fields(self) -> None:
        """
        Test ActionResponse with string fields.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(
            status_code = 200,
            message = "Success",
            fields = "test string"
        )

        self.assertEqual(response.fields, "test string")

    def test_action_response_with_numeric_fields(self) -> None:
        """
        Test ActionResponse with numeric fields.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(
            status_code = 200,
            fields = 42
        )

        self.assertEqual(response.fields, 42)

    def test_action_response_with_boolean_fields(self) -> None:
        """
        Test ActionResponse with boolean fields.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(
            status_code = 200,
            fields = True
        )

        self.assertTrue(response.fields)

    def test_action_response_with_float_fields(self) -> None:
        """
        Test ActionResponse with float fields.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(
            status_code = 200,
            fields = 3.14
        )

        self.assertEqual(response.fields, 3.14)

    def test_action_response_description(self) -> None:
        """
        Test ActionResponse description method.

        Returns:
            None: This test does not return a value.
        """
        description = ActionResponse.description()

        self.assertEqual(description, "The schema used as a standard response returned by ActionRunner.run()")

    def test_action_response_discriminator(self) -> None:
        """
        Test ActionResponse discriminator method.

        Returns:
            None: This test does not return a value.
        """
        discriminator = ActionResponse.discriminator()

        self.assertEqual(discriminator, "ActionResponse")

    def test_action_response_inheritance(self) -> None:
        """
        Test that ActionResponse inherits from ActionSchema.

        Returns:
            None: This test does not return a value.
        """
        from core.action_schema import ActionSchema

        # ActionResponse is always a subclass of ActionSchema by design
        self.assertIsInstance(ActionResponse, type)

    def test_action_response_to_dict(self) -> None:
        """
        Test ActionResponse to_dict method.

        Returns:
            None: This test does not return a value.
        """
        result = ActionResponse.to_dict()

        self.assertIn("ActionResponse", result)
        self.assertIn("description", result["ActionResponse"])
        self.assertIn("fields", result["ActionResponse"])

        fields = result["ActionResponse"]["fields"]
        self.assertIn("status_code", fields)
        self.assertIn("message", fields)
        self.assertIn("fields", fields)

    def test_action_response_json_serialization(self) -> None:
        """
        Test ActionResponse JSON serialization.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(
            status_code = 200,
            message = "Success",
            fields = {"key": "value"}
        )

        json_str = response.model_dump_json()
        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed["status_code"], 200)
        self.assertEqual(parsed["message"], "Success")
        self.assertEqual(parsed["fields"], {"key": "value"})

    def test_action_response_validation(self) -> None:
        """
        Test ActionResponse field validation.

        Returns:
            None: This test does not return a value.
        """
        # Valid status codes should work
        response1 = ActionResponse(status_code = 200)
        response2 = ActionResponse(status_code = 404)
        response3 = ActionResponse(status_code = 500)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 404)
        self.assertEqual(response3.status_code, 500)

    def test_action_response_with_none_values(self) -> None:
        """
        Test ActionResponse with None values for optional fields.

        Returns:
            None: This test does not return a value.
        """
        response = ActionResponse(
            status_code = 200,
            message = None,
            fields = None
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.message)
        self.assertIsNone(response.fields)


if __name__ == "__main__":
    from unittest import main
    main()
