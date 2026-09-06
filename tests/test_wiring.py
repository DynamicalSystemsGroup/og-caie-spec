"""The assemblage is fully wired: every interface usage connects two ports
that exist on the named parts with matching (conjugated) types, and every
port of every part in the assembly is connected exactly once. Strict
validation does not check this, so the test does."""
import re

from conftest import ROOT

MODEL = (ROOT / "model" / "og-caie.sysml").read_text()


def part_defs():
    out = {}
    for m in re.finditer(r"part def (\w+) :> (?:HumanAgent|MachineAgent) \{(.*?)\n    \}", MODEL, re.S):
        ports = dict(re.findall(r"port (\w+) : (~?\w+);", m.group(2)))
        out[m.group(1)] = ports
    return out


def assembly():
    body = re.search(r"part def OgCaieEvaluation \{(.*?)\n    \}", MODEL, re.S).group(1)
    parts = dict(re.findall(r"^\s+part (\w+) : (\w+);", body, re.M))
    ifaces = re.findall(r"interface (\w+) : (\w+) connect (\w+)\.(\w+) to (\w+)\.(\w+);", body)
    return parts, ifaces


def interface_defs():
    return dict(re.findall(r"interface def (\w+) \{ end supplier : (\w+); end consumer : ~\2; \}", MODEL))


def test_twelve_interfaces_connect_existing_conjugate_ports():
    defs, (parts, ifaces), idefs = part_defs(), assembly(), interface_defs()
    assert len(ifaces) == 12
    for name, itype, a, pa, b, pb in ifaces:
        assert itype in idefs, itype
        supplier_type = idefs[itype]
        assert defs[parts[a]][pa] == supplier_type, f"{name}: {a}.{pa} is {defs[parts[a]][pa]}, expected {supplier_type}"
        assert defs[parts[b]][pb] == "~" + supplier_type, f"{name}: {b}.{pb} is {defs[parts[b]][pb]}, expected ~{supplier_type}"


def test_every_port_connected_exactly_once():
    defs, (parts, ifaces), _ = part_defs(), assembly(), interface_defs()
    used = {}
    for name, _, a, pa, b, pb in ifaces:
        for end in ((a, pa), (b, pb)):
            used[end] = used.get(end, 0) + 1
    for part, pdef in parts.items():
        for port in defs[pdef]:
            assert used.get((part, port), 0) == 1, f"{part}.{port} connected {used.get((part, port), 0)} times"
    assert sum(used.values()) == 24


def test_interfaces_declared_before_parts():
    body = re.search(r"part def OgCaieEvaluation \{(.*?)\n    \}", MODEL, re.S).group(1)
    assert body.find("interface ") < body.find("\n        part ")


def test_humans_and_machines_split():
    assert set(re.findall(r"part def (\w+) :> HumanAgent", MODEL)) == {"DomainExpert", "Evaluator", "Sponsor"}
    assert set(re.findall(r"part def (\w+) :> MachineAgent", MODEL)) == {
        "SystemUnderTest", "ProbeDeriver", "ConformanceChecker", "Recorder", "CoverageCalculator"}
