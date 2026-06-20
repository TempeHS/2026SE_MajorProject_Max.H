import subprocess


def test_live_server_mods():
    cmd = [
        "curl",
        "-X",
        "GET",
        "http://157.211.242.198:9106/api/mods",
        "-H",
        "accept: application/json",
        "-H",
        "Authorization: Bearer mcsapi_f7bc8b785de41d18299af1e0a36ce660e61de1480b7ddaa3",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)


if __name__ == "__main__":
    test_live_server_mods()
