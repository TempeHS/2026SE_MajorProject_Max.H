import unittest
import mcwebapi


class TestMcRestCurlCommand(unittest.TestCase):
    def test_build_curl_command_default_timeout(self):
        cmd = mcwebapi.build_mcrest_curl_command(
            serverHost="1.2.3.4",
            serverPort=8080,
            serverKey="mcsapi_testkey",
        )
        expected = (
            "curl -sS -m 5 -H 'Authorization: Bearer mcsapi_testkey' "
            "http://1.2.3.4:8080/api/server"
        )
        self.assertEqual(cmd, expected)

    def test_build_curl_command_custom_timeout(self):
        cmd = mcwebapi.build_mcrest_curl_command(
            serverHost="example.com",
            serverPort=9000,
            serverKey="mcsapi_abc123",
            timeout=10,
        )
        expected = (
            "curl -sS -m 10 -H 'Authorization: Bearer mcsapi_abc123' "
            "http://example.com:9000/api/server"
        )
        self.assertEqual(cmd, expected)


if __name__ == "__main__":
    unittest.main()
