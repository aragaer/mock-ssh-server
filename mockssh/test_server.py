import codecs
import platform
import subprocess
import tempfile

from pytest import raises


def test_echo(server):
    for uid in server.users:
        with server.client(uid) as c:
            shell = c.invoke_shell()
            shell.sendall(b"hello, world")
            assert shell.recv(4096) == b"hello, world"


def test_multiple_connections1(server):
    _test_multiple_connections(server)


def test_multiple_connections2(server):
    _test_multiple_connections(server)


def test_multiple_connections3(server):
    _test_multiple_connections(server)


def test_multiple_connections4(server):
    _test_multiple_connections(server)


def test_multiple_connections5(server):
    _test_multiple_connections(server)


def _test_multiple_connections(server):
    # This test will deadlock without ea1e0f80aac7253d2d346732eefd204c6627f4c8
    fd, pkey_path = tempfile.mkstemp()
    user, private_key = list(server._users.items())[0]
    open(pkey_path, 'w').write(open(private_key[0]).read())
    ssh_command = 'ssh -oStrictHostKeyChecking=no '
    ssh_command += "-i %s -p %s %s@localhost " % (pkey_path, server.port, user)
    ssh_command += 'echo hello'
    p = subprocess.check_output(ssh_command, shell=True)
    assert p.decode('utf-8').strip() == 'hello'


def test_invalid_user(server):
    with raises(KeyError) as exc:
        server.client("unknown-user")
    assert exc.value.args[0] == "unknown-user"


def test_add_user(server, user_key_path):
    with raises(KeyError):
        server.client("new-user")

    server.add_user("new-user", user_key_path)
    with server.client("new-user") as c:
        _, stdout, _ = c.exec_command("echo 42")
        assert codecs.decode(stdout.read().strip(), "utf8") == "42"
