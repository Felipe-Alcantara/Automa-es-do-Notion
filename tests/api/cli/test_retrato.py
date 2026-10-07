import argparse
import json

from felixo_notion_mcp.api.cli.retrato import retratar_parser


def _parser():
    p = argparse.ArgumentParser(prog="x")
    sub = p.add_subparsers(dest="comando")
    el = sub.add_parser("editar-linha", aliases=["el"])
    el.add_argument("pagina_id")
    el.add_argument("--set", action="append", dest="valores")
    el.add_argument("--sim", action="store_true")
    return p


def test_retrato_registra_subcomandos_aliases_e_argumentos():
    r = retratar_parser(_parser())
    assert set(r["subcomandos"]) == {"editar-linha", "el"}
    args = {a["destino"]: a for a in r["subcomandos"]["editar-linha"]["argumentos"]}
    assert args["pagina_id"]["opcoes"] == []
    assert args["valores"]["opcoes"] == ["--set"]
    assert args["valores"]["acao"] == "_AppendAction"
    assert args["sim"]["padrao"] == "False"


def test_retrato_e_deterministico_e_serializavel():
    a = json.dumps(retratar_parser(_parser()), sort_keys=True)
    b = json.dumps(retratar_parser(_parser()), sort_keys=True)
    assert a == b
